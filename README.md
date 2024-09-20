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

Copy the repo's contents, optionally without
`cwc-client/node_modules/` or `.git/`, to the machine where you'll be
serving it.

Run the application like this

```
poetry run hypercorn cwc_server:app
```

A systemd service file could look something like

```
[Unit]
Description=Continuous Wave Chat
After=network.target

[Service]
User=you
WorkingDirectory=/path/to/cwc-main/cwc-server
ExecStart=/path/to/.local/bin/poetry run hypercorn cwc_server:app
Type=simple
Restart=on-failure

[Install]
WantedBy=default.target
```

The stanza for an nginx reverse proxy might include

```
location / {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Host $host;
    proxy_http_version 1.1;
    proxy_buffering off;
    proxy_read_timeout 20m;
    proxy_pass http://127.0.0.1:8000/;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

## Future work

Features that may be added later include

- better/controllable declicking of audio
- a decoder and keyer allowing input in Morse via keyboard or key
- a mechanism for including messages from external sources, like Slack
- some mechanism for auth
- serve both parts of the application from a subdirectory
