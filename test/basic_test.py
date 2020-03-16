# Example of test: Just for Integrating travis PR
# TODO: Add real tests https://github.com/gnosis/dex-cli/issues/25

def inc(x):
    return x + 1


def test_answer():
    assert inc(4) == 5
