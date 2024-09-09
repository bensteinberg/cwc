import asyncio
import os

from quart import Quart, render_template, websocket, send_from_directory

from cwc_server.broker import Broker


app = Quart(
    __name__,
    static_folder = "../../../cwc-client/dist/assets",
    template_folder = "../../../cwc-client/dist"
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
