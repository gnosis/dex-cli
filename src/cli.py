#!/usr/bin/env python3

from commands.orders import get_orders
from commands.tokens import get_tokens
from commands.trades import get_trades

import click

from constants import SEPARATOR


@click.group()
def main():
    """
    dFusion CLI ✨
    """
    pass


@main.command()
@click.option('--count', default=100, help='Number of tokens to return, used for pagination')
@click.option('--skip', default=0, help='Number of tokens to skip, used for pagination')
@click.option('--sort', default="symbol", help='Sort result by a field, used for pagination')
@click.option('--format', default="pretty", help='Format type i.e. pretty, csv')
@click.option('-v', '--verbose', count=True)
def tokens(count, skip, sort, format, verbose):
    """Get tokens listed in dFusion. For more details, see https://docs.gnosis.io/dfusion/docs/addtoken1"""
    get_tokens(count=count, skip=skip, sort=sort, format=format, verbose=verbose)


@main.command()
@click.option('--count', default=10, help='Number of trades to return, used for pagination')
@click.option('--skip', default=0, help='Number of trades to skip, used for pagination')
@click.option('--sort', default="tradeBatchId", help='Sort result by a field, used for pagination')
@click.option('--format', default="pretty", help='Format type i.e. pretty, csv')
@click.option('-v', '--verbose', count=True)
@click.option('--trader', help='Ethereum address of the trader')
def trades(count, skip, sort, format, verbose, trader):
    """Get trades"""
    get_trades(count=count, skip=skip, sort=sort, format=format, verbose=verbose, trader=trader)


@main.command()
@click.option('--count', default=10, help='Number of orders to return, used for pagination')
@click.option('--skip', default=0, help='Number of orders to skip, used for pagination')
@click.option('--sort', default="fromBatchId", help='Sort result by a field, used for pagination')
@click.option('--format', default="pretty", help='Format type i.e. pretty, csv')
@click.option('-v', '--verbose', count=True)
@click.option('--trader', help='Ethereum address of the trader')
def orders(count, skip, sort, format, verbose, trader):
    """Get orders"""
    get_orders(count=count, skip=skip, sort=sort, format=format, verbose=verbose, trader=trader)


if __name__ == "__main__":
    click.echo('\n' + click.style('''\
     _______         _             
    | |  ___|       (_)            
  __| | |_ _   _ ___ _  ___  _ __  
 / _` |  _| | | / __| |/ _ \| '_ \ 
| (_| | | | |_| \__ \ | (_) | | | |
 \__,_\_|  \__,_|___/_|\___/|_| |_|''', fg='yellow', bold=True) + '\n')
    main()
