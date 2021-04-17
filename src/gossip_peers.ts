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
  readonly id: String
  readonly address: PeerAddress
  readonly live: boolean
  readonly useSocket: (socket: Socket) => void
}

let peers: {[key: string]: PeerState} = {}
let pendingPeers: [PeerAddress] = {}

function runPeer(peer: PeerAddress) {
  async function stateWrap() {
    try { 
      peers[peer.id] = createState()
      await peerThread()
    } catch (err) {
      log(`dropping peer ${peer.id}: ${err}`)
    } finally {  
      delete(peers[peer.id])
    }
  }

  function createState() {
    peers[peer.id] = {
      id: peer.id,
      address: peer,
      live: false,
      useSocket: () => {}
    }
  }

  async function peerThread(initialSocket?: Socket) {
    let obtainedSocket = initialSocket ? initialSocket : await obtainSocket()

    while(true) {
      // a new socket per loop
      peers[peer.id].useSocket = useSocket
      useSocket(obtainedSocket)

      while(true) {
        try {
          sendHeartbeat(peers[peer.id].socket)
          await timersPromises.setTimeout(config.gossip.gossipIntervalMillis)
        } catch (err) {
          // our socket is broken, need a new one, log this
          obtainedSocket = await obtainSocket()
          break
        }
      }
    }
  }

  function setupListen() {
    //...
  }

  function sendHeartbeat() {
    //...
  }

  function useSocket(sock: Socket) {
    if(peers[peer.id].socket)
      peers[peer.id].socket.close()

    peers[peer.id].socket = sock
    setupListen(sock)
  }

  function obtainSocket() {
    let outside = Promise.new((resolve, reject) => {
      peers[peer.id].useSocket = resolve
    })
    return connectSocket(outside)
  }

  function connectSocket(
    preemptPromise: Promise<Socket>,
    attemptNumber: number = 1)
  : Promise<Socket> {

    let attempt = Promise((resolve, reject) => {
      let candidateSocket = new net.Socket()
      candidateSocket.on('connect', () => resolve(candidateSocket))
      candidateSocket.on('error', reject)
      timers.setTimeout(config.gossip.connectionTimeoutMillis, reject)
    })

    let preemptableAttempt = Promise.race([attempt, preemptPromise])

    if(attemptNumber >= config.gossip.connectionMaxRetries) {
      return preemptableAttempt
    } else {
      let delayFactor = config.gossip.connectionRetryBackoffFactor ** (attemptNumber - 1)
      let delay = config.gossip.connectionRetryBaseMillis * delayFactor
      return preemptableAttempt
        .catch(() => timersPromises.setTimeout(delay))
        .then(() => connectSocket(preemptPromise, attemptNumber+1))
    }
  }
}

export function GossipPeers(): Net{
  log("initializing net")


  function evaluateNewPeer() {
   if(!pendingPeers.length) {
      return

    let candidatePeer = pendingPeers.pop()
    if(peers.some(peer => peer.id === candidatePeer.id))
      evaluateNewPeer()

    peers[peer.id] = initPeer(peer)
  }

  function registerPeer(peer: PeerAddress, socket?: Socket) {
    if(peers[peer.id]) {
      if(socket) {
        peers[peer.id].offerSocket(socket);
        return
      }
    }
    runPeer(peer, socket)
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

