#!/usr/bin/env python3
"""The World in One Day -- Tuesday 24 November 2026.
Draws a dense newspaper front page (1024x1024 PNG) from 36 verified
stories of 24 Nov 2026, using only the Python standard library.
No network, no clock, no unseeded randomness: two runs are byte-identical.
Writes to $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png).
"""
import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)
INK = (22, 22, 20)
RED = (178, 38, 30)
NAVY = (31, 58, 95)
TEAL = (15, 118, 110)
GOLD = (176, 124, 0)
GREY = (110, 108, 100)
LIGHT = (232, 226, 210)
SKY = (168, 205, 224)
GRASS = (122, 158, 92)
SAND = (214, 196, 150)
WHITE = (255, 255, 255)
SMOKE = (150, 148, 140)

# ------------------------------------------------- single-stroke vector font
# Glyphs are polylines on a 5 wide x 7 tall grid (y grows downward).
# Written by hand for this entry: every stroke is my own design.
FONT = {
    "A": (((0, 7), (2.5, 0), (5, 7)), ((1.4, 4.6), (3.6, 4.6))),
    "B": (((0.7, 0), (0.7, 7), (4, 7), (4.7, 5.5), (4, 3.8), (0.7, 3.8)),
           ((0.7, 0), (4, 0), (4.7, 1.5), (4, 3.8))),
    "C": (((4.6, 1.2), (3.4, 0), (1.2, 0), (0, 1.8), (0, 5.2), (1.2, 7), (3.4, 7), (4.6, 5.8)),),
    "D": (((0.7, 0), (0.7, 7), (3.6, 7), (5, 5.4), (5, 1.6), (3.6, 0), (0.7, 0)),),
    "E": (((4.4, 0), (0.7, 0), (0.7, 7), (4.4, 7)), ((0.7, 3.5), (3.6, 3.5))),
    "F": (((0.7, 0), (0.7, 7)), ((0.7, 0), (4.4, 0)), ((0.7, 3.5), (3.6, 3.5))),
    "G": (((4.6, 1.2), (3.4, 0), (1.2, 0), (0, 1.8), (0, 5.2), (1.2, 7),
            (3.4, 7), (4.6, 5.8), (4.6, 3.6), (2.4, 3.6)),),
    "H": (((0.7, 0), (0.7, 7)), ((4.3, 0), (4.3, 7)), ((0.7, 3.5), (4.3, 3.5))),
    "I": (((2.5, 0), (2.5, 7)), ((1, 0), (4, 0)), ((1, 7), (4, 7))),
    "J": (((1.4, 0), (4.6, 0)), ((3.6, 0), (3.6, 5.4), (2.6, 7), (1, 7), (0.4, 5.8))),
    "K": (((0.7, 0), (0.7, 7)), ((4.4, 0), (0.7, 3.6)), ((2.2, 4.8), (4.4, 7))),
    "L": (((0.7, 0), (0.7, 7), (4.4, 7)),),
    "M": (((0.5, 7), (0.5, 0), (2.5, 4), (4.5, 0), (4.5, 7)),),
    "N": (((0.7, 7), (0.7, 0), (4.3, 7), (4.3, 0)),),
    "O": (((1.4, 0), (3.6, 0), (5, 1.6), (5, 5.4), (3.6, 7), (1.4, 7),
            (0, 5.4), (0, 1.6), (1.4, 0)),),
    "P": (((0.7, 7), (0.7, 0), (4, 0), (4.8, 1.4), (4, 3.4), (0.7, 3.4)),),
    "Q": (((1.4, 0), (3.6, 0), (5, 1.6), (5, 5.4), (3.6, 7), (1.4, 7),
            (0, 5.4), (0, 1.6), (1.4, 0)), ((3.4, 5), (5, 7))),
    "R": (((0.7, 7), (0.7, 0), (4, 0), (4.8, 1.4), (4, 3.4), (0.7, 3.4)),
           ((2.6, 3.8), (4.8, 7))),
    "S": (((4.4, 1.4), (3.2, 0), (1.4, 0), (0.4, 1.2), (0.8, 3), (2.6, 3.8),
            (4.2, 4.4), (4.6, 5.8), (3.4, 7), (1.6, 7), (0.4, 5.8)),),
    "T": (((0.5, 0), (4.5, 0)), ((2.5, 0), (2.5, 7))),
    "U": (((0.7, 0), (0.7, 5.4), (1.8, 7), (3.2, 7), (4.3, 5.4), (4.3, 0)),),
    "V": (((0.5, 0), (2.5, 7), (4.5, 0)),),
    "W": (((0.5, 0), (1.3, 7), (2.5, 3.5), (3.7, 7), (4.5, 0)),),
    "X": (((0.7, 0), (4.3, 7)), ((4.3, 0), (0.7, 7))),
    "Y": (((0.7, 0), (2.5, 3.4), (4.3, 0)), ((2.5, 3.4), (2.5, 7))),
    "Z": (((0.7, 0), (4.3, 0), (0.7, 7), (4.3, 7)),),
    "0": (((1.4, 0), (3.6, 0), (5, 1.6), (5, 5.4), (3.6, 7), (1.4, 7),
            (0, 5.4), (0, 1.6), (1.4, 0)),),
    "1": (((1.2, 1.6), (2.8, 0), (2.8, 7)), ((1, 7), (4.4, 7))),
    "2": (((0.8, 1.6), (1.8, 0), (3.6, 0), (4.4, 1.2), (4.4, 2.6), (0.8, 7), (4.4, 7)),),
    "3": (((0.8, 0.8), (2, 0), (3.6, 0), (4.4, 1), (4.4, 2.8), (3, 3.6),
            (4.4, 4.4), (4.4, 5.8), (3.4, 7), (1.8, 7), (0.8, 6.2)),),
    "4": (((3.6, 0), (3.6, 7)), ((0.6, 4.6), (4.4, 4.6)), ((3.6, 0), (0.6, 4.6))),
    "5": (((4.4, 0), (0.8, 0), (0.8, 3.4), (3.4, 3.4), (4.4, 4.6), (4.4, 5.8),
            (3.4, 7), (1.6, 7), (0.8, 6)),),
    "6": (((4.2, 1), (3, 0), (1.2, 0), (0.4, 1.6), (0.4, 5.4), (1.4, 7),
            (3.2, 7), (4.4, 5.6), (4.4, 3.8), (3, 3), (1, 3.4)),),
    "7": (((0.8, 0), (4.4, 0), (2.2, 7)),),
    "8": (((1.2, 0.2), (3.8, 0.2), (4.6, 1.6), (3.8, 3.4), (1.2, 3.4),
            (0.4, 1.6), (1.2, 0.2)),
           ((1.2, 3.6), (3.8, 3.6), (4.6, 5.2), (3.6, 6.8), (1.4, 6.8),
            (0.4, 5.2), (1.2, 3.6))),
    "9": (((0.8, 6), (2, 7), (3.8, 7), (4.6, 5.4), (4.6, 1.6), (3.6, 0),
            (1.8, 0), (0.6, 1.4), (0.6, 3.2), (2, 3.8), (4, 3.4)),),
    ".": (((2.2, 6.2), (2.8, 6.2), (2.8, 7), (2.2, 7)),),
    ",": (((2.6, 6), (2.4, 7)),),
    ":": (((2.2, 1.8), (2.8, 1.8), (2.8, 2.6), (2.2, 2.6)),
           ((2.2, 5.2), (2.8, 5.2), (2.8, 6), (2.2, 6))),
    ";": (((2.2, 1.8), (2.8, 1.8), (2.8, 2.6), (2.2, 2.6)), ((2.6, 5), (2.4, 7))),
    "!": (((2.5, 0), (2.5, 4.8)), ((2.2, 6.2), (2.8, 6.2), (2.8, 7), (2.2, 7))),
    "?": (((1, 1.4), (2, 0), (3.6, 0), (4.4, 1), (4.2, 2.6), (2.5, 3.6), (2.5, 4.6)),
           ((2.2, 6.2), (2.8, 6.2), (2.8, 7), (2.2, 7))),
    "-": (((0.8, 3.6), (4.2, 3.6)),),
    "\u2014": (((0.2, 3.6), (4.8, 3.6)),),
    "/": (((4, 0), (1, 7)),),
    "%": (((4, 0), (1, 7)),
           ((0.8, 1.2), (1.8, 1.2), (1.8, 2.2), (0.8, 2.2), (0.8, 1.2)),
           ((3.2, 4.8), (4.2, 4.8), (4.2, 5.8), (3.2, 5.8), (3.2, 4.8))),
    "$": (((2.5, 0), (2.5, 7)),
           ((4.2, 1.4), (3, 0.2), (1.4, 0.6), (0.8, 2), (1.6, 3.4),
            (3.4, 3.8), (4.2, 5), (3, 6.8), (1.6, 6.6), (0.8, 5.4))),
    "&": (((4, 0.6), (3, 0), (1.6, 0.6), (1.4, 2.4), (3.4, 4.4), (4.4, 6),
            (4.2, 7), (2.6, 7), (1.2, 5.6), (2.2, 3.4), (4.4, 1.8)),),
    "+": (((2.5, 1), (2.5, 6)), ((0.8, 3.5), (4.2, 3.5))),
    "=": (((0.8, 2.4), (4.2, 2.4)), ((0.8, 4.8), (4.2, 4.8))),
    "(": (((3.6, 0), (2.2, 1.8), (2.2, 5.2), (3.6, 7)),),
    ")": (((1.4, 0), (2.8, 1.8), (2.8, 5.2), (1.4, 7)),),
    '"': (((1.6, 0), (1.6, 2)), ((3.4, 0), (3.4, 2))),
    "'": (((2.5, 0), (2.5, 2)),),
    "*": (((2.5, 0.6), (2.5, 6.4)), ((0.6, 2), (4.4, 5)), ((4.4, 2), (0.6, 5))),
    "\u2022": (((1.8, 2.8), (3.2, 2.8), (3.2, 4.2), (1.8, 4.2)),),
    "[": (((4, 0), (1, 0), (1, 7), (4, 7)),),
    "]": (((1, 0), (4, 0), (4, 7), (1, 7)),),
    "~": (((0.8, 4), (1.8, 2.6), (3, 4), (4.2, 2.6)),),
    " ": (),
}
ADV = 6.0  # glyph advance in grid units


def text_width(text, size):
    return len(text) * ADV * size / 7.0


def wrap(text, size, max_w):
    """Greedy word wrap; returns list of lines, each fitting max_w."""
    words = text.split(" ")
    lines, cur = [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_width(trial, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self):
        self.buf = bytearray(bytes(PAPER) * (W * H))
        self.boxes = []      # (x0, y0, x1, y1, label) text boxes, must not overlap
        self.pins = []       # (x, y, n) map pins, must not collide

    def px(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            self.buf[i:i + len(row)] = row

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def _dot(self, x, y, c, r):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r + r:
                    self.px(x + dx, y + dy, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        r = max(0, (t - 1) // 2)
        for i in range(steps + 1):
            x = round(x0 + dx * i / steps)
            y = round(y0 + dy * i / steps)
            if t <= 1:
                self.px(x, y, c)
            else:
                self._dot(x, y, c, r)

    def poly(self, pts, c, t=1, closed=False):
        n = len(pts)
        for i in range(n - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], c, t)
        if closed and n > 2:
            self.line(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1], c, t)

    def poly_fill(self, pts, c):
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa, xb = int(math.ceil(xs[k])), int(math.floor(xs[k + 1]))
                if xb >= xa:
                    self.fill_rect(xa, y, xb - xa + 1, 1, c)

    def circle(self, cx, cy, r, c, fill=True):
        if fill:
            for y in range(cy - r, cy + r + 1):
                half = int(math.sqrt(max(0, r * r - (y - cy) ** 2)))
                self.fill_rect(cx - half, y, half * 2 + 1, 1, c)
        else:
            for a in range(360):
                th = math.radians(a)
                self.px(cx + int(r * math.cos(th)), cy + int(r * math.sin(th)), c)

    # ------------------------------------------------------------- text
    def _glyph(self, ch, x, y, size, c):
        if ch not in FONT:
            raise ValueError("missing glyph: %r" % ch)
        sc = size / 7.0
        thick = 1 if size < 11 else (2 if size < 22 else max(2, int(size / 9)))
        for stroke in FONT[ch]:
            for (ax, ay), (bx, by) in zip(stroke, stroke[1:]):
                self.line(round(x + ax * sc), round(y + ay * sc),
                          round(x + bx * sc), round(y + by * sc), c, thick)

    def text(self, x, y, s, size, c, align="left"):
        """Draw one line at (x, y) top-left (or centred / right). Registers box."""
        s = s.upper()  # the hand-drawn font is caps-only; normalise here
        w = text_width(s, size)
        if align == "center":
            x = round(x - w / 2)
        elif align == "right":
            x = round(x - w)
        for i, ch in enumerate(s):
            if ch == " ":
                continue
            self._glyph(ch, x + i * ADV * size / 7.0, y, size, c)
        self.boxes.append((x, y, x + int(math.ceil(w)), y + size, s[:24]))
        return w

    def para(self, x, y, s, size, c, max_w, lh, max_lines=None):
        lines = wrap(s, size, max_w)
        if max_lines is not None and len(lines) > max_lines:
            raise ValueError("text overflows: %r wraps to %d lines (max %d)"
                             % (s[:40], len(lines), max_lines))
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, size, c)
        return len(lines)


# ---------------------------------------------------------------------- PNG
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, cv):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += cv.buf[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", comp)
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------------------- stories
# (number, kicker, headline, sub-line, scene key) -- all verified 24 Nov 2026
MAIN = [
    (1, "GAZA", "ISRAELI STRIKES KILL HAMAS SECURITY CHIEF",
     "Naeem Abu Nahel among 7 dead in Gaza City and Khan Younis", "gaza"),
    (2, "UKRAINE", "RUSSIAN STRIKE HITS FLATS IN ZAPORIZHZHIA",
     "2 killed, 40 hurt, 4 of them children, in overnight attack", "flats"),
    (3, "KOREA", "JETS PUT KOREAN SKIES ON ALERT",
     "Russian planes enter Seoul's defence zone; island shelters", "jets"),
    (4, "MARKETS", "ASIA SURGES ON NVIDIA RALLY",
     "Nikkei +3.9%, Kospi +6.7%, Taiwan +9.1%; Wall St futures slip", "chart"),
    (5, "NEPAL", "QUAKE SHAKES NEPAL AND THE REGION",
     "5.4 in Koshi Province; tremors in India, Bhutan, Bangladesh, China", "quake"),
    (6, "CONGO", "FIGHTING TRAPS EBOLA TEAMS IN ITURI",
     "Clashes near a hospital halt responders in DR Congo", "hospital"),
    (7, "GERMANY", "BERLIN FIRST INTO UKRAINE'S DELTA SYSTEM",
     "Germany gains access to Kyiv's battlefield management network", "screens"),
    (8, "IRAQ", "BAGHDAD TAKES OVER KURDISH OILFIELDS",
     "PM orders ministry to run fields in Kurdish-held areas", "oil"),
    (9, "TIGRAY", "AMNESTY: PROBE TIGRAY STRIKES AS WAR CRIMES",
     "Ethiopian artillery hit crowded towns, report says", "town"),
    (10, "BANGLADESH", "HASINA PLANS RETURN - 'IN HANDCUFFS', SAYS MINISTER",
     "Ex-PM asks Dhaka to fly her home on 16 December", "plane"),
    (11, "JAPAN", "JAPAN PAYS ICC EARLY BEFORE US SANCTIONS",
     "Tokyo to pay full 2027 contribution by year's end", "court"),
    (12, "EXAMS", "SEOUL PUTS $375,000 ON AI EXAM CHEATS",
     "Rewards for tips that catch AI cheating in college test", "exam"),
    (13, "TAIWAN", "CHINA AI CAMPAIGN TARGETS TAIWAN VOTE",
     "US report finds coordinated AI posts ahead of elections", "phones"),
]

ALSO = [
    "1. US to train Syrian soldiers in demining - Reuters",
    "2. Huckabee doubts US will end $3.8bn Israel aid - Reuters",
    "3. Senate probes Vance role in Vitol Venezuela oil deal - Reuters",
    "4. FBI deputy director Raia to retire by year's end - NYT",
    "5. REPORTED: Russia may launch nuclear-armed satellite",
    "6. UN seeks probe into Benghazi port attacks - UNSMIL",
    "7. REPORTED: DOJ admits it deported a US citizen by mistake",
    "8. Texas AG Paxton drops trans-care suits vs two doctors - AP",
    "9. Latvia: Ukraine war may hit tipping point next year - Reuters",
    "10. Norway in dialogue with Ukraine on regional stability - Reuters",
    "11. UK logs record Iranian attacks in Strait of Hormuz - REPORTED",
    "12. Houthis claim Saudi airstrike kills 17 in Hodeida - REPORTED",
    "13. Somalia and Uganda step up fight against al-Shabaab",
    "14. Arm extends CEO Rene Haas' tenure to 2033",
    "15. Aviation groups seek $30bn+ for FAA modernisation",
    "16. Court clears Iowa explosives detonation for Wednesday",
    "17. REPORTED: Trump's Nvidia stake gains up to $15m",
    "18. Vance lobbied Nvidia board to bring Huang back - report",
    "19. Congress presses ahead with China chip probe",
    "20. UAE launches 'Mira', an AI government aide",
    "21. Zambia charges opposition leader Mundubile with treason",
    "22. Big Tech faces billions in fines under Australian safety bill",
    "23. Macy's Thanksgiving parade braces for wind and rain",
]

DATECHECK = [
    "FIFA names 2031 Women's Cup hosts - 23 Nov",
    "Huang reinstated as Nvidia CEO - 23 Nov",
    "700,000 Russian war dead, new estimate - 23 Nov",
    "COP31 collapses, no deal - 23 Nov",
    "BepiColombo reaches Mercury - 23 Nov",
    "Zanzibar hotel fire - 21 Nov",
    "Amtrak derailment, Louisiana - 22 Nov",
    "Honda recalls 810,592 cars - 19 Nov",
    "Oregon & Virginia sue over Grok images - 23 Nov",
    "Colombia drone attack - 23 Nov",
]

NUM1 = "7 KILLED IN GAZA STRIKES  \u2022  2 DEAD, 40 WOUNDED IN ZAPORIZHZHIA  \u2022  NEPAL QUAKE 5.4, PAKISTAN 4.1"
NUM2 = "NIKKEI +3.9%  \u2022  KOSPI +6.7%  \u2022  TAIWAN +9.1%  \u2022  GOLD ~$3,660  \u2022  BRENT ~$89.50  \u2022  $375,000 AI-CHEAT REWARD"
SOURCES = ("Sources: Reuters, AP, BBC, NYT, WSJ, Bloomberg, UN News, Kyiv Independent, "
           "Just Security - all reported 24 Nov 2026 unless marked REPORTED.")

# Map pins: (number, x, y) inside the map box, hand-placed so none collide.
PINS = [(1, 368, 730), (2, 392, 698), (3, 537, 712), (4, 512, 730),
        (5, 448, 712), (6, 358, 756), (7, 332, 696), (8, 408, 724),
        (9, 383, 740), (10, 478, 736), (11, 560, 706), (12, 518, 696),
        (13, 548, 738)]


# -------------------------------------------------------------------- scenes
def _windows(cv, x, y, w, h, c):
    for wy in range(y + 3, y + h - 2, 6):
        for wx in range(x + 3, x + w - 3, 8):
            cv.fill_rect(wx, wy, 3, 3, c)


def _smoke(cv, x, y, c=SMOKE):
    cv.circle(x, y, 4, c)
    cv.circle(x + 3, y - 6, 5, c)
    cv.circle(x + 1, y - 13, 6, c)


def scene(cv, key, x, y, w, h):
    """Small flat vector scene inside rect (x, y, w, h). No faces, no logos."""
    cv.fill_rect(x, y, w, h, SKY if key not in ("chart", "screens", "phones", "exam") else LIGHT)
    if key == "gaza":
        cv.fill_rect(x, y + h - 12, w, 12, SAND)
        for i, bh in enumerate((16, 22, 13, 19, 15)):
            bx = x + 4 + i * (w // 5)
            cv.fill_rect(bx, y + h - 12 - bh, w // 5 - 5, bh, NAVY)
            _windows(cv, bx, y + h - 12 - bh, w // 5 - 5, bh, GOLD)
        _smoke(cv, x + w - 18, y + 12)
        _smoke(cv, x + 24, y + 8)
    elif key == "flats":
        cv.fill_rect(x, y + h - 10, w, 10, GRASS)
        cv.fill_rect(x + 8, y + 6, w - 40, h - 16, (196, 120, 90))
        _windows(cv, x + 8, y + 6, w - 40, h - 16, WHITE)
        cv.line(x + w - 26, y + h - 10, x + w - 10, y + 4, RED, 2)
        cv.line(x + w - 22, y + h - 10, x + w - 6, y + 8, RED, 2)
        cv.circle(x + 14, y + 10, 5, SMOKE)
    elif key == "jets":
        cv.circle(x + w - 22, y + 16, 13, WHITE)
        cv.circle(x + w - 22, y + 16, 13, INK, fill=False)
        cv.line(x + w - 22, y + 16, x + w - 12, y + 6, RED, 2)
        cv.poly_fill([(x + 8, y + 12), (x + 34, y + 18), (x + 8, y + 24)], NAVY)
        cv.poly_fill([(x + 20, y + 26), (x + 46, y + 32), (x + 20, y + 38)], TEAL)
        cv.fill_rect(x + 6, y + h - 10, 26, 10, GRASS)
        cv.fill_rect(x + 10, y + h - 18, 18, 8, SAND)
    elif key == "chart":
        cv.line(x + 6, y + h - 8, x + w - 6, y + h - 8, INK, 2)
        cv.line(x + 6, y + h - 8, x + 6, y + 6, INK, 2)
        pts = [(x + 8, y + h - 14), (x + 26, y + h - 18), (x + 44, y + h - 26),
               (x + 62, y + h - 22), (x + 80, y + h - 34), (x + w - 10, y + 10)]
        cv.poly(pts, TEAL, 3)
        cv.poly([(x + w - 10, y + 10), (x + w - 18, y + 12), (x + w - 10, y + 10),
                 (x + w - 12, y + 18)], TEAL, 3)
        cv.circle(x + 44, y + h - 26, 3, RED)
    elif key == "quake":
        cv.poly_fill([(x + 4, y + h - 8), (x + 26, y + 10), (x + 48, y + h - 8)], (120, 130, 150))
        cv.poly_fill([(x + 40, y + h - 8), (x + 66, y + 4), (x + 92, y + h - 8)], (90, 100, 125))
        cv.fill_rect(x, y + h - 8, w, 8, GRASS)
        pts = [(x + 6, y + 6), (x + 16, y + 6), (x + 20, y + 2), (x + 24, y + 10),
               (x + 28, y + 6), (x + 40, y + 6), (x + 44, y + 1), (x + 48, y + 11),
               (x + 52, y + 6), (x + w - 6, y + 6)]
        cv.poly(pts, RED, 2)
    elif key == "hospital":
        cv.fill_rect(x + 6, y + 8, w - 46, h - 18, WHITE)
        cv.rect(x + 6, y + 8, w - 46, h - 18, INK, 1)
        for wx in range(x + 12, x + w - 52, 14):
            cv.fill_rect(wx, y + 12, 6, 5, SKY)
            cv.fill_rect(wx, y + h - 26, 6, 5, SKY)
        cx, cy = x + 6 + (w - 46) // 2, y + 8 + (h - 18) // 2
        cv.fill_rect(cx - 2, cy - 8, 4, 16, RED)
        cv.fill_rect(cx - 8, cy - 2, 16, 4, RED)
        cv.poly_fill([(x + w - 38, y + h - 12), (x + w - 22, y + 12), (x + w - 6, y + h - 12)], TEAL)
        cv.fill_rect(x + w - 34, y + h - 12, 4, 12, INK)
        cv.fill_rect(x + 4, y + h - 10, 30, 8, (200, 60, 50))
        cv.circle(x + 10, y + h - 2, 3, INK)
        cv.circle(x + 28, y + h - 2, 3, INK)
    elif key == "screens":
        for i in range(3):
            sx = x + 4 + i * (w // 3)
            cv.fill_rect(sx, y + 4, w // 3 - 6, h - 14, NAVY)
            cv.rect(sx, y + 4, w // 3 - 6, h - 14, INK, 1)
            cv.poly([(sx + 4, y + h - 16), (sx + 12, y + 12), (sx + 20, y + 18),
                     (sx + 28, y + 10)], (120, 200, 120), 2)
            cv.circle(sx + 12, y + 14, 2, RED)
            cv.circle(sx + 22, y + 20, 2, GOLD)
        cv.fill_rect(x + 4, y + h - 8, w - 8, 4, INK)
    elif key == "oil":
        cv.fill_rect(x, y + h - 8, w, 8, SAND)
        for i, dx in enumerate((6, w // 2 - 6)):
            cv.poly([(x + dx, y + h - 8), (x + dx + 12, y + 6), (x + dx + 24, y + h - 8)], INK, 2)
            cv.line(x + dx + 12, y + 6, x + dx + 12, y + 16, INK, 2)
            cv.circle(x + dx + 12, y + 18, 3, RED)
        cv.line(x + 6, y + h - 16, x + w - 6, y + h - 16, TEAL, 3)
    elif key == "town":
        cv.fill_rect(x, y + h - 10, w, 10, SAND)
        for i, bh in enumerate((14, 20, 12, 17)):
            bx = x + 4 + i * (w // 4)
            cv.fill_rect(bx, y + h - 10 - bh, w // 4 - 5, bh, (150, 110, 80))
        _smoke(cv, x + w - 20, y + 10)
        cv.circle(x + 12, y + 10, 5, GOLD)
    elif key == "plane":
        cv.poly_fill([(x + 6, y + 14), (x + w - 20, y + 14), (x + w - 6, y + 20),
                      (x + w - 20, y + 26), (x + 6, y + 26)], NAVY)
        cv.poly_fill([(x + 20, y + 14), (x + 30, y + 4), (x + 38, y + 14)], NAVY)
        cv.poly_fill([(x + 24, y + 26), (x + 32, y + 34), (x + 40, y + 26)], NAVY)
        cv.fill_rect(x, y + h - 12, w, 12, SAND)
        for i, bh in enumerate((10, 14, 9)):
            bx = x + 6 + i * 22
            cv.fill_rect(bx, y + h - 12 - bh, 16, bh, NAVY)
    elif key == "court":
        cv.fill_rect(x + 8, y + 14, w - 16, h - 22, WHITE)
        cv.rect(x + 8, y + 14, w - 16, h - 22, INK, 1)
        for i in range(4):
            cx = x + 16 + i * ((w - 32) // 3)
            cv.fill_rect(cx, y + 18, 4, h - 30, INK)
        cv.poly_fill([(x + 2, y + 14), (x + w // 2, y + 2), (x + w - 2, y + 14)], RED)
        cx, cy = x + w - 16, y + h - 14
        cv.line(cx, cy - 12, cx, cy, INK, 2)
        cv.line(cx - 10, cy - 12, cx + 10, cy - 12, INK, 2)
        cv.line(cx - 10, cy - 12, cx - 13, cy - 5, INK, 2)
        cv.line(cx + 10, cy - 12, cx + 13, cy - 5, INK, 2)
    elif key == "exam":
        for r in range(2):
            for c in range(3):
                dx = x + 6 + c * (w // 3)
                dy = y + 6 + r * (h // 2)
                cv.fill_rect(dx, dy, w // 3 - 10, 8, (190, 150, 110))
                cv.circle(dx + 8, dy - 2 if r == 0 else dy + 12, 3, NAVY)
        cv.fill_rect(x + w - 24, y + 4, 14, 22, INK)
        cv.fill_rect(x + w - 22, y + 6, 10, 14, SKY)
    elif key == "phones":
        for i in range(3):
            px = x + 6 + i * (w // 3)
            cv.fill_rect(px, y + 4, w // 3 - 8, h - 16, INK)
            cv.fill_rect(px + 2, y + 6, w // 3 - 12, h - 20, WHITE)
            cv.line(px + 4, y + 10, px + w // 3 - 12, y + 10, TEAL, 2)
            cv.line(px + 4, y + 16, px + w // 3 - 12, y + 16, RED, 2)
        cv.fill_rect(x + w - 30, y + h - 14, 24, 12, RED)
        cv.fill_rect(x + w - 26, y + h - 18, 16, 4, INK)


# ---------------------------------------------------------------------- map
def draw_map(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (224, 236, 228))
    cv.rect(x, y, w, h, INK, 1)
    # simplified continents (abstract shapes, no borders drawn precisely)
    land = (196, 208, 170)
    cv.poly_fill([(x + 20, y + 18), (x + 130, y + 10), (x + 190, y + 30), (x + 170, y + 70),
                  (x + 120, y + 80), (x + 60, y + 66), (x + 16, y + 46)], land)          # N America
    cv.poly_fill([(x + 170, y + 96), (x + 220, y + 92), (x + 236, y + 130), (x + 210, y + 160),
                  (x + 186, y + 132)], land)                                              # S America
    cv.poly_fill([(x + 300, y + 22), (x + 380, y + 14), (x + 400, y + 34), (x + 360, y + 52),
                  (x + 310, y + 46)], land)                                              # Europe
    cv.poly_fill([(x + 320, y + 62), (x + 400, y + 58), (x + 420, y + 96), (x + 390, y + 140),
                  (x + 350, y + 132), (x + 322, y + 96)], land)                          # Africa
    cv.poly_fill([(x + 410, y + 16), (x + 560, y + 10), (x + 620, y + 34), (x + 600, y + 80),
                  (x + 540, y + 96), (x + 480, y + 78), (x + 420, y + 60)], land)         # Asia
    cv.poly_fill([(x + 540, y + 118), (x + 600, y + 112), (x + 610, y + 132),
                  (x + 560, y + 140)], land)                                              # Australia
    for gy in range(y + 28, y + h, 28):
        cv.line(x, gy, x + w, gy, (200, 212, 206), 1)
    for n, px, py in PINS:
        cv.circle(px, py, 9, RED)
        cv.circle(px, py, 9, WHITE)
        cv.circle(px, py, 8, RED)
        lab = str(n)
        lw = text_width(lab, 8)
        bx = px - lw / 2
        for i, ch in enumerate(lab):
            cv._glyph(ch, bx + i * ADV * 8 / 7.0, py - 4, 8, WHITE)
        cv.pins.append((px, py, n))


# -------------------------------------------------------------------- layout
def build():
    cv = Canvas()
    cv.fill_rect(0, 0, W, H, PAPER)
    cv.rect(2, 2, W - 4, H - 4, INK, 2)

    # masthead
    cv.text(512, 10, "THE WORLD IN ONE DAY", 42, INK, align="center")
    cv.fill_rect(40, 56, 944, 2, RED)
    cv.text(512, 62, "TUESDAY 24 NOVEMBER 2026  \u2022  36 STORIES", 15, RED, align="center")

    # numbers strip
    cv.fill_rect(8, 82, 1008, 40, NAVY)
    cv.text(512, 87, NUM1, 10, WHITE, align="center")
    cv.text(512, 103, NUM2, 10, WHITE, align="center")

    # main panels: 3 columns; col 1 has 5, cols 2-3 have 4
    cols = [(8, 328, [0, 1, 2, 3, 4]), (344, 328, [5, 6, 7, 8]), (680, 336, [9, 10, 11, 12])]
    kick_cols = [RED, NAVY, TEAL, GOLD, RED, NAVY, TEAL, GOLD, RED, NAVY, TEAL, GOLD, RED]
    for cx, cw, idxs in cols:
        n = len(idxs)
        ph = 100 if n == 5 else 125
        gap = 3 if n == 5 else 4
        for k, i in enumerate(idxs):
            num, kick, head, sub, skey = MAIN[i]
            py = 126 + k * (ph + gap)
            cv.fill_rect(cx, py, cw, ph, WHITE)
            cv.rect(cx, py, cw, ph, INK, 1)
            big = (n == 4)
            hs = 12.5 if big else 11.5
            ss = 9 if big else 8
            slh = 11 if big else 10
            cv.fill_rect(cx + 6, py + 4, 4, 10, kick_cols[i])
            cv.text(cx + 14, py + 4, "%02d \u2022 %s" % (num, kick), 8.5, kick_cols[i])
            cv.para(cx + 6, py + 17, head, hs, INK, cw - 12, 15 if big else 14, max_lines=2)
            cv.para(cx + 6, py + 48 if big else py + 44, sub, ss, (60, 60, 58),
                    cw - 12, slh, max_lines=3)
            sh = 36 if big else 24
            scene(cv, skey, cx + 6, py + ph - sh - 4, cw - 12, sh)

    # map + date check
    cv.text(8, 644, "WHERE IT HAPPENED - 24 NOV 2026", 10, INK)
    draw_map(cv, 8, 660, 648, 168)
    dx = 664
    cv.fill_rect(dx, 644, 352, 184, (250, 238, 220))
    cv.rect(dx, 644, 352, 184, RED, 2)
    cv.text(dx + 10, 650, "DATE CHECK - NOT TODAY, LEFT OUT", 10, RED)
    cv.text(dx + 10, 666, "These happened on other days - not 24 Nov:", 8, INK)
    for i, ln in enumerate(DATECHECK):
        cv.text(dx + 10, 682 + i * 14, "\u2022 " + ln, 8, INK)

    # ALSO list
    cv.fill_rect(8, 834, 1008, 2, INK)
    cv.text(8, 840, "ALSO - 23 MORE STORIES FROM 24 NOVEMBER", 11, INK)
    for i, ln in enumerate(ALSO):
        col = 0 if i < 12 else 1
        row = i if i < 12 else i - 12
        cv.text(8 + col * 512, 858 + row * 12, ln, 8, INK)

    # sources
    cv.text(512, 1006, SOURCES, 7.5, GREY, align="center")
    return cv


# -------------------------------------------------------------------- checks
def self_check(cv, size):
    for (x0, y0, x1, y1, lab) in cv.boxes:
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            raise ValueError("text box outside canvas: %r" % lab)
    for i, a in enumerate(cv.boxes):
        for b in cv.boxes[i + 1:]:
            if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                raise ValueError("text boxes overlap: %r vs %r" % (a[4], b[4]))
    for i, a in enumerate(cv.pins):
        for b in cv.pins[i + 1:]:
            d = math.hypot(a[0] - b[0], a[1] - b[1])
            if d < 16:
                raise ValueError("map pins collide: %d and %d (%.1f px)" % (a[2], b[2], d))
    if size >= 1048576:
        raise ValueError("PNG too big: %d bytes" % size)
    if len(cv.pins) != 13:
        raise ValueError("expected 13 pins, got %d" % len(cv.pins))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if len(sys.argv) > 1:
        out_dir = sys.argv[1]
    if not out_dir:
        out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, cv)
    self_check(cv, size)
    print("wrote %s (%d bytes, %d text boxes, %d pins)"
          % (path, size, len(cv.boxes), len(cv.pins)))


if __name__ == "__main__":
    main()
