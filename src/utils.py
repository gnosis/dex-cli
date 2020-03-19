from datetime import datetime
from decimal import ROUND_DOWN, Context, Decimal, getcontext

import click
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from constants import (BATCH_TIME_SECONDS, COLOR_LABEL, COLOR_SECONDARY,
                       COLOR_SEPARATOR, RETRIES, SEPARATOR, URL_API_THE_GRAPH,
                       URL_UI_THE_GRAPH)

MAX_EPOCH = 253402300799
MAX_BATCH_ID = 844674335
MAX_AMOUNT = Decimal('340282366920938463463374607431768211455')

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

def isUnlimitedAmount(amount):
  global MAX_AMOUNT

  return amount == MAX_AMOUNT

def format_amount_in_weis(amount, decimals, rounding=ROUND_DOWN, unlimitedLabel='Unlimited'):
  if isUnlimitedAmount(amount):
    return unlimitedLabel
  else:
    value = amount / Decimal(10 ** decimals)
    return format_amount(value, decimals=decimals, rounding=rounding)

def format_price(amount, decimals=10, rounding=ROUND_DOWN, currency=''):
  price = format_amount(amount, decimals=decimals, rounding=rounding)
  return price + ' ' + currency if currency else price

def format_percentage(value, total):
  if isUnlimitedAmount(total):
    return ''
  else:
    percentage = (Decimal(value) / Decimal(total)) * Decimal(100)
    return format_amount(percentage, decimals=2) + '%'

def format_amount(amount, decimals=18, rounding=ROUND_DOWN):
  quantize_value = Decimal(10) ** -Decimal(decimals)
  rounded_value = Decimal(amount).quantize(quantize_value, context=Context(prec=40), rounding=rounding)

  return f'{{:,.{decimals}f}}'.format(rounded_value).rstrip('0').rstrip('.')

def format_date(date):
  return '' if date is None else date.strftime("%d/%m/%y")

def format_date_time(date, tooBigLabel='Never'):  
    return tooBigLabel if date == datetime.max else date.strftime("%d/%m/%y %H:%M:%S")

def format_batch_id_with_date(batchId, tooBigLabel='Never expires'):
  if batchId:
    return tooBigLabel if batchId >= MAX_BATCH_ID else (
      format_integer(batchId) + 
      f" ({ format_date_time(to_date_from_batch_id(batchId))})"
    )
  else:
    return ''

def to_date_from_epoch(epoch):
  global MAX_EPOCH

  if epoch < MAX_EPOCH:
    return datetime.utcfromtimestamp(epoch) if epoch else None
  else:
    return datetime.max

def to_etherscan_link(hash):
  return 'https://etherscan.io/tx/' + hash

def to_date_from_batch_id(batchId):
  return to_date_from_epoch(batchId * BATCH_TIME_SECONDS)

def calculate_price(numerator, denominator, decimals_numerator, decimals_denominator):
  numerator_dec = Decimal(numerator)
  denominator_dec = Decimal(denominator)

  if denominator_dec.is_zero():
    return Decimal(1) if numerator_dec.is_zero() else Infinity
  else:
    precision_factor = Decimal(10) ** Decimal(abs(decimals_numerator - decimals_denominator))
    if decimals_numerator > decimals_denominator:
      return numerator_dec / denominator_dec / precision_factor
    else:
      return numerator_dec / (denominator_dec / precision_factor)

  if decimals_numerator > decimals_denominator:
    return Decimal(numerator) * precision_factor / Decimal(denominator)
  else:
    return Decimal(numerator) / Decimal(denominator) * precision_factor

def parse_date_from_epoch(epoch):
  return to_date_from_epoch(int(epoch)) if epoch else None

def debug_query(query, verbose):
  if verbose > 0:
    click.echo(f'''\
{click.style('GraphQl query: ', fg=COLOR_LABEL, underline=True)}
  API: {click.style(URL_API_THE_GRAPH, fg=COLOR_SECONDARY)}
  Subgraph: {click.style(URL_UI_THE_GRAPH, fg=COLOR_SECONDARY)}

{query}''')

def gql_sort_by(sort, sort_direction):
  return f'orderBy: {sort}, orderDirection: {sort_direction}'

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
