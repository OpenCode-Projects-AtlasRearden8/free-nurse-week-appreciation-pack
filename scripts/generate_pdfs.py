#!/usr/bin/env python3
"""Nurses Week Appreciation Pack — PDF generator.

Builds every printable in the pack:
  - fold-over thank-you cards (preceptor / coworker / anytime)
  - potluck sign-up sheets (Nurses Week themed + generic)
  - badge-reel compliment tags
  - team banner templates (Happy Nurses Week / Thank You Nurses / blank flags)
  - low-cost celebration-from-plan checklist

Usage:
    python3 scripts/generate_pdfs.py [output_dir]   # default: ./pdfs

Free printable from Asdale Dynamics, LLC. Education only — not medical advice.
"""

import os
import random
import sys

from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = letter  # 612 x 792 pt (8.5 x 11 in)

# ---- palette ---------------------------------------------------------------
TEAL = (0.165, 0.616, 0.561)
CORAL = (0.906, 0.435, 0.318)
NAVY = (0.149, 0.275, 0.325)
CREAM = (0.980, 0.953, 0.878)
PINK = (0.988, 0.800, 0.847)
GOLD = (0.914, 0.769, 0.416)
SKY = (0.553, 0.761, 0.867)
LILAC = (0.741, 0.675, 0.863)

FOOTER = "Free printable from Asdale Dynamics, LLC  •  dylanasdale.github.io  •  Education only — not medical advice"

PDF_META = {
    "author": "Asdale Dynamics, LLC",
    "subject": "Free printable — Nurses Week appreciation pack (education only, not medical advice)",
}


# ---- low-level drawing helpers ---------------------------------------------
def dashed_cut(c, x1, y1, x2, y2):
    c.saveState()
    c.setDash(4, 4)
    c.setStrokeColorRGB(0.65, 0.65, 0.65)
    c.setLineWidth(0.6)
    c.line(x1, y1, x2, y2)
    c.restoreState()


def wrap_text(c, text, font, size, max_width):
    return simpleSplit(text, font, size, max_width)


def footer(c, page_num=1):
    c.saveState()
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.45, 0.45, 0.45)
    c.drawCentredString(PAGE_W / 2, 0.32 * 72, FOOTER)
    if page_num > 1:
        c.drawRightString(PAGE_W - 0.4 * 72, 0.32 * 72, f"Page {page_num}")
    c.restoreState()


def heart(c, cx, cy, size, color):
    s = size
    c.saveState()
    c.setFillColorRGB(*color)
    p = c.beginPath()
    p.moveTo(cx, cy - s * 0.55)
    p.curveTo(cx - s * 1.1, cy + s * 0.05, cx - s * 0.6, cy + s * 0.75, cx, cy + s * 0.25)
    p.curveTo(cx + s * 0.6, cy + s * 0.75, cx + s * 1.1, cy + s * 0.05, cx, cy - s * 0.55)
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()


def ecg_heart(c, cx, cy, size, color):
    """Heart with a white ECG zig-zag running through it."""
    s = size
    heart(c, cx, cy, s, color)
    c.saveState()
    c.setStrokeColorRGB(1, 1, 1)
    c.setLineWidth(max(1.0, s * 0.13))
    zig = [
        (cx - s * 0.62, cy - s * 0.05),
        (cx - s * 0.35, cy - s * 0.05),
        (cx - s * 0.22, cy + s * 0.18),
        (cx - s * 0.05, cy - s * 0.28),
        (cx + s * 0.08, cy - s * 0.05),
        (cx + s * 0.62, cy - s * 0.05),
    ]
    for i in range(len(zig) - 1):
        c.line(*zig[i], *zig[i + 1])
    c.restoreState()


def plus_doodle(c, cx, cy, size, color, line_w=1.6):
    c.saveState()
    c.setStrokeColorRGB(*color)
    c.setLineWidth(line_w)
    c.setLineCap(1)
    c.line(cx - size / 2, cy, cx + size / 2, cy)
    c.line(cx, cy - size / 2, cx, cy + size / 2)
    c.restoreState()


def scatter_doodles(c, ink, x0, x1, y0, y1, seed=0):
    """A few small crosses + hearts scattered in a region (deterministic)."""
    rng = random.Random(seed)
    for i in range(5):
        x = rng.uniform(x0, x1)
        y = rng.uniform(y0, y1)
        col = ink[i % len(ink)]
        if i % 2 == 0:
            plus_doodle(c, x, y, rng.uniform(6, 9), col)
        else:
            heart(c, x, y, rng.uniform(3.5, 5), col)


# ---- thank-you cards --------------------------------------------------------
CARD_W, CARD_H = PAGE_W / 2, PAGE_H / 2  # 4.25in x 5.5in quadrant
FOLD_Y = CARD_H / 2  # fold line inside each quadrant

CARD_SETS = {
    "thank-you-cards-preceptor": [
        ("Preceptor Edition", "Thank You,", "Preceptor!", (CREAM, TEAL, CORAL), 11),
        ("Preceptor Edition", "You Taught Me", "So Much", (SKY, TEAL, CORAL), 12),
        ("Preceptor Edition", "Heartfelt", "Thanks, Mentor", (PINK, TEAL, NAVY), 13),
        ("Preceptor Edition", "For Your", "Extra Time & Care", (GOLD, TEAL, NAVY), 14),
    ],
    "thank-you-cards-preceptor-2": [
        ("Preceptor Edition", "For Your", "Patience & Wisdom", (CREAM, CORAL, TEAL), 21),
        ("Preceptor Edition", "New-Grad", "Yoda", (SKY, GOLD, NAVY), 22),
        ("Preceptor Edition", "Thanks For", "Showing Me the Ropes", (PINK, CORAL, NAVY), 23),
        ("Preceptor Edition", "Preceptor", "Superpowers", (CREAM, LILAC, NAVY), 24),
    ],
    "thank-you-cards-coworker": [
        ("Coworker Edition", "Thank You,", "Teammate!", (CREAM, CORAL, TEAL), 31),
        ("Coworker Edition", "Unit", "All-Star", (SKY, GOLD, NAVY), 32),
        ("Coworker Edition", "Thanks For", "Having My Back", (PINK, TEAL, NAVY), 33),
        ("Coworker Edition", "Best Shift", "Partner Ever", (GOLD, CORAL, NAVY), 34),
    ],
    "thank-you-cards-coworker-2": [
        ("Coworker Edition", "You Make", "Hard Days Lighter", (CREAM, LILAC, NAVY), 41),
        ("Coworker Edition", "Ride-Or-Die", "Shift Partner", (SKY, CORAL, NAVY), 42),
        ("Coworker Edition", "Grateful For", "You, Seriously", (PINK, GOLD, NAVY), 43),
        ("Coworker Edition", "Thank You For", "Picking Up That Shift", (CREAM, TEAL, NAVY), 44),
    ],
    "thank-you-cards-anytime": [
        ("Anytime Edition", "Thank You,", "Nurse!", (CREAM, GOLD, CORAL), 51),
        ("Anytime Edition", "You Are", "Appreciated", (SKY, CORAL, NAVY), 52),
        ("Anytime Edition", "A Little", '"Thanks,", A Big Deal', (PINK, TEAL, NAVY), 53),
        ("Anytime Edition", "World-Class", "Care Taker", (GOLD, NAVY, CREAM), 54),
    ],
    "thank-you-cards-anytime-2": [
        ("Anytime Edition", "World's Best", "Charge Nurse", (PINK, CORAL, NAVY), 61),
        ("Anytime Edition", "Thanks For", "Everything", (CREAM, TEAL, GOLD), 62),
        ("Anytime Edition", "You Make This", "Unit Better", (SKY, LILAC, NAVY), 63),
        ("Anytime Edition", "Just Because", "You Rock", (GOLD, PINK, NAVY), 64),
    ],
}

CARD_NOTE = "Print at 100% (Actual Size) on US Letter, single-sided. Cut into quarters, fold each card up on the fold line, write, done."


def draw_card(c, qx, qy, eyebrow, l1, l2, colorway, seed):
    """One 4.25 x 5.5 fold-over card drawn inside a quadrant with origin (qx, qy)."""
    bg, accent, accent2 = colorway
    x0, y0 = qx, qy
    # internal cut guides
    if y0 > 0:
        dashed_cut(c, x0, y0, x0 + CARD_W, y0)
    if x0 > 0:
        dashed_cut(c, x0, y0, x0, y0 + CARD_H)

    # ---- front face (top half of quadrant, above the fold)
    fy = y0 + FOLD_Y
    c.saveState()
    c.setFillColorRGB(*bg)
    c.rect(x0, fy, CARD_W, FOLD_Y, stroke=0, fill=1)
    # accent band along the top edge
    c.setFillColorRGB(*accent)
    c.rect(x0, fy + FOLD_Y - 9, CARD_W, 9, stroke=0, fill=1)
    c.restoreState()

    scatter_doodles(c, [accent2, accent, GOLD], x0 + 10, x0 + 60, fy + 12, fy + FOLD_Y - 26, seed)
    scatter_doodles(c, [accent2, accent, GOLD], x0 + CARD_W - 60, x0 + CARD_W - 10, fy + 12, fy + FOLD_Y - 26, seed + 1)

    cx = x0 + CARD_W / 2
    top = fy + FOLD_Y
    ecg_heart(c, cx, top - 60, 23, accent)
    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(cx, top - 92, eyebrow.upper())
    c.setFont("Helvetica-Bold", 15)
    c.setFillColorRGB(*accent)
    c.drawCentredString(cx, top - 110, l1)
    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawCentredString(cx, top - 126, l2)

    # name line on the front
    c.setStrokeColorRGB(*NAVY)
    c.setLineWidth(0.8)
    c.setDash(1, 2)
    c.line(x0 + 44, top - 158, x0 + CARD_W - 44, top - 158)
    c.setDash()
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.drawString(x0 + 44, top - 168, "For:")
    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica", 6.5)
    c.drawRightString(x0 + CARD_W - 44, top - 168, "write a little note inside")

    # ---- inside face (bottom half): ruled lines
    iy = y0
    c.saveState()
    c.setStrokeColorRGB(0.82, 0.82, 0.80)
    c.setLineWidth(0.8)
    start_y = iy + FOLD_Y - 48
    for i in range(5):
        yy = start_y - i * 24
        c.line(x0 + 38, yy, x0 + CARD_W - 38, yy)
    c.setStrokeColorRGB(*accent)
    heart(c, x0 + 32, iy + 38, 7, accent)
    c.setFont("Helvetica-Oblique", 7)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.drawString(x0 + 46, iy + 35, "Thanks for all you do.")
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.setFont("Helvetica", 7)
    c.drawString(x0 + CARD_W / 2 + 10, iy + 35, "With gratitude,")
    c.setDash(1, 2)
    c.line(x0 + CARD_W / 2 + 10, iy + 21, x0 + CARD_W - 38, iy + 21)
    c.setDash()
    c.restoreState()

    # fold guide
    dashed_cut(c, x0 + 12, fy, x0 + CARD_W - 12, fy)
    c.saveState()
    c.setFont("Helvetica", 5.5)
    c.setFillColorRGB(0.6, 0.6, 0.6)
    c.drawString(x0 + 16, fy + 1.5, "fold")
    c.restoreState()


def build_card_set(c, name):
    cards = CARD_SETS[name]
    # tiny rotated page label in the left margin
    c.saveState()
    c.setFont("Helvetica-Bold", 7)
    c.setFillColorRGB(*NAVY)
    c.translate(0.16 * 72, PAGE_H - 1.1 * 72)
    c.rotate(90)
    c.drawString(0, 0, "Thank-You Cards — " + name.replace("thank-you-cards-", "").replace("-", " ").title())
    c.setFont("Helvetica", 5.5)
    c.setFillColorRGB(0.45, 0.45, 0.45)
    c.drawString(0, -9, CARD_NOTE)
    c.restoreState()

    origins = [
        (0, CARD_H),
        (CARD_W, CARD_H),
        (0, 0),
        (CARD_W, 0),
    ]
    for (eyebrow, l1, l2, colorway, seed), (qx, qy) in zip(cards, origins):
        draw_card(c, qx, qy, eyebrow, l1, l2, colorway, seed)
    c.showPage()


# ---- potluck sign-up sheets --------------------------------------------------
POTLUCK_CATEGORIES = [
    ("Mains", CORAL),
    ("Sides & Salads", TEAL),
    ("Desserts", PINK),
    ("Drinks", SKY),
    ("Plates, Cups", GOLD),
]


def potluck_table(c, rows, top_y):
    left = 0.6 * 72
    right = PAGE_W - 0.6 * 72
    widths = [0.30, 0.40, 0.13, 0.17]
    headers = ["Name / Who", "Item (mention the category)", "Servings", "Notes"]
    fs = 9
    xs = []
    acc = left
    for wfrac in widths:
        xs.append(acc)
        acc += (right - left) * wfrac
    row_h = 0.44 * 72

    c.saveState()
    c.setFillColorRGB(*NAVY)
    c.rect(left, top_y - fs - 12, right - left, fs + 12, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", fs)
    for x, h in zip(xs, headers):
        c.drawString(x + 6, top_y - fs + 4, h)
    c.setStrokeColorRGB(0.6, 0.6, 0.65)
    c.setLineWidth(0.7)
    bottom = top_y - fs - 12 - row_h * rows
    for i in range(rows + 1):
        yy = top_y - fs - 12 - row_h * i
        c.line(left, yy, right, yy)
    c.line(left, top_y - fs - 12, left, bottom)
    c.line(right, top_y - fs - 12, right, bottom)
    for x in xs[1:-1]:
        c.line(x, top_y - fs - 12, x, bottom)
    c.restoreState()
    return bottom


def build_potluck(c, themed=True):
    if themed:
        c.saveState()
        c.setFillColorRGB(*CREAM)
        c.rect(0, PAGE_H - 2.35 * 72, PAGE_W, 2.35 * 72, stroke=0, fill=1)
        ecg_heart(c, 0.85 * 72, PAGE_H - 1.5 * 72, 18, CORAL)
        c.setFillColorRGB(*NAVY)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(1.15 * 72, PAGE_H - 1.25 * 72, "Potluck Sign-Up — Nurses Week")
        c.setFont("Helvetica", 9.5)
        c.setFillColorRGB(*TEAL)
        c.drawString(1.15 * 72, PAGE_H - 1.52 * 72, "Celebrating our nurses May 6-12 (and any week). Pick a slot, write it in, bring it in.")
        c.setFont("Helvetica", 8.5)
        c.setFillColorRGB(0.35, 0.35, 0.35)
        c.drawString(0.6 * 72, PAGE_H - 1.92 * 72, "Date / shift:")
        c.drawString(0.6 * 72, PAGE_H - 2.18 * 72, "Time:")
        c.drawString(3.0 * 72, PAGE_H - 1.92 * 72, "Location:")
        c.drawString(3.0 * 72, PAGE_H - 2.18 * 72, "Unit:")
        c.setStrokeColorRGB(0.55, 0.55, 0.55)
        c.setLineWidth(0.8)
        c.setDash(1, 2)
        c.line(1.75 * 72, PAGE_H - 1.90 * 72, 2.85 * 72, PAGE_H - 1.90 * 72)
        c.line(1.05 * 72, PAGE_H - 2.16 * 72, 2.85 * 72, PAGE_H - 2.16 * 72)
        c.line(3.65 * 72, PAGE_H - 1.90 * 72, 5.45 * 72, PAGE_H - 1.90 * 72)
        c.line(3.3 * 72, PAGE_H - 2.16 * 72, 5.45 * 72, PAGE_H - 2.16 * 72)
        c.restoreState()

        # category legend, right side
        cats_x = PAGE_W - 0.6 * 72
        for i, (cat, col) in enumerate(POTLUCK_CATEGORIES):
            yy = PAGE_H - 1.92 * 72 - i * 13.5
            c.saveState()
            c.setFillColorRGB(*col)
            c.circle(cats_x - 2, yy + 2.5, 3, stroke=0, fill=1)
            c.restoreState()
            c.setFillColorRGB(0.3, 0.3, 0.3)
            c.setFont("Helvetica", 7)
            c.drawRightString(cats_x - 9, yy, cat)

        bottom = potluck_table(c, rows=13, top_y=PAGE_H - 2.85 * 72)
        c.saveState()
        c.setStrokeColorRGB(*TEAL)
        heart(c, 0.7 * 72, bottom - 0.42 * 72, 7, TEAL)
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(0.9 * 72, bottom - 0.45 * 72, "Organizer tip: snap a photo of this sheet and post it in the break room and the unit group chat.")
        c.setFont("Helvetica", 7.5)
        c.drawString(0.9 * 72, bottom - 0.62 * 72, "Cups, napkins and forks from the dollar store — the 'supplies' rows keep costs low for everyone.")
        c.restoreState()
        footer(c)
        c.showPage()
        return

    # generic sheet
    c.saveState()
    c.setFillColorRGB(*NAVY)
    c.rect(0, PAGE_H - 1.95 * 72, PAGE_W, 1.95 * 72, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(0.6 * 72, PAGE_H - 1.15 * 72, "Potluck Sign-Up")
    c.setFont("Helvetica", 9.5)
    c.setFillColorRGB(*CREAM)
    c.drawString(0.6 * 72, PAGE_H - 1.45 * 72, "One sheet, any occasion — unit potlucks, graduations, appreciation days, shower parties.")
    c.restoreState()
    c.saveState()
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.setFont("Helvetica", 9)
    for label, lx in [("Date:", 0.6 * 72), ("Time:", 3.1 * 72), ("Location:", 5.4 * 72)]:
        c.drawString(lx, PAGE_H - 2.28 * 72, label)
    c.setStrokeColorRGB(0.55, 0.55, 0.55)
    c.setDash(1, 2)
    for lx, w in [(1.05 * 72, 1.75 * 72), (3.55 * 72, 1.55 * 72), (6.2 * 72, 2.35 * 72)]:
        c.line(lx, PAGE_H - 2.26 * 72, lx + w, PAGE_H - 2.26 * 72)
    c.setDash()
    c.restoreState()
    potluck_table(c, rows=16, top_y=PAGE_H - 2.8 * 72)
    footer(c)
    c.showPage()


# ---- badge-reel compliment tags ----------------------------------------------
TAG_TEXTS = [
    ("RN MVP", True),
    ("YOU ROCK", True),
    ("TEAM HERO", True),
    ("BIG THANKS", True),
    ("NIGHT OWL LEGEND", False),
    ("DAY SHIFT STAR", False),
    ("PRECEPTOR POWER", False),
    ("YOU'VE GOT THIS", False),
    ("KIND HEART", True),
    ("SCRUB STAR", True),
    ("CHARGE QUEEN", False),
    ("WE LOVE YOU", False),
    ("CARE ROCK STAR", False),
    ("GO GETTER", True),
    ("YOU MATTER", True),
    ("THANK YOU", True),
]


def build_badge_tags(c):
    c.saveState()
    c.setFillColorRGB(*NAVY)
    c.rect(0, PAGE_H - 1.35 * 72, PAGE_W, 1.35 * 72, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.6 * 72, PAGE_H - 0.75 * 72, "Badge-Reel Compliment Tags")
    c.setFont("Helvetica", 8.5)
    c.setFillColorRGB(*CREAM)
    c.drawString(
        0.6 * 72,
        PAGE_H - 1.08 * 72,
        "Sixteen 1.6-inch tags. Cut (or 1.6 in square punch), then tape to a badge reel, an ID badge or a cute pen.",
    )
    c.restoreState()

    size = 1.6 * 72
    gap = 0.22 * 72
    cols, rows = 4, 4
    left0 = (PAGE_W - (cols * size + (cols - 1) * gap)) / 2
    top0 = PAGE_H - 1.6 * 72

    combos = [(TEAL, CREAM), (CORAL, CREAM), (PINK, NAVY), (GOLD, NAVY), (SKY, NAVY), (LILAC, NAVY)]
    for r in range(rows):
        for i in range(cols):
            idx = r * cols + i
            x = left0 + i * (size + gap)
            y = top0 - (r + 1) * (size + gap) + gap
            fillc, txtc = combos[idx % len(combos)]
            c.saveState()
            c.setFillColorRGB(*fillc)
            c.roundRect(x, y, size, size, 10, stroke=0, fill=1)
            # badge-reel attachment hole (punch out or just decor)
            c.setFillColorRGB(1, 1, 1)
            c.circle(x + size / 2, y + size - 13, 4.5, stroke=0, fill=1)
            c.setStrokeColorRGB(*txtc)
            c.setLineWidth(1.1)
            c.circle(x + size / 2, y + size - 13, 4.5, stroke=1, fill=0)
            # decorative dashed inner frame
            c.setDash(3, 3)
            c.roundRect(x + 7, y + 7, size - 14, size - 14, 7, stroke=1, fill=0)
            c.restoreState()

            text = TAG_TEXTS[idx][0]
            lines = text.split(" ") if not TAG_TEXTS[idx][1] else [text]
            fsize = 14 if len(lines) == 1 else 11.5
            c.saveState()
            c.setFillColorRGB(*txtc)
            c.setFont("Helvetica-Bold", fsize)
            lh = fsize * 1.15
            base_y = y + size / 2 - 8 + (len(lines) - 1) * lh / 2
            for j, ln in enumerate(lines):
                c.drawCentredString(x + size / 2, base_y - j * lh, ln)
            heart(c, x + size / 2, y + 18, 5, txtc)
            c.restoreState()

    c.saveState()
    c.setFont("Helvetica", 7.5)
    c.setFillColorRGB(0.45, 0.45, 0.45)
    tip_y = top0 - rows * (size + gap) + gap - 14
    c.drawCentredString(
        PAGE_W / 2,
        tip_y,
        "The circle at the top is the badge-reel spot — punch it or leave it and tape the back. Write a name on the back first!",
    )
    c.restoreState()
    footer(c)
    c.showPage()


# ---- banner templates ---------------------------------------------------------
BANNER_H = 3.7 * 72          # pennant height
BANNER_TAB = 0.45 * 72       # fold tab height
BANNER_GAP = 12
BANNER_HALF_W = (PAGE_W - 1.2 * 72) / 2
BANNER_TOP_BASE = PAGE_H - 1.5 * 72


def draw_pennant(c, col, row, letter_txt, color_bg, color_txt):
    w = BANNER_HALF_W
    x0 = 0.6 * 72 + w * col
    qy = BANNER_TOP_BASE - (row + 1) * (BANNER_H + BANNER_TAB + BANNER_GAP) + BANNER_GAP

    c.saveState()
    # fold tab
    c.setFillColorRGB(*color_bg)
    c.setStrokeColorRGB(*color_txt)
    c.setLineWidth(1.2)
    c.rect(x0 + w / 2 - 1.05 * 72, qy + BANNER_H, 2.1 * 72, BANNER_TAB, stroke=1, fill=1)
    c.circle(x0 + w / 2, qy + BANNER_H + BANNER_TAB / 2, 0.09 * 72, stroke=1, fill=0)
    # pennant triangle
    p = c.beginPath()
    p.moveTo(x0, qy + BANNER_H)
    p.lineTo(x0 + w, qy + BANNER_H)
    p.lineTo(x0 + w / 2, qy)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    # white medallion
    c.setFillColorRGB(1, 1, 1)
    c.circle(x0 + w / 2, qy + BANNER_H - 1.1 * 72, 0.62 * 72, stroke=0, fill=1)
    if letter_txt:
        c.setFillColorRGB(*color_txt)
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(x0 + w / 2, qy + BANNER_H - 1.24 * 72, letter_txt)
    else:
        ecg_heart(c, x0 + w / 2, qy + BANNER_H - 1.1 * 72, 17, color_txt)
    c.restoreState()


def banner_header(c, subtitle):
    c.saveState()
    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.6 * 72, PAGE_H - 0.7 * 72, "Team Banner Template")
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.45, 0.45, 0.45)
    c.drawString(0.6 * 72, PAGE_H - 0.92 * 72, subtitle)
    c.restoreState()


PALETTE = [(TEAL, CREAM), (CORAL, CREAM), (GOLD, NAVY), (SKY, NAVY), (PINK, NAVY), (NAVY, CREAM)]


def build_banner(c, phrase):
    letters = list(phrase)
    subtitle = (
        f"Spell it out: '{phrase}'. Cut flags, fold the tab over string or ribbon, tape or staple. 4 flags per page."
    )
    page = 0
    i = 0
    while i < len(letters):
        page += 1
        banner_header(c, subtitle)
        for row in range(2):
            for col in range(2):
                if i >= len(letters):
                    break
                ch = letters[i]
                bg, txt = PALETTE[i % len(PALETTE)]
                draw_pennant(c, col, row, "" if ch == " " else ch, bg, txt)
                i += 1
        footer(c, page)
        c.showPage()


def build_blank_flags(c):
    banner_header(
        c,
        "4 blank/heart flags — write your unit name, staff names, or your own message.",
    )
    blanks = [(CREAM, TEAL), (SKY, NAVY), (PINK, CORAL), (GOLD, NAVY), (CREAM, CORAL), (LILAC, NAVY), (SKY, TEAL), (PINK, NAVY)]
    i = 0
    for row in range(2):
        for col in range(2):
            bg, txt = blanks[i]
            draw_pennant(c, col, row, "", bg, txt)
            i += 1
    footer(c, 1)
    c.showPage()


# ---- celebration checklist ------------------------------------------------------
CHECKLIST_SECTIONS = [
    (
        "3-4 weeks out — plan it (30 minutes, coffee optional)",
        CORAL,
        [
            "Pick the date(s) during Nurses Week (May 6-12) that fit the schedule",
            "Set a budget per person (aim low: $3-8 covers everything below)",
            "Ask whoever approves things for permission + break-room space",
            "Post the potluck sign-up sheet on the unit board + break room",
            "Recruit 1-2 helpers per shift — don't carry this alone",
            "Scout dollar-store decor and small prize loot on one trip",
        ],
    ),
    (
        "Week of — set the scene",
        TEAL,
        [
            "Print thank-you cards (preceptor + coworker sets) and badge tags",
            "Assemble the banner: cut flags, spell it out, hang near the break room",
            "Fill a low-cost snack basket: tea, cocoa, fun bandages, granola bars",
            "Queue a sticky-note shout-out wall for staff",
            "Confirm potluck coverage: who brings what, who covers the phones",
        ],
    ),
    (
        "Day of — keep it easy",
        GOLD,
        [
            "Set out cards + pens where people actually pause (break room, med room)",
            "Badge tag stand: pick a tag, tape it on, tag a friend",
            "Run the potluck: label items, assign a drinks-watch person",
            "Snap photos for the unit board / private group (never patient info)",
            "Draw any raffle winners (gift card, fuzzy socks, coffee run)",
        ],
    ),
    (
        "Wrap-up — 15 minutes",
        SKY,
        [
            "Return borrowed items; recycle plates and cups",
            "Thank helpers by name — a card from this pack counts",
            "Jot down what worked + what to skip for next year",
            "File extra printables for year-round birthdays and thank-yous",
        ],
    ),
]


def build_checklist(c):
    page_num = 0
    idx = 0
    per_page = 2
    while idx < len(CHECKLIST_SECTIONS):
        page_num += 1
        c.saveState()
        c.setFillColorRGB(*CREAM)
        c.rect(0, PAGE_H - 1.85 * 72, PAGE_W, 1.85 * 72, stroke=0, fill=1)
        ecg_heart(c, 0.85 * 72, PAGE_H - 0.95 * 72, 16, CORAL)
        c.setFillColorRGB(*NAVY)
        c.setFont("Helvetica-Bold", 17)
        c.drawString(1.12 * 72, PAGE_H - 0.95 * 72, "Celebration-from-Plan Checklist — Nurses Week")
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(*TEAL)
        c.drawString(1.12 * 72, PAGE_H - 1.22 * 72, "A low-cost plan you can actually pull off between shifts. May 6-12 — and honestly, any week works.")
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(1.12 * 72, PAGE_H - 1.48 * 72, "Check boxes as you go. Potluck + printables + a little dollar-store magic, done.")
        c.restoreState()

        y = PAGE_H - 2.3 * 72
        for sec_title, color, items in CHECKLIST_SECTIONS[idx: idx + per_page]:
            c.saveState()
            c.setFillColorRGB(*color)
            c.roundRect(0.6 * 72, y - 0.34 * 72, PAGE_W - 1.2 * 72, 0.36 * 72, 6, stroke=0, fill=1)
            c.setFillColorRGB(1, 1, 1)
            c.setFont("Helvetica-Bold", 10.5)
            c.drawString(0.75 * 72, y - 0.25 * 72, sec_title)
            c.restoreState()
            yy = y - 0.66 * 72
            for item in items:
                c.saveState()
                c.setStrokeColorRGB(*NAVY)
                c.setLineWidth(1.1)
                c.roundRect(0.68 * 72, yy - 2, 13, 13, 3, stroke=1, fill=0)
                c.restoreState()
                wrapped = wrap_text(c, item, "Helvetica", 9.5, PAGE_W - 1.7 * 72)
                c.setFont("Helvetica", 9.5)
                c.setFillColorRGB(0.2, 0.2, 0.2)
                for j, ln in enumerate(wrapped):
                    c.drawString(0.95 * 72, yy + (len(wrapped) - 1 - j) * 12, ln)
                yy -= 12 * len(wrapped) + 15
            y = yy - 0.14 * 72
        footer(c, page_num)
        c.showPage()
        idx += per_page


# ---- assembly -------------------------------------------------------------------
def build_all(out_dir="pdfs"):
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    built = []

    def make(rel, fn, *args):
        path = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # pageCompression=0 keeps content streams plain text — friendlier for
        # diffing and for the test suite to verify drawn content.
        sub = canvas.Canvas(path, pagesize=letter, pageCompression=0)
        sub.setTitle(rel.rsplit("/", 1)[-1].replace(".pdf", "").replace("-", " ").title())
        sub.setAuthor(PDF_META["author"])
        sub.setSubject(PDF_META["subject"])
        fn(sub, *args)
        sub.save()
        built.append(path)

    for name in CARD_SETS:
        make(f"cards/{name}.pdf", build_card_set, name)
    make("potluck/potluck-signup-nurses-week.pdf", build_potluck, True)
    make("potluck/potluck-signup-generic.pdf", build_potluck, False)
    make("badge-tags/badge-reel-compliment-tags.pdf", build_badge_tags)
    make("banner/banner-happy-nurses-week.pdf", build_banner, "HAPPY NURSES WEEK")
    make("banner/banner-thank-you-nurses.pdf", build_banner, "THANK YOU NURSES")
    make("banner/banner-blank-flags.pdf", build_blank_flags)
    make("checklist/celebration-plan-checklist.pdf", build_checklist)
    return built


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "pdfs"
    files = build_all(out_dir)
    for f in files:
        print("wrote", f)
    print(f"done: {len(files)} PDFs")


if __name__ == "__main__":
    main()
