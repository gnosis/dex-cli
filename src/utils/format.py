from datetime import datetime
from decimal import ROUND_DOWN, Context, Decimal

from constants import BATCH_TIME_SECONDS, MAX_BATCH_ID, DATE_FORMAT, DATE_TIME_FORMAT
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
  return f'{number:,d}'


def format_amount_in_weis(amount, decimals, rounding=ROUND_DOWN, unlimited_label='Unlimited', thousands_separator=True):
  if is_unlimited_amount(amount):
    return unlimited_label
  else:
    value = amount / Decimal(10 ** decimals)
    return format_amount(value, decimals=decimals, rounding=rounding, thousands_separator=thousands_separator)

def format_price(amount, decimals=10, rounding=ROUND_DOWN, currency=''):
  price = format_amount(amount, decimals=decimals, rounding=rounding)
  return price + ' ' + currency if currency else price

def format_percentage(value, total):
  if is_unlimited_amount(total):
    return ''
  else:
    percentage = (Decimal(value) / Decimal(total)) * Decimal(100)
    return format_amount(percentage, decimals=2) + '%'

def format_amount(amount, decimals=18, rounding=ROUND_DOWN, thousands_separator=True):
  rounded_value = format_amount_raw(amount, decimals, rounding)

  if thousands_separator:
    return f'{rounded_value:,.{decimals}f}'.rstrip('0').rstrip('.')
  else:
    return f'{rounded_value:.{decimals}f}'.rstrip('0').rstrip('.')

def format_amount_raw(amount, decimals=18, rounding=ROUND_DOWN) -> Decimal:
  quantize_value = Decimal(10) ** -Decimal(decimals)
  rounded_value = Decimal(amount).quantize(quantize_value, context=Context(prec=40), rounding=rounding)
  return rounded_value

def format_date(date):
  return '' if date is None else date.strftime(DATE_FORMAT)


def format_date_time(date, tooBigLabel='Never'):
    return tooBigLabel if date == datetime.max else date.strftime(DATE_TIME_FORMAT)


def format_date_time_iso8601(date, tooBigLabel='Never'):
  if not date:
    return ''
  return tooBigLabel if date == datetime.max else datetime.isoformat(date)


def format_batch_id_with_date(batch_id, tooBigLabel='Never expires'):
  if batch_id:
    return tooBigLabel if batch_id >= MAX_BATCH_ID else (
      f"{format_integer(batch_id)} ({ format_date_time(to_date_from_batch_id(batch_id))})"
    )
  else:
    return ''


def parse_date_from_epoch(epoch):
  return to_date_from_epoch(int(epoch)) if epoch else None
