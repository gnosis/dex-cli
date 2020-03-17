from decimal import ROUND_DOWN, Decimal

import click
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from constants import (BATCH_TIME_SECONDS, COLOR_LABEL, COLOR_SECONDARY,
                       COLOR_SEPARATOR, RETRIES, SEPARATOR, URL_API_THE_GRAPH,
                       URL_UI_THE_GRAPH)

graphql_client = None

def format_token_long(token):
  symbol = token['symbol']
  address = token['address']
  name = token['name']
  label = symbol or name

  if label:
    return f'{label} ({address})'
  else:
    return address

def format_token_short(token):
  symbol = token['symbol']
  address = token['address']
  name = token['name']
  label = symbol or name

  return label if label else address


def format_integer(number):
  return '{:,d}'.format(number)

def format_amount_in_weis(amount, decimals, rounding=ROUND_DOWN):
  value = amount / Decimal(10 ** decimals)
  return format_amount(value, decimals=decimals, rounding=rounding)

def format_price(amount, decimals=10, rounding=ROUND_DOWN, currency=''):
  price = format_amount(amount, decimals=decimals, rounding=rounding)
  return price + ' ' + currency if currency else price

def format_amount(amount, decimals=18, rounding=ROUND_DOWN):
  quantize_value = Decimal(10) ** -Decimal(decimals)
  rounded_value = Decimal(amount).quantize(quantize_value, rounding=rounding)

  return f'{{:,.{decimals}f}}'.format(rounded_value).rstrip('0').rstrip('.')

def format_date(date):
  return '' if date is None else date.strftime("%d/%m/%y")

def format_date_time(date):
  return '' if date is None else date.strftime("%d/%m/%y %H:%M:%S")

def to_date_from_epoch(epoch):
  return epoch # TODO: Date from epoch

def to_etherscan_link(hash):
  return 'https://etherscan.io/tx/' + hash

def toDateFromBatchId(batchId):
  return batchId * BATCH_TIME_SECONDS # TODO: Dates in python

def calculate_price(numerator, denominator, decimals_numerator, decimals_denominator):
  precision_factor = Decimal(10) ** Decimal(abs(decimals_numerator - decimals_denominator))
  if decimals_numerator > decimals_denominator:
    return Decimal(numerator) * precision_factor / Decimal(denominator)
  else:
    return Decimal(numerator) / Decimal(denominator) * precision_factor

def debug_query(query, verbose):
  if verbose > 0:
    click.echo(f'''\
{click.style('GraphQl query: ', fg=COLOR_LABEL, underline=True)}
  API: {click.style(URL_API_THE_GRAPH, fg=COLOR_SECONDARY)}
  Subgraph: {click.style(URL_UI_THE_GRAPH, fg=COLOR_SECONDARY)}

{query}''')

def get_graphql_client():
  global graphql_client
  if graphql_client is None:
    graphql_client = Client(
      retries = RETRIES,
      transport = RequestsHTTPTransport(
        url = URL_API_THE_GRAPH,
        use_json = True
      )
    )

  return graphql_client
