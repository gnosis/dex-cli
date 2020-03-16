# dFusion CLI

![](docs/CLI-demo.gif)

## Setup

```bash
# Setup virtual env
python3 -m venv ENV
source ./ENV/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Basic commands

```bash
# help command
python dfusion.py --help
python dfusion.py

# Get trades
./dfusion trades

# Get first 5 trades
./dfusion trades --count 5 --skip 0

# Filter by trader
./dfusion trades --trader 0x7b2e78d4dfaaba045a167a70da285e30e8fca196
```

# Debug - Verbose

Verbose mode prints the query and the subgraph URL:

```
# Verbose mode (-v)
./dfusion trades -v
```

![](docs/CLI-verbose.png)
