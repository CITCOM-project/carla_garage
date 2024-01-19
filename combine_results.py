#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 11:42:15 2023

@author: michael
"""

import json
from glob import glob
import os
import argparse
import pandas as pd
import networkx as nx

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--ego_vehicle", type=str)
parser.add_argument("-c", "--carla_version", type=int)
parser.add_argument("-r", "--index", type=int)
parser.add_argument("-s", "--scenario", type=int)

for s in [1, 3, 4, 7, 8, 9]:
    print(f"# Scenario {s}")
    for f in glob(f"leaderboard/data/citcom_data/Town01_Scenario{s}/*.xml"):
        r = f.split("_")[3].split(".")[0]
        if not os.path.exists(f"results/c_10_r_{r}_s_{s}/data_collect_town01_results.json"):
            print(f"#  missing: results/c_10_r_{r}_s_{s}/data_collect_town01_results.json")
            print(f"bash leaderboard/scripts/data_collection.sh -c 10 -r {r} -s {s}")
        if not os.path.exists(f"results/c_11_r_{r}_s_{s}/data_collect_town01_results.json"):
            print(f"#  missing: results/c_11_r_{r}_s_{s}/data_collect_town01_results.json")
            print(f"bash leaderboard/scripts/data_collection.sh -c 10 -r {r} -s {s}")

# data = []
# for fname in glob("results/*/data_collect*.json"):
#     args = os.path.normpath(fname).split(os.sep)[-2]
#     args = [f"-{x}" if i % 2 == 0 else x for i, x in enumerate(args.split("_"))]
#     args = vars(parser.parse_args(args))
#     with open(fname) as f:
#         records = json.load(f)["_checkpoint"]["records"]
#         if not len(records) == 1:
#             print(
#                 f"bash leaderboard/scripts/data_collection.sh -v {args['ego_vehicle']} -c {args['carla_version']} -r {args['index']}"
#             )
#             continue
#         # assert len(records) == 1, f"Bad record {args} ({len(records)})"
#         record = records[0]
#     # record.pop("friction")
#     record = record | {k: len(v) for k, v in record.pop("infractions").items()}
#     # record = record | record.pop("weather")
#     record = record | record.pop("scores")
#     record = record | record.pop("meta")
#     data.append(record | args)
# data = pd.DataFrame(data)
# data["route_id"] = [f"RouteScenario_{i}" for i in data["index"]]
# data.sort_index(inplace=True)
# data.index.name = None
# data["completion_score"] = data.pop("score_route")
# data["driving_score"] = data.pop("score_composed")
# data["infraction_penalty"] = data.pop("score_penalty")
# data["npc_vehicles"] = 120  # Fixed 120 drivers for Town01
# # Scenario 3 has a pedestrian crossing the road. Otherwise they are not supported
# data["pedestrians"] = int(args["scenario"] == 3)
# data["simulation_time"] = data.pop("duration_game")
# data["system_time"] = data.pop("duration_system")

data = pd.read_csv("results/data_bmw.csv", index_col=0)
print(data)

infractions = data.filter(regex="collisions_.*|red_light|.*_infraction")
print(data)
print(list(data["collisions_layout"]))
data["infraction_name"] = pd.from_dummies(infractions[infractions.columns], default_category="none")

dag = nx.Graph(nx.nx_pydot.read_dot("../case-studies/new/dag.dot"))

for n in sorted(dag.nodes):
    print(n.ljust(18), n in data)
print(sorted(data.columns))

data.to_csv("results/data.csv")
