from dataclasses import dataclass
from amaranthie import config

@dataclass
class LocalPeerRef:
    host: str
    port: int

def local_peers():
    base_port = config.get(config.udp_port)
    import sys
    return [LocalPeerRef('localhost', base_port+i) for i in range(8) if i != int(sys.argv[1])]
