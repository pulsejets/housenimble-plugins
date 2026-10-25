-- HouseNimble development API 1: owner-provisioned Lua core required.
-- No sockets, HTTP client, credentials, files, LVGL pointers or core internals.
local count = 0
local plugin = {}

function plugin.create(ctx)
    count = tonumber(ctx.storage.get("count", 0)) or 0
    count = math.max(0, math.min(9999, math.floor(count)))
    ctx.ui.page({ title = "Mit første plugin" })
    ctx.ui.label({ id = "counter", text = tostring(count) })
    ctx.ui.button({ id = "increase", text = "Tæl op", event = "increase" })
end

function plugin.show(ctx)
    ctx.ui.set_text("counter", tostring(count))
end

function plugin.hide(ctx)
    -- Core cancels this plugin's pending requests/timers when it is hidden.
end

function plugin.event(ctx, event)
    if event.name == "increase" then
        count = (count + 1) % 10000
        ctx.ui.set_text("counter", tostring(count))
        -- Only an explicit interaction writes flash; no periodic write loop.
        ctx.storage.set("count", count)
    end
end

function plugin.destroy(ctx)
    -- Core destroys owned widgets, requests, timers and handles after return.
end

return plugin
