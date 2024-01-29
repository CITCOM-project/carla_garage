for s in 1 3 4 7 8 9
do
    for f in leaderboard/data/citcom_data/Town01_Scenario${s}/*.xml
    do
      split=$(echo $f | tr "_" "\n")
      split=($split)
      split=$(echo ${split[3]} | tr "." "\n")
      split=($split)
      r=${split[0]}
      bash leaderboard/scripts/local_evaluation.sh -c 11 -v vehicle.lincoln.mkz2017 -s $s -r $r
      bash leaderboard/scripts/local_evaluation.sh -c 11 -v vehicle.bmw.isetta -s $s -r $r
    done
done
