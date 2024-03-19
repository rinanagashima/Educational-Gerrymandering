# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 18:19:23 2024

@author: rinan
"""

from gerrychain import Graph, Partition, Election, proposals, updaters, constraints, accept 
from gerrychain import MarkovChain
from gerrychain.proposals import recom
from functools import partial
from gerrychain.accept import always_accept
from gerrychain.updaters import Tally
import geopandas as gpd
from shapely.geometry import Point
import networkx as nx

# Create a test graph with 5 nodes
G = nx.Graph()
G.add_nodes_from([1, 2, 3, 4, 5])
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)])

# Create an assignment mapping nodes to districts (as an example)
assign = {1: 'A', 2: 'A', 3: 'B', 4: 'B', 5: 'C'}

# Mock population data for each node
pop_data = {'total': {1: 100, 2: 150, 3: 120, 4: 130, 5: 110},
            'blackpop': {1: 20, 2: 30, 3: 25, 4: 35, 5: 20},
            'hispanicpop': {1: 50, 2: 60, 3: 55, 4: 60, 5: 50},
            'asianpop': {1: 10, 2: 15, 3: 20, 4: 15, 5: 10},
            'nativeamericanpop': {1: 5, 2: 10, 3: 5, 4: 10, 5: 5},
            'nhpipop': {1: 3, 2: 5, 3: 2, 4: 5, 5: 3},
            'multiracepop': {1: 7, 2: 10, 3: 8, 4: 10, 5: 7},
            'whitepop': {1: 10, 2: 20, 3: 15, 4: 5, 5: 20}}

# Add the population data to the graph
for node in G.nodes:
    for key, value in pop_data.items():
        G.nodes[node][key] = value[node]

initial_partition = Partition(G, 
                              assignment=assign, 
                              updaters={"population": Tally("total", alias = "population"), 
                                        "black population": Tally('blackpop', alias = "black population"),
                                        "hispanic population": Tally('hispanicpop', alias = "hispanic population"),
                                        "asian population": Tally('asianpop', alias = "asian population"),
                                        "native american population": Tally('nativeamericanpop', alias = "native american population"),
                                        "native hawaiian population": Tally('nhpipop', alias = "native hawaiian population"),
                                        "multiracial population": Tally('multiracepop', alias = "multiracial population"),
                                        "white population": Tally('whitepop', alias = "white population")
                                        })

ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)

proposal = partial(recom, 
                   pop_col="total", 
                   pop_target=ideal_population, 
                   epsilon=.5, 
                   node_repeats=2)

chain = MarkovChain(proposal=proposal, 
                    constraints=[],
                    accept=always_accept, 
                    initial_state=initial_partition, 
                    total_steps=10000)

for step, part in enumerate(chain):
    print("Available keys in the partition:", list(part.keys()))
    node_data_sample = next(iter(part.graph.nodes(data=True)))[1]
    print(f"Sample node data at step {step}: {node_data_sample}")
    try:
        print(f"Step {step}: {part['white population']}")
    except Exception as e:
        print(f"Error at step {step}: {e}")
        break  # Exit the loop or handle the error as needed

