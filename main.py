#!/usr/bin/env python3
"""The World in One Day -- Wednesday 25 November 2026.

Renders entry.png (1024x1024), a legibility-first poster summing up the
world news of Wednesday 25 November 2026, from the 13 verified stories in
the brief. Pure Python 3.13 standard library only: own PNG encoder
(zlib + struct) and own 5x7 bitmap font. Deterministic: same bytes on
every run. Honors MAKEFUN_OUTPUT_DIR (default /output).
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (251, 248, 241)
NAVY = (11, 31, 58)
RED = (200, 16, 46)
GOLD = (201, 162, 39)
GOLD_DARK = (176, 132, 24)
WHITE = (255, 255, 255)
CARD = (255, 255, 255)
SMOKE = (140, 140, 138)

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font. Each glyph is 7 rows of 5 bits, leftmost bit first.
# Only uppercase + digits + punctuation are needed; text is uppercased.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}


def text_width(text, scale, adv=6):
    return len(text) * adv * scale


def wrap_text(text, scale, max_w, adv=6):
    """Greedy word wrap; returns a list of lines."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale, adv) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def fill_rect(self, x, y, w, h, color):
        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)
        x = max(0, x)
        w = min(w, self.w - x)
        h = min(h, self.h - y)
        if w <= 0 or h <= 0:
            return
        row = bytes(color) * w
        for yy in range(y, y + h):
            off = (yy * self.w + x) * 3
            self.px[off:off + w * 3] = row

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, dx * 2 + 1, 1, color)

    def fill_polygon(self, points, color):
        """Scanline polygon fill (points: list of (x, y))."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x1, y1 = points[i]
                x2, y2 = points[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    t = (y - y1) / (y2 - y1)
                    xs.append(x1 + t * (x2 - x1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                x0 = int(xs[i] + 0.5)
                x1 = int(xs[i + 1] + 0.5)
                if x1 >= x0:
                    self.fill_rect(x0, y, x1 - x0 + 1, 1, color)

    def draw_text(self, x, y, scale, text, color, adv=6):
        text = text.upper()
        for i, ch in enumerate(text):
            glyph = FONT.get(ch, FONT[" "])
            ox = x + i * adv * scale
            for r, row in enumerate(glyph):
                bits = int(row, 2)
                for c in range(5):
                    if bits & (1 << (4 - c)):
                        x0 = int(round(ox + c * scale))
                        x1 = int(round(ox + (c + 1) * scale))
                        y0 = int(round(y + r * scale))
                        y1 = int(round(y + (r + 1) * scale))
                        self.fill_rect(x0, y0, x1 - x0, y1 - y0, color)

    def draw_text_centered(self, cx, y, scale, text, color, adv=6):
        x = cx - text_width(text, scale, adv) // 2
        self.draw_text(x, y, scale, text, color, adv)
        return x


# ----------------------------------------------------------------- png ----
def encode_png(w, h, px):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)  # filter: none
        raw += px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# -------------------------------------------------------------- layout ----
def draw_masthead(c):
    c.draw_text_centered(W // 2, 22, 6, "THE WORLD IN ONE DAY", NAVY)
    c.fill_rect(W // 2 - 110, 72, 220, 4, RED)
    c.draw_text_centered(W // 2, 84, 4, "WEDNESDAY 25 NOVEMBER 2026", RED)
    c.draw_text_centered(W // 2, 120, 2.5,
                         "ALL STORIES FROM THE 25 NOVEMBER WIRES "
                         "AND MORNING EDITIONS", NAVY, adv=5)
    c.fill_rect(16, 146, W - 32, 3, NAVY)


def draw_hero(c):
    # Headline, two lines, full width.
    c.draw_text_centered(W // 2, 158, 8, "RIYADH'S TALLEST", NAVY)
    c.draw_text_centered(W // 2, 230, 8, "TOWER HIT AGAIN", NAVY)
    c.draw_text_centered(W // 2, 306, 3,
                         "HOUTHIS HIT PIF TOWER IN RIYADH", RED,
                         adv=5)
    # The two big numbers, left half.
    c.draw_text(70, 355, 12, "11", GOLD_DARK)
    c.draw_text(70, 448, 5, "WOUNDED", NAVY)
    c.draw_text(330, 355, 12, "2ND", RED)
    c.draw_text(330, 448, 5, "STRIKE", NAVY)
    # Tower graphic, right half: tapered gold tower, antenna, blast.
    tx = 830  # tower centre x
    # Blast spikes (behind the circles).
    import math
    for k in range(8):
        ang = math.pi * k / 4.0
        tip_x = int(tx + 58 * math.cos(ang))
        tip_y = int(345 + 58 * math.sin(ang))
        base1 = (int(tx + 14 * math.cos(ang + 0.35)),
                 int(345 + 14 * math.sin(ang + 0.35)))
        base2 = (int(tx + 14 * math.cos(ang - 0.35)),
                 int(345 + 14 * math.sin(ang - 0.35)))
        c.fill_polygon([(tip_x, tip_y), base1, base2], GOLD)
    c.fill_circle(tx, 345, 40, GOLD)
    c.fill_circle(tx, 345, 26, RED)
    c.fill_circle(tx, 345, 12, WHITE)
    # Tower body: tapered trapezoid, gold with navy windows.
    c.fill_polygon([(760, 510), (900, 510), (858, 370), (802, 370)], GOLD)
    c.fill_rect(826, 345, 8, 26, NAVY)  # antenna
    c.fill_circle(830, 343, 4, RED)     # beacon
    for row in range(6):
        wy = 390 + row * 20
        # windows across the tower width at this height
        nwin = 5 - row // 2
        for k in range(nwin):
            wx = int(830 - (nwin - 1) * 11 + k * 22)
            c.fill_rect(wx - 4, wy, 8, 10, NAVY)
    c.draw_text_centered(tx, 522, 2.5, "PIF TOWER", NAVY, adv=5)
    c.fill_rect(16, 548, W - 32, 4, NAVY)


SECONDARY = [
    ("UKRAINE", "UKRAINE ADMITS FINLAND SHIP STRIKE",
     "Zelenskiy: Kyiv hit the ship."),
    ("USA / TECH", "HUAWEI CONVICTED OF FRAUD",
     "Bank fraud and trade-secret plot."),
    ("USA", "TRUMP HONOURS GIULIANI",
     "Giuliani gets Medal of Freedom."),
    ("CYBER", "CIA, ODNI HIT BY BREACH",
     "Unclassified data taken in breach."),
]


def draw_secondary(c):
    xs = [16, 516]
    ys = [556, 690]
    for idx, (label, headline, body) in enumerate(SECONDARY):
        x = xs[idx % 2]
        y = ys[idx // 2]
        w = 492
        h = 126
        c.fill_rect(x, y, w, h, CARD)
        # Navy border.
        c.fill_rect(x, y, w, 3, NAVY)
        c.fill_rect(x, y + h - 3, w, 3, NAVY)
        c.fill_rect(x, y, 3, h, NAVY)
        c.fill_rect(x + w - 3, y, 3, h, NAVY)
        # Red label bar.
        c.fill_rect(x + 3, y + 3, w - 6, 28, RED)
        c.draw_text(x + 16, y + 9, 2.5, label, WHITE, adv=5)
        # Headline, wrapped to at most 2 lines, >= 26px type.
        lines = wrap_text(headline, 4, w - 28)
        for li, line in enumerate(lines[:2]):
            c.draw_text(x + 14, y + 38 + li * 32, 4, line, NAVY)
        # One body line, >= 16px type.
        c.draw_text(x + 14, y + 104, 2.5, body, NAVY, adv=5)


STRIP = [
    "NATO SENDS WARNING JETS TO POLAND",
    "3 TANKERS HIT BY MINES IN HORMUZ",
    "SARKOZY CORRUPTION CASE TO TRIAL",
    "KOREA MINISTER QUITS IN EXAM SCANDAL",
    "5.6 QUAKE SHAKES NEPAL, FELT IN INDIA",
    "ENGLAND BEAT AUSTRALIA BY 8 WICKETS",
    "NEW ZEALAND HOLD INDIA TO TEST DRAW",
    "MODI, MERZ HOLD INDIA-GERMANY TALKS",
]


def draw_strip(c):
    c.draw_text(16, 828, 3, "ALSO TODAY", RED)
    c.fill_rect(16, 856, W - 32, 3, GOLD)
    col_x = [16, 524]
    for idx, item in enumerate(STRIP):
        col = idx % 2
        row = idx // 2
        y = 870 + row * 38
        x = col_x[col]
        c.fill_rect(x, y + 4, 10, 10, RED)
        c.draw_text(x + 18, y, 2.5, item, NAVY, adv=5)


def render():
    c = Canvas(W, H, PAPER)
    # Outer navy frame.
    c.fill_rect(0, 0, W, 5, NAVY)
    c.fill_rect(0, H - 5, W, 5, NAVY)
    c.fill_rect(0, 0, 5, H, NAVY)
    c.fill_rect(W - 5, 0, 5, H, NAVY)
    draw_masthead(c)
    draw_hero(c)
    draw_secondary(c)
    draw_strip(c)
    return encode_png(W, H, c.px)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = render()
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
