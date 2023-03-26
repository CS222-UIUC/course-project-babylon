
const Alpaca = require("@alpacahq/alpaca-trade-api")

const API_KEY = "<Your-API-Key>"
const API_SECRET = "<Your-API-Secret>"
const alpaca = new Alpaca({
  keyId: API_KEY,
  secretKey: API_SECRET,
  paper: false
})