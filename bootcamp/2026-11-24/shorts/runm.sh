#!/bin/bash
# параллельный рендер оверлеев: по одному процессу на ролик (ONLY), затем VP9-alpha
cd /home/claude/news_generator/graphics/overlays
D=/home/claude/work/b1124/shorts
IDS=$(python3 -c "import json;print(' '.join(s['id'] for s in json.load(open('$D/specs_motion.json'))))")
for id in ${1:-$IDS}; do
  ( ONLY=$id TPL=nation_motion.html node render_vertical.js $D/specs_motion.json $D/pngm >> $D/renderm.log 2>&1 && \
    ffmpeg -v error -y -framerate 25 -i $D/pngm/$id/f%04d.png -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 -b:v 3M -deadline realtime -cpu-used 8 $D/ovm_$id.webm && echo "webm $id" >> $D/renderm.log && rm -rf $D/pngm/$id ) &
done
wait; echo ALLDONE >> $D/renderm.log
