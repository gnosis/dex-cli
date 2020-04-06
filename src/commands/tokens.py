from datetime import datetime

import click
from gql import gql

from constants import COLOR_LABEL, COLOR_SEPARATOR, OWL_DECIMALS, SEPARATOR
from utils.format import (format_amount_in_weis, format_date_time, format_date_time_iso8601,
                          format_integer, parse_date_from_epoch)
from utils.graphql import (debug_query, get_graphql_client, gql_filter,
                           gql_sort_by)
from utils.misc import to_date_from_epoch, to_etherscan_link, get_csv_writer

TOKEN_FIELDS_BASIC = 'id, name, symbol, address, decimals'

# Batch entity fields
#   See https://thegraph.com/explorer/subgraph/gnosis/dfusion
TOKENS_FIELDS = '''
    id
    address
    decimals
    name
    symbol
    createEpoch
    txHash  
'''


def to_token(token):
  return {
    "id": token['id'],
    "name": token['name'],
    "symbol": token['symbol'],
    "address": token['address'],
    "decimals": int(token['decimals'] or '18')
  }


def get_tokens(count, skip, sort, sort_ascending, print_format, verbose, token_id, symbol, address):
  filters = gql_filter({
    "id": token_id,
    "address": address.lower() if address else None,
    "symbol": symbol
  })

  query = f'''
{{
  tokens (first: {count} , skip: {skip}, {gql_sort_by(sort, sort_ascending)}{filters}) {{{TOKENS_FIELDS}  }}
}}
    '''  
  debug_query(query, verbose)
  client = get_graphql_client()
  result = client.execute(gql(query))
  tokens_dto = [to_token_dto(token) for token in result['tokens']]
  print_tokens(tokens_dto, print_format)


def print_tokens(tokens, print_format):
  if print_format == 'pretty':    
    print_tokens_pretty(tokens)
  elif print_format == 'csv':
    print_tokens_csv(tokens)
  else:
    raise Exception('Format "%s" is not supported. Supported formats are: pretty, csv' % (print_format))  


def to_token_dto(token):
  return {
    "id": int(token['id']),
    "address": token['address'],
    "decimals": int(token['decimals'] or '18'),
    "name": token['name'],
    "symbol": token['symbol'],
    "create_date": parse_date_from_epoch(token['createEpoch']),
    "tx_hash": token['txHash']
  }


def print_tokens_pretty(tokens):
  click.echo(click.style(SEPARATOR, fg=COLOR_SEPARATOR))

  for token in tokens:
    symbol = token['symbol'] or ''
    name = token['name'] or ''
    click.echo( 
      click.style('  Id', fg=COLOR_LABEL) + ': ' + 
      str(token['id']) + '\n' +

      click.style('  Address', fg=COLOR_LABEL) + ': ' + 
      token['address'] + '\n\n' +

      click.style('  Symbol', fg=COLOR_LABEL) + ': ' + 
      symbol + '\n' +

      click.style('  Name', fg=COLOR_LABEL) + ': ' + 
      name + '\n' +

      click.style('  Decimals', fg=COLOR_LABEL) + ': ' + 
      str(token['decimals']) + '\n\n' +

      click.style('  Registered', fg=COLOR_LABEL) + ': ' + 
      format_date_time(token['create_date']) + '\n' +

      click.style('  Transaction', fg=COLOR_LABEL) + ': ' + 
      to_etherscan_link(token['tx_hash']) + '\n' + 

      click.style(SEPARATOR, fg=COLOR_SEPARATOR)
    )


def print_tokens_csv(tokens):

  writer = get_csv_writer()

  writer.writerow(['ID', 'Symbol', 'Name', 'Decimals', 'Registered', 'Transaction'])

  for token in tokens:
    writer.writerow([token['id'],
      token.get('symbol', ''),
      token.get('name', ''),
      token['decimals'],
      token['address'],
      format_date_time_iso8601(token['create_date']),
      to_etherscan_link(token['tx_hash'])])
