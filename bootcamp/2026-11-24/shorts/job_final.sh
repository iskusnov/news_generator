#!/bin/bash
# шортсы урока 12: шаг 3 (оверлей + звук) и уборка кусков
caffeinate -dimsu -w $$ &
export PATH=/opt/homebrew/bin:$PATH
mkdir -p /Users/anton/PokaTySpal/out/b1124/shorts; cd /Users/anton/PokaTySpal/jobs/b1124/shorts
for s in ${ONLY:-s01_chetyre_dollara s02_odna_iz_sta s03_gitlab_bot s04_eto_ne_zadacha s05_spec_pri_ustanovke s06_logika_chelovecheskim s07_pervyi_prompt s08_otvetstvennost s09_openhands s10_bezopasnost s11_vosem_chasov s12_chelovek_ili_ii s13_testy_v_otryve }; do echo "== $s $(date +%T)"; bash rm_$s.sh 3 && /opt/homebrew/bin/ffprobe -v error -show_entries format=duration -of csv=p=0 /Users/anton/PokaTySpal/out/b1124/shorts/$s.mp4 || echo "FAIL3 $s"; done
echo FINAL_OK
