# TCP Chat (Python)

A tiny multi-client TCP chat: one **server** (supervisor) and multiple **clients** (players).

## Prerequisites
- Python 3.8+ (standard library only)
- xterm
  
## Install
```bash
git clone https://github.com/Aeshmedai/tcp-sockets-python-chat.git
cd tcp-sockets-python-chat
```

## Run
### Server (supervisor)
```bash
python3 chat_killer_server.py <PORT>
# e.g. python3 chat_killer_server.py 42042
```

### Client (supervisor)
```bash
python3 chat_killer_client.py <SERVER_IP> <PORT>
# e.g. python3 chat_killer_client.py 127.1 42042
```

## Quick use
- Public message: type text and press Enter
- Create a user: `@username`, your session will be saved through a cookie
- Private message: `@alice hi`
- Multi-recipient: `@alice @bob secret`
- Commands (all): `!help`, `!list`, `!quit`


## supervisor
- `!start` — start/lock the room
- `@user !suspend` — suspend a player
- `@user !forgive` — restore a player
- `@user !ban` — ban a player

## Troubleshooting
- Port in use → pick another port
- Local test → use `127.0.0.1`
