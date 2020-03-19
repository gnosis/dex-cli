from commands.tokens import TOKEN_FIELDS_BASIC, to_token
from decimal import Decimal

import click
from gql import gql

from constants import (COLOR_LABEL, COLOR_LABEL_DELETED, COLOR_SECONDARY,
                       COLOR_SEPARATOR, SEPARATOR)
from utils import (calculate_price, debug_query, format_amount,
                   format_amount_in_weis, format_batch_id_with_date,
                   format_date_time, format_integer, format_percentage,
                   format_price, format_token_long, format_token_short,
                   get_graphql_client, gql_sort_by, isUnlimitedAmount,
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

def get_orders(count, skip, sort, sort_direction, format, verbose, trader):
    if trader:
      filters = f', where: {{ owner:"{trader.lower()}"}}'
    else:
      filters = ''

    query = f'''
{{
  orders (first: {count} , skip: {skip}, {gql_sort_by(sort, sort_direction)}{filters}) {{ {ORDERS_FIELDS} }}
}}
    '''
    
    debug_query(query, verbose)
    client = get_graphql_client()
    result = client.execute(gql(query))
    ordersDto = map(to_order_dto, result['orders'])
    print_orders(ordersDto, format)


def print_orders(orders, format):
  if format == 'pretty':    
    print_orders_pretty(orders)
  elif format == 'csv':
    print_orders_csv(orders)
  else:
    raise Exception('Format "%s" is not supported. Supported formats are: pretty, csv' % (format))  


def to_order_dto(order):
  return {
    "owner_address": order['owner']['id'],
    "order_id": int(order['orderId']),
    "fromBatchId": int(order['fromBatchId']),
    "untilBatchId": int(order['untilBatchId']),
    "sellToken": to_token(order['sellToken']),
    "buyToken": to_token(order['buyToken']),
    "priceNumerator": Decimal(order['priceNumerator']),
    "priceDenominator": Decimal(order['priceDenominator']),
    "maxSellAmount": Decimal(order['maxSellAmount']),
    "soldVolume": Decimal(order['soldVolume']),
    "boughtVolume": Decimal(order['boughtVolume']),
    "createDate": parse_date_from_epoch(order['createEpoch']),
    "cancelDate": parse_date_from_epoch(order['cancelEpoch']),
    "deleteDate": parse_date_from_epoch(order['deleteEpoch']),
    "txHash": order['txHash']
  }

def print_orders_pretty(orders):
  click.echo(click.style(SEPARATOR, fg=COLOR_SEPARATOR))

  for order in orders:
    cancelDate, deleteDate = order['cancelDate'], order['deleteDate']
    priceNumerator, priceDenominator = order['priceNumerator'], order['priceDenominator']
    sellToken, soldVolume, maxSellAmount = order['sellToken'], order['soldVolume'], order['maxSellAmount']
    buyToken, boughtVolume = order['buyToken'], order['boughtVolume']
    sellTokenDecimals, sellTokenLabel = sellToken['decimals'], format_token_short(sellToken)
    buyTokenDecimals, buyTokenLabel = buyToken['decimals'], format_token_short(buyToken)

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

    tradePriceText = ''
    if soldVolume > 0:
      tradePriceText = (
        click.style(f'  Avg. Traded Price {sellTokenLabel}/{buyTokenLabel}', fg=labelColor) + ': ' + 
        format_price(
          calculate_price(
            numerator=boughtVolume,
            denominator=soldVolume,
            decimals_numerator=buyTokenDecimals,
            decimals_denominator=sellTokenDecimals
          ), 
          currency=buyTokenLabel
        ) +
        '\n' +
        click.style(f'  Avg. Traded Price {buyTokenLabel}/{sellTokenLabel}', fg=labelColor) + ': ' + 
        format_price(
          calculate_price(
            numerator=soldVolume,
            denominator=boughtVolume,
            decimals_numerator=sellTokenDecimals,
            decimals_denominator=buyTokenDecimals
          ),
          currency=sellTokenLabel
        ) +
        '\n'
      )

    percentageText = ''
    if not isUnlimitedAmount(maxSellAmount):
      percentageText = click.style(f" ({format_percentage(value=soldVolume, total=maxSellAmount)})", fg=COLOR_SECONDARY)

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

      click.style('  Sell Token', fg=labelColor) + ': ' + 
      format_token_long(sellToken) + '\n' + 

      click.style('  Buy Token', fg=labelColor) + ': ' + 
      format_token_long(buyToken) + '\n' +

      click.style('  Sold volume', fg=labelColor) + ': ' + 
      format_amount_in_weis(soldVolume, sellTokenDecimals) +
      ' of ' +
      format_amount_in_weis(maxSellAmount, sellTokenDecimals) + ' ' + sellTokenLabel + 
      percentageText +
      '\n' + 

      (
        click.style('  Bought volume', fg=labelColor) + ': ' + 
        format_amount_in_weis(boughtVolume, buyTokenDecimals) + ' ' + buyTokenLabel +      
        '\n'
        if soldVolume else ''
      ) + # TODO: Add percentage https://github.com/gnosis/dex-cli/issues/31
      '\n' +

      click.style(f'  Limit Price {sellTokenLabel}/{buyTokenLabel}', fg=labelColor) + ': ' + 
      format_price(calculate_price(
        numerator=priceNumerator,
        denominator=priceDenominator,
        decimals_numerator=buyTokenDecimals,
        decimals_denominator=sellTokenDecimals
      ), currency=buyTokenLabel) + '\n' +      

      click.style(f'  Limit Price {buyTokenLabel}/{sellTokenLabel}', fg=labelColor) + ': ' + 
      format_price(calculate_price(
        numerator=priceDenominator,
        denominator=priceNumerator,
        decimals_numerator=sellTokenDecimals,
        decimals_denominator=buyTokenDecimals
      ), currency=sellTokenLabel) + '\n' +

      tradePriceText +
      '\n' +

      click.style('  Transaction', fg=labelColor) + ': ' + 
      to_etherscan_link(order['txHash']) + '\n' + 

      click.style(SEPARATOR, fg=COLOR_SEPARATOR)
    )

def print_orders_csv(orders):
  # TODO: Implement here the CSV formatting
  click.echo("Not implemented yet")
