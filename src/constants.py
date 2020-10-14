from decimal import Decimal
import os

# Datasource
if 'NETWORK' in os.environ and os.environ['NETWORK'] == "xdai":
  URL_API_THE_GRAPH = 'https://api.thegraph.com/subgraphs/name/gnosis/protocol-xdai'
  URL_UI_THE_GRAPH = 'https://thegraph.com/explorer/subgraph/gnosis/protocol-xdai'
  TX_EXPLORER_BASE_URL = 'https://blockscout.com/poa/xdai'
elif 'NETWORK' in os.environ and os.environ['NETWORK'] == "rinkeby":
  URL_API_THE_GRAPH = 'https://api.thegraph.com/subgraphs/name/gnosis/protocol-rinkeby'
  URL_UI_THE_GRAPH = 'https://thegraph.com/explorer/subgraph/gnosis/protocol-rinkeby'
  TX_EXPLORER_BASE_URL = 'https://rinkeby.etherscan.io'
else:
  URL_API_THE_GRAPH = 'https://api.thegraph.com/subgraphs/name/gnosis/protocol'
  URL_UI_THE_GRAPH = 'https://thegraph.com/explorer/subgraph/gnosis/protocol'
  TX_EXPLORER_BASE_URL = 'https://etherscan.io'

RETRIES = 3

# Model
BATCH_TIME_SECONDS = 300
OWL_DECIMALS = 18

MAX_EPOCH = 253402300799
MAX_BATCH_ID = 844674335
MAX_AMOUNT = Decimal('340282366920938463463374607431768211455')


# Presentation
SEPARATOR = '----------------------------'

# Colors
COLOR_LABEL = 'green'
COLOR_LABEL_DELETED = 'red'
COLOR_SEPARATOR = 'blue'
COLOR_SECONDARY = 'cyan'

# CSV Output
CSV_DELIMITER = ','
CSV_QUOTE = '"'

# Date and time
DATE_TIME_FORMAT = "%d/%m/%y %H:%M:%S"
DATE_FORMAT = "%d/%m/%y"
