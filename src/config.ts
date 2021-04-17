import * as random from "./random.js"

export default {
  id: random.id(),

  gossip: {
    listenPort: 1234,
    gossipIntervalMillis: 30000,

    connectionRetryBaseMillis: 5000,
    connectionRetryBackoffFactor: 2,
    connectionMaxRetries: 10,
    connectionTimeoutMillis: 5000
  },
}
