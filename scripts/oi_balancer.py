from brownie import Contract
import json


def load_contract(address):
    try:
        return Contract(address)
    except ValueError:
        return Contract.from_explorer(address)


def read_json(filename):
    constants_path = 'scripts/constants/'
    f = open(constants_path + filename)
    return json.load(f)


def get_markets():
    return read_json('markets.json')


def get_imbalance(market):
    long_oi, short_oi = market.oiLong(), market.oiShort()
    return long_oi - short_oi


def main():
    # Get all market addresses and contract objects
    market_addrs = list(get_markets().values())
    markets = []
    for m in market_addrs:
        markets.append(load_contract(m))

    for m in markets:
        # Get imbalance on all markets
        imb = get_imbalance(m)

        # Calculate OVL amounts that need to be added or removed to balance
        

    # Get current positions of DAO

    # Decide whether to build or unwind or position

    # Make transactions
