-- Independent public Lua view; all network/TLS stays with the bounded host.
local plugin = {}
local state
local instance = 0
local R = 6371.0088
local PI = math.pi
local function finite(n) return type(n)=="number" and n==n and n~=math.huge and n~=-math.huge end
local function number(n,lo,hi,fallback)
    return finite(n) and n>=lo and n<=hi and n or fallback
end
local function short(s,n)
    if type(s)~="string" then return "" end
    local first,last=1,math.min(#s,n)
    while first<=last and string.byte(s,first)<=32 do first=first+1 end
    while last>=first and string.byte(s,last)<=32 do last=last-1 end
    -- Provider identifiers are ASCII. Reject control/non-ASCII instead of truncating UTF-8.
    for i=first,last do local c=string.byte(s,i);if c<32 or c>126 then return "" end end
    return string.sub(s,first,last)
end
local function hex(s)
    if type(s)~="string" or #s~=6 then return nil end
    for i=1,6 do local c=string.byte(s,i);if not ((c>=48 and c<=57) or (c>=65 and c<=70) or (c>=97 and c<=102)) then return nil end end
    return string.lower(s)
end
local function distance(lat,lon)
    local a,b=state.lat*PI/180,lat*PI/180
    local dlat=(lat-state.lat)*PI/180;local dlon=(lon-state.lon)*PI/180
    local h=math.sin(dlat/2)^2+math.cos(a)*math.cos(b)*math.sin(dlon/2)^2
    return 2*R*math.asin(math.sqrt(math.max(0,math.min(1,h))))
end
local function capability(ctx)
    return type(ctx.http)=="table" and type(ctx.http.request)=="function" and type(ctx.http.cancel)=="function"
end
local function message(da,en) state.message=state.english and en or da end
local function age()
    if state.fetched==nil then return nil end
    return math.max(0,math.floor((state.now-state.fetched)/1000))
end
local function render(ctx)
    if not state.visible or state.destroyed then return end
    local elapsed=age()
    local status=state.message
    if elapsed then
        status=status..string.format(state.english and " · data age %ds" or " · data %ds gamle",elapsed)
    end
    ctx.ui.set_text("status",status)
    ctx.ui.set_text("area",string.format("%.4f, %.4f · %.0f km · %d %s",state.lat,state.lon,state.radius,#state.aircraft,state.english and "aircraft" or "fly"))
    local start=math.floor((state.cursor-1)/3)*3+1
    for row=1,3 do
        local i=start+row-1;local a=state.aircraft[i];local text="-"
        if a then
            local altitude=a.altitude and string.format(state.metric and "%.0f m" or "%.0f ft",state.metric and a.altitude or a.altitude/0.3048) or "?"
            local speed=a.speed and string.format(state.metric and "%.0f km/t" or "%.0f kn",state.metric and a.speed or a.speed/1.852) or "?"
            local heading=a.heading and string.format("%.0f°",a.heading) or "?"
            local dist=string.format(state.metric and "%.1f km" or "%.1f NM",state.metric and a.distance or a.distance/1.852)
            text=(i==state.cursor and "> " or "")..a.callsign.." · "..dist.." · "..altitude.." · "..speed.." · "..heading
            if a.seen+ (elapsed or 0)>60 then text=text..(state.english and " · OLD" or " · GAMMEL") end
        end
        ctx.ui.set_text("row"..row,text)
    end
    local selected=state.aircraft[state.cursor]
    ctx.ui.set_text("details",selected and ((selected.registration~="" and selected.registration or selected.hex).." · "..(selected.kind~="" and selected.kind or "?")..string.format(" · %.4f, %.4f",selected.lat,selected.lon)) or
        (state.english and "No recent positions within the chosen radius" or "Ingen friske positioner inden for valgt radius"))
end
local function refresh(ctx)
    if not capability(ctx) then message("Kræver en nyere core med Flight-netværk.","Requires a newer core with Flight networking.");return end
    if state.pending or state.now<state.next then return end
    state.sequence=state.sequence+1
    local tag=tostring(state.instance)..":"..state.sequence
    local url=string.format("https://opendata.adsb.fi/api/v3/lat/%.5f/lon/%.5f/dist/%.3f",state.lat,state.lon,state.radius/1.852)
    local id=ctx.http.request({method="GET",url=url,tag=tag,timeout_ms=8000,max_response_bytes=32768})
    state.next=state.now+state.interval
    if not id then message("Netværk optaget; prøver igen senere.","Network busy; retrying later.");return end
    state.pending={id=id,tag=tag};message("Henter flydata...","Loading aircraft...")
end
local function parse(body)
    if type(body)~="table" or type(body.ac)~="table" or #body.ac>80 then return nil end
    local items,seen={},{}
    for _,row in ipairs(body.ac) do
        if type(row)~="table" then return nil end
        local id=hex(row.hex)
        local lat=number(row.lat,-90,90,nil);local lon=number(row.lon,-180,180,nil)
        local seconds=number(row.seen_pos,0,60,nil)
        if id and not seen[id] and lat and lon and seconds then
            seen[id]=true
            local dist=distance(lat,lon)
            local ground=row.alt_baro=="ground"
            if dist<=state.radius and (not ground or state.show_ground) then
                local callsign=short(row.flight,16)
                local feet=ground and 0 or number(row.alt_baro,-2000,100000,nil)
                local knots=number(row.gs,0,2000,nil)
                items[#items+1]={hex=id,callsign=callsign~="" and callsign or id,registration=short(row.r,16),kind=short(row.t,8),
                    lat=lat,lon=lon,seen=seconds,distance=dist,altitude=feet and feet*0.3048 or nil,
                    speed=knots and knots*1.852 or nil,heading=number(row.track,0,360,nil)}
            end
        end
    end
    table.sort(items,function(a,b)if a.distance==b.distance then return a.hex<b.hex end;return a.distance<b.distance end)
    while #items>state.maximum do table.remove(items) end
    return items
end
function plugin.create(ctx)
    local c=type(ctx.config)=="table" and ctx.config or {}
    instance=instance+1
    state={instance=instance,visible=true,destroyed=false,english=c.language=="en",lat=number(c.latitude,-85,85,55.6761),lon=number(c.longitude,-180,180,12.5683),
        radius=number(c.radius_km,1,450,30),interval=1000*math.floor(number(c.refresh_seconds,10,300,15)),
        maximum=math.floor(number(c.max_aircraft,1,80,30)),show_ground=c.show_ground==true,
        now=0,next=0,sequence=0,metric=true,aircraft={},cursor=1,message=""}
    ctx.ui.page({title=state.english and "Flight · nearby aircraft" or "Flight · fly i nærheden"})
    for _,id in ipairs({"status","area","row1","row2","row3","details"}) do ctx.ui.label({id=id,text=" "}) end
    ctx.ui.label({id="attribution",text="Data: adsb.fi · https://adsb.fi/"})
    ctx.ui.button({id="previous",text=state.english and "Previous" or "Forrige",event="previous"})
    ctx.ui.button({id="next",text=state.english and "Next" or "Næste",event="next"})
    ctx.ui.button({id="refresh",text=state.english and "Refresh" or "Opdater",event="refresh"})
    ctx.ui.button({id="units",text=state.english and "Units" or "Enheder",event="units"})
    message("Klar til at hente flydata","Ready to fetch aircraft");render(ctx)
end
function plugin.show(ctx)
    if not state or state.destroyed then return end
    state.visible=true;refresh(ctx);render(ctx)
end
function plugin.hide(ctx)
    if not state then return end
    state.visible=false
    if state.pending and capability(ctx) then ctx.http.cancel(state.pending.id) end
    state.pending=nil
end
function plugin.destroy(ctx)
    if not state then return end
    plugin.hide(ctx);state.destroyed=true;state.aircraft={}
end
function plugin.event(ctx,event)
    if not state or state.destroyed or not state.visible or type(event)~="table" then return end
    if finite(event.now_ms) and event.now_ms>=state.now then state.now=event.now_ms end
    if event.name=="http" then
        local pending=state.pending
        if not pending or event.id~=pending.id or event.tag~=pending.tag then return end
        state.pending=nil
        state.next=math.max(state.next,state.now+state.interval)
        if event.status==429 then
            local wait=number(event.retry_after_ms,0,9007199254740000,60000)
            state.next=math.max(state.next,state.now+wait);message("Datakilden beder om en pause.","Data provider requested a pause.")
        elseif event.status~=200 or event.error then message("Flydata kunne ikke hentes.","Could not fetch aircraft.")
        else
            local items=parse(event.json)
            if not items then message("Ugyldigt svar fra flytjenesten.","Invalid aircraft response.")
            else
                local selected=state.aircraft[state.cursor] and state.aircraft[state.cursor].hex
                state.aircraft=items;state.cursor=1;state.fetched=state.now
                for i,a in ipairs(items)do if a.hex==selected then state.cursor=i;break end end
                message(#items>0 and "Live flydata" or "Ingen friske fly fundet",#items>0 and "Live aircraft" or "No recent aircraft found")
                if event.json.truncated then state.message=state.message..(state.english and " · response limited" or " · svaret er begrænset") end
            end
        end
    elseif event.name=="tick" or event.name=="refresh" then refresh(ctx)
    elseif event.name=="previous" then state.cursor=math.max(1,state.cursor-1)
    elseif event.name=="next" then state.cursor=math.max(1,math.min(#state.aircraft,state.cursor+1))
    elseif event.name=="units" then state.metric=not state.metric end
    render(ctx)
end
return plugin
