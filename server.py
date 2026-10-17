#!/usr/bin/env python3
"""
NeonSyncs Server
================
Serveur de synchronisation de lecture vidéo, inspiré de Syncplay.
Les clients se connectent, rejoignent une "room", et le serveur
rediffuse l'état de lecture (pause/lecture, position, fichier) à
tous les autres membres de la room.

Protocole : messages JSON séparés par '\n' (newline-delimited JSON).

Messages client -> serveur :
  {"type": "hello", "room": "salon1", "username": "badre", "password": "..."}
  {"type": "state", "paused": true/false, "position": 12.34,
   "file": "nom_du_fichier.mkv", "duration": 5400.0}
  {"type": "chat", "message": "salut"}
  {"type": "ping", "t": 1234.5}

Messages serveur -> client :
  {"type": "state", "paused": ..., "position": ..., "file": ...,
   "duration": ..., "from": "username", "server_time": ...}
  {"type": "userlist", "users": ["a", "b"]}
  {"type": "chat", "from": "...", "message": "..."}
  {"type": "pong", "t": 1234.5}
  {"type": "error", "message": "..."}

Usage:
  python3 server.py --host 0.0.0.0 --port 8999
  python3 server.py --host 0.0.0.0 --port 8999 --password monmotdepasse
"""
import asyncio
import json
import time
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("neonsyncs-server")


class Client:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.username = None
        self.room = None

    async def send(self, obj: dict):
        try:
            data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
            self.writer.write(data)
            await self.writer.drain()
        except (ConnectionResetError, BrokenPipeError):
            pass


class Room:
    def __init__(self, name: str):
        self.name = name
        self.clients: set[Client] = set()
        # Dernier état connu de la room
        self.state = {
            "file": None,
            "duration": 0.0,
            "paused": True,
            "position": 0.0,
            "position_at": time.time(),  # timestamp serveur du dernier update
        }

    def current_position(self) -> float:
        """Estime la position actuelle en tenant compte du temps écoulé si en lecture."""
        if self.state["paused"]:
            return self.state["position"]
        elapsed = time.time() - self.state["position_at"]
        return self.state["position"] + elapsed

    async def broadcast(self, obj: dict, exclude: Client = None):
        dead = []
        for c in self.clients:
            if c is exclude:
                continue
            try:
                await c.send(obj)
            except Exception:
                dead.append(c)
        for c in dead:
            self.clients.discard(c)

    async def broadcast_userlist(self):
        users = [c.username for c in self.clients if c.username]
        await self.broadcast({"type": "userlist", "users": users})


class SyncServer:
    def __init__(self, password: str = None):
        self.rooms: dict[str, Room] = {}
        self.password = password or None

    def get_room(self, name: str) -> Room:
        if name not in self.rooms:
            self.rooms[name] = Room(name)
        return self.rooms[name]

    async def handle_client(self, reader, writer):
        peer = writer.get_extra_info("peername")
        client = Client(reader, writer)
        log.info(f"Nouvelle connexion: {peer}")
        reason = "fermeture normale"
        try:
            while True:
                line = await reader.readline()
                if not line:
                    reason = "le client a ferme la connexion (ou coupure reseau/NAT)"
                    break
                try:
                    msg = json.loads(line.decode("utf-8").strip())
                except json.JSONDecodeError:
                    continue
                await self.dispatch(client, msg)
        except (ConnectionResetError, asyncio.IncompleteReadError) as e:
            reason = f"connexion coupee brutalement ({type(e).__name__}: {e})"
        except Exception as e:
            reason = f"erreur inattendue ({type(e).__name__}: {e})"
        finally:
            await self.disconnect(client)
            log.info(f"Déconnexion: {peer} ({client.username}) - raison: {reason}")

    async def dispatch(self, client: Client, msg: dict):
        mtype = msg.get("type")

        if mtype == "hello":
            if self.password and msg.get("password") != self.password:
                await client.send({"type": "error", "message": "Mot de passe incorrect"})
                client.writer.close()
                log.info(f"Connexion refusee (mot de passe incorrect) depuis {client.writer.get_extra_info('peername')}")
                return

            room_name = msg.get("room", "default")
            client.username = msg.get("username", "anonyme")
            client.room = self.get_room(room_name)
            client.room.clients.add(client)
            # Envoie l'état actuel de la room au nouvel arrivant
            room = client.room
            await client.send({
                "type": "state",
                "paused": room.state["paused"],
                "position": room.current_position(),
                "file": room.state["file"],
                "duration": room.state["duration"],
                "from": "server",
                "server_time": time.time(),
            })
            await room.broadcast_userlist()
            log.info(f"{client.username} a rejoint la room '{room_name}'")

        elif mtype == "state":
            if not client.room:
                return
            room = client.room
            room.state["paused"] = bool(msg.get("paused", room.state["paused"]))
            room.state["position"] = float(msg.get("position", room.state["position"]))
            room.state["position_at"] = time.time()
            if msg.get("file"):
                room.state["file"] = msg.get("file")
            if msg.get("duration"):
                room.state["duration"] = msg.get("duration")
            # Rediffuse aux autres clients de la room
            await room.broadcast({
                "type": "state",
                "paused": room.state["paused"],
                "position": room.state["position"],
                "file": room.state["file"],
                "duration": room.state["duration"],
                "from": client.username,
                "server_time": time.time(),
            }, exclude=client)

        elif mtype == "chat":
            if not client.room:
                return
            await client.room.broadcast({
                "type": "chat",
                "from": client.username,
                "message": msg.get("message", ""),
            })

        elif mtype == "ping":
            await client.send({"type": "pong", "t": msg.get("t")})

    async def disconnect(self, client: Client):
        if client.room:
            client.room.clients.discard(client)
            await client.room.broadcast_userlist()


async def main():
    parser = argparse.ArgumentParser(description="Serveur NeonSyncs")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8999)
    parser.add_argument("--password", default=None,
                         help="Mot de passe requis pour se connecter (optionnel, "
                              "recommande si le serveur est expose sur internet "
                              "via No-IP/DynDNS)")
    args = parser.parse_args()

    server_logic = SyncServer(password=args.password)
    server = await asyncio.start_server(server_logic.handle_client, args.host, args.port)
    log.info(f"Serveur NeonSyncs en écoute sur {args.host}:{args.port}")
    if args.password:
        log.info("Mot de passe active.")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
