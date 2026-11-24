#!/bin/bash
set -e
caffeinate -dimsu -w $$ &
export PATH=/opt/homebrew/bin:$PATH
mkdir -p /Users/anton/PokaTySpal/out/b1124/shorts; cd /Users/anton/PokaTySpal/jobs/b1124/shorts
for s in s01_chetyre_dollara s02_odna_iz_sta s03_gitlab_bot s04_eto_ne_zadacha s05_spec_pri_ustanovke s06_logika_chelovecheskim s07_pervyi_prompt s08_otvetstvennost s09_openhands s10_bezopasnost s11_vosem_chasov s12_chelovek_ili_ii s13_testy_v_otryve ; do echo "== $s $(date +%T)"; bash rm_$s.sh 1 || bash rm_$s.sh 1 || bash rm_$s.sh 1; bash rm_$s.sh 2; bash rm_$s.sh 3; rm -rf $HOME/vrtmp/$s; done
echo SHORTS_OK
