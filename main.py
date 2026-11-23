#!/usr/bin/env python3
"""THE WORLD IN ONE PAGE - Monday 23 November 2026.

Pure-stdlib renderer: draws a 1024x1024 newspaper front page summing up
23 November 2026 world news (48 stories, 16 pictured, 7 regions), rendered
at 2x supersample (2048x2048) and box-downscaled to 1024x1024.

All text uses a hand-built 5x7 pixel font. All pictures are flat coloured
shapes drawn in code. No network, no third-party packages, deterministic:
two runs write byte-identical entry.png.

Usage:  MAKEFUN_OUTPUT_DIR=out python3 main.py
        VARIANT=B MAKEFUN_OUTPUT_DIR=outB python3 main.py   (alt layout)
"""
import os
import struct
import zlib

S = 2                      # supersample factor
W = 1024 * S
H = 1024 * S
VARIANT = os.environ.get("VARIANT", "B").upper()

# ---------------------------------------------------------------- font -----
# 5x7 pixel glyphs, "#" = on. Uppercase + digits + punctuation only;
# every string drawn is upper-cased by draw_text().
GLYPHS = {
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
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
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
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "X2": ("00000", "10001", "01010", "00100", "01010", "10001", "00000"),
    ">": ("00000", "01000", "00100", "00010", "00100", "01000", "00000"),
    "<": ("00000", "00010", "00100", "01000", "00100", "00010", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "·": ("00000", "00000", "00000", "01100", "01100", "00000", "00000"),
    "•": ("00000", "00000", "01110", "01110", "01110", "00000", "00000"),
    "°": ("01100", "10010", "01100", "00000", "00000", "00000", "00000"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
    "—": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "–": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "’": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "‘": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "“": ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "”": ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "×": ("00000", "10001", "01010", "00100", "01010", "10001", "00000"),
    "→": ("00000", "00100", "00010", "11111", "00010", "00100", "00000"),
    "★": ("00100", "00100", "11111", "01110", "01010", "10001", "10001"),
    "✓": ("00000", "00001", "00010", "10100", "01000", "00100", "00000"),
}

# ------------------------------------------------------------- canvas ------
# RGB bytearray, W*H*3. All coordinates here are in canvas (2x) pixels.
buf = bytearray(W * H * 3)


def fill(rgb):
    r, g, b = rgb
    row = bytes((r, g, b)) * W
    for y in range(H):
        buf[y * W * 3:(y + 1) * W * 3] = row


def rect(x, y, w, h, rgb):
    """Filled rectangle, clipped to canvas."""
    if w <= 0 or h <= 0:
        return
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    r, g, b = rgb
    span = bytes((r, g, b)) * (x1 - x0)
    for yy in range(y0, y1):
        o = (yy * W + x0) * 3
        buf[o:o + len(span)] = span


def hline(x, y, w, rgb, t=1):
    rect(x, y, w, t, rgb)


def vline(x, y, h, rgb, t=1):
    rect(x, y, t, h, rgb)


def frame(x, y, w, h, rgb, t=2):
    hline(x, y, w, rgb, t)
    hline(x, y + h - t, w, rgb, t)
    vline(x, y, h, rgb, t)
    vline(x + w - t, y, h, rgb, t)


def circle(cx, cy, r, rgb):
    """Filled circle via scanlines."""
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        rect(cx - dx, cy + dy, 2 * dx + 1, 1, rgb)


def disc_ring(cx, cy, r, rgb, t=3):
    for k in range(t):
        rr = r - k
        for dy in range(-rr, rr + 1):
            dx = int((rr * rr - dy * dy) ** 0.5)
            rect(cx - dx, cy + dy, 1, 1, rgb)
            rect(cx + dx, cy + dy, 1, 1, rgb)


def poly(points, rgb):
    """Filled polygon via scanline fill."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        xs = []
        n = len(points)
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            if y1 == y2:
                continue
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        if len(xs) >= 2:
            xs.sort()
            rect(int(xs[0]), y, int(xs[-1]) - int(xs[0]) + 1, 1, rgb)


def star(cx, cy, r, rgb, points=8):
    """Multi-point starburst."""
    import math
    pts = []
    for i in range(points * 2):
        ang = math.pi * i / points - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.38
        pts.append((cx + int(rr * math.cos(ang)), cy + int(rr * math.sin(ang))))
    poly(pts, rgb)


# -------------------------------------------------------------- text -------
def text_w(s, sc):
    """Width in canvas px of string s at glyph scale sc."""
    return len(s) * 6 * sc


def draw_glyph(x, y, ch, sc, rgb):
    g = GLYPHS.get(ch)
    if g is None:
        return
    for row in range(7):
        bits = g[row]
        for col in range(5):
            if bits[col] == "1":
                rect(x + col * sc, y + row * sc, sc, sc, rgb)


def draw_text(x, y, s, sc, rgb):
    """Draw one line, upper-cased. Returns width drawn."""
    s = s.upper()
    cx = x
    for ch in s:
        draw_glyph(cx, y, ch, sc, rgb)
        cx += 6 * sc
    return cx - x


def draw_text_c(x, y, w, s, sc, rgb):
    """Centred one line inside [x, x+w)."""
    tw = text_w(s.upper(), sc)
    draw_text(x + max(0, (w - tw) // 2), y, s, sc, rgb)


def wrap(s, sc, max_w):
    """Greedy word wrap; returns list of lines (upper-cased)."""
    words = s.upper().split(" ")
    lines = []
    cur = ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_w(trial, sc) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, w, s, sc, rgb, lh=None, max_lines=None):
    """Wrapped paragraph; returns y after last line."""
    if lh is None:
        lh = 9 * sc
    lines = wrap(s, sc, w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        draw_text(x, y, ln, sc, rgb)
        y += lh
    return y


def fit_scale(s, sc, max_w):
    """Lower the scale until the line fits (min scale 2)."""
    while sc > 2 and text_w(s.upper(), sc) > max_w:
        sc -= 1
    return sc

# ------------------------------------------------------------ palette ------
PAPER = (247, 240, 220)     # warm newsprint
PAPER2 = (255, 252, 240)    # panel paper
INK = (17, 17, 17)
RED = (200, 16, 46)
NAVY = (20, 38, 77)
NAVY2 = (28, 58, 112)
TEAL = (14, 124, 123)
ORANGE = (232, 90, 20)
GOLD = (214, 158, 20)
GREEN = (34, 139, 60)
SKY = (64, 142, 198)
SEA = (16, 68, 120)
SEA2 = (30, 96, 158)
SAND = (226, 196, 130)
GREY = (110, 110, 105)
LIGHT = (235, 228, 208)
WHITE = (255, 255, 255)
DARKB = (12, 24, 48)        # variant B masthead
CORAL = (228, 87, 46)
CREAM = (250, 244, 228)

# --------------------------------------------------------- png encode ------
def write_png(path):
    """Box-downscale 2048 -> 1024 and write a deterministic PNG."""
    out = bytearray()
    raw = bytearray()
    for oy in range(1024):
        raw.append(0)  # filter: none
        y0 = oy * 2
        for ox in range(1024):
            x0 = ox * 2
            r = g = b = 0
            for dy in (0, 1):
                base = ((y0 + dy) * W + x0) * 3
                for dx in (0, 1):
                    o = base + dx * 3
                    r += buf[o]
                    g += buf[o + 1]
                    b += buf[o + 2]
            raw.append(r // 4)
            raw.append(g // 4)
            raw.append(b // 4)
    comp = zlib.compress(bytes(raw), 6)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", 1024, 1024, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# -------------------------------------------------------- illustrations ----
# Every illustrator draws inside (x, y, w, h) in CANVAS pixels.
# Flat saturated shapes, no text inside the picture.

def illu_ship(x, y, w, h):
    """Sea, sinking warship, drones, explosion."""
    rect(x, y, w, h, SEA)
    rect(x, y + int(h * 0.62), w, h - int(h * 0.62), SEA2)
    for i, wy in enumerate((0.66, 0.74, 0.84, 0.93)):
        c = (120, 180, 220) if i % 2 == 0 else (200, 225, 245)
        for k in range(3):
            wx = x + int(w * (0.12 + 0.3 * k + 0.07 * i)) % w
            rect(wx, y + int(h * wy), int(w * 0.16), max(3, h // 32), c)
    # hull, listing to starboard, lighter grey with red waterline
    poly([(x + int(w * 0.16), y + int(h * 0.55)),
          (x + int(w * 0.80), y + int(h * 0.46)),
          (x + int(w * 0.76), y + int(h * 0.62)),
          (x + int(w * 0.22), y + int(h * 0.66))], (118, 124, 132))
    rect(x + int(w * 0.20), y + int(h * 0.60), int(w * 0.56), max(3, h // 40),
         (200, 40, 50))
    for k in range(5):
        px = x + int(w * (0.26 + 0.09 * k))
        py = y + int(h * 0.52)
        rect(px, py, max(3, w // 90), max(3, h // 30), (240, 240, 235))
    rect(x + int(w * 0.30), y + int(h * 0.38), int(w * 0.10), int(h * 0.16),
         (140, 146, 152))
    rect(x + int(w * 0.46), y + int(h * 0.42), int(w * 0.07), int(h * 0.12),
         (140, 146, 152))
    # explosion at the stern
    star(x + int(w * 0.82), y + int(h * 0.40), int(h * 0.28), ORANGE)
    star(x + int(w * 0.82), y + int(h * 0.40), int(h * 0.16), GOLD)
    circle(x + int(w * 0.82), y + int(h * 0.40), max(4, h // 28), WHITE)
    # smoke, small and dark
    circle(x + int(w * 0.72), y + int(h * 0.26), int(h * 0.07), (70, 70, 74))
    circle(x + int(w * 0.77), y + int(h * 0.20), int(h * 0.05), (96, 96, 100))
    # sea drones: small crosses above the water
    for dx, dy in ((0.30, 0.18), (0.52, 0.12), (0.66, 0.24)):
        cx, cy = x + int(w * dx), y + int(h * dy)
        rect(cx - 8, cy - 2, 16, 4, WHITE)
        rect(cx - 2, cy - 8, 4, 16, WHITE)


def illu_globe(x, y, w, h):
    """Earth with a red dashed ring and rising sun."""
    rect(x, y, w, h, NAVY2)
    rect(x, y + int(h * 0.72), w, h - int(h * 0.72), (18, 44, 66))
    cx, cy = x + w // 2, y + int(h * 0.52)
    r = int(h * 0.42)
    circle(cx, cy, r, (52, 168, 110))
    circle(cx - r // 3, cy - r // 4, r // 3, GREEN)
    circle(cx + r // 3, cy + r // 4, r // 4, GREEN)
    circle(cx + r // 5, cy - r // 2, r // 5, GREEN)
    disc_ring(cx, cy, r + max(3, h // 18), RED, t=max(3, h // 24))
    # sun
    circle(x + int(w * 0.84), y + int(h * 0.18), max(4, h // 16), GOLD)
    for k in range(8):
        import math
        a = math.pi * k / 4
        sx, sy = x + int(w * 0.84), y + int(h * 0.18)
        rect(sx + int((h // 10) * math.cos(a)) - 2, sy + int((h // 10) * math.sin(a)) - 2,
             4, 4, GOLD)


def illu_building(x, y, w, h):
    """Apartment block, blast, smoke, rescue light."""
    rect(x, y, w, h, (42, 52, 84))
    rect(x, y + int(h * 0.78), w, h - int(h * 0.78), (30, 30, 34))
    bx, by = x + int(w * 0.14), y + int(h * 0.22)
    bw, bh = int(w * 0.52), int(h * 0.60)
    rect(bx, by, bw, bh, (196, 164, 110))
    # windows
    for r in range(4):
        for c in range(4):
            wx = bx + int(bw * (0.12 + 0.22 * c))
            wy = by + int(bh * (0.12 + 0.22 * r))
            col = GOLD if (r + c) % 3 else (60, 60, 70)
            rect(wx, wy, max(3, bw // 12), max(3, bh // 14), col)
    # collapsed corner + explosion
    poly([(bx + bw, by + int(bh * 0.55)), (x + w, by + int(bh * 0.4)),
          (x + w, by + bh), (bx + bw, by + bh)], (120, 100, 70))
    star(x + int(w * 0.82), y + int(h * 0.42), int(h * 0.24), ORANGE)
    star(x + int(w * 0.82), y + int(h * 0.42), int(h * 0.13), GOLD)
    circle(x + int(w * 0.70), y + int(h * 0.18), int(h * 0.09), (96, 96, 98))
    circle(x + int(w * 0.78), y + int(h * 0.12), int(h * 0.07), (130, 130, 132))


def illu_chart(x, y, w, h):
    """Stock chart: red plunge, green rebound, chip."""
    rect(x, y, w, h, (14, 18, 34))
    # grid lines
    for gy in (0.25, 0.5, 0.75):
        hline(x, y + int(h * gy), w, (40, 48, 70), 2)
    pts = [(0.04, 0.30), (0.20, 0.42), (0.36, 0.34), (0.52, 0.72),
           (0.66, 0.62), (0.80, 0.30), (0.96, 0.18)]
    for i in range(len(pts) - 1):
        x1 = x + int(w * pts[i][0])
        y1 = y + int(h * pts[i][1])
        x2 = x + int(w * pts[i + 1][0])
        y2 = y + int(h * pts[i + 1][1])
        col = RED if i < 3 else GREEN
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for s in range(steps + 1):
            px = x1 + (x2 - x1) * s // steps
            py = y1 + (y2 - y1) * s // steps
            rect(px - 3, py - 3, 6, 6, col)
    # chip
    cx, cy = x + int(w * 0.82), y + int(h * 0.78)
    rect(cx - 18, cy - 14, 36, 28, TEAL)
    rect(cx - 10, cy - 7, 20, 14, (10, 60, 60))
    for k in range(4):
        rect(cx - 18 + k * 10, cy - 20, 4, 6, GOLD)
        rect(cx - 18 + k * 10, cy + 14, 4, 6, GOLD)


def illu_parliament(x, y, w, h):
    """Capitol dome and columns, blue sky."""
    rect(x, y, w, h, SKY)
    rect(x, y + int(h * 0.80), w, h - int(h * 0.80), GREEN)
    bx = x + int(w * 0.22)
    by = y + int(h * 0.30)
    bw = int(w * 0.56)
    rect(bx, by + int(h * 0.28), bw, int(h * 0.52), PAPER2)
    for c in range(5):
        rect(bx + int(bw * (0.08 + 0.19 * c)), by + int(h * 0.28),
             max(3, bw // 18), int(h * 0.44), WHITE)
    poly([(bx + int(bw * 0.30), by + int(h * 0.28)),
          (bx + int(bw * 0.70), by + int(h * 0.28)),
          (bx + bw // 2, by)], WHITE)
    circle(bx + bw // 2, by + int(h * 0.06), max(4, h // 14), GOLD)
    rect(bx - 8, by + int(h * 0.72), bw + 16, max(3, h // 26), NAVY)


def illu_fire(x, y, w, h):
    """Factory silhouette with flames and smoke."""
    rect(x, y, w, h, (58, 30, 34))
    rect(x, y + int(h * 0.72), w, h - int(h * 0.72), (24, 20, 22))
    rect(x + int(w * 0.10), y + int(h * 0.52), int(w * 0.55), int(h * 0.24), (90, 70, 66))
    rect(x + int(w * 0.68), y + int(h * 0.34), int(w * 0.08), int(h * 0.42), (90, 70, 66))
    poly([(x + int(w * 0.10), y + int(h * 0.52)), (x + int(w * 0.375), y + int(h * 0.36)),
          (x + int(w * 0.65), y + int(h * 0.52))], (70, 54, 50))
    for fx, fh in ((0.22, 0.34), (0.40, 0.44), (0.56, 0.30)):
        poly([(x + int(w * fx) - int(h * 0.10), y + int(h * 0.66)),
              (x + int(w * fx), y + int(h * (0.66 - fh))),
              (x + int(w * fx) + int(h * 0.10), y + int(h * 0.66))], ORANGE)
        poly([(x + int(w * fx) - int(h * 0.05), y + int(h * 0.66)),
              (x + int(w * fx), y + int(h * (0.66 - fh * 0.55))),
              (x + int(w * fx) + int(h * 0.05), y + int(h * 0.66))], GOLD)
    circle(x + int(w * 0.82), y + int(h * 0.22), int(h * 0.10), (110, 104, 100))
    circle(x + int(w * 0.88), y + int(h * 0.14), int(h * 0.07), (140, 134, 128))


def illu_houses(x, y, w, h):
    """Village houses, one burning, dusk sky."""
    rect(x, y, w, h, (214, 140, 80))
    circle(x + int(w * 0.82), y + int(h * 0.20), max(4, h // 14), (255, 220, 130))
    rect(x, y + int(h * 0.70), w, h - int(h * 0.70), (120, 84, 48))
    for i, hx in enumerate((0.08, 0.38, 0.68)):
        hw = int(w * 0.24)
        hh = int(h * 0.30)
        hx0 = x + int(w * hx)
        hy0 = y + int(h * 0.70) - hh
        rect(hx0, hy0, hw, hh, (236, 222, 190) if i != 1 else (200, 170, 130))
        poly([(hx0 - 6, hy0), (hx0 + hw // 2, hy0 - int(h * 0.16)),
              (hx0 + hw + 6, hy0)], (150, 60, 40) if i == 1 else (120, 70, 50))
        rect(hx0 + hw // 2 - 4, hy0 + hh // 2, 8, hh // 2, (70, 50, 30))
    poly([(x + int(w * 0.50) - 10, y + int(h * 0.52)),
          (x + int(w * 0.50), y + int(h * 0.30)),
          (x + int(w * 0.50) + 10, y + int(h * 0.52))], ORANGE)
    circle(x + int(w * 0.56), y + int(h * 0.22), int(h * 0.07), (90, 88, 86))


def illu_flags(x, y, w, h):
    """Three flags on poles: US, China, Russia (abstract bars)."""
    rect(x, y, w, h, (36, 64, 110))
    rect(x, y + int(h * 0.78), w, h - int(h * 0.78), (24, 40, 70))
    specs = [((200, 40, 50), (255, 255, 255), (40, 60, 160)),
             ((222, 40, 40), (255, 235, 60), None),
             ((255, 255, 255), (40, 90, 200), (220, 40, 40))]
    for i, cols in enumerate(specs):
        fx = x + int(w * (0.10 + 0.30 * i))
        fy = y + int(h * 0.16)
        fw = int(w * 0.24)
        fh = int(h * 0.34)
        vline(fx, fy - int(h * 0.06), int(h * 0.62), (200, 200, 200), 3)
        band = fh // 3
        for j, c in enumerate(cols):
            if c is None:
                continue
            rect(fx + 3, fy + j * band, fw, band, c)
        if i == 1:
            star(fx + 3 + fw // 4, fy + fh // 4, max(3, fh // 6), GOLD, points=5)


def illu_drone(x, y, w, h):
    """Night sky, drone silhouette, city lights below."""
    rect(x, y, w, h, (16, 22, 52))
    for sx, sy in ((0.15, 0.18), (0.35, 0.10), (0.60, 0.22), (0.80, 0.12), (0.90, 0.30)):
        rect(x + int(w * sx), y + int(h * sy), 4, 4, WHITE)
    rect(x, y + int(h * 0.74), w, h - int(h * 0.74), (10, 14, 30))
    for i in range(6):
        bx = x + int(w * (0.06 + 0.15 * i))
        bh = int(h * (0.10 + 0.06 * ((i * 7) % 3)))
        rect(bx, y + int(h * 0.74) - bh, int(w * 0.10), bh, (30, 36, 60))
        rect(bx + 4, y + int(h * 0.74) - bh + 6, 6, 6, GOLD)
    # drone
    cx, cy = x + w // 2, y + int(h * 0.38)
    rect(cx - 26, cy - 6, 52, 12, (180, 180, 185))
    rect(cx - 4, cy - 16, 8, 10, (120, 120, 125))
    for dx in (-30, 30):
        rect(cx + dx - 10, cy - 12, 20, 3, (220, 220, 220))
    circle(cx - 30, cy - 10, 4, RED)
    circle(cx + 30, cy - 10, 4, RED)
    circle(cx, cy + 14, 5, ORANGE)


def illu_desert(x, y, w, h):
    """Cracked desert ground, warning sign, sun."""
    rect(x, y, w, h, (232, 190, 120))
    circle(x + int(w * 0.80), y + int(h * 0.18), max(4, h // 14), (255, 200, 90))
    rect(x, y + int(h * 0.62), w, h - int(h * 0.62), (198, 150, 84))
    for i in range(4):
        cx0 = x + int(w * (0.10 + 0.24 * i))
        poly([(cx0, y + int(h * 0.66)), (cx0 + int(w * 0.10), y + int(h * 0.72)),
              (cx0 + int(w * 0.05), y + int(h * 0.66))], (170, 124, 60))
    # warning triangle
    tx, ty = x + w // 2, y + int(h * 0.30)
    poly([(tx, ty - int(h * 0.16)), (tx - int(h * 0.16), ty + int(h * 0.12)),
          (tx + int(h * 0.16), ty + int(h * 0.12))], (250, 200, 30))
    rect(tx - 3, ty - int(h * 0.06), 6, int(h * 0.10), INK)
    rect(tx - 3, ty + int(h * 0.06), 6, 6, INK)


def illu_court(x, y, w, h):
    """Scales of justice on deep red."""
    rect(x, y, w, h, (122, 24, 34))
    cx, cy = x + w // 2, y + int(h * 0.50)
    vline(cx - 2, cy - int(h * 0.30), int(h * 0.52), GOLD, 5)
    hline(cx - int(w * 0.30), cy - int(h * 0.30), int(w * 0.60), GOLD, 5)
    rect(cx - int(w * 0.16), cy + int(h * 0.20), int(w * 0.32), max(3, h // 24), GOLD)
    for dx in (-1, 1):
        px = cx + dx * int(w * 0.28)
        vline(px - 2, cy - int(h * 0.28), int(h * 0.28), GOLD, 3)
        poly([(px - int(w * 0.12), cy + int(h * 0.04)),
              (px + int(w * 0.12), cy + int(h * 0.04)),
              (px, cy + int(h * 0.22))], (240, 210, 120))
    circle(cx, cy - int(h * 0.34), max(4, h // 18), GOLD)


def illu_stage(x, y, w, h):
    """Concert stage, lights, crowd silhouettes."""
    rect(x, y, w, h, (30, 16, 52))
    rect(x, y + int(h * 0.55), w, int(h * 0.10), (60, 40, 90))
    for i, lx in enumerate((0.18, 0.42, 0.66, 0.86)):
        col = (RED, GOLD, TEAL, ORANGE)[i % 4]
        poly([(x + int(w * lx) - 8, y + int(h * 0.55)),
              (x + int(w * lx) + 8, y + int(h * 0.55)),
              (x + int(w * lx), y + int(h * 0.08))], col)
        circle(x + int(w * lx), y + int(h * 0.10), max(4, h // 18), col)
    rect(x, y + int(h * 0.65), w, h - int(h * 0.65), (16, 10, 30))
    for i in range(8):
        hx = x + int(w * (0.06 + 0.12 * i))
        circle(hx, y + int(h * 0.78), max(3, h // 22), (70, 60, 100))
        rect(hx - 6, y + int(h * 0.82), 12, int(h * 0.16), (70, 60, 100))


def illu_exam(x, y, w, h):
    """Exam paper, pencil, red check cross."""
    rect(x, y, w, h, (24, 90, 130))
    px, py = x + int(w * 0.28), y + int(h * 0.14)
    pw, ph = int(w * 0.44), int(h * 0.72)
    rect(px, py, pw, ph, WHITE)
    for r in range(4):
        hline(px + 8, py + int(ph * (0.22 + 0.18 * r)), pw - 16, (160, 160, 160), 3)
    rect(px + 8, py + 8, pw // 2, max(3, ph // 14), RED)
    # pencil diagonal
    poly([(x + int(w * 0.72), y + int(h * 0.78)), (x + int(w * 0.88), y + int(h * 0.30)),
          (x + int(w * 0.94), y + int(h * 0.34)), (x + int(w * 0.78), y + int(h * 0.82))],
         GOLD)
    poly([(x + int(w * 0.88), y + int(h * 0.30)), (x + int(w * 0.94), y + int(h * 0.34)),
          (x + int(w * 0.92), y + int(h * 0.24))], (240, 200, 160))
    # red X over the paper corner
    rect(px + pw - 22, py + 6, 26, 5, RED)
    rect(px + pw - 22, py + 6, 5, 26, RED)


def illu_space(x, y, w, h):
    """Mercury: cratered planet, stars, probe."""
    rect(x, y, w, h, (8, 10, 26))
    for sx, sy in ((0.12, 0.14), (0.30, 0.08), (0.55, 0.20), (0.78, 0.10), (0.90, 0.28)):
        rect(x + int(w * sx), y + int(h * sy), 4, 4, WHITE)
    cx, cy = x + int(w * 0.42), y + int(h * 0.55)
    r = int(h * 0.32)
    circle(cx, cy, r, (176, 152, 128))
    for crx, cry, crr in ((-0.4, -0.3, 0.28), (0.3, 0.2, 0.34), (-0.1, 0.4, 0.22), (0.45, -0.35, 0.18)):
        circle(cx + int(r * crx), cy + int(r * cry), max(3, int(r * crr)), (140, 118, 96))
    # probe with solar panels
    px, py = x + int(w * 0.78), y + int(h * 0.30)
    rect(px - 26, py - 4, 52, 8, NAVY2)
    rect(px - 6, py - 8, 12, 16, GOLD)
    rect(px - 34, py - 3, 8, 6, TEAL)


def illu_tennis(x, y, w, h):
    """Tennis court, net, ball, trophy."""
    rect(x, y, w, h, (34, 120, 70))
    rect(x, y + int(h * 0.30), w, int(h * 0.44), (52, 150, 90))
    hline(x, y + int(h * 0.52), w, WHITE, 3)
    vline(x + w // 2, y + int(h * 0.30), int(h * 0.44), WHITE, 3)
    rect(x, y + int(h * 0.30), w, 3, WHITE)
    rect(x, y + int(h * 0.74) - 3, w, 3, WHITE)
    circle(x + int(w * 0.72), y + int(h * 0.40), max(4, h // 16), (220, 240, 60))
    # trophy
    tx, ty = x + int(w * 0.20), y + int(h * 0.44)
    rect(tx - 10, ty, 20, 22, GOLD)
    rect(tx - 14, ty + 22, 28, 5, GOLD)
    circle(tx - 12, ty + 8, 5, GOLD)
    circle(tx + 12, ty + 8, 5, GOLD)

# ----------------------------------------------------------- story data ----
# All stories first reported on Monday 23 November 2026 (UTC) unless the
# item itself says it happened over the weekend and was reported Monday.
# Sources: One Turn day page (BBC, Reuters, AP, France 24, Guardian,
# Al Jazeera wires), Just Security Early Edition 23 Nov, Open Chronicle,
# Reuters via Kitco/BigGo, detik/ANTARA, CNBC Indonesia, Acast sports wires.

HERO = {
    "kicker": "BENGHAZI · LIBYA · CONFLICT",
    "headline": "UKRAINE SINKS RUSSIAN WARSHIP IN LIBYA",
    "body": ("Seven Ukrainian sea drones sank the Russian corvette Merkury "
             "at Benghazi on Sunday. Ten people were hurt."),
    "illu": illu_ship,
}

STACK = [
    {
        "kicker": "CLIMATE · TURKEY",
        "headline": "COP31 COLLAPSES WITHOUT A DEAL",
        "body": ("The UN climate summit in Antalya ended Sunday after a "
                 "record 49 hours of overtime. The EU and 130 parties "
                 "rejected a draft with no fossil fuels."),
        "illu": illu_globe,
    },
    {
        "kicker": "DYMER · UKRAINE · WAR",
        "headline": "STRIKE ON FLATS KILLS AT LEAST 11",
        "body": ("A Russian drone strike partly collapsed a five-storey block "
                 "in Dymer, north of Kyiv. A boy of seven was pulled alive "
                 "after 14 hours."),
        "illu": illu_building,
    },
]

WIDE = {
    "kicker": "MARKETS · TECH",
    "headline": "HUANG RETURNS AS NVIDIA CHIEF; AI STOCKS REBOUND",
    "body": ("Nvidia's board reinstated founder Jensen Huang as CEO on Monday, "
             "11 days after he resigned. Shares jumped 9% pre-market after "
             "Friday's 14% rout."),
    "illu": illu_chart,
}

GRID = [
    {
        "kicker": "WASHINGTON · POLITICS",
        "headline": "DEMOCRATS WIN HOUSE MAJORITY SINCE 1992",
        "body": "At least 258 seats after a recount win.",
        "illu": illu_parliament,
    },
    {
        "kicker": "BANTEN · INDONESIA · DISASTER",
        "headline": "CANDY FACTORY FIRE KILLS 24",
        "body": "Banten candy factory fire; dozens missing.",
        "illu": illu_fire,
    },
    {
        "kicker": "WEST BANK · CONFLICT",
        "headline": "EISENKOT SLAMS SETTLER ARSON",
        "body": "PM-elect condemned settler arson.",
        "illu": illu_houses,
    },
    {
        "kicker": "SHENZHEN · CHINA · DIPLOMACY",
        "headline": "TRUMP CALLS PUTIN 'MY FRIEND'",
        "body": "After a three-way summit with Xi in Shenzhen.",
        "illu": illu_flags,
    },
    {
        "kicker": "KHARTOUM · SUDAN · WAR",
        "headline": "DRONE STRIKES HIT KHARTOUM",
        "body": "Strikes hit homes and a UN building in Khartoum.",
        "illu": illu_drone,
    },
    {
        "kicker": "GAZA · CONFLICT",
        "headline": "GAZA WAR LEFT 99% CONTAMINATED",
        "body": "Oxfam: contamination across Gaza.",
        "illu": illu_desert,
    },
    {
        "kicker": "SOUTH SUDAN · CONFLICT",
        "headline": "24 CIVILIANS KILLED IN S. SUDAN",
        "body": "Paramilitary attack killed 24 civilians.",
        "illu": illu_houses,
    },
    {
        "kicker": "SINALOA · MEXICO · JUSTICE",
        "headline": "'EL CHAPO ISIDRO' CAPTURED",
        "body": "Mexico captured the FBI most-wanted cartel boss.",
        "illu": illu_court,
    },
    {
        "kicker": "MANCHESTER · UK · SOCIETY",
        "headline": "12,000 EVACUATED FROM CONCERT",
        "body": "Unknown substance found at a Manchester concert.",
        "illu": illu_stage,
    },
    {
        "kicker": "SEOUL · SOUTH KOREA · POLITICS",
        "headline": "MINISTER QUITS OVER AI EXAM CHEATING",
        "body": "Seoul minister quit after an AI cheating scandal.",
        "illu": illu_exam,
    },
    {
        "kicker": "SPACE · MERCURY",
        "headline": "BEPICOLOMBO REACHES MERCURY",
        "body": "Probe reached Mercury after 8 years.",
        "illu": illu_space,
    },
    {
        "kicker": "TURIN · ITALY · SPORT",
        "headline": "ALCARAZ WINS FIRST ATP FINALS TITLE",
        "body": "Beat Zverev 6-2, 7-6 in the Turin final.",
        "illu": illu_tennis,
    },
]

BRIEFS = [
    "LIVERPOOL 4-0 MAN UTD",
    "BOCA WIN COPA SUDAMERICANA",
    "PUGH SWIMS HORMUZ STRAIT",
    "MARIANA VOLCANOES FOUND",
    "NEPAL PM VISITS INDIA",
    "ICE VIDEO SPARKS PROTESTS",
    "CITIZEN DEPORTED TO MEXICO",
    "NINE SHOT IN CALIFORNIA",
    "KENYA, CONGO RESTORE TIES",
    "BELGIAN AIRPORTS SHUT",
    "CAPITA SHARES PLUNGE 67%",
    "CONOCO EXITS NORWAY",
    "TATA STEEL $1.67BN STAKE",
    "COALITION TALKS FAIL",
    "IRAN VOWS VS BLOCKADE",
    "FREIGHTER HIT OFF FINLAND",
    "DENMARK: PLOT ON RAPPER",
    "EU UNVEILS 22ND SANCTIONS",
    "NATO MEETS OVER POLAND",
    "BOLSONARO IN ICU",
    "STORM KILLS FIVE IN BRAZIL",
    "NIGERIA ENDS SUICIDE JAIL",
    "OTTERS RETURN TO KL RIVER",
    "NEPAL: FIRST LOSS PAYOUT",
    "NEW THUMB IMPLANT",
    "TAMAGOTCHI TURNS 30",
    "DOCTOR WHO: 63 YEARS ON",
    "SKUBAL'S $450M METS DEAL",
    "COWBOYS 51-30 TITANS",
    "IHSG UP AS RUPIAH HITS LOW",
    "DRUG RING BUST: 378KG METH",
    "PRABOWO NAMES VP PICKS",
    "UN SEEKS MERKURY INQUIRY",
]

NUMBERS = ("NIKKEI -5.1% · S&P -3.7% · GOLD +3.1% · 258 SEATS · 24 DEAD · "
           "12,000 EVACUATED · 7 SEA DRONES · 49H OVERTIME")

TIMELINE = [
    ("OVERNIGHT", "DYMER FLATS HIT"),
    ("MORNING", "NIKKEI -5.1%"),
    ("MIDDAY", "EU SANCTIONS #22"),
    ("AFTERNOON", "MERKURY SUNK"),
    ("EVENING", "HUANG RETURNS"),
]

SOURCES = ("SOURCES: BBC · REUTERS · AP · FRANCE 24 · GUARDIAN · AL JAZEERA · "
           "ANTARA · DETIK")
DATECHECK = ("DATE-CHECKED 23 NOV 2026: EVERY STORY FIRST REPORTED ON THIS DAY")

# ------------------------------------------------------------- layout ------
# All layout numbers below are FINAL pixels (1024x1024); F() doubles them
# to canvas pixels.

def F(v):
    return v * S


def panel(x, y, w, h, bg=PAPER2):
    rect(F(x), F(y), F(w), F(h), bg)
    frame(F(x), F(y), F(w), F(h), INK, 3)


def draw_story(x, y, w, h, st, illu_h, kicker_sc, head_sc, body_sc,
               head_max=2, body_max=3, kicker_col=RED, head_col=INK,
               body_col=(64, 64, 64), show_kicker=True):
    """Picture on top, then kicker / headline / body, stacked in canvas px."""
    panel(x, y, w, h)
    st["illu"](F(x + 2), F(y + 2), F(w - 4), F(illu_h))
    cy = F(y + 2 + illu_h + 3)
    if show_kicker and st.get("kicker"):
        draw_text(F(x + 8), cy, st["kicker"], kicker_sc, kicker_col)
        cy += 9 * kicker_sc + 2 * S
    cy = draw_para(F(x + 8), cy, F(w - 16), st["headline"], head_sc, head_col,
                   lh=9 * head_sc, max_lines=head_max) + 2 * S
    draw_para(F(x + 8), cy, F(w - 16), st["body"], body_sc, body_col,
              lh=9 * body_sc, max_lines=body_max)


def draw_numbers_bar(y, h):
    rect(F(8), F(y), F(1008), F(h), NAVY)
    sc = fit_scale(NUMBERS, 3, F(1008))
    tw = text_w(NUMBERS, sc)
    draw_text(F(8) + (F(1008) - tw) // 2, F(y) + (F(h) - 7 * sc) // 2,
              NUMBERS, sc, WHITE)


def draw_timeline(y, h):
    rect(F(8), F(y), F(1008), F(h), LIGHT)
    frame(F(8), F(y), F(1008), F(h), INK, 3)
    cells = TIMELINE + [("DATE-CHECKED", "23 NOV 2026")]
    cw = 1008 // 6
    for i, (lab, ev) in enumerate(cells):
        cx = 8 + i * cw
        if i:
            vline(F(cx), F(y + 4), F(h - 8), GREY, 2)
        draw_text(F(cx + 8), F(y + 5), lab, 3, RED)
        draw_text(F(cx + 8), F(y + 5) + 9 * 3, ev, 3, INK)


def draw_briefs(y, lh):
    for col in range(3):
        bx = 8 + col * 338
        for row in range(11):
            idx = col * 11 + row
            if idx >= len(BRIEFS):
                continue
            by = y + row * lh
            draw_text(F(bx), F(by), "•", 4, RED)
            draw_text(F(bx + 14), F(by), BRIEFS[idx], 4, INK)


def draw_brief_header(y):
    draw_text(F(8), F(y), "IN BRIEF · THE REST OF MONDAY", 3, RED)
    src = SOURCES
    tw = text_w(src, 3)
    draw_text(F(1016) - tw, F(y), src, 3, GREY)


def layout_a():
    fill(PAPER)
    # masthead
    hline(F(8), F(4), F(1008), INK, 4)
    draw_text_c(F(8), F(10), F(1008), "THE WORLD IN ONE PAGE", 11, INK)
    hline(F(8), F(56), F(1008), INK, 4)
    # dateline
    draw_text(F(8), F(64), "MONDAY · 23 NOVEMBER 2026", 4, RED)
    dt = "49 STORIES · 16 PICTURED · 7 REGIONS"
    draw_text(F(1016) - text_w(dt, 4), F(64), dt, 4, INK)
    hline(F(8), F(84), F(1008), GREY, 2)
    # day in numbers
    draw_numbers_bar(88, 24)
    # hero + stack
    draw_story(8, 116, 500, 246, HERO, 110, 4, 6, 4, head_max=2, body_max=3)
    sy = 116
    for st in STACK:
        draw_story(516, sy, 500, 120, st, 30, 3, 4, 3, head_max=1, body_max=3)
        sy += 128
    # wide panel: picture left, text right
    panel(8, 368, 1008, 80)
    WIDE["illu"](F(10), F(370), F(180), F(76))
    tx = 198
    draw_text(F(tx), F(374), WIDE["kicker"], 4, RED)
    draw_para(F(tx), F(392), F(1008 - tx - 8), WIDE["headline"], 5, INK,
              lh=45, max_lines=1)
    draw_para(F(tx), F(392 + 24), F(1008 - tx - 8), WIDE["body"], 3,
              (64, 64, 64), lh=27, max_lines=2)
    # grid 4 x 3 (no kicker: headline + body carry the story)
    for r in range(3):
        for c in range(4):
            st = GRID[r * 4 + c]
            draw_story(8 + c * 254, 454 + r * 110, 246, 110, st, 38, 3, 4, 3,
                       head_max=2, body_max=2, show_kicker=False)
    # timeline + briefs
    draw_timeline(790, 30)
    draw_brief_header(826)
    draw_briefs(844, 16)


def layout_b():
    fill(CREAM)
    # dark masthead band
    rect(F(6), F(6), F(1012), F(58), DARKB)
    draw_text_c(F(6), F(12), F(1012), "THE WORLD IN ONE PAGE", 11, WHITE)
    draw_text(F(16), F(46), "MONDAY · 23 NOVEMBER 2026", 4, GOLD)
    dt = "49 STORIES · 16 PICTURED · 7 REGIONS"
    draw_text(F(1008) - text_w(dt, 4), F(46), dt, 4, WHITE)
    # numbers rail (left) + hero (right)
    rect(F(8), F(72), F(240), F(264), NAVY2)
    frame(F(8), F(72), F(240), F(264), INK, 3)
    draw_text(F(20), F(82), "THE DAY IN", 4, WHITE)
    draw_text(F(20), F(100), "NUMBERS", 4, GOLD)
    nums = [("-5.1%", "NIKKEI"), ("+3.1%", "GOLD"), ("258", "HOUSE SEATS"),
            ("24", "DEAD IN BANTEN"), ("12,000", "EVACUATED"),
            ("49H", "COP31 OVERTIME")]
    ny = 122
    for big, lab in nums:
        draw_text(F(20), F(ny), big, 5, GOLD)
        draw_text(F(20), F(ny + 23), lab, 3, WHITE)
        ny += 36
    draw_story(256, 72, 760, 264, HERO, 160, 4, 6, 4, head_max=1, body_max=2)
    # middle row: COP31 / Dymer / Nvidia with short bodies
    mid = [
        dict(STACK[0], body="Record 49h overtime; EU rejected a draft with "
                            "no fossil fuels."),
        dict(STACK[1], body="A boy of seven was pulled alive after 14 hours "
                            "under the rubble."),
        dict(WIDE, body="Huang returns as CEO; shares jumped 9% after "
                        "Friday's 14% rout."),
    ]
    for i, st in enumerate(mid):
        draw_story(8 + i * 338, 344, 330, 128, st, 40, 3, 4, 3,
                   head_max=2, body_max=2)
    # grid 4 x 3 (shorter panels, no kicker)
    for r in range(3):
        for c in range(4):
            st = GRID[r * 4 + c]
            draw_story(8 + c * 254, 480 + r * 105, 246, 102, st, 30, 3, 4, 3,
                       head_max=2, body_max=2, show_kicker=False)
    # timeline + briefs
    draw_timeline(798, 30)
    draw_brief_header(830)
    draw_briefs(848, 16)


# -------------------------------------------------------------- main -------
def main():
    if VARIANT == "B":
        layout_b()
    else:
        layout_a()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(path)
    print(f"variant {VARIANT}: wrote {path} ({size} bytes)")


if __name__ == "__main__":
    main()
