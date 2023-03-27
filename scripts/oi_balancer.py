from brownie import Contract, multicall, accounts
import json
import pandas as pd
from itertools import compress


def load_contract(address):
    try:
        return Contract(address)
    except ValueError:
        return Contract.from_explorer(address)


def read_json(filename):
    constants_path = 'scripts/constants/'
    f = open(constants_path + filename)
    return json.load(f)


def get_constants():
    return read_json('constants.json')


def get_imbalance(market):
    long_oi, short_oi = market.oiLong(), market.oiShort()
    return long_oi - short_oi


def get_all_builds(market, from_block):
    # Get all builds
    all_builds = market.events.get_sequence(from_block=from_block,
                                            event_type='Build')
    # Convert to list of DFs
    df_l = [pd.json_normalize(dict(b.args)) for b in all_builds]
    # Single DF from list of DFs
    df = pd.concat(df_l, ignore_index=True)
    return df


def get_dao_builds(market, from_block, dao_acc):
    # Get all builds
    df = get_all_builds(market, from_block)
    # Filter down to DAOs builds
    return df[df.sender.str.lower()==dao_acc.address.lower()]


def get_values_dao_pos(market, from_block, dao_acc, mc_addr, state):
    '''
    Get current values of positions held by input account (DAO)
    '''
    df = get_dao_builds(market, from_block, dao_acc)
    ids = list(df.positionId)
    multicall(address=mc_addr)
    with multicall:
        values = [state.value(market, dao_acc, id) for id in ids]
    if sum(values) == 0:
        return 0
    else:
        return [list(pair) for pair in zip(ids, values) if pair[1] != 0]


def main(acc):
    # Init account
    acc = accounts.load(acc)
    # Get all market addresses and contract objects
    const = get_constants()
    market_addrs = list(const['market'].values())
    markets = []
    for m in market_addrs:
        markets.append(load_contract(m))
    
    # Get state contract
    state_addr = const['state']
    state = load_contract(state_addr)

    ovl_imb = []
    curr_pos = []
    for m in markets:
        # Get imbalance on all markets
        imb = get_imbalance(m)

        # Calculate OVL amounts that need to be added or removed to balance OI
        ovl_imb.append((imb * state.mid(markets[0]))/1e36)
        curr_pos.append(
            get_values_dao_pos(
                m, const['start_block'], acc, const['multicall'], state
            )
        )

    breakpoint()
    # Get current positions of DAO

    # Decide whether to build or unwind position

    # Make transactions
