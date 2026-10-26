-- Independently written Lua controller. No private firmware, tokens or bridge.
-- HTTP binding below is a documented proposal; current dev-core has no HTTP/OAuth.
local plugin = {}
local state
local lifetime = 0
local BASE = "https://api.spotify.com/v1"
local ids = {"previous", "play", "next", "quieter", "louder", "shuffle", "repeat", "devices", "library"}
local words = {
    da = {previous="Forrige", play="Afspil", pause="Pause", next="Næste", quieter="Lavere", louder="Højere",
        shuffle="Bland", repeat_button="Gentag", devices="Højttalere", library="Bibliotek", choose="Vælg", back="Tilbage",
        missing="Afventer HTTP/OAuth i core. Ingen forbindelse til Spotify.", select="Vælg en højttaler først.",
        empty="Intet at vise", loading="Henter…", ready="Klar", no_device="Ingen tilgængelige højttalere",
        busy="Afventer igangværende handling", failed="Handlingen mislykkedes. Ingen automatisk gentagelse.",
        login="Tilslut Spotify under core-indstillinger.", forbidden="Spotify afviser adgang; kontrollér konto og tilladelser.",
        limited="Spotify beder om en pause. Handlingen gentages ikke.", unavailable="Valgt højttaler er væk eller kan ikke styres.",
        invalid="Ugyldigt svar fra Spotify", other="En anden højttaler er aktiv. Ingen gammel sang vises.",
        quiet="Lydstyrke er ikke tilgængelig på denne højttaler.", query="Indtast søgetekst i pluginets indstillinger.",
        playlists="Mine playlister", liked="Gemte sange", search="Søgning", no_play="Vælg en afspillelig sang, kunstner, playliste eller et album.",
        full="Kommandokøen er fuld", changed="Højttaler valgt. Der startes ikke automatisk musik."},
    en = {previous="Previous", play="Play", pause="Pause", next="Next", quieter="Quieter", louder="Louder",
        shuffle="Shuffle", repeat_button="Repeat", devices="Speakers", library="Library", choose="Choose", back="Back",
        missing="Waiting for core HTTP/OAuth. Not connected to Spotify.", select="Choose a speaker first.",
        empty="Nothing to show", loading="Loading…", ready="Ready", no_device="No available speakers",
        busy="Waiting for the current action", failed="Action failed. No automatic retry.",
        login="Connect Spotify in core settings.", forbidden="Spotify denied access; check account and permissions.",
        limited="Spotify requested a pause. The action will not be retried.", unavailable="The selected speaker is missing or restricted.",
        invalid="Invalid Spotify response", other="Another speaker is active. Old track metadata is cleared.",
        quiet="Volume control is unavailable for this speaker.", query="Enter search text in plugin settings.",
        playlists="My playlists", liked="Liked songs", search="Search", no_play="Choose a playable track, artist, playlist or album.",
        full="Command queue is full", changed="Speaker selected. Playback does not start automatically."}
}

local function finite(n) return type(n)=="number" and n==n and n~=math.huge and n~=-math.huge end
local function integer(n, low, high, fallback)
    if not finite(n) then return fallback end
    return math.max(low, math.min(high, math.floor(n)))
end
local function text(value, limit)
    if type(value)~="string" then return "" end
    value=value:gsub("[%z\1-\31]", " ")
    local n=math.min(#value, limit or 110)
    while n>0 and n<#value do
        local b=value:byte(n+1)
        if b<128 or b>=192 then break end
        n=n-1
    end
    return value:sub(1,n)
end
local function identifier(value)
    return type(value)=="string" and #value>0 and #value<=128 and value:match("^[A-Za-z0-9_-]+$") and value or nil
end
local function uri(value)
    if type(value)~="string" or #value>128 then return nil end
    for _,kind in ipairs({"track", "album", "artist", "playlist"}) do
        if value:match("^spotify:"..kind..":[A-Za-z0-9]+$") then return value end
    end
end
local function encode(value)
    return (value:gsub("[^A-Za-z0-9_.~-]", function(c) return string.format("%%%02X", string.byte(c)) end))
end
local function message(key) state.message=state.words[key] or key end
local function available(ctx)
    return type(ctx.http)=="table" and type(ctx.http.request)=="function" and type(ctx.http.cancel)=="function"
end
local function clock(event)
    if finite(event.now_ms) and event.now_ms>=state.now then state.now=event.now_ms end
end
local function clear_pending(ctx)
    local pending=state.pending
    state.pending=nil; state.epoch=state.epoch+1
    if pending and available(ctx) then ctx.http.cancel(pending.id) end
end
local function item_title(item)
    if type(item)~="table" then return "", "" end
    local artist=""
    if type(item.artists)=="table" and type(item.artists[1])=="table" then artist=text(item.artists[1].name,60) end
    return text(item.name,90),artist
end
local function render(ctx)
    if not state or not state.visible or state.destroyed then return end
    local title, detail="Spotify", state.target and state.target.name or state.words.select
    if state.mode=="devices" then
        local room=state.rooms[state.cursor]
        title=room and room.name or state.words.no_device
        detail=state.words.devices.." · "..state.cursor.."/"..#state.rooms
    elseif state.mode~="player" then
        local item=state.items[state.cursor]
        title,detail=item_title(item)
        if title=="" then title=state.words.empty end
        detail=state.words[state.mode].." · "..state.cursor.."/"..#state.items..(detail~="" and " · "..detail or "")
    elseif state.playback then
        title,detail=item_title(state.playback.item)
        if title=="" then title=state.words.empty end
        detail=(state.target and state.target.name or "")..(detail~="" and " · "..detail or "")
        if state.volume then detail=detail.." · "..state.volume.."%" end
    end
    ctx.ui.set_text("title",text(title,120))
    ctx.ui.set_text("detail",text(detail,150))
    ctx.ui.set_text("status",text(state.message,150))
    for _,id in ipairs(ids) do
        local label=state.words[id=="repeat" and "repeat_button" or id]
        if id=="play" then
            label=state.mode=="devices" and state.words.choose or
                (state.mode=="player" and state.playback and state.playback.is_playing and state.words.pause or state.words.play)
        elseif id=="devices" and state.mode=="devices" then label=state.words.back end
        ctx.ui.set_text(id,label)
    end
end
local function request(ctx,kind,path,method,body,command)
    if state.pending or state.now<state.blocked_until or not available(ctx) then return false end
    state.sequence=state.sequence+1
    local tag=tostring(state.instance)..":"..tostring(state.epoch)..":"..tostring(state.sequence)
    local id=ctx.http.request({method=method or "GET",url=BASE..path,credential="spotify",json=body,
        tag=tag,timeout_ms=8000,max_response_bytes=32768})
    if id==nil then message("failed"); return false end
    state.pending={id=id,tag=tag,kind=kind,command=command}
    message("loading"); return true
end
local function rooms(body)
    if type(body)~="table" or type(body.devices)~="table" or #body.devices>48 then return nil end
    local result,seen={},{}
    for _,room in ipairs(body.devices) do
        if type(room)~="table" then return nil end
        local id=identifier(room.id)
        if id and seen[id] then return nil end
        if id then seen[id]=true end
        if id and room.is_restricted==false then
            result[#result+1]={id=id,name=(text(room.name,80)~="" and text(room.name,80) or "Spotify Connect"),supports_volume=room.supports_volume==true}
        end
    end
    return result
end
local function find_room(list,id)
    for _,room in ipairs(list) do if room.id==id then return room end end
end
local function status(ctx)
    state.next_poll=state.now+state.poll_ms
    if not state.target then return request(ctx,"devices","/me/player/devices") end
    return request(ctx,"status","/me/player")
end
local function browse(ctx)
    local path
    if state.mode=="playlists" then path="/me/playlists?limit=10"
    elseif state.mode=="liked" then path="/me/tracks?limit=10"
    elseif state.mode=="search" then
        if state.query=="" then state.items={}; message("query"); return end
        path="/search?type=track&q="..encode(state.query).."&limit=10"
        if state.country~="GLOBAL" then path=path.."&market="..state.country end
    end
    if path then request(ctx,"browse",path) end
end
local function pump(ctx)
    if state.pending or not state.visible or state.now<state.blocked_until then return end
    local command=table.remove(state.queue,1)
    if command then
        if not state.target or state.target.id~=command.target then state.queue={}; message("unavailable"); return end
        request(ctx,"validate","/me/player/devices","GET",nil,command)
    elseif state.needs_status then
        state.needs_status=false; status(ctx)
    end
end
local function enqueue(ctx,action,path,method,body,volume)
    if not state.target then message("select"); return end
    if state.now<state.blocked_until then message("limited"); return end
    if #state.queue>=8 then message("full"); return end
    state.queue[#state.queue+1]={target=state.target.id,action=action,path=path,method=method,body=body,volume=volume}
    pump(ctx)
end
local function control(ctx,name)
    if not state.target then message("select"); return end
    local device="device_id="..encode(state.target.id)
    if name=="next" or name=="previous" then
        enqueue(ctx,name,"/me/player/"..name.."?"..device,"POST")
    elseif name=="play" then
        if state.pending or #state.queue>0 then message("busy"); return end
        local playing=state.playback and state.playback.is_playing==true
        enqueue(ctx,name,"/me/player/"..(playing and "pause" or "play").."?"..device,"PUT")
    elseif name=="quieter" or name=="louder" then
        if not state.target.supports_volume or state.volume==nil then message("quiet"); return end
        local baseline=state.volume
        if state.pending and state.pending.command and state.pending.command.volume then baseline=state.pending.command.volume end
        for _,queued in ipairs(state.queue) do if queued.volume then baseline=queued.volume end end
        local value=math.max(0,math.min(100,baseline+(name=="louder" and state.step or -state.step)))
        enqueue(ctx,name,"/me/player/volume?volume_percent="..value.."&"..device,"PUT",nil,value)
    elseif name=="shuffle" or name=="repeat" then
        if not state.playback then message("invalid"); return end
        if state.pending or #state.queue>0 then message("busy"); return end
        if name=="shuffle" then
            if type(state.playback.shuffle_state)~="boolean" then message("invalid"); return end
            enqueue(ctx,name,"/me/player/shuffle?state="..tostring(not state.playback.shuffle_state).."&"..device,"PUT")
        else
            local value=({off="context",context="track",track="off"})[state.playback.repeat_state]
            if not value then message("invalid"); return end
            enqueue(ctx,name,"/me/player/repeat?state="..value.."&"..device,"PUT")
        end
    end
end
local function reply(ctx,event)
    local pending=state.pending
    if not pending or event.id~=pending.id or event.tag~=pending.tag then return end
    state.pending=nil
    if event.status==429 then
        local delay=finite(event.retry_after_ms) and math.max(0,event.retry_after_ms) or 60000
        state.blocked_until=math.max(state.blocked_until,state.now+delay)
        state.queue={}; state.needs_status=false; message("limited"); return
    end
    if event.error or not finite(event.status) or event.status<200 or event.status>=300 then
        state.queue={}; state.needs_status=false
        message(event.status==401 and "login" or event.status==403 and "forbidden" or "failed")
        -- The outcome of a control request may be unknown. Never replay or fall back.
        return
    end
    if pending.kind=="devices" or pending.kind=="validate" then
        local list=rooms(event.json)
        if not list then state.queue={}; message("invalid"); return end
        state.rooms=list
        if pending.kind=="validate" then
            local command=pending.command
            local room=find_room(list,command.target)
            if not room or not state.target or room.id~=state.target.id or
                (command.volume and not room.supports_volume) then
                state.queue={}; state.playback=nil; state.volume=nil; message("unavailable"); return
            end
            request(ctx,"command",command.path,command.method,command.body,command)
        else
            local desired=state.target and state.target.id or state.default_id
            local selected=desired and find_room(list,desired)
            if selected then state.target=selected; state.needs_status=true
            elseif state.target then state.target=nil; state.playback=nil; state.volume=nil; message("unavailable")
            else message(#list>0 and "select" or "no_device") end
        end
    elseif pending.kind=="command" then
        state.needs_status=true; message("ready")
    elseif pending.kind=="status" then
        state.playback=nil; state.volume=nil
        local body=event.json
        if event.status==204 then message("empty")
        elseif type(body)~="table" or type(body.device)~="table" or type(body.is_playing)~="boolean" then message("invalid")
        elseif not state.target or body.device.id~=state.target.id then message("other")
        elseif body.device.is_restricted~=false then message("unavailable")
        else
            state.playback={is_playing=body.is_playing,shuffle_state=body.shuffle_state,repeat_state=body.repeat_state,item=body.item}
            if state.target.supports_volume then state.volume=integer(body.device.volume_percent,0,100,nil) end
            message("ready")
        end
    elseif pending.kind=="browse" then
        local body=event.json
        if state.mode=="search" and type(body)=="table" then body=body.tracks end
        if type(body)~="table" or type(body.items)~="table" or #body.items>10 then message("invalid"); return end
        state.items={}; state.cursor=1
        for _,item in ipairs(body.items) do
            if state.mode=="liked" and type(item)=="table" then item=item.track end
            if type(item)=="table" then
                local title,artist=item_title(item)
                local item_uri=uri(item.uri)
                if item_uri then state.items[#state.items+1]={name=title,artists={{name=artist}},uri=item_uri} end
            end
        end
        message(#state.items>0 and "ready" or "empty")
    end
    pump(ctx)
end

function plugin.create(ctx)
    local config=type(ctx.config)=="table" and ctx.config or {}
    local country=({GLOBAL=true,DK=true,SE=true,DE=true,NO=true,FI=true,GB=true,US=true})[config.country] and config.country or "GLOBAL"
    lifetime=lifetime+1
    state={instance=lifetime,words=words[config.language] or words.da,mode="player",visible=true,destroyed=false,rooms={},items={},cursor=1,
        queue={},sequence=0,epoch=0,now=0,blocked_until=0,next_poll=0,needs_status=false,
        poll_ms=1000*integer(config.poll_seconds,10,300,15),step=integer(config.volume_step,1,10,5),
        country=country,query=text(config.search_query,120),default_id=identifier(config.device_id)}
    ctx.ui.page({title="Spotify og Sonos"})
    for _,id in ipairs({"title","detail","status"}) do ctx.ui.label({id=id,text=" "}) end
    for _,id in ipairs(ids) do ctx.ui.button({id=id,text="…",event=id}) end
    message(available(ctx) and "select" or "missing"); render(ctx)
end
function plugin.show(ctx)
    if not state or state.destroyed then return end
    state.visible=true
    if available(ctx) and not state.pending then request(ctx,"devices","/me/player/devices") end
    render(ctx)
end
function plugin.hide(ctx)
    if not state then return end
    state.visible=false; state.queue={}; state.needs_status=false; clear_pending(ctx)
end
function plugin.destroy(ctx)
    if not state then return end
    state.visible=false; state.destroyed=true; state.queue={}; state.rooms={}; state.items={}; clear_pending(ctx)
end
function plugin.event(ctx,event)
    if not state or state.destroyed or not state.visible or type(event)~="table" then return end
    clock(event)
    if event.name=="http" then reply(ctx,event)
    elseif event.name=="tick" then
        if available(ctx) and state.now>=state.blocked_until then
            pump(ctx)
            if not state.pending and state.mode=="player" and state.now>=state.next_poll then status(ctx) end
        end
    elseif not available(ctx) then message("missing")
    elseif event.name=="devices" or event.name=="library" then
        if #state.queue>0 or (state.pending and (state.pending.kind=="command" or state.pending.kind=="validate")) then message("busy")
        else
            clear_pending(ctx); state.cursor=1; state.items={}
            if event.name=="devices" then
                state.mode=state.mode=="devices" and "player" or "devices"
                if state.mode=="devices" then request(ctx,"devices","/me/player/devices") else status(ctx) end
            else
                state.mode=({player="playlists",devices="playlists",playlists="liked",liked="search",search="player"})[state.mode]
                if state.mode=="player" then status(ctx) else browse(ctx) end
            end
        end
    elseif state.mode=="devices" then
        if event.name=="previous" or event.name=="next" then
            state.cursor=math.max(1,math.min(#state.rooms,state.cursor+(event.name=="next" and 1 or -1)))
        elseif event.name=="play" then
            local selected=state.rooms[state.cursor]
            if selected then
                clear_pending(ctx); state.queue={}; state.target=selected; state.playback=nil; state.volume=nil
                state.mode="player"; message("changed"); status(ctx)
            end
        end
    elseif state.mode~="player" then
        if event.name=="previous" or event.name=="next" then
            state.cursor=math.max(1,math.min(#state.items,state.cursor+(event.name=="next" and 1 or -1)))
        elseif event.name=="play" then
            local item=state.items[state.cursor]
            if item and uri(item.uri) and state.target then
                local body=item.uri:match("^spotify:track:") and {uris={item.uri}} or {context_uri=item.uri}
                enqueue(ctx,"browse_play","/me/player/play?device_id="..encode(state.target.id),"PUT",body)
            else message("no_play") end
        end
    else control(ctx,event.name) end
    render(ctx)
end
return plugin
