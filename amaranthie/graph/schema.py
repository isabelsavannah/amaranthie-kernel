import strawberry
import typing
from typing import List

@strawberry.type
class LocalPeer:
    peer_id: str
    host: str
    port: int

@strawberry.type
class Query:

    @strawberry.field
    def hello() -> str:
        return "hello, world"

    #@strawberry.field
    #def local_peer(peer_id: str) -> LocalPeer:
    #    return LocalPeer(peers.running_server.peers[peer_id])

    #@strawberry.field
    #def local_peers() -> List[LocalPeer]:
    #    return [LocalPeer(peer_id=peer.address["id"], host=peer.address["host"], port=peer.address["port"]) for peer in peers.running_server.peers.values()]

schema = strawberry.Schema(query=Query)
