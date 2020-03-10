import click

from .constants import SEPARATOR
from .tokens import TOKEN_FIELDS_BASIC, toToken
from .utils import toEtherescanLink, format_integer, format_amount_in_weis, format_token

# Trade entity fields
#   See https://thegraph.com/explorer/subgraph/gnosis/dfusion
TRADE_FIELDS = '''
    owner { id}
    order { orderId }
    tradeBatchId
    sellToken { %s }
    buyToken { %s }
    sellVolume
    buyVolume
    txHash
''' %(TOKEN_FIELDS_BASIC, TOKEN_FIELDS_BASIC)

def toTradeDto(trade):
  return {
    "owner_address": trade['owner']['id'],
    "order_id": int(trade['order']['orderId']),
    "sellToken": toToken(trade['sellToken']),
    "buyToken": toToken(trade['buyToken']),
    "tradeBatchId": int(trade['tradeBatchId']),
    "sellVolume": int(trade['sellVolume']),
    "buyVolume": int(trade['buyVolume']),
    "txHash": trade['txHash']
  }

def print_trades_pretty(trades):
  click.echo(click.style(SEPARATOR, fg='red'))

  for trade in trades:
    sellToken = trade['sellToken']
    buyToken = trade['buyToken']

    click.echo(
      click.style('  Batch Id', fg='green') + ': ' + 
      format_integer(trade['tradeBatchId']) + '\n' + 

      click.style('  Trader', fg='green') + ':' + 
      trade['owner_address'] + '\n' + 

      click.style('  Order Id', fg='green') + ': ' + 
      format_integer(trade['order_id']) + '\n' + 

      click.style('  Sell Token', fg='green') + ': ' + 
      format_token(sellToken) + '\n' + 

      click.style('  Buy Token', fg='green') + ': ' + 
      format_token(buyToken) + '\n' +       

      click.style('  Sell volume', fg='green') + ': ' + 
      format_amount_in_weis(trade['sellVolume'], sellToken['decimals']) + '\n' + 

      click.style('  Buy volume', fg='green') + ': ' + 
      format_amount_in_weis(trade['buyVolume'], buyToken['decimals']) + '\n' + 

      click.style('  Transaction', fg='green') + ': ' + 
      toEtherescanLink(trade['txHash']) + '\n' + 

      click.style(SEPARATOR, fg='red')
    )

def print_trades_csv(trade):
  # TODO: Implement here the CSV formatting
  click.echo("Not implemented yet")