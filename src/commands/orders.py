
from commands.tokens import TOKEN_FIELDS_BASIC, to_token
from decimal import Decimal

import click
from gql import gql

from constants import (COLOR_LABEL, COLOR_LABEL_DELETED, COLOR_SECONDARY,
                       COLOR_SEPARATOR, SEPARATOR)
from utils.format import (format_amount, format_amount_in_weis,
                          format_batch_id_with_date, format_date_time,
                          format_integer, format_percentage, format_price,
                          format_token_long, format_token_short,
                          parse_date_from_epoch)
from utils.graphql import (debug_query, get_graphql_client, gql_filter,
                           gql_sort_by)
from utils.misc import (calculate_price, is_unlimited_amount,
                        to_date_from_batch_id, to_date_from_epoch,
                        to_etherscan_link)

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

def get_orders(count, skip, sort, sort_direction, print_format, verbose, trader):
    filters = gql_filter({
      "owner": trader.lower() if trader else None,
    })

    query = f'''
{{
  orders (first: {count} , skip: {skip}, {gql_sort_by(sort, sort_direction)}{filters}) {{ {ORDERS_FIELDS} }}
}}
    '''
    
    debug_query(query, verbose)
    client = get_graphql_client()
    result = client.execute(gql(query))
    orders_dto = [to_order_dto(order) for order in result['orders']] 
    print_orders(orders_dto, print_format)


def print_orders(orders, print_format):
  if print_format == 'pretty':    
    print_orders_pretty(orders)
  elif print_format == 'csv':
    print_orders_csv(orders)
  else:
    raise Exception('Format "%s" is not supported. Supported formats are: pretty, csv' % (print_format))  


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


def _get_price_text (label, sell_label, buy_label, numerator, denominator, decimals_numerator, decimals_denominator, label_color):
  return (
    click.style(f'  {label} {sell_label}/{buy_label}', fg=label_color) + ': ' +
    format_price(
      calculate_price(
        numerator=numerator,
        denominator=denominator,
        decimals_numerator=decimals_numerator,
        decimals_denominator=decimals_denominator
      ), 
      currency=buy_label
    )
  )


def print_orders_pretty(orders):
  click.echo(click.style(SEPARATOR, fg=COLOR_SEPARATOR))

  for order in orders:
    cancelDate, deleteDate = order['cancelDate'], order['deleteDate']
    priceNumerator, priceDenominator = order['priceNumerator'], order['priceDenominator']
    sellToken, soldVolume, maxSellAmount = order['sellToken'], order['soldVolume'], order['maxSellAmount']
    buyToken, boughtVolume = order['buyToken'], order['boughtVolume']
    sellTokenDecimals, sellTokenLabel = sellToken['decimals'], format_token_short(sellToken)
    buyTokenDecimals, buyTokenLabel = buyToken['decimals'], format_token_short(buyToken)

    # Canceled trade date
    label_color = COLOR_LABEL
    if cancelDate is None:
      cancelDateText = ''
    else:
      label_color = COLOR_LABEL_DELETED
      cancelDateText = click.style('  Cancel date', fg=label_color) + ': ' + click.style(format_date_time(cancelDate), bg=COLOR_LABEL_DELETED) + '\n'

    # Deleted trade date
    if deleteDate is None:
      deleteDateText = ''
    else:
      label_color = COLOR_LABEL_DELETED
      deleteDateText = click.style('  Deleted date', fg=label_color) + ': ' + click.style(format_date_time(deleteDate), bg=COLOR_LABEL_DELETED) + '\n'


    # Limit Price
    order_price_text_1 = _get_price_text(
      label='Limit Price',
      sell_label=sellTokenLabel,
      buy_label=buyTokenLabel,
      numerator=priceNumerator,
      denominator=priceDenominator,
      decimals_numerator=buyTokenDecimals,
      decimals_denominator=sellTokenDecimals,
      label_color=label_color
    )
    order_price_text_2 = _get_price_text(
      label='Limit Price',
      sell_label=buyTokenLabel,
      buy_label=sellTokenLabel,
      numerator=priceDenominator,
      denominator=priceNumerator,
      decimals_numerator=buyTokenDecimals,
      decimals_denominator=sellTokenDecimals,
      label_color=label_color
    )
    

    # Get the actual averaged trade price, if the order was partially/totally executed
    trade_price_text = ''
    if soldVolume > 0:      
      trade_price_text_1 = _get_price_text(
        label='Avg. Traded Price',
        sell_label=sellTokenLabel,
        buy_label=buyTokenLabel,
        numerator=boughtVolume,
        denominator=soldVolume,
        decimals_numerator=buyTokenDecimals,
        decimals_denominator=sellTokenDecimals,
        label_color=label_color
      )

      trade_price_text_2 = _get_price_text(
        label='Avg. Traded Price',
        sell_label=buyTokenLabel,
        buy_label=sellTokenLabel,
        numerator=soldVolume,
        denominator=boughtVolume,
        decimals_numerator=sellTokenDecimals,
        decimals_denominator=buyTokenDecimals,
        label_color=label_color
      )
      trade_price_text = f'{trade_price_text_1}\n{trade_price_text_2}\n'
      

    # Calculate percentage, if not unlimited amount
    percentageText = ''
    if not is_unlimited_amount(maxSellAmount):
      percentageText = click.style(f" ({format_percentage(value=soldVolume, total=maxSellAmount)})", fg=COLOR_SECONDARY)

    click.echo(
      click.style('  Order date', fg=label_color) + ': ' + 
      format_date_time(order['createDate']) + '\n' +       
      cancelDateText + 
      deleteDateText + 
      '\n' + 

      click.style('  Trader', fg=label_color) + ': ' + 
      order['owner_address'] + '\n' + 

      click.style('  Order Id', fg=label_color) + ': ' + 
      format_integer(order['order_id']) + '\n' + 

      click.style('  From batch', fg=label_color) + ': ' + 
      format_batch_id_with_date(order['fromBatchId']) + '\n' +

      click.style('  To batch', fg=label_color) + ': ' +
      format_batch_id_with_date(order['untilBatchId']) + 
      '\n\n' + 

      click.style('  Sell Token', fg=label_color) + ': ' + 
      format_token_long(sellToken) + '\n' + 

      click.style('  Buy Token', fg=label_color) + ': ' + 
      format_token_long(buyToken) + '\n' +

      click.style('  Sold volume', fg=label_color) + ': ' + 
      format_amount_in_weis(soldVolume, sellTokenDecimals) +
      ' of ' +
      format_amount_in_weis(maxSellAmount, sellTokenDecimals) + ' ' + sellTokenLabel + 
      percentageText +
      '\n' + 

      (
        click.style('  Bought volume', fg=label_color) + ': ' + 
        format_amount_in_weis(boughtVolume, buyTokenDecimals) + ' ' + buyTokenLabel +      
        '\n'
        if soldVolume else ''
      ) +
      '\n' +

      # Prices
      f'{order_price_text_1}\n{order_price_text_2}\n' +
      trade_price_text +
      '\n' +

      click.style('  Transaction', fg=label_color) + ': ' + 
      to_etherscan_link(order['txHash']) + '\n' + 

      click.style(SEPARATOR, fg=COLOR_SEPARATOR)
    )

def print_orders_csv(orders):
  # TODO: Implement here the CSV formatting
  click.echo("Not implemented yet")
