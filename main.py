import asyncio
import sys

from amaranthie.peers import PeerServer
from amaranthie.config import config

if(len(sys.argv) > 1):
    print(f"setting listen port to {int(sys.argv[1])}")
    config["peers"]["listen_port"] = int(sys.argv[1])
s = PeerServer()
if(len(sys.argv) > 1):
    s.introduce("noone", "localhost", 2000)
asyncio.run(s.run())


