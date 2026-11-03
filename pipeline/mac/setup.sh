#!/bin/bash
# Разовая настройка Mac для рендера «Пока ты спал» (ffmpeg с аппаратным ускорением Apple)
set -e
echo "== 1/3 Homebrew"
if ! command -v brew >/dev/null 2>&1 && [ ! -x /opt/homebrew/bin/brew ]; then
  echo "Homebrew не найден — ставлю (попросит пароль от Mac, это нормально)"
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
grep -q 'brew shellenv' ~/.zprofile 2>/dev/null || echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
echo "== 2/3 ffmpeg"
command -v ffmpeg >/dev/null 2>&1 || brew install ffmpeg
ffmpeg -hide_banner -encoders 2>/dev/null | grep -E "videotoolbox" || echo "!! нет videotoolbox"
echo "== 3/3 команда pts"
grep -q 'alias pts=' ~/.zshrc 2>/dev/null || echo "alias pts='bash ~/Downloads/transcribe/render/job.sh'" >> ~/.zshrc
mkdir -p ~/Downloads/transcribe/render
echo "ffmpeg: $(command -v ffmpeg)" > ~/Downloads/transcribe/render/setup_ok.txt
ffmpeg -hide_banner -encoders 2>/dev/null | grep videotoolbox >> ~/Downloads/transcribe/render/setup_ok.txt || true
echo; echo "ГОТОВО. Закрой и открой Терминал заново — команда pts заработает."
