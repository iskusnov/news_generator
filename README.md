# News Generator — «Пока ты спал · Новости AI»

Конвейер ежедневного YouTube-выпуска про ИИ: сбор новостей → сценарий → запись → монтаж → проверка → публикация.
Ведущий — Антон. Выпуск пн–сб, запись в 06:00 по Мадриду, эксперимент на 90 дней.

| Где | Что |
|---|---|
| GitHub (этот репозиторий) | код, правила, шаблоны графики, данные выпусков (тексты, монтажные листы) |
| Google Drive `News_generator/` (аккаунт tony.alexandridis, расшарен на aiskusnov) | видео, скриншоты, музыка, B-roll, рендеры |
| Mac Антона | Drive for desktop (`~/Library/CloudStorage/GoogleDrive-tony.alexandridis@gmail.com/My Drive/News_generator`), DaVinci Resolve |

> **Хочешь просто сделать рилс/шортс из своего видео** (монтаж без пауз, субтитры по словам, обложка) — читай [`docs/REELS_GUIDE.md`](docs/REELS_GUIDE.md).

Начни с:
- [`AGENTS.md`](AGENTS.md) — общие правила для любой модели;
- [`CLAUDE.md`](CLAUDE.md) — как Claude ведёт выпуск от записи до готовых файлов;
- [`agents/GEMINI.md`](agents/GEMINI.md) — YouTube-редактор (названия, описания, аналитика);
- [`agents/GROK.md`](agents/GROK.md) — ночная выгрузка из X;
- [`docs/STANDARD.md`](docs/STANDARD.md) — стандарт монтажа (проверяется скриптами);
- [`docs/PIPELINE.md`](docs/PIPELINE.md) — этапы, команды, форматы файлов.

## Структура
```
pipeline/     скрипты этапов: transcribe, signals (паузы), gaze (взгляд), cut (монтажный лист), fcpxml, srt, qa
graphics/     HyperFrames-композиции (интро) + оверлеи (плашки, выноски, шортсы, превью), шрифты, логотипы
episodes/     данные каждого выпуска: takes.json, edl.json, specs.json, shorts.json, publish.md (без видео)
agents/       инструкции для Gemini и Grok
docs/         стандарт монтажа, описание конвейера, выгрузка проекта «Контент»
```

Ключи (Groq, Pixabay) и видео в репозиторий не попадают никогда: ключи лежат у Антона на Mac в `~/Downloads/transcribe/`.
