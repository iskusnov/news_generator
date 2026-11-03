#!/bin/bash
# Фоновая служба рендера «Пока ты спал»: выполняет задания из ~/PokaTySpal/queue/*.sh по одному.
export PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
R=$HOME/PokaTySpal; mkdir -p $R/queue $R/running $R/done $R/logs
mkdir $R/.lock 2>/dev/null || exit 0          # уже идёт задание
trap 'rmdir $R/.lock' EXIT
for j in $R/queue/*.sh; do
  [ -e "$j" ] || break
  n=$(basename "$j" .sh); mv "$j" $R/running/
  echo "$(date '+%F %T') start $n" >> $R/logs/service.log
  bash $R/running/$n.sh > $R/logs/$n.log 2>&1; rc=$?
  echo "$(date '+%F %T') end $n rc=$rc" >> $R/logs/service.log
  echo $rc > $R/logs/$n.rc; mv $R/running/$n.sh $R/done/
done
