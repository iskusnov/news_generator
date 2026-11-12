#!/bin/bash
set -e
caffeinate -dimsu -w $$ &
export PATH=/opt/homebrew/bin:$PATH
FREE=$(df -g "$HOME" | awk 'NR==2{print $4}'); echo "free ${FREE}G"
mkdir -p /Users/anton/PokaTySpal/out/b2710/shorts; cd /Users/anton/PokaTySpal/jobs/b2710/shorts
echo "== s01_prototip_eto_tz $(date +%T)"; bash rm_s01_prototip_eto_tz.sh 1 || bash rm_s01_prototip_eto_tz.sh 1 || bash rm_s01_prototip_eto_tz.sh 1; bash rm_s01_prototip_eto_tz.sh 2; bash rm_s01_prototip_eto_tz.sh 3
echo "== s02_ot_prototipa_k_api $(date +%T)"; bash rm_s02_ot_prototipa_k_api.sh 1 || bash rm_s02_ot_prototipa_k_api.sh 1 || bash rm_s02_ot_prototipa_k_api.sh 1; bash rm_s02_ot_prototipa_k_api.sh 2; bash rm_s02_ot_prototipa_k_api.sh 3
echo "== s03_chto_nuzhno_bylo_zakazchiku $(date +%T)"; bash rm_s03_chto_nuzhno_bylo_zakazchiku.sh 1 || bash rm_s03_chto_nuzhno_bylo_zakazchiku.sh 1 || bash rm_s03_chto_nuzhno_bylo_zakazchiku.sh 1; bash rm_s03_chto_nuzhno_bylo_zakazchiku.sh 2; bash rm_s03_chto_nuzhno_bylo_zakazchiku.sh 3
echo "== s04_vykinte_i_sdelayte_zanovo $(date +%T)"; bash rm_s04_vykinte_i_sdelayte_zanovo.sh 1 || bash rm_s04_vykinte_i_sdelayte_zanovo.sh 1 || bash rm_s04_vykinte_i_sdelayte_zanovo.sh 1; bash rm_s04_vykinte_i_sdelayte_zanovo.sh 2; bash rm_s04_vykinte_i_sdelayte_zanovo.sh 3
echo "== s05_60_agentov $(date +%T)"; bash rm_s05_60_agentov.sh 1 || bash rm_s05_60_agentov.sh 1 || bash rm_s05_60_agentov.sh 1; bash rm_s05_60_agentov.sh 2; bash rm_s05_60_agentov.sh 3
echo "== s06_monolit_v_agenta $(date +%T)"; bash rm_s06_monolit_v_agenta.sh 1 || bash rm_s06_monolit_v_agenta.sh 1 || bash rm_s06_monolit_v_agenta.sh 1; bash rm_s06_monolit_v_agenta.sh 2; bash rm_s06_monolit_v_agenta.sh 3
echo "== s07_kognitivnaya_nagruzka $(date +%T)"; bash rm_s07_kognitivnaya_nagruzka.sh 1 || bash rm_s07_kognitivnaya_nagruzka.sh 1 || bash rm_s07_kognitivnaya_nagruzka.sh 1; bash rm_s07_kognitivnaya_nagruzka.sh 2; bash rm_s07_kognitivnaya_nagruzka.sh 3
echo "== s08_kod_ne_chitaem $(date +%T)"; bash rm_s08_kod_ne_chitaem.sh 1 || bash rm_s08_kod_ne_chitaem.sh 1 || bash rm_s08_kod_ne_chitaem.sh 1; bash rm_s08_kod_ne_chitaem.sh 2; bash rm_s08_kod_ne_chitaem.sh 3
echo "== s09_zoom_s_zakazchikom $(date +%T)"; bash rm_s09_zoom_s_zakazchikom.sh 1 || bash rm_s09_zoom_s_zakazchikom.sh 1 || bash rm_s09_zoom_s_zakazchikom.sh 1; bash rm_s09_zoom_s_zakazchikom.sh 2; bash rm_s09_zoom_s_zakazchikom.sh 3
echo "== s10_freymvork_za_12_chasov $(date +%T)"; bash rm_s10_freymvork_za_12_chasov.sh 1 || bash rm_s10_freymvork_za_12_chasov.sh 1 || bash rm_s10_freymvork_za_12_chasov.sh 1; bash rm_s10_freymvork_za_12_chasov.sh 2; bash rm_s10_freymvork_za_12_chasov.sh 3
echo SHORTS_OK $(date +%T)
