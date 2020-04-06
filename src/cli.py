#!/usr/bin/env python3

from commands.orders import get_orders
from commands.prices import get_prices
from commands.tokens import get_tokens
from commands.trades import get_trades

import click


def show_header(ctx, param, value):
    """Display header if requested format allows that"""
    if value == 'pretty':

        click.echo('\n' + click.style('''\
     _______         _             
    | |  ___|       (_)            
  __| | |_ _   _ ___ _  ___  _ __  
 / _` |  _| | | / __| |/ _ \| '_ \ 
| (_| | | | |_| \__ \ | (_) | | | |
 \__,_\_|  \__,_|___/_|\___/|_| |_|''', fg='yellow', bold=True) + '\n')

    return value


@click.group()
def main():
    pass


@main.command()
@click.option('--count', default=100, help='Number of tokens to return, used for pagination')
@click.option('--skip', default=0, help='Number of tokens to skip, used for pagination')
@click.option('--sort', default="symbol", help='Sort result by a field, used for pagination')
@click.option('--asc/--desc', 'sort_ascending', default=True, help='Sort direction. "asc" (default) for ascending, "desc" for descending')
@click.option('--format', 'print_format', default="pretty", expose_value=True, is_eager=False, callback=hide_header, help='Format type i.e. pretty, csv')
@click.option('-v', '--verbose', count=True)
@click.option('--id', 'token_id', help='Token id')
@click.option('--symbol', help='Token symbol')
@click.option('--address', help='Token address')
def tokens(count, skip, sort, sort_ascending, print_format, verbose, token_id, symbol, address):
    """Get tokens listed in dFusion. For more details, see https://docs.gnosis.io/dfusion/docs/addtoken1"""
    get_tokens(
      # Pagination
      count=count,
      skip=skip,
      sort=sort,
      sort_ascending=sort_ascending,
      
      # Format/debug
      print_format=print_format,
      verbose=verbose,

      # Filters
      token_id=token_id,
      address=address,
      symbol=symbol
    )


@main.command()
@click.option('--count', default=100, help='Number of prices to return, used for pagination')
@click.option('--skip', default=0, help='Number of prices to skip, used for pagination')
@click.option('--sort', default="batchId", help='Sort result by a field, used for pagination')
@click.option('--asc/--desc', 'sort_ascending', default=False, help='Sort direction. "desc" (default) for ascending, "desc" for descending')
@click.option('--format', 'print_format', default="pretty", expose_value=True, is_eager=False, callback=hide_header, help='Format type i.e. pretty, csv')
@click.option('--batch', 'batch_id', help='Batch id')
@click.option('--token', 'token_id', help='Token id')
@click.option('--tx', 'tx_hash', help='Transaction hash for the price (same as solution submission)')
@click.option('-v', '--verbose', count=True)
def prices(count, skip, sort, sort_ascending, print_format, verbose, batch_id, token_id, tx_hash):
    """Get historic prices"""
    get_prices(count=count, skip=skip, sort=sort, sort_ascending=sort_ascending, print_format=print_format, verbose=verbose, batch_id=batch_id, token_id=token_id, tx_hash=tx_hash)


@main.command()
@click.option('--count', default=10, help='Number of trades to return, used for pagination')
@click.option('--skip', default=0, help='Number of trades to skip, used for pagination')
@click.option('--sort', default="tradeBatchId", help='Sort result by a field, used for pagination')
@click.option('--asc/--desc', 'sort_ascending', default=False, help='Sort direction. "desc" (default) for ascending, "desc" for descending')
@click.option('--format', 'print_format', default="pretty", expose_value=True, is_eager=False, callback=hide_header, help='Format type i.e. pretty, csv')
@click.option('-v', '--verbose', count=True)
@click.option('--trader', help='Ethereum address of the trader')
@click.option('--batch', 'batch_id', help='Batch id')
@click.option('--buy', 'buy_token_id', help='Buy token id')
@click.option('--sell', 'sell_token_id', help='Sell token id')
@click.option('--tx', 'tx_hash', help='Transaction hash for the trade (same as solution submission)')
def trades(count, skip, sort, sort_ascending, print_format, verbose, trader, batch_id, buy_token_id, sell_token_id, tx_hash):
    """Get trades"""
    get_trades(count=count, skip=skip, sort=sort, sort_ascending=sort_ascending, print_format=print_format, verbose=verbose, trader=trader, batch_id=batch_id, buy_token_id=buy_token_id, sell_token_id=sell_token_id, tx_hash=tx_hash)


@main.command()
@click.option('--count', default=10, help='Number of orders to return, used for pagination')
@click.option('--skip', default=0, help='Number of orders to skip, used for pagination')
@click.option('--sort', default="createEpoch", help='Sort result by a field, used for pagination')
@click.option('--asc/--desc', 'sort_ascending', default=False, help='Sort direction. "desc" (default) for ascending, "desc" for descending')
@click.option('--format', 'print_format', default="pretty", expose_value=True, is_eager=False, callback=hide_header, help='Format type i.e. pretty, csv')
@click.option('-v', '--verbose', count=True)
@click.option('--trader', help='Ethereum address of the trader')
@click.option('--id', 'order_id', help='Order id')
@click.option('--buy', 'buy_token_id', help='Buy token id')
@click.option('--sell', 'sell_token_id', help='Sell token id')
@click.option('--traded/--not-traded', 'has_traded', default=None, help='The order has been executed, either totally or partially')
@click.option('--tx', 'tx_hash', help='Transaction hash for the trade (same as solution submission)')
def orders(count, skip, sort, sort_ascending, print_format, verbose, trader, order_id, buy_token_id, sell_token_id, has_traded, tx_hash):
    """Get orders"""
    get_orders(count=count, skip=skip, sort=sort, sort_ascending=sort_ascending, print_format=print_format, verbose=verbose, trader=trader, order_id=order_id, buy_token_id=buy_token_id, sell_token_id=sell_token_id, has_traded=has_traded, tx_hash=tx_hash)


if __name__ == "__main__":
    main()
