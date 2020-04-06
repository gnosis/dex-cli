from commands.tokens import TOKEN_FIELDS_BASIC, to_token
from decimal import Decimal

import click
from gql import gql

from constants import (COLOR_LABEL, COLOR_LABEL_DELETED, COLOR_SEPARATOR,
                       SEPARATOR)
from utils.format import (format_amount, format_amount_in_weis,
                          format_batch_id_with_date, format_date_time, format_date_time_iso8601,
                          format_integer, format_percentage, format_price,
                          format_token_long, format_token_short,
                          parse_date_from_epoch)
from utils.graphql import (debug_query, get_graphql_client, gql_filter,
                           gql_sort_by)
from utils.misc import (calculate_price, is_unlimited_amount,
                        to_date_from_batch_id, to_date_from_epoch,
                        to_etherscan_link, get_csv_writer)

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
    "trade_date": parse_date_from_epoch(trade['tradeEpoch']),
    "revert_date": parse_date_from_epoch(trade['revertEpoch']),
    "sell_token": to_token(trade['sellToken']),
    "buy_token": to_token(trade['buyToken']),
    "trade_batch_id": int(trade['tradeBatchId']),
    "sell_volume": Decimal(trade['sellVolume']),
    "buy_volume": Decimal(trade['buyVolume']),
    "tx_hash": trade['txHash']
  }

def get_trades(count, skip, sort, sort_ascending, print_format, verbose, trader, batch_id, buy_token_id, sell_token_id, tx_hash):
    filters = gql_filter({
      "owner": trader.lower() if trader else None,
      # TODO: https://github.com/gnosis/dex-cli/issues/50
      #"order": order_id if order_id else None,
      "tradeBatchId": batch_id if batch_id else None,
      "buyToken": buy_token_id if buy_token_id else None,
      "sellToken": sell_token_id if sell_token_id else None,
      "txHash": tx_hash.lower() if tx_hash else None
    })

    query = f'''
{{
  trades (first: {count} , skip: {skip}, {gql_sort_by(sort, sort_ascending)}{filters}) {{{TRADE_FIELDS}  }}
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
    revert_date = trade['revert_date']
    sell_token, sell_volume = trade['sell_token'], trade['sell_volume']
    buy_token, buy_volume = trade['buy_token'], trade['buy_volume']
    sellTokenDecimals, sellTokenLabel = sell_token['decimals'], format_token_short(sell_token)
    buyTokenDecimals, buyTokenLabel = buy_token['decimals'], format_token_short(buy_token)

    # Revert date
    if revert_date is None:
      label_color = COLOR_LABEL
      revert_date_text = ''
    else:
      label_color = COLOR_LABEL_DELETED
      revert_date_text = click.style('  Reverted date', fg=label_color) + ': ' + click.style(format_date_time(revert_date), bg=COLOR_LABEL_DELETED) + '\n'

    # Prices
    order_price_text_1 = _get_price_text(
      label='Price',
      sell_label=sellTokenLabel,
      buy_label=buyTokenLabel,
      numerator=buy_volume,
      denominator=sell_volume,
      decimals_numerator=buyTokenDecimals,
      decimals_denominator=sellTokenDecimals,
      label_color=label_color
    )
    order_price_text_2 = _get_price_text(
      label='Price',
      sell_label=buyTokenLabel,
      buy_label=sellTokenLabel,
      numerator=sell_volume,
      denominator=buy_volume,
      decimals_numerator=sellTokenDecimals,
      decimals_denominator=buyTokenDecimals,
      label_color=label_color
    )
      
    click.echo(
      click.style('  Trade date', fg=label_color) + ': ' + 
      format_date_time(trade['trade_date']) + '\n' +       
      revert_date_text + 
      '\n' + 

      click.style('  Batch Id', fg=label_color) + ': ' + 
      format_integer(trade['trade_batch_id']) + '\n' + 

      click.style('  Trader', fg=label_color) + ': ' + 
      trade['owner_address'] + '\n' + 

      click.style('  Order Id', fg=label_color) + ': ' + 
      format_integer(trade['order_id']) + '\n\n' + 
      
      click.style('  Sell Token', fg=label_color) + ': ' + 
      format_token_long(sell_token) + '\n' + 

      click.style('  Buy Token', fg=label_color) + ': ' + 
      format_token_long(buy_token) + '\n' +

      # Prices
      f'{order_price_text_1}\n{order_price_text_2}\n' +

      click.style('  Sell volume', fg=label_color) + ': ' + 
      format_amount_in_weis(sell_volume, sellTokenDecimals) + ' ' + sellTokenLabel + '\n' + 

      click.style('  Buy volume', fg=label_color) + ': ' + 
      format_amount_in_weis(buy_volume, buyTokenDecimals) + ' ' + buyTokenLabel + '\n\n' + 


      click.style('  Transaction', fg=label_color) + ': ' + 
      to_etherscan_link(trade['tx_hash']) + '\n' + 

      click.style(SEPARATOR, fg=COLOR_SEPARATOR)
    )


def print_trades_csv(trades):
  writer = get_csv_writer()

  writer.writerow(['Date',
                   'Reverted',
                   'Batch Id',
                   'Trader Address',
                   'Order Id',
                   'Price SELL/BUY',
                   'Price BUY/SELL',
                   'Sell Volume', 'Sell Token',
                   'Buy Volume', 'Buy Token',
                   'Sell Token Address',
                   'Buy Token Address',
                   'Transaction'])

  for trade in trades:

    revert_date = trade.get('revert_date', None)
    revert_date_text = format_date_time_iso8601(revert_date) if revert_date else ''

    sell_token, sell_volume = trade['sell_token'], trade['sell_volume']
    buy_token, buy_volume = trade['buy_token'], trade['buy_volume']

    price_sell_buy = format_price(
      calculate_price(
          numerator=buy_volume,
          denominator=sell_volume,
          decimals_numerator=buy_token['decimals'],
          decimals_denominator=sell_token['decimals'],
      ))

    price_buy_sell = format_price(
      calculate_price(
        numerator=sell_volume,
        denominator=buy_volume,
        decimals_numerator=sell_token['decimals'],
        decimals_denominator=buy_token['decimals'],
      ))

    writer.writerow([format_date_time_iso8601(trade['trade_date']),
        revert_date_text,
        trade['trade_batch_id'],
        trade['owner_address'],
        trade['order_id'],
        price_sell_buy,
        price_buy_sell,
        format_amount_in_weis(sell_volume, sell_token['decimals']),
        format_token_short(sell_token),
        format_amount_in_weis(buy_volume, buy_token['decimals']),
        format_token_short(buy_token),
        sell_token['address'],
        buy_token['address'],
        to_etherscan_link(trade['tx_hash'])
    ])


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
