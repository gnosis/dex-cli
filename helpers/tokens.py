
TOKEN_FIELDS_BASIC = 'id, name, symbol, address, decimals'

def toToken(token):
  return {
    "id": token['id'],
    "name": token['name'],
    "symbol": token['symbol'],
    "address": token['address'],
    "decimals": int (token['decimals'] or '18')
  }