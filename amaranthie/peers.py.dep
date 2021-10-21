import asyncio
import json
import random
import logging

from collections import deque
from dataclasses import dataclass

from amaranthie.config import config
from amaranthie.asy import create_task_watch_error

log = logging.getLogger(__name__)
log.trace = lambda *x: log.log(5, *x)
protocol_channel = "local_peers_protocol"

running_server = None

def peer_address(id, host, port):
    return {"id": id, "host": host, "port": port}

class ProtocolError(Exception):
    pass

# not going to bother with a reconnect protocol. just rely on discovery.
class PeerServer:
    def __init__(self):
        self.peers = {}
        self.peers_queue = []
        self.address = peer_address(config["id"], "localhost", config["peers"]["listen_port"])
        global running_server
        running_server = self

    def set_graph_port(self, port):
        self.address["graphql_port"] = port

    async def run(self):
        log.info(f"Starting server as {self.address}")
        log.warning("using hacky peers port selection")
        for i in range(100):
            try:
                attempt_listen_port = config["peers"]["listen_port"]+i
                log.trace("attempting peers listen port %s", attempt_listen_port)
                server = await asyncio.start_server(self._handle_connection, port=attempt_listen_port)
                config["peers"]["real_listen_port"] = attempt_listen_port
                log.info("selected peers listen port %s", attempt_listen_port)
                self.address["port"]=attempt_listen_port
                break
            except OSError:
                continue

        if not config["peers"]["real_listen_port"]:
            raise Exception("failed to find a peers listen port")

        self.connect_thread = create_task_watch_error(self._connect_peers())
        await server.serve_forever()

    async def _connect_peers(self): 
        while True:
            max_sleep = config["peers"]["connect_interval_seconds"]
            await asyncio.sleep(random.randrange(max_sleep/2, max_sleep))
            if len(self.peers_queue) == 0:
                continue
            address = self.peers_queue.pop()
            if self._is_new_address(address):
                log.info(f"trying to establish connection with {address}")
                create_task_watch_error(self._connect_to(address))

    async def _connect_to(self, address):
        (reader, writer) = await asyncio.open_connection(address["host"], address["port"])
        await self._handle_connection(reader, writer)

    async def _handle_connection(self, reader, writer): 
        log.debug(f"got socket with {writer.transport.get_extra_info('peername')}")
        socket = ChunkedSocket(reader, writer)
        try:
            partner = await self._handshake(socket)
            create_task_watch_error(self._socket_lifecycle(partner, socket))
        except Exception as err:
            logging.error(f"dropping unidentified socket because {err}")

    async def _handshake(self, socket):
        create_task_watch_error(socket.write_message(json.dumps(self.write_heartbeat())))
        message = await socket.read_message()
        try:
            obj = json.loads(message)
            sender = obj["sender"]
            log.info(f"socket identified as {sender}")
            self.handle_message(obj)
            return sender
        except Exception as err:
            raise ProtocolError(err)

    async def _socket_lifecycle(self, address, socket):
        try:
            peer_socket = PeerSocket(socket, self, address)
            peer_socket.address = address
            if address["id"] in self.peers.keys():
                self.peers[address["id"]].close()
            self.peers[address["id"]] = peer_socket
            await peer_socket.wait_err()
        finally:
            log.info(f"connection with {address} broken")
            if address["id"] in self.peers:
                self.peers[address["id"]].close()
                del self.peers[address["id"]]

    def _is_new_address(self, address):
        if(address["id"] == self.address["id"]):
            return False
        if(address["id"] in self.peers.keys()):
            return False
        return True

    def write_heartbeat(self):
        result = {"sender": self.address, "channel": protocol_channel}
        if len(self.peers) > 0:
            peer_id = random.choice(list(self.peers.keys()))
            result["peer"] = self.peers[peer_id].address
        return result

    def handle_message(self, message):
        if message["channel"] == protocol_channel:
            self._handle_heartbeat(message)
        else:
            local_pubsub.pub(message["channel"], message)

    def _handle_heartbeat(self, heartbeat):
        if "peer" in heartbeat.keys():
            peer = heartbeat["peer"]
            log.trace("handling a heartbeat from %s", peer["id"])
            if self._is_new_address(peer):
                self.peers_queue.append(peer)

    def introduce(self, id, host, peer):
        self.peers_queue.append(peer_address(id, host, peer))

class PeerSocket:
    def __init__(self, socket, server, address):
        self.socket = socket
        self.read_thread = asyncio.create_task(self._read())
        self.write_thread = asyncio.create_task(self._write())
        self.server = server
        self.peer_address = address

    async def _read(self):
        while True:
            message = await self.socket.read_message()
            try:
                obj = json.loads(message)
                self.server.handle_message(obj)
            except Exception as err:
                log.error(f"ignoring message {message} because {err}")

    async def _write(self):
        while True:
            log.trace("writing a heartbeat to %s", self.address["id"])
            await self.socket.write_message(json.dumps(self.server.write_heartbeat()))
            max_sleep = config["peers"]["heartbeat_interval_seconds"]
            await asyncio.sleep(max_sleep/2, max_sleep)

    async def wait_err(self):
        await asyncio.wait([self.read_thread, self.write_thread], return_when=asyncio.FIRST_EXCEPTION)

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
