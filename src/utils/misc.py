from datetime import datetime
from decimal import ROUND_DOWN, Decimal

import csv
import os
import sys

from constants import (BATCH_TIME_SECONDS, ETHERSCAN_BASE_URL, MAX_AMOUNT,
                       MAX_EPOCH, CSV_DELIMITER, CSV_QUOTE)


def is_unlimited_amount(amount):
  global MAX_AMOUNT

  return amount == MAX_AMOUNT


def to_date_from_epoch(epoch):
  global MAX_EPOCH

  if epoch < MAX_EPOCH:
    return datetime.utcfromtimestamp(epoch) if epoch else None
  else:
    return datetime.max


def to_date_from_batch_id(batch_id):
  return to_date_from_epoch(batch_id * BATCH_TIME_SECONDS)


def calculate_price(numerator, denominator, decimals_numerator, decimals_denominator):
  numerator_dec = Decimal(numerator)
  denominator_dec = Decimal(denominator)

  if denominator_dec.is_zero():
    return Decimal(1) if numerator_dec.is_zero() else Decimal('Infinity')
  else:
    precision_factor = Decimal(10) ** Decimal(abs(decimals_numerator - decimals_denominator))
    if decimals_numerator > decimals_denominator:
      return numerator_dec / denominator_dec / precision_factor
    else:
      return numerator_dec / (denominator_dec / precision_factor)


def to_etherscan_link(hash):
  return ETHERSCAN_BASE_URL + '/tx/' + hash


def get_csv_writer() -> csv.writer:
  return csv.writer(sys.stdout, lineterminator=os.linesep, delimiter=CSV_DELIMITER,
                      quotechar=CSV_QUOTE, quoting=csv.QUOTE_MINIMAL)
