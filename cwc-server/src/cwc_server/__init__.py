import asyncio
import json

from quart import (
    Quart,
    render_template,
    websocket,
    send_from_directory,
    request,
    abort
)

from cwc_server.broker import Broker


app = Quart(
    __name__,
    static_folder="../../../cwc-client/dist/assets",
    template_folder="../../../cwc-client/dist"
)


def run() -> None:
    app.run()


@app.get("/")
async def index():
    return await render_template("index.html")


@app.route('/favicon.ico')
async def favicon():
    return await send_from_directory(
        app.static_folder,
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

broker = Broker()


async def _receive() -> None:
    while True:
        message = await websocket.receive()
        await broker.publish(message)


@app.websocket("/ws")
async def ws() -> None:
    try:
        task = asyncio.ensure_future(_receive())
        async for message in broker.subscribe():
            await websocket.send(message)
    finally:
        task.cancel()
        await task


@app.post("/api/v1/send")
async def api_send() -> None:
    try:
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            transmission = await request.get_json()
            message = json.dumps(
                {
                    "channel": transmission["channel"],
                    "message": transmission["message"]
                }
            )
        else:
            message = json.dumps(
                {
                    "channel": int((await request.form)["channel"]),
                    "message": (await request.form)["message"]
                }
            )
        await broker.publish(message)
        return "", 200
    except KeyError:
        abort(400)
