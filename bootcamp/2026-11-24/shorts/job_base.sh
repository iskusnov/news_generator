#!/bin/bash
# шортсы урока 12: шаги 1–2 (куски + склейка) для всех роликов
caffeinate -dimsu -w $$ &
export PATH=/opt/homebrew/bin:$PATH
cd /Users/anton/PokaTySpal/jobs/b1124/shorts
for s in ${ONLY:-s01_chetyre_dollara s02_odna_iz_sta s03_gitlab_bot s04_eto_ne_zadacha s05_spec_pri_ustanovke s06_logika_chelovecheskim s07_pervyi_prompt s08_otvetstvennost s09_openhands s10_bezopasnost s11_vosem_chasov s12_chelovek_ili_ii s13_testy_v_otryve }; do echo "== $s $(date +%T)"; bash rm_$s.sh 1 || bash rm_$s.sh 1 || bash rm_$s.sh 1 || echo "FAIL1 $s"; bash rm_$s.sh 2 || echo "FAIL2 $s"; ls -la $HOME/vrtmp/$s/base.mov; done
df -h $HOME | tail -1
echo BASE_OK
