# CLAUDE.md — как вести выпуск

Сначала прочитай `AGENTS.md` и `docs/STANDARD.md`. Конвейер зафиксирован: не изобретай новые инструменты, меняй только через этот репозиторий.

## Окружение
- Облачный контейнер Claude: Python 3.13 (+3.12 с mediapipe==0.10.14 для gaze.py), Node 22, ffmpeg, Chromium (Playwright) — графика и анализ.
- Mac Антона через мост (`device_bash`, Linux-VM, лимит 180 с на вызов): исходники 4K, ffmpeg для нарезки шортсов/прокси. `$HOME/mnt/CloudStorage/GoogleDrive-tony.alexandridis@gmail.com/My Drive/News_generator` = папка Drive. Файлы в облаке без «Доступно офлайн» дают «Resource deadlock avoided» — попроси отметить папку выпуска офлайн или застейдж файл (`device_stage_files`).
- Ключи на Mac: `~/Downloads/transcribe/.groq_key_claude` (Groq), `~/Downloads/transcribe/.pixabay_key` (Pixabay). Никогда не выводить в чат.
- HyperFrames: `cd graphics && npm i`, `HYPERFRAMES_BROWSER_PATH=$(node -e "console.log(require('playwright').chromium.executablePath())")`.

## Шаги после записи (папка выпуска `выпуски/ГГГГ-ММ-ДД/`)
1. **Звук и прокси** (Mac): `ffmpeg -i ЗАПИСЬ -vn -ac 1 -ar 16000 -c:a aac -b:a 48k audio.m4a`; прокси для взгляда частями ≤120 с: `ffmpeg -ss X -t 120 -i ЗАПИСЬ -vf fps=5,scale=640:-2 -an proxy_X.mp4`. Застейджить.
2. **Распознавание**: Groq whisper-large-v3, `timestamp_granularities[]=word` и `segment` → `words.json` (см. pipeline/groq_transcribe.py; для слов добавить word).
3. **Сигналы**: `python3 pipeline/signals.py audio.m4a silence.json`; `python3.12 pipeline/gaze.py proxy_X.mp4 gaze_X.json --offset X` (склеить away).
4. **Дубли** (решаешь ты по сценарию из `02_сценарий` и тексту слов): `takes.json` — порядок кусков. Начало всегда: **тизер 5–10 с** (3–4 самые цепляющие фразы из разных новостей, по 1,5–3 с, tag `teaser`) → интро (`opener_after` = число кусков тизера) → привет и новости. Каждая новость = блок; служебное и брак не берём.
5. **Монтажный лист**: `python3 pipeline/cut.py takes.json words.json silence.json gaze.json edl.json`. Всё из `covers` закрыть визуалом новости.
5a. **Сверка до рендера (обязательно)**: `python3 pipeline/review.py edl.json words.json silence.json --audio audio.m4a draft.mp3 > review.txt`. Все ПОВТОР/ОБРЫВОК/ОБРЫВ исправить в takes; каждое РАСТЯНУТО переслушать — перераспознать 3–5 с вокруг через Groq (Whisper прячет «тьфу» и второй заход в одно длинное слово). Антону — лист склеек + `draft.mp3`, ждать «ок» или правок; графику и 4K не рендерить до «ок» (если Антон недоступен — сверку делаешь сам и пишешь, что проверено).
6. **Графика**: интро (`graphics/compositions/intro.html` + vars: день, дата, 3 главные новости с логотипами; трек из `_бренд/музыка`), плашки/вырезки/выноски (`graphics/overlays`). Прозрачные слои → ProRes 4444 на Mac (VP9-alpha webm → `prores_ks -profile:v 4444`).
7. **Таймлайн**: `pipeline/fcpxml.py` → `04_монтаж/*.fcpxml`. Импорт в DaVinci: сначала перетащить исходник и `gfx/` в медиапул, затем Import Timeline без «Automatically import source clips».
8. **Шортсы/Reels**: вертикальный кроп 1215×2160 → 1080×1920 + оверлей с логотипами на первом кадре, хуком и словесными субтитрами (graphics/overlays/shorts.html), рендер ffmpeg на Mac.
9. **Проверка**: черновой рендер 540p по edl + `pipeline/qa.py` → `04_монтаж/qa.txt`. С замечаниями не сдавать.
10. **Публикация**: главы из edl → `chapters.txt`; превью A/B (`graphics/overlays/thumbnail.html`); тексты — Gemini по `agents/GEMINI.md` (или Claude по тем же правилам). Отдать Антону: таймлайн, шортсы, превью, тексты — одним сообщением, всё сразу.
11. Закоммитить `episodes/ГГГГ-ММ-ДД/` (takes, edl, specs, shorts, publish, transcript).

## Reels / Shorts (Toxic TV и нарезки)
- Тон и бренд: Toxic TV — чёрный + кислотно-розовый #FF2E93 + вольт #E8FF2E, штампы, «7 vs 18», капс-субтитры (graphics/overlays/toxic_reels.html). Новостные шортсы — бренд «Пока ты спал» (graphics/overlays/shorts.html).
- Порядок: `takes.json` на каждый ролик → `CUT_GAP=0.22 CUT_PAD=0.07 python3 pipeline/cut.py …` → **сверка** `pipeline/review.py … --audio` (см. 5a) и «ок» Антона → `reels_config.json` (заголовок, штампы, списки, vs в секундах исходника) → `python3 pipeline/reels.py` → рендер графики (`TPL=toxic_reels.html node graphics/overlays/render_vertical.js`) → VP9-alpha → B-roll из Pixabay на окна `covers` → `python3 pipeline/vertical_render.py … > render.sh` → на Mac `bash render.sh 1`, `2`, `3` (каждый шаг < 180 с; шаг 1 можно повторять — готовые куски пропускаются).
- Финальная карточка не перекрывает речь: `tail` в reels_config (стоп-кадр после последнего слова, = endDur). Части на Mac называются по содержимому (`p_<src_in>_<кадры>_<scale>.mov`) — после правки монтажа перерендериваются только изменённые куски.
- Куски рендерятся по одному с точной длиной звука (PCM + apad + -t), иначе звук уезжает; несколько 4K-декодеров сразу VM убивает.

## Сдача
В ответе Антону 3–5 строк: что готово, где лежит, что проверить руками. Не «готово», пока qa.py не прошёл.
