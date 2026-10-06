"""Bounded traversal of the science-edition hierarchy, never full expansion."""
import json
from itertools import islice, product
from pathlib import Path


def sample(limit=16):
    if type(limit) is not int or not 1<=limit<=256:
        raise ValueError('Sample limit must be 1..256')
    manifest=json.loads((Path(__file__).resolve().parents[1]/'Rasniki-Science-Hierarchy.json').read_text())
    levels=manifest['levels'];branches=manifest['children_per_nonterminal_node']
    if len(levels)!=16 or branches!=4:
        raise ValueError('Unsupported hierarchy revision')
    # islice materialises only the requested finite prefix of the symbolic tree.
    addresses=list(islice(product(range(branches),repeat=len(levels)-1),limit))
    return {'levels':levels,'potential_ops_per_stanza':branches**(len(levels)-1),
            'addresses':[list(address) for address in addresses],
            'sampled_positions':limit,'ops_executed':0}
