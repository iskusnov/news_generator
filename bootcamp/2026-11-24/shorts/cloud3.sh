#!/bin/bash
# шаг 3 (оверлей + звук −14 LUFS) в облаке по base.mov с Mac (очередь Mac занята рендером урока)
cd /home/claude/work/b1124/shorts
for f in rm_s*.sh; do id=${f#rm_}; id=${id%.sh}; [ -s out/$id.mp4 ] && continue
  sed -n '/STEP" = 3/,/^fi/p' $f | sed -n 2p | sed "s#\$HOME/vrtmp/$id/base.mov#/mnt/user-data/uploads/vrtmp/$id/base.mov#; s#/Users/anton/PokaTySpal/jobs/b1124/shorts/#/home/claude/work/b1124/shorts/#g; s#/Users/anton/PokaTySpal/out/b1124/shorts/#/home/claude/work/b1124/shorts/out/#" > /tmp/claude-0/sc/t3_$id.sh
  bash /tmp/claude-0/sc/t3_$id.sh > /dev/null && echo "done $id"
done
echo CLOUD_OK
