import * as random from "./random.js"

export default {
  id: random.id(),

  gossip: {
    listenPort: 1234,
    gossipIntervalMillis: 30000,
    aliveGraceMillis: 65000,
    forgetGraceMillis: 600000,
    connectionRetryBaseMillis: 5000,
    connectionRetryBackoffFactor: 2,
    nonceWindow: 3,
  },
}
