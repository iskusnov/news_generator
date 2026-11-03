#!/bin/bash
# Разовая установка фоновой службы рендера (запускать из Терминала)
set -e
R=$HOME/PokaTySpal; mkdir -p $R/bin $R/queue $R/running $R/done $R/logs $R/out
cp ~/Downloads/transcribe/render/watch.sh $R/bin/watch.sh; chmod +x $R/bin/watch.sh
P=$HOME/Library/LaunchAgents/com.pokatyspal.render.plist; mkdir -p $(dirname $P)
cat > $P <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.pokatyspal.render</string>
<key>ProgramArguments</key><array><string>/bin/bash</string><string>$R/bin/watch.sh</string></array>
<key>StartInterval</key><integer>20</integer>
<key>RunAtLoad</key><true/>
<key>StandardErrorPath</key><string>$R/logs/launchd.err</string>
</dict></plist>
PL
launchctl bootout gui/$(id -u) $P 2>/dev/null || true
launchctl bootstrap gui/$(id -u) $P
echo "ГОТОВО: служба рендера запущена. Папка: $R"
