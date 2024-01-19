#!/bin/bash
# Roach data collection
while getopts "p:d:w:s:v:c:r:" flag; do
  case "$flag" in
    # v) egoVehicle=$OPTARG;;
    c) carlaVersion=$OPTARG;;
    r) routeIndex=$OPTARG;;
    s) scenarioIndex=${OPTARG}
  esac
done

carlaVersion=${carlaVersion:-10}

export CARLA_ROOT="../CARLA-$carlaVersion"
export WORK_DIR=.

export CARLA_SERVER=${CARLA_ROOT}/CarlaUE4.sh
export PYTHONPATH=$PYTHONPATH:${CARLA_ROOT}/PythonAPI
export PYTHONPATH=$PYTHONPATH:${CARLA_ROOT}/PythonAPI/carla
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.${carlaVersion}-py3.7-linux-x86_64.egg
export SCENARIO_RUNNER_ROOT=${WORK_DIR}/scenario_runner
export LEADERBOARD_ROOT=${WORK_DIR}/leaderboard
export PYTHONPATH="${CARLA_ROOT}/PythonAPI/carla/":"${SCENARIO_RUNNER_ROOT}":"${LEADERBOARD_ROOT}":${PYTHONPATH}

# export ROUTES=${WORK_DIR}/leaderboard/data/longest6.xml
export ROUTES=${WORK_DIR}/leaderboard/data/citcom_data/Town01_Scenario${scenarioIndex}/route_${routeIndex}.xml
export SCENARIOS=${WORK_DIR}/leaderboard/data/training/scenarios/s${scenarioIndex}/Town01_Scenario${scenarioIndex}.json

function join_by {
  local d=${1-} f=${2-}
  if shift 2; then
    printf %s "$f" "${@/#/$d}"
  fi
}

SAVE_DIR=$(join_by _ ${@:1:$OPTIND})
export SAVE_PATH="${WORK_DIR}/results/${SAVE_DIR//-/""}"
export CHECKPOINT_ENDPOINT=${SAVE_PATH}/data_collect_town01_results.json

export REPETITIONS=1
export CHALLENGE_TRACK_CODENAME=SENSORS
export TEAM_AGENT=${WORK_DIR}/team_code/sensor_agent.py
export TEAM_CONFIG=${WORK_DIR}/pretrained_models/leaderboard/tfpp_wp_all_0
export DEBUG_CHALLENGE=0
export RESUME=1
export DATAGEN=0
# export BENCHMARK=longest6
export UNCERTAINTY_THRESHOLD=0.33
export STOP_CONTROL=1
export DIRECT=0



python3 ${LEADERBOARD_ROOT}/leaderboard/leaderboard_evaluator_local.py \
--scenarios=${SCENARIOS}  \
--routes=${ROUTES} \
--repetitions=${REPETITIONS} \
--track=${CHALLENGE_TRACK_CODENAME} \
--checkpoint=${CHECKPOINT_ENDPOINT} \
--agent=${TEAM_AGENT} \
--agent-config=${TEAM_CONFIG} \
--debug=0 \
--resume=${RESUME} \
--timeout=600
