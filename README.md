# Nurses Week Appreciation Pack

Free printable PDFs that make it easy to celebrate nursing staff during **Nurses Week (May 6–12)** — and, honestly, any week of the year. Built by **Asdale Dynamics, LLC** (Dylan Asdale, RN): warm, low-cost, unit-organizer friendly, and ready to print on a break.

**Education only — not medical advice.**

A freebie from [Asdale Dynamics, LLC](https://dylanasdale.github.io) · beginner-friendly AI books, guides, and practical tools; the code is MIT licensed — use it, adapt it, share it.

> **How this differs from a personal thank-you pack:** this is a *unit-organizer* kit — fold-over cards for preceptors and coworkers, a potluck sign-up, badge-reel tags, a team banner, and a celebration checklist you can hand to whoever volunteers to "do a little something" for the unit.

---

## What's inside

| Deliverable | Files | Pages |
|---|---|---|
| Fold-over thank-you cards (4 per sheet, two designs + two alternates per edition) | `pdfs/cards/thank-you-cards-preceptor.pdf`, `thank-you-cards-preceptor-2.pdf` | 1 page each |
| | `thank-you-cards-coworker.pdf`, `thank-you-cards-coworker-2.pdf` | |
| | `thank-you-cards-anytime.pdf`, `thank-you-cards-anytime-2.pdf` | |
| Potluck sign-up sheets (Nurses Week themed + generic) | `pdfs/potluck/potluck-signup-nurses-week.pdf`, `potluck-signup-generic.pdf` | 1 page each |
| Badge-reel compliment tags (16 per sheet, 1.6 in) | `pdfs/badge-tags/badge-reel-compliment-tags.pdf` | 1 page |
| Team banner templates (2 phrases + blank/heart flags) | `pdfs/banner/banner-happy-nurses-week.pdf` (4 pp), `banner-thank-you-nurses.pdf` (4 pp), `banner-blank-flags.pdf` (1 p) | |
| Low-cost celebration-from-plan checklist | `pdfs/checklist/celebration-plan-checklist.pdf` | 2 pages |

13 PDFs total, all US Letter (8.5 × 11 in), all generated from one Python script.

## How to print

- Print at **100% / Actual Size** (turn off "fit to page") on US Letter paper.
- **Cards:** one sheet = 4 cards. Cut into quarters (dashed lines), then fold each card up along the fold line — art on the front, ruled lines inside. Write a note, sign the bottom, done. Cardstock is nicer; plain paper is fine.
- **Badge tags:** cut on the dashed frame (or use a 1.6 in square punch). The small circle marks the badge-reel attachment spot; the back stays blank for a name or tiny note.
- **Banner:** cut the pennants, fold the top tab over string or ribbon, tape or staple. Alternate-color flags keep it festive.
- Everything also reads fine in grayscale if a color printer isn't handy.

## Browse & download

Open `site/index.html` in any browser for a friendly index with descriptions, printing tips, and download links for every PDF.

## Regenerating the PDFs

Requires Python 3 and [`reportlab`](https://pypi.org/project/reportlab/):

```bash
pip install reportlab    # once
python3 scripts/generate_pdfs.py        # writes ./pdfs/
python3 scripts/generate_pdfs.py /tmp/pdfs   # or anywhere else
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The tests rebuild all PDFs into a temp directory and verify file presence, PDF integrity, page counts, the LICENSE copyright line, and that the site + README links match real files.

## Design notes

- Hand-drawn feel: ECG hearts, scattered plus-signs, scalloped bands — drawn with vector shapes in `reportlab`, no binary fonts or images needed.
- Footer on every page credits **Asdale Dynamics, LLC** and carries the "education only — not medical advice" reminder.
- PDF metadata (Title/Author/Subject) is set on every file.

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Asdale Dynamics, LLC.

Print freely for personal and workplace use. No patient data, no secrets, no tracking — it's all local files.
