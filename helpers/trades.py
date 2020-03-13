import click
from datetime import datetime
from gql import gql

from .constants import SEPARATOR, COLOR_LABEL, COLOR_LABEL_DELETED, COLOR_SEPARATOR
from .tokens import TOKEN_FIELDS_BASIC, to_token
from .utils import get_graphql_client, to_etherscan_link, format_integer, format_amount_in_weis, format_token_long, format_token_short, debug_query, format_date_time

# Trade entity fields
#   See https://thegraph.com/explorer/subgraph/gnosis/dfusion
TRADE_FIELDS = f'''
    owner {{ id}}
    order {{ orderId }}
    tradeBatchId
    sellToken {{ {TOKEN_FIELDS_BASIC} }}
    buyToken {{ {TOKEN_FIELDS_BASIC} }}
    sellVolume
    buyVolume
    tradeEpoch
    revertEpoch
    txHash
'''

def to_trade_dto(trade):
  revertEpoch = trade['revertEpoch']
  if revertEpoch:
    revertDate = datetime.utcfromtimestamp(int(revertEpoch))
  else:
    revertDate = None

  return {
    "owner_address": trade['owner']['id'],
    "order_id": int(trade['order']['orderId']),
    "tradeDate": datetime.utcfromtimestamp(int(trade['tradeEpoch'])),
    "revertDate": revertDate,
    "sellToken": to_token(trade['sellToken']),
    "buyToken": to_token(trade['buyToken']),
    "tradeBatchId": int(trade['tradeBatchId']),
    "sellVolume": int(trade['sellVolume']),
    "buyVolume": int(trade['buyVolume']),
    "txHash": trade['txHash']
  }

def get_trades(count, skip, sort, format, verbose, trader):
    if trader:
      filters = ', where: { owner:"%s"}' % (trader)
    else:
      filters = ''

    query = f'''
{{
  trades (first: {count} , skip: {skip}, orderBy: {sort}{filters}) {{{TRADE_FIELDS}  }}
}}
    '''
    
    debug_query(query, verbose)
    client = get_graphql_client()
    result = client.execute(gql(query))
    tradesDto = map(to_trade_dto, result['trades'])
    print_trades(tradesDto, format)


def print_trades(trades, format):
  if format == 'pretty':    
    print_trades_pretty(trades)
  elif format == 'csv':
    print_trades_csv(trades)
  else:
    raise Exception('Format "%s" is not supported. Supported formats are: pretty, csv' % (format))  


def print_trades_pretty(trades):
  click.echo(click.style(SEPARATOR, fg=COLOR_SEPARATOR))

  for trade in trades:
    sellToken = trade['sellToken']
    buyToken = trade['buyToken']
    revertDate = trade['revertDate']

    if revertDate is None:
      labelColor = COLOR_LABEL
      revertDateText = ''
    else:
      labelColor = COLOR_LABEL_DELETED
      revertDateText = click.style('  Reverted date', fg=labelColor) + ': ' + click.style(format_date_time(revertDate), bg=COLOR_LABEL_DELETED) + '\n'
      
    click.echo(
      click.style('  Trade date', fg=labelColor) + ': ' + 
      format_date_time(trade['tradeDate']) + '\n' +       
      revertDateText + 
      '\n' + 

      click.style('  Batch Id', fg=labelColor) + ': ' + 
      format_integer(trade['tradeBatchId']) + '\n' + 

      click.style('  Trader', fg=labelColor) + ': ' + 
      trade['owner_address'] + '\n' + 

      click.style('  Order Id', fg=labelColor) + ': ' + 
      format_integer(trade['order_id']) + '\n\n' + 
      
      click.style('  Sell Token', fg=labelColor) + ': ' + 
      format_token_long(sellToken) + '\n' + 

      click.style('  Buy Token', fg=labelColor) + ': ' + 
      format_token_long(buyToken) + '\n' +       

      click.style('  Sell volume', fg=labelColor) + ': ' + 
      format_amount_in_weis(trade['sellVolume'], sellToken['decimals']) + ' ' + format_token_short(sellToken) + '\n' + 

      click.style('  Buy volume', fg=labelColor) + ': ' + 
      format_amount_in_weis(trade['buyVolume'], buyToken['decimals']) + ' ' + format_token_short(buyToken) + '\n\n' + 


      click.style('  Transaction', fg=labelColor) + ': ' + 
      to_etherscan_link(trade['txHash']) + '\n' + 

      click.style(SEPARATOR, fg=COLOR_SEPARATOR)
    )

def print_trades_csv(trade):
  # TODO: Implement here the CSV formatting
  click.echo("Not implemented yet")
