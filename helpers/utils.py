from .constants import BATCH_TIME_SECONDS

def format_token(token):
  symbol = token['symbol']
  address = token['address']
  name = token['name']
  label = symbol or name

  if label:
    return label + ' (' + address + ')'
  else:
    return address

def format_integer(number):
  return str(number) # TODO: Format better the numbers

def format_amount_in_weis(amount, decimals):
  return str(amount / (10 ** decimals)) # TODO: Format better the weis

def format_date(date):
  return str(date) # TODO: Improve date formatting

def toDateFromEpoch(epoch):
  return epoch # TODO: Date from epoch

def toEtherescanLink(hash):
  return 'https://etherscan.io/tx/' + hash

def toDateFromBatchId(batchId):
  return batchId * BATCH_TIME_SECONDS # TODO: Dates in python

def calculate_price(numerator, denominator, decimals_numerator, decimals_denominator):
  return numerator/denominator # TODO: Take decimals into account