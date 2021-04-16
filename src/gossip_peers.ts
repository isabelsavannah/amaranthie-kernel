import log from "./log.js"
import config from "./config.js"
import * as random from "./random.js"

interface GossipPeers {
  start: () => void
  introduce: (host: string, port: number) => void
  currentPeers: () => [PeerAddress]
}

interface PeerAddress {
  id: string
  host: string
  port: string
}

interface PeerState {
  address: PeerAddress
  lastNonceSent: number
  lastNonceRecvd: number
  lastKnownLive: number
}

export function GossipPeers(): Net{
  log("initializing net")

  let peers = []
  let pendingPeers = []
  let liveConnections = {}

  function getConnection(

  function evaluateNewPeer() {
    if(!pendingPeers.length) {
      return

    let candidatePeer = pendingPeers.pop()
    if(peers.some(peer => peer.id === candidatePeer.id))
      evalu

  function tick() {
    evaluateNewPeer
    

  return {
    start: function() {
      return
    },

    introduce: function (host: string, port: number) {
      return
    },
  }
}
