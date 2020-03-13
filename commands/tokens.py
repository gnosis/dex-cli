from datetime import datetime

import click
from gql import gql

from constants import SEPARATOR, OWL_DECIMALS, COLOR_LABEL, COLOR_SEPARATOR
from helpers.utils import debug_query, get_graphql_client, format_amount_in_weis, format_integer, format_date_time, to_date_from_epoch, to_etherscan_link

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


def get_tokens(count, skip, sort, format, verbose):

    query = f'''
{{
  tokens (first: {count} , skip: {skip}, orderBy: {sort}) {{{TOKENS_FIELDS}  }}
}}
    '''
    
    debug_query(query, verbose)
    client = get_graphql_client()
    result = client.execute(gql(query))
    tokens_dto = map(to_token_dto, result['tokens'])
    print_tokens(tokens_dto, format)


def print_tokens(tokens, format):
  if format == 'pretty':    
    print_tokens_pretty(tokens)
  elif format == 'csv':
    print_tokens_csv(tokens)
  else:
    raise Exception('Format "%s" is not supported. Supported formats are: pretty, csv' % (format))  


def to_token_dto(token):
  return {
    "id": int(token['id']),
    "address": token['address'],
    "decimals": int(token['decimals'] or '18'),
    "name": token['name'],
    "symbol": token['symbol'],
    "createEpoch": datetime.utcfromtimestamp(int(token['createEpoch'])),
    "txHash": token['txHash']
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
      format_date_time(token['createEpoch']) + '\n' +

      click.style('  Transaction', fg=COLOR_LABEL) + ': ' + 
      to_etherscan_link(token['txHash']) + '\n' + 

      click.style(SEPARATOR, fg=COLOR_SEPARATOR)
    )

def print_tokens_csv(tokens):
  # TODO: Implement here the CSV formatting
  click.echo("Not implemented yet")