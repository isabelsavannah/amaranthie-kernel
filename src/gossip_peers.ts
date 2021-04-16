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

interface Peer {
  readonly address: PeerAddress
  readonly lastKnownLive: number
  readonly knownLive: boolean
  readonly useSocket: (socket: Socket) => void
}

function initPeer(peer: PeerAddress, destroy: () => void): Peer {
  let lastNonceSent = []
  let lastNonceRecvd = 0
  let socket = null
  let openSocketAttempts = 0

  let publicState = {
    address: peer,
    knownLive: false,
    lastKnownLive: Date.now(),
    useSocket: () => void,
  }

  async function runPeer() {
    while(true) {
      try {
        let socket = await getSocket()
      } catch (err) {
        destroy()
        break
      }


      
    getSocket()
      .then(/*send heartbeat messages until error/*, reject)
      .catch(


  function getSocket(attemptNumber: number = 1): Promise<Socket> {
    let attempt = Promise((resolve, reject) => {
      let candidateSocket = new net.Socket()
      candidateSocket.on('connect', () => resolve(candidateSocket))
      candidateSocket.on('error', reject)
    })

    if(attemptNumber >= config.gossip.connectionMaxRetries) {
      return attempt
    } else {
      let delayFactor = config.gossip.connectionRetryBackoffFactor ** (attemptNumber - 1)
      let delay = config.gossip.connectionRetryBaseMillis * delayFactor
      return attempt
        .catch(() => timersPromises.setTimeout(delay))
        .then(() => getSocket(attemptNumber+1))
    }
  }

  function tick(socket: Socket) {
    // send heartbeat
    // then weait
    // then repeat
    // if we fail, open a new socket
    // 


  function run() {
    getSocket()
      .then(

  async function tend() {
    while(true) {
      let socket = await getSocket()

      



}
    


export function GossipPeers(): Net{
  log("initializing net")

  let peers: {[key: string]: PeerState} = {}
  let pendingPeers: [PeerAddress] = {}

  function evaluateNewPeer() {
   if(!pendingPeers.length) {
      return

    let candidatePeer = pendingPeers.pop()
    if(peers.some(peer => peer.id === candidatePeer.id))
      evaluateNewPeer()

    peers[peer.id] = initPeer(peer)
  }

  function tick() {
    //...
  }

  return {
    start: function() {
      tick()
    },

    introduce: function (host: string, port: number) {
      return
    },
  }
}
