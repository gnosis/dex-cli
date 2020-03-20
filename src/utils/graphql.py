import click
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from constants import (COLOR_LABEL, COLOR_SECONDARY, RETRIES,
                       URL_API_THE_GRAPH, URL_UI_THE_GRAPH)

# Singleton GraphQL client instance
graphql_client = None


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


def debug_query(query, verbose):
  if verbose > 0:
    click.echo(f'''\
{click.style('GraphQl query: ', fg=COLOR_LABEL, underline=True)}
  API: {click.style(URL_API_THE_GRAPH, fg=COLOR_SECONDARY)}
  Subgraph: {click.style(URL_UI_THE_GRAPH, fg=COLOR_SECONDARY)}

{query}''')


def gql_sort_by(sort, sort_direction):
  return f'orderBy: {sort}, orderDirection: {sort_direction}'


def gql_filter(filters):
  filter_conditions = [f'{key}: "{value}"' for key, value in filters.items() if value is not None]
  return f', where: {{ {", ".join(filter_conditions)} }}' if filter_conditions else ''
