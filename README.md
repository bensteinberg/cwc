# cwc

`cwc` is continuous wave chat, a toy for sending messages in Morse
code via the web.

## Development

The application is in two parts: a server, written in Python, which is
essentially the chat server from the [Quart
tutorial](https://quart.palletsprojects.com/en/latest/tutorials/chat_tutorial.html),
and the front-end client, written in Vue. Setting up the server
requires [Poetry](https://python-poetry.org/), and looks like this:

```
cd cwc-server
poetry install
```

Setting up the client requires `npm`:

```
cd cwc-client
npm install
```

To try it out locally, run 

```
cd cwc-server
poetry run start
```

and in another terminal, run

```
cd cwc-client
npm run dev
```

You should then be able to visit http://localhost:5173/ to use the
application.

## Deployment

(This is work in progress.)

In the `cwc-client/` directory, create the file
`.env.production.local` with the line 

```
VITE_WEBSOCKET=wss://<your hostname here>/ws
```

then run 

```
npm run build
```

Copy the repo's contents, without `node_modules/`, to the machine
where you'll be serving it.

Run the application like this

```
poetry run hypercorn cwc_server:app
```

TODO: example nginx stanza and systemd service file

## Future work

Features that may be added later include

- a toggle for QSK aka full break-in; this might queue messages when
  turned off, or queue them for a limited amount of time
- better/controllable declicking of audio
- a decoder and keyer allowing input in Morse via keyboard or key
- channels: a simulation of different radio frequencies
- a mechanism for including messages from external sources, like Slack
- some mechanism for auth
- serve both parts of the application from a subdirectory
