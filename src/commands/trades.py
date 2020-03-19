from commands.tokens import TOKEN_FIELDS_BASIC, to_token
from decimal import Decimal

import click
from gql import gql

from constants import (COLOR_LABEL, COLOR_LABEL_DELETED, COLOR_SEPARATOR,
                       SEPARATOR)
from utils import (calculate_price, debug_query, format_amount,
                   format_amount_in_weis, format_date_time, format_integer,
                   format_price, format_token_long, format_token_short,
                   get_graphql_client, gql_filter, gql_sort_by,
                   parse_date_from_epoch, to_etherscan_link)

# Trade entity fields
#   See https://thegraph.com/explorer/subgraph/gnosis/dfusion
TRADE_FIELDS = f'''
    owner {{ id }}
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
  return {
    "owner_address": trade['owner']['id'],
    "order_id": int(trade['order']['orderId']),
    "tradeDate": parse_date_from_epoch(trade['tradeEpoch']),
    "revertDate": parse_date_from_epoch(trade['revertEpoch']),
    "sellToken": to_token(trade['sellToken']),
    "buyToken": to_token(trade['buyToken']),
    "tradeBatchId": int(trade['tradeBatchId']),
    "sellVolume": Decimal(trade['sellVolume']),
    "buyVolume": Decimal(trade['buyVolume']),
    "txHash": trade['txHash']
  }

def get_trades(count, skip, sort, sort_direction, print_format, verbose, trader):
    filters = gql_filter({
      "owner": trader.lower() if trader else None,
    })

    query = f'''
{{
  trades (first: {count} , skip: {skip}, {gql_sort_by(sort, sort_direction)}{filters}) {{{TRADE_FIELDS}  }}
}}
    '''
    
    debug_query(query, verbose)
    client = get_graphql_client()
    result = client.execute(gql(query))
    trades_dto = [to_trade_dto(trade) for trade in result['trades']] 
    print_trades(trades_dto, print_format)


def print_trades(trades, print_format):
  if print_format == 'pretty':    
    print_trades_pretty(trades)
  elif print_format == 'csv':
    print_trades_csv(trades)
  else:
    raise Exception('Format "%s" is not supported. Supported formats are: pretty, csv' % (print_format))  


def print_trades_pretty(trades):
  click.echo(click.style(SEPARATOR, fg=COLOR_SEPARATOR))

  for trade in trades:
    revertDate = trade['revertDate']
    sellToken, sellVolume = trade['sellToken'], trade['sellVolume']
    buyToken, buyVolume = trade['buyToken'], trade['buyVolume']
    sellTokenDecimals, sellTokenLabel = sellToken['decimals'], format_token_short(sellToken)
    buyTokenDecimals, buyTokenLabel = buyToken['decimals'], format_token_short(buyToken)

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

      click.style(f'  Price {sellTokenLabel}/{buyTokenLabel}', fg=labelColor) + ': ' + 
      format_price(calculate_price(
        numerator=buyVolume,
        denominator=sellVolume,
        decimals_numerator=buyTokenDecimals,
        decimals_denominator=sellTokenDecimals
      ), currency=buyTokenLabel) + '\n' +      

      click.style(f'  Price {buyTokenLabel}/{sellTokenLabel}', fg=labelColor) + ': ' + 
      format_price(calculate_price(
        numerator=sellVolume,
        denominator=buyVolume,
        decimals_numerator=sellTokenDecimals,
        decimals_denominator=buyTokenDecimals
      ), currency=sellTokenLabel) + '\n' +

      click.style('  Sell volume', fg=labelColor) + ': ' + 
      format_amount_in_weis(sellVolume, sellTokenDecimals) + ' ' + sellTokenLabel + '\n' + 

      click.style('  Buy volume', fg=labelColor) + ': ' + 
      format_amount_in_weis(buyVolume, buyTokenDecimals) + ' ' + buyTokenLabel + '\n\n' + 


      click.style('  Transaction', fg=labelColor) + ': ' + 
      to_etherscan_link(trade['txHash']) + '\n' + 

      click.style(SEPARATOR, fg=COLOR_SEPARATOR)
    )

def print_trades_csv(trade):
  # TODO: Implement here the CSV formatting
  click.echo("Not implemented yet")
