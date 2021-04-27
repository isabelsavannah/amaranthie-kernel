import asyncio
import json
import random
import logging

from collections import deque
from dataclasses import dataclass

from amaranthie.config import config

log = logging.getLogger(__name__)

def peer_address(id, host, port):
    return {"id": id, "host": host, "port": port}

#TDD into reestablishing broken connections

class PeerServer:
    def __init__(self):
        self.peers = {}
        self.peers_queue = []
        self.address = peer_address(config["id"], "localhost", config["peers"]["listen_port"])

    async def run(self):
        log.info(f"Starting server as {self.address}")
        server = await asyncio.start_server(self._handle_connection, port=config["peers"]["listen_port"])
        self.connect_thread = asyncio.create_task(self._connect_peers())
        await server.serve_forever()

    async def _connect_peers(self): 
        while True:
            await asyncio.sleep(config["peers"]["connect_interval_seconds"])
            if len(self.peers_queue) == 0:
                continue
            address = self.peers_queue.pop()
            if self._is_new_address(address):
                log.info(f"trying to establish connection with {address}")
                asyncio.create_task(self._connect_to(address))

    async def _connect_to(self, address):
        (reader, writer) = await asyncio.open_connection(address["host"], address["port"])
        await self._handle_connection(reader, writer)

    async def _handle_connection(self, reader, writer): 
        log.debug("got socket")
        socket = ChunkedSocket(reader, writer)
        asyncio.create_task(socket.write_message(json.dumps(self.write_heartbeat())))
        message = await socket.read_message()
        try:
            obj = json.loads(message)
            sender = obj["sender"]
            log.info(f"incoming socket identified as {sender}")
            self._got_socket(sender, socket)
            self.handle_heartbeat(obj)
        except Exception as err:
            log.error(f"socket dropped because handshake message doesn't have sender: {message} {err}")

    def _got_socket(self, address, socket):
        peer_socket = PeerSocket(socket, self)
        peer_socket.address = address
        if address["id"] in self.peers.keys():
            self.peers[address["id"]].close()
        self.peers[address["id"]] = peer_socket

    def _is_new_address(self, address):
        if(address["id"] == self.address["id"]):
            return False
        if(address["id"] in self.peers.keys()):
            return False
        return True

    def write_heartbeat(self):
        result = {"sender": self.address}
        if len(self.peers) > 0:
            peer_id = random.choice(list(self.peers.keys()))
            result["peer"] = self.peers[peer_id].address
        return result

    def handle_heartbeat(self, heartbeat):
        if "peer" in heartbeat.keys():
            peer = heartbeat["peer"]
            if self._is_new_address(peer):
                self.peers_queue.append(peer)

    def introduce(self, id, host, peer):
        self.peers_queue.append(peer_address(id, host, peer))

class PeerSocket:
    def __init__(self, socket, server):
        self.socket = socket
        self.read_thread = asyncio.create_task(self._read())
        self.write_thread = asyncio.create_task(self._write())
        self.server = server

    async def _read(self):
        while True:
            message = await self.socket.read_message()
            try:
                obj = json.loads(message)
                self.server.handle_heartbeat(obj)
            except Exception as err:
                log.error(f"ignoring message {message} because {err}")

    async def _write(self):
        while True:
            await self.socket.write_message(json.dumps(self.server.write_heartbeat()))
            await asyncio.sleep(config["peers"]["heartbeat_interval_seconds"])

    def close(self):
        self.read_thread.cancel()
        self.write_thread.cancel()
        self.socket.close()

class ChunkedSocket:
    terminator = "#"

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    def _prefix(self, length):
        return f"{length}{self.terminator}".encode("utf-8")

    async def write_message(self, data):
        encoded_data = data.encode("utf-8")
        encoded_prefix = self._prefix(len(encoded_data))

        self.writer.write(encoded_prefix)
        await self.writer.drain()
        self.writer.write(encoded_data)
        await self.writer.drain()

    async def read_message(self):
        prefix = (await self.reader.readuntil(self.terminator.encode("utf-8"))).decode("utf-8")
        length = int(prefix[:-len(self.terminator)])
        return (await self.reader.readexactly(length)).decode("utf-8")

    def close(self):
        self.writer.close()
