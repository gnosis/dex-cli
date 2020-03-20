from datetime import datetime
from decimal import ROUND_DOWN, Context, Decimal

from constants import BATCH_TIME_SECONDS, MAX_BATCH_ID
from utils.misc import (is_unlimited_amount, to_date_from_batch_id,
                        to_date_from_epoch)


def format_token_long(token):
  symbol = token['symbol']
  address = token['address']
  name = token['name']
  label = symbol or name

  return f'{label} ({address})' if label else address

def format_token_short(token):
  symbol = token['symbol']
  address = token['address']
  name = token['name']
  label = symbol or name

  return label if label else address


def format_integer(number):
  return '{:,d}'.format(number)


def format_amount_in_weis(amount, decimals, rounding=ROUND_DOWN, unlimited_label='Unlimited'):
  if is_unlimited_amount(amount):
    return unlimited_label
  else:
    value = amount / Decimal(10 ** decimals)
    return format_amount(value, decimals=decimals, rounding=rounding)

def format_price(amount, decimals=10, rounding=ROUND_DOWN, currency=''):
  price = format_amount(amount, decimals=decimals, rounding=rounding)
  return price + ' ' + currency if currency else price

def format_percentage(value, total):
  if is_unlimited_amount(total):
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


def parse_date_from_epoch(epoch):
  return to_date_from_epoch(int(epoch)) if epoch else None
