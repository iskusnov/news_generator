# Конвейер: этапы и форматы

Архитектура и решения: Claude Doc «News Generator — архитектура системы» (https://claude.ai/artifact/BVT3SE3ozcfkVMgWGKH41H).

| Время (Мадрид) | Этап | Кто | Результат |
|---|---|---|---|
| 03:30 | Выгрузка X | Grok Bot (agents/GROK.md) | 01_новости/grok.md + скриншоты |
| 03:50 | Сбор новостей, сценарий v1 | Claude (проект «Контент») | 02_сценарий/scenario.md |
| до 05:00 | Сценарий у Антона | — | правки, «ок» |
| 06:00 | Запись | Антон | 03_запись/ |
| после | Монтаж, графика, шортсы, проверка | Claude (CLAUDE.md) | 04_монтаж/, 05_публикация/ |
| после | Тексты публикации | Gemini (agents/GEMINI.md) | 05_публикация/publish |

## Форматы файлов
- `takes.json` — `{fps, tc_start, opener_after, opener_gap, segments:[{in,out,tag}]}` (секунды исходника). Первые куски — `tag: teaser` (5–10 с суммарно), `opener_after` = их число: после них встаёт интро.
- `edl.json` — `{fps, tc_start, total, gap_at, gap, edl:[{src_in,src_out,rec,tag,scale}], covers:[{rec_in,rec_out}]}`.
- `specs.json` — графика: `[{id,type,rec,dur,...параметры}]`, типы: opener, lower, kicker, stat, strike, chip, quote, day, poll, end (graphics/overlays/template.html).
- `shorts.json` — `[{id,title,dur,pieces:[{src_in,src_out}],chunks:[{s,e,words}],cta,poll?}]`.
- `silence.json` — `[[start,end]]`; `gaze.json` — `{away:[[t0,t1]],samples:[...]}`.

## Чистка (еженедельно)
| Что | Срок |
|---|---|
| Исходник 4K | 30 дней после публикации |
| Промежуточное (ProRes-графика, прокси, кадры) | до публикации |
| Финал, шортсы, Reels, превью | 90 дней |
| Тексты и данные | навсегда (GitHub) |
