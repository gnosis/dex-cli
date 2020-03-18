from commands.tokens import TOKEN_FIELDS_BASIC, to_token
from decimal import Decimal

import click
from gql import gql

from constants import COLOR_LABEL, COLOR_SEPARATOR, OWL_DECIMALS, SEPARATOR
from utils import (debug_query, format_amount_in_weis,
                   format_batch_id_with_date, format_integer,
                   format_token_long, get_graphql_client, gql_sort_by,
                   to_etherscan_link)

# Price entity fields
#   See https://thegraph.com/explorer/subgraph/gnosis/dfusion
PRICES_FIELDS = f'''
  token {{ {TOKEN_FIELDS_BASIC} }}
  batchId
  priceInOwl
  volume  
  txHash
'''

def get_prices(count, skip, sort, sort_direction, print_format, verbose):
    query = f'''
{{
  prices (first: {count} , skip: {skip}, {gql_sort_by(sort, sort_direction)}) {{{PRICES_FIELDS}  }}
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
    "batchId": int(price['batchId']),
    "priceInOwl": Decimal(price['priceInOwl']),
    "volume": Decimal(price['volume']),
    "txHash": price['txHash']
  }

def print_prices_pretty(prices):
  click.echo(click.style(SEPARATOR, fg=COLOR_SEPARATOR))

  for price in prices:

    click.echo(
      click.style('  Token', fg=COLOR_LABEL) + ': ' + 
      format_token_long(price['token']) + '\n' + 

      click.style('  Batch Id', fg=COLOR_LABEL) + ': ' + 
      format_batch_id_with_date(price['batchId']) + '\n' + 

      click.style('  Price in OWL', fg=COLOR_LABEL) + ': ' + 
      format_amount_in_weis(price['priceInOwl'], OWL_DECIMALS) + '\n' + 

      click.style('  Transaction', fg=COLOR_LABEL) + ': ' + 
      to_etherscan_link(price['txHash']) + '\n' + 

      click.style(SEPARATOR, fg=COLOR_SEPARATOR)
    )

def print_prices_csv(prices):
  # TODO: Implement here the CSV formatting
  click.echo("Not implemented yet")
