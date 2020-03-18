from commands.tokens import TOKEN_FIELDS_BASIC, to_token

import click
from gql import gql

from constants import (COLOR_LABEL, COLOR_LABEL_DELETED, COLOR_SEPARATOR,
                       SEPARATOR)
from utils import (calculate_price, debug_query, format_amount,
                   format_amount_in_weis, format_batch_id_with_date,
                   format_date_time, format_integer, format_price,
                   format_token_long, format_token_short, get_graphql_client,
                   parse_date_from_epoch, to_date_from_batch_id,
                   to_date_from_epoch, to_etherscan_link)

# Orders entity fields
#   See https://thegraph.com/explorer/subgraph/gnosis/dfusion
ORDERS_FIELDS = f'''
  owner {{ id }}
  orderId
  fromBatchId
  untilBatchId
  buyToken {{ {TOKEN_FIELDS_BASIC} }}
  sellToken {{ {TOKEN_FIELDS_BASIC} }}
  priceNumerator
  priceDenominator
  maxSellAmount
  soldVolume
  boughtVolume
  createEpoch
  cancelEpoch
  deleteEpoch
  txHash
'''

def get_orders(count, skip, sort, format, verbose, trader):
    if trader:
      filters = f', where: {{ owner:"{trader.lower()}"}}'
    else:
      filters = ''

    query = f'''
{{
  orders (first: {count} , skip: {skip}, orderBy: {sort}{filters}) {{{ORDERS_FIELDS}  }}
}}
    '''
    
    debug_query(query, verbose)
    client = get_graphql_client()
    result = client.execute(gql(query))
    tradesDto = map(to_order_dto, result['orders'])
    print_orders(tradesDto, format)


def print_orders(trades, format):
  if format == 'pretty':    
    print_orders_pretty(trades)
  elif format == 'csv':
    print_orders_csv(trades)
  else:
    raise Exception('Format "%s" is not supported. Supported formats are: pretty, csv' % (format))  


def to_order_dto(order):
  return {
    "owner_address": order['owner']['id'],
    "order_id": int(order['orderId']),
    "fromBatchId": int(order['fromBatchId']),
    "untilBatchId": int(order['untilBatchId']),
    "buyToken": order['buyToken'],
    "sellToken": order['sellToken'],
    "priceNumerator": order['priceNumerator'],
    "priceDenominator": order['priceDenominator'],
    "maxSellAmount": order['maxSellAmount'],
    "soldVolume": order['soldVolume'],
    "boughtVolume": order['boughtVolume'],
    "createDate": parse_date_from_epoch(order['createEpoch']),
    "cancelDate": parse_date_from_epoch(order['cancelEpoch']),
    "deleteDate": parse_date_from_epoch(order['deleteEpoch']),
    "txHash": order['txHash']
  }

def print_orders_pretty(orders):
  click.echo(click.style(SEPARATOR, fg=COLOR_SEPARATOR))

  for order in orders:
    cancelDate, deleteDate = order['cancelDate'], order['deleteDate']
    labelColor = COLOR_LABEL
    if cancelDate is None:
      cancelDateText = ''
    else:
      labelColor = COLOR_LABEL_DELETED
      cancelDateText = click.style('  Cancel date', fg=labelColor) + ': ' + click.style(format_date_time(cancelDate), bg=COLOR_LABEL_DELETED) + '\n'

    if deleteDate is None:
      deleteDateText = ''
    else:
      labelColor = COLOR_LABEL_DELETED
      deleteDateText = click.style('  Deleted date', fg=labelColor) + ': ' + click.style(format_date_time(deleteDate), bg=COLOR_LABEL_DELETED) + '\n'

    click.echo(
      click.style('  Order date', fg=labelColor) + ': ' + 
      format_date_time(order['createDate']) + '\n' +       
      cancelDateText + 
      deleteDateText + 
      '\n' + 

      click.style('  Trader', fg=labelColor) + ': ' + 
      order['owner_address'] + '\n' + 

      click.style('  Order Id', fg=labelColor) + ': ' + 
      format_integer(order['order_id']) + '\n' + 

      click.style('  From batch', fg=labelColor) + ': ' + 
      format_batch_id_with_date(order['fromBatchId']) + '\n' +

      click.style('  To batch', fg=labelColor) + ': ' +
      format_batch_id_with_date(order['untilBatchId']) + 
      '\n\n' + 


      # click.style('  Buy token', fg=labelColor) + ': ' + 
      # format_token_long(order['buyToken']) + '\n' + 

      # click.style('  Until Batch Id', fg=labelColor) + ': ' + 
      # format_token_long(order['sellToken']) + '\n' + 

      # click.style(f'  Price {sellTokenLabel}/{buyTokenLabel}', fg=labelColor) + ': ' + 
      # format_price(calculate_price(
      #   numerator=buyVolume,
      #   denominator=sellVolume,
      #   decimals_numerator=buyTokenDecimals,
      #   decimals_denominator=sellTokenDecimals
      # ), currency=buyTokenLabel) + '\n' +      

      # click.style(f'  Price {buyTokenLabel}/{sellTokenLabel}', fg=labelColor) + ': ' + 
      # format_price(calculate_price(
      #   numerator=sellVolume,
      #   denominator=buyVolume,
      #   decimals_numerator=sellTokenDecimals,
      #   decimals_denominator=buyTokenDecimals
      # ), currency=sellTokenLabel) + '\n' +

      # click.style('  Buy volume', fg=labelColor) + ': ' + 
      # str(order['buyVolume']) + '\n' +  # TODO: Units

      # click.style('  Max Sell Amount', fg=labelColor) + ': ' + 
      # str(order['maxSellAmount']) + '\n' +  # TODO: Units

      # click.style('  Sold Volume', fg=labelColor) + ': ' + 
      # str(order['soldVolume']) + '\n' + # TODO: Units

      # click.style('  Bought Volume', fg=labelColor) + ': ' + 
      # str(order['boughtVolume']) + '\n' + # TODO: Units

      # TODO: Show number of trades
      # TODO: Show optionally the trades of one order?
      # TODO: Show creation date?


      click.style('  Transaction', fg=labelColor) + ': ' + 
      to_etherscan_link(order['txHash']) + '\n' + 

      click.style(SEPARATOR, fg=COLOR_SEPARATOR)
    )

def print_orders_csv(orders):
  # TODO: Implement here the CSV formatting
  click.echo("Not implemented yet")
