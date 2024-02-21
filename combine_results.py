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
import re

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--ego_vehicle", type=str)
parser.add_argument("-c", "--carla_version", type=int)
parser.add_argument("-r", "--index", type=int)
parser.add_argument("-s", "--scenario", type=int)

total = 0
data = []

lane_re = re.compile(
    r"Agent went outside its route lanes for about ([\d.]+) meters \(([\d.]+)% of the completed route\)"
)

root = "privileged"

for c in [10, 11]:
    for v in ["vehicle.bmw.isetta", "vehicle.lincoln.mkz2017"]:
        for s in [1, 3, 4, 7, 8, 9]:
            for f in glob(f"leaderboard/data/citcom_data/Town01_Scenario{s}/*.xml"):
                total += 1
                r = f.split("_")[3].split(".")[0]
                fname = f"{root}/c_{c}_v_{v}_s_{s}_r_{r}/data_collect_town01_results.json"
                run_command = f"bash leaderboard/scripts/local_evaluation.sh -c {c} -v {v} -s {s} -r {r}"
                if not os.path.exists(fname):
                    print(f"# missing data for {fname}")
                    print(run_command)
                else:
                    args = os.path.normpath(fname).split(os.sep)[-2]
                    args = [f"-{x}" if i % 2 == 0 else x for i, x in enumerate(args.split("_"))]
                    args = vars(parser.parse_args(args))
                    with open(fname) as f:
                        records = json.load(f)["_checkpoint"]["records"]
                        if not len(records) == 1:
                            print(f"# missing data for {fname}")
                            print(run_command)
                            continue
                    # assert len(records) == 1, f"Bad record {args} ({len(records)})"
                    record = records[0]
                    # record.pop("friction")
                    infractions = record.pop("infractions")
                    record = record | {k: len(v) for k, v in infractions.items()}
                    record["scenario"] = s
                    record["outside_route_lanes"] = (
                        float(lane_re.match(infractions["outside_route_lanes"][0]).group(2))
                        if len(infractions["outside_route_lanes"]) > 0
                        else 0
                    )
                    # record = record | record.pop("weather")
                    record = record | record.pop("scores")
                    record = record | record.pop("meta")
                    data.append(record | args)

print(f"df should have {total} rows")


data = pd.DataFrame(data)
print(data)
data["route_id"] = [f"RouteScenario_{s}_{i}" for s, i in zip(data["scenario"], data["route_id"])]
data.sort_index(inplace=True)
data.index.name = None
data["completion_score"] = data.pop("score_route")
data["driving_score"] = data.pop("score_composed")
data["infraction_penalty"] = data.pop("score_penalty")
data["npc_vehicles"] = 120  # Fixed 120 drivers for Town01
# Scenario 3 has a pedestrian crossing the road. Otherwise they are not supported
data["pedestrians"] = int(args["scenario"] == 3)
data["simulation_time"] = data.pop("duration_game")
data["system_time"] = data.pop("duration_system")

data.to_csv(f"{root}/data.csv")
print(f"data has {len(data)} rows")

infractions = data.filter(regex="collisions_.*|red_light|.*_infraction")
data["infraction_name"] = pd.from_dummies(infractions[infractions.columns], default_category="none")

dag = nx.Graph(nx.nx_pydot.read_dot("../studied-cases/dag.dot"))

for n in sorted(dag.nodes):
    print(n.ljust(18), n in data)
print(sorted(data.columns))

data.to_csv(f"{root}/data.csv")
