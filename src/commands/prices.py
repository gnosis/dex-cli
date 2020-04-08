from commands.tokens import TOKEN_FIELDS_BASIC, to_token
from decimal import Decimal

import click
from gql import gql

from constants import COLOR_LABEL, COLOR_SEPARATOR, OWL_DECIMALS, SEPARATOR
from utils.format import (format_amount_in_weis, format_batch_id_with_date, format_price,
                          format_date_time, format_integer, format_date_time_iso8601, format_token_long,
                          format_token_short)
from utils.graphql import (debug_query, get_graphql_client, gql_filter,
                           gql_sort_by)
from utils.misc import to_date_from_epoch, to_etherscan_link, get_csv_writer, to_date_from_batch_id

# Price entity fields
#   See https://thegraph.com/explorer/subgraph/gnosis/dfusion
PRICES_FIELDS = f'''
  token {{ {TOKEN_FIELDS_BASIC} }}
  batchId
  priceInOwlNumerator
  priceInOwlDenominator
  volume  
  txHash
'''

def get_prices(count, skip, sort, sort_ascending, print_format, verbose, batch_id, token_id, tx_hash):
    filters = gql_filter({
      "batchId": batch_id if batch_id else None,
      "token": token_id if token_id else None,
      "txHash": tx_hash.lower() if tx_hash else None
    })

    query = f'''
{{
  prices (first: {count} , skip: {skip}, {gql_sort_by(sort, sort_ascending)}{filters}) {{{PRICES_FIELDS}  }}
}}
    '''
    
    debug_query(query, verbose)
    client = get_graphql_client()
    result = client.execute(gql(query))    
    prices_dto = [to_price_dto(price) for price in result['prices']]
    print_prices(prices_dto, print_format)


def print_prices(prices, print_format):
  if print_format == 'pretty':    
    print_prices_pretty(prices)
  elif print_format == 'csv':
    print_prices_csv(prices)
  else:
    raise Exception('Format "%s" is not supported. Supported formats are: pretty, csv' % (print_format))  


def to_price_dto(price):
  # No transformation is needed
  return {
    "token": to_token(price['token']),
    "batch_id": int(price['batchId']),
    "price_in_owl_numerator": Decimal(price['priceInOwlNumerator']),
    "price_in_owl_denominator": Decimal(price['priceInOwlDenominator']),
    "volume": Decimal(price['volume']),
    "tx_hash": price['txHash']
  }


def print_prices_pretty(prices):
  click.echo(click.style(SEPARATOR, fg=COLOR_SEPARATOR))

  for price in prices:

    click.echo(
      click.style('  Token', fg=COLOR_LABEL) + ': ' + 
      format_token_long(price['token']) + '\n' + 

      click.style('  Batch Id', fg=COLOR_LABEL) + ': ' + 
      format_batch_id_with_date(price['batch_id']) + '\n' + 

      click.style('  Price in OWL', fg=COLOR_LABEL) + ': ' + 
      format_price_in_owl(price) + '\n' +

      click.style('  Transaction', fg=COLOR_LABEL) + ': ' + 
      to_etherscan_link(price['tx_hash']) + '\n' + 

      click.style(SEPARATOR, fg=COLOR_SEPARATOR)
    )


def print_prices_csv(prices):
  writer = get_csv_writer()

  writer.writerow(['Token',
                   'Registered',
                   'Batch Id',
                   'Batch Start',  # artificial
                   'Price in OWL',
                   'Transaction'])

  for price in prices:
    writer.writerow([
      format_token_short(price['token']),
      price['token']['address'],
      price['batch_id'],
      format_date_time_iso8601(to_date_from_batch_id(price['batch_id'])),
      format_price_in_owl(price),
      price['tx_hash']])


def format_price_in_owl(price):
  return format_price(price['price_in_owl_numerator'] / price['price_in_owl_denominator'], OWL_DECIMALS)
