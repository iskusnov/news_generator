#!/bin/bash
set -e
STEP=${1:-all}; mkdir -p $HOME/vrtmp/reel3_agents
if [ "$STEP" = all ] || [ "$STEP" = 1 ]; then
[ -s $HOME/vrtmp/reel3_agents/s00.mov ] || { ffmpeg -v error -y -ss 232.600 -i '../03_запись/A001_11022038_C022.mov' -vf crop=1214:2160:1313:0,scale=1080:1920,setsar=1,fps=25 -af afade=t=in:d=0.015,afade=t=out:st=7.465:d=0.015,apad -t 7.480 -c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p -c:a pcm_s16le -ar 48000 $HOME/vrtmp/reel3_agents/tmp_00.mov && mv $HOME/vrtmp/reel3_agents/tmp_00.mov $HOME/vrtmp/reel3_agents/s00.mov; }
[ -s $HOME/vrtmp/reel3_agents/s01.mov ] || { ffmpeg -v error -y -ss 240.920 -i '../03_запись/A001_11022038_C022.mov' -vf crop=1084:1928:1378:81,scale=1080:1920,setsar=1,fps=25 -af afade=t=in:d=0.015,afade=t=out:st=3.745:d=0.015,apad -t 3.760 -c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p -c:a pcm_s16le -ar 48000 $HOME/vrtmp/reel3_agents/tmp_01.mov && mv $HOME/vrtmp/reel3_agents/tmp_01.mov $HOME/vrtmp/reel3_agents/s01.mov; }
[ -s $HOME/vrtmp/reel3_agents/s02.mov ] || { ffmpeg -v error -y -ss 245.720 -i '../03_запись/A001_11022038_C022.mov' -vf crop=1214:2160:1313:0,scale=1080:1920,setsar=1,fps=25 -af afade=t=in:d=0.015,afade=t=out:st=1.385:d=0.015,apad -t 1.400 -c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p -c:a pcm_s16le -ar 48000 $HOME/vrtmp/reel3_agents/tmp_02.mov && mv $HOME/vrtmp/reel3_agents/tmp_02.mov $HOME/vrtmp/reel3_agents/s02.mov; }
[ -s $HOME/vrtmp/reel3_agents/s03.mov ] || { ffmpeg -v error -y -ss 279.000 -i '../03_запись/A001_11022038_C022.mov' -vf crop=1084:1928:1378:81,scale=1080:1920,setsar=1,fps=25 -af afade=t=in:d=0.015,afade=t=out:st=6.625:d=0.015,apad -t 6.640 -c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p -c:a pcm_s16le -ar 48000 $HOME/vrtmp/reel3_agents/tmp_03.mov && mv $HOME/vrtmp/reel3_agents/tmp_03.mov $HOME/vrtmp/reel3_agents/s03.mov; }
fi
if [ "$STEP" = all ] || [ "$STEP" = 2 ]; then
( for f in $HOME/vrtmp/reel3_agents/s*.mov; do echo "file '$(basename $f)'"; done ) > $HOME/vrtmp/reel3_agents/list.txt
ffmpeg -v error -y -f concat -safe 0 -i $HOME/vrtmp/reel3_agents/list.txt -c copy $HOME/vrtmp/reel3_agents/base.mov
fi
if [ "$STEP" = all ] || [ "$STEP" = 3 ]; then
ffmpeg -v error -y -i $HOME/vrtmp/reel3_agents/base.mov -ss 1 -t 3.00 -i broll/agents.mp4 -c:v libvpx-vp9 -i gfx/reel3_agents.webm -filter_complex '[1:v]scale=-2:1920,crop=1080:1920,setsar=1,fps=25,setpts=PTS-STARTPTS+7.92/TB[b1];[0:v][b1]overlay=0:0:eof_action=pass:enable='"'"'between(t,7.92,10.92)'"'"'[c1];[2:v]format=yuva420p[ov];[c1][ov]overlay=0:0:format=auto[vout];[0:a]loudnorm=I=-14:TP=-1:LRA=11[aout]' -map '[vout]' -map '[aout]' -c:v libx264 -preset veryfast -crf 19 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -movflags +faststart -t 19.28 '../05_публикация/reel3_agents.mp4' && echo OK '../05_публикация/reel3_agents.mp4'
fi
