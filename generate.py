#!/usr/bin/env python3
"""news-image-20261126 v2 — 'The World in One Day' front page.
Draws a 1024x1024 newspaper front page from FACTS.md only.
Deterministic: no random, no time, no network. Pure PIL.
Prints WARNING for any text overflow/truncation; exit code 1 if any.
"""
import hashlib
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 28
CW = W - 2 * MARGIN  # 968

PAPER = (247, 241, 227)
CARD = (255, 253, 247)
NAVY = (27, 42, 74)
BRICK = (179, 64, 42)
INK = (26, 26, 26)
MUTED = (90, 84, 70)
RULE = (196, 182, 150)
GOLD = (201, 162, 39)
MAP_BG = (238, 233, 216)
LAND = (203, 178, 127)
LAND_EDGE = (120, 100, 66)
SKY = (223, 232, 238)

WARNINGS = []

FD = "/usr/share/fonts/truetype/dejavu"


def font(size, bold=False, serif=False):
    if serif:
        name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
    else:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FD, name), size)


def warn(msg):
    WARNINGS.append(msg)
    print("WARNING:", msg, file=sys.stderr)


def wrap(draw, text, fnt, maxw):
    """Greedy wrap; returns list of lines. Warns if a single word is too wide."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            if draw.textlength(w, font=fnt) > maxw:
                warn(f"word too wide for {maxw}px: {w!r}")
                lines.append(w)
            else:
                cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_fit(draw, x, y, text, fnt, maxw, max_lines, line_h, fill, align="left"):
    """Draw wrapped text; warn + truncate with ellipsis if it exceeds max_lines."""
    lines = wrap(draw, text, fnt, maxw)
    if len(lines) > max_lines:
        warn(f"overflow ({len(lines)}>{max_lines} lines): {text!r}")
        lines = lines[:max_lines]
        # trim last line to fit ellipsis
        while lines and draw.textlength(lines[-1] + "\u2026", font=fnt) > maxw:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + "\u2026"
    for i, ln in enumerate(lines):
        yy = y + i * line_h
        if align == "center":
            draw.text((x + maxw / 2, yy), ln, font=fnt, fill=fill, anchor="ma")
        else:
            draw.text((x, yy), ln, font=fnt, fill=fill)
    return len(lines)


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


# ---------------------------------------------------------------- pictograms
def flame(d, cx, base_y, s):
    """Simple flame: outer orange, inner yellow."""
    d.polygon([(cx - 0.55 * s, base_y), (cx - 0.25 * s, base_y - 0.9 * s),
               (cx - 0.05 * s, base_y - 0.45 * s), (cx + 0.15 * s, base_y - 1.05 * s),
               (cx + 0.35 * s, base_y - 0.5 * s), (cx + 0.55 * s, base_y)],
              fill=(230, 110, 20))
    d.polygon([(cx - 0.28 * s, base_y), (cx - 0.12 * s, base_y - 0.5 * s),
               (cx + 0.05 * s, base_y - 0.25 * s), (cx + 0.12 * s, base_y - 0.6 * s),
               (cx + 0.28 * s, base_y)], fill=(245, 200, 40))


def smoke(d, cx, top_y, s, col=(120, 120, 120)):
    for i, (dx, dy, r) in enumerate([(-0.5, 0.3, 0.34), (0.1, 0.0, 0.42),
                                     (0.55, -0.35, 0.36), (-0.1, -0.6, 0.30)]):
        d.ellipse([cx + (dx - r) * s, top_y + (dy - r) * s,
                   cx + (dx + r) * s, top_y + (dy + r) * s], fill=col)


def draw_refinery(d, x, y, w, h):
    """Hero 1: refinery towers with fire and smoke."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(201, 184, 150))
    base = y + h - 18
    # towers
    for tx, th, tw in [(0.12, 0.62, 0.10), (0.30, 0.78, 0.11), (0.50, 0.55, 0.10)]:
        px, pw, ph = x + tx * w, tw * w, th * h
        d.rectangle([px, base - ph, px + pw, base], fill=(90, 100, 115))
        d.polygon([(px, base - ph), (px + pw / 2, base - ph - 12),
                   (px + pw, base - ph)], fill=(60, 68, 82))
        for k in range(3):
            yy = base - ph + 8 + k * (ph - 16) / 2
            d.line([px, yy, px + pw, yy], fill=(60, 68, 82), width=2)
    # storage tank
    d.ellipse([x + 0.68 * w, base - 34, x + 0.94 * w, base], fill=(150, 158, 168))
    d.rectangle([x + 0.68 * w, base - 26, x + 0.94 * w, base - 8], fill=(150, 158, 168))
    # flames + smoke on middle tower
    flame(d, x + 0.35 * w, base - 0.78 * h - 2, 16)
    smoke(d, x + 0.35 * w, y + 8, 16)
    flame(d, x + 0.82 * w, base - 36, 12)


def draw_tanker(d, x, y, w, h):
    """Hero 2: fuel tanker truck on fire."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 208))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(120, 118, 112))
    d.line([x, y + h - 26, x + w, y + h - 26], fill=(240, 240, 240), width=2)
    base = y + h - 26
    # tank (capsule)
    tx0, tx1, ty0, ty1 = x + 0.10 * w, x + 0.66 * w, base - 52, base - 12
    d.rounded_rectangle([tx0, ty0, tx1, ty1], radius=18, fill=(196, 198, 200),
                        outline=(90, 92, 96), width=2)
    d.line([tx0 + 14, ty0 + 4, tx0 + 14, ty1 - 4], fill=(150, 152, 156), width=2)
    d.line([tx1 - 14, ty0 + 4, tx1 - 14, ty1 - 4], fill=(150, 152, 156), width=2)
    # cab
    cx0 = x + 0.70 * w
    d.rectangle([cx0, base - 46, cx0 + 0.20 * w, base - 10], fill=BRICK)
    d.rectangle([cx0 + 0.05 * w, base - 42, cx0 + 0.13 * w, base - 24],
                fill=(180, 210, 225))
    # wheels
    for wx in [0.18, 0.42, 0.60, 0.82]:
        px = x + wx * w
        d.ellipse([px - 9, base - 12, px + 9, base + 6], fill=(30, 30, 30))
        d.ellipse([px - 4, base - 7, px + 4, base + 1], fill=(150, 150, 150))
    # flames over the tank
    flame(d, x + 0.30 * w, ty0 - 2, 15)
    flame(d, x + 0.52 * w, ty0 - 2, 12)
    smoke(d, x + 0.40 * w, y + 6, 15)


def draw_bars(d, x, y, w, h):
    """Hero 3: tariff bar chart CN 20% / EU 15% / IN 17%."""
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    base = y + h - 26
    top = y + 22
    vals = [("CHINA", 20, NAVY), ("EU", 15, (90, 110, 150)), ("INDIA", 17, BRICK)]
    bw = 52
    gap = (w - 3 * bw) / 4
    f_lab = font(13, bold=True)
    f_val = font(16, bold=True)
    for i, (lab, v, col) in enumerate(vals):
        bx = x + gap + i * (bw + gap)
        bh = (v / 20.0) * (base - top - 6)
        d.rectangle([bx, base - bh, bx + bw, base], fill=col)
        d.text((bx + bw / 2, base - bh + 5), f"{v}%", font=f_val,
               fill=(255, 255, 255), anchor="ma")
        d.text((bx + bw / 2, base + 6), lab, font=f_lab, fill=MUTED, anchor="ma")
    d.line([x + 10, base, x + w - 10, base], fill=INK, width=2)
    d.text((x + w - 12, y + 4), "PROPOSED CAP, %", font=font(11, bold=True),
           fill=MUTED, anchor="ra")


def pic_burst(d, cx, cy, s):
    pts = []
    import math
    for i in range(16):
        ang = i * math.pi / 8
        r = s if i % 2 == 0 else s * 0.45
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.polygon(pts, fill=(240, 170, 30), outline=(200, 90, 20))
    d.ellipse([cx - s * 0.25, cy - s * 0.25, cx + s * 0.25, cy + s * 0.25],
              fill=(200, 60, 20))


def pic_drone(d, cx, cy, s):
    d.rectangle([cx - 0.28 * s, cy - 0.12 * s, cx + 0.28 * s, cy + 0.12 * s],
                fill=(60, 68, 82))
    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        d.line([cx, cy, cx + dx * 0.7 * s, cy + dy * 0.55 * s],
               fill=(60, 68, 82), width=3)
        d.ellipse([cx + dx * 0.7 * s - 0.22 * s, cy + dy * 0.55 * s - 0.07 * s,
                   cx + dx * 0.7 * s + 0.22 * s, cy + dy * 0.55 * s + 0.07 * s],
                  fill=(150, 155, 165))


def pic_mine(d, cx, cy, s):
    import math
    for i in range(8):
        ang = i * math.pi / 4
        d.line([cx + 0.55 * s * math.cos(ang), cy + 0.55 * s * math.sin(ang),
                cx + 0.95 * s * math.cos(ang), cy + 0.95 * s * math.sin(ang)],
               fill=(40, 40, 40), width=3)
    d.ellipse([cx - 0.6 * s, cy - 0.6 * s, cx + 0.6 * s, cy + 0.6 * s],
              fill=(40, 40, 40))
    for wy in [0.85, 1.05]:
        d.arc([cx - 1.1 * s, cy + wy * s - 8, cx - 0.3 * s, cy + wy * s + 8],
              0, 180, fill=(70, 110, 150), width=3)
        d.arc([cx + 0.3 * s, cy + wy * s - 8, cx + 1.1 * s, cy + wy * s + 8],
              0, 180, fill=(70, 110, 150), width=3)


def pic_chip(d, cx, cy, s):
    d.rectangle([cx - 0.5 * s, cy - 0.5 * s, cx + 0.5 * s, cy + 0.5 * s],
                fill=NAVY)
    d.rectangle([cx - 0.22 * s, cy - 0.22 * s, cx + 0.22 * s, cy + 0.22 * s],
                fill=GOLD)
    for i in (-1, 0, 1):
        d.line([cx + i * 0.3 * s, cy - 0.5 * s, cx + i * 0.3 * s, cy - 0.75 * s],
               fill=NAVY, width=3)
        d.line([cx + i * 0.3 * s, cy + 0.5 * s, cx + i * 0.3 * s, cy + 0.75 * s],
               fill=NAVY, width=3)
        d.line([cx - 0.5 * s, cy + i * 0.3 * s, cx - 0.75 * s, cy + i * 0.3 * s],
               fill=NAVY, width=3)
        d.line([cx + 0.5 * s, cy + i * 0.3 * s, cx + 0.75 * s, cy + i * 0.3 * s],
               fill=NAVY, width=3)


def pic_no_fly(d, cx, cy, s):
    # simple plane silhouette
    d.polygon([(cx - 0.9 * s, cy + 0.1 * s), (cx - 0.5 * s, cy - 0.05 * s),
               (cx + 0.5 * s, cy - 0.25 * s), (cx + 0.9 * s, cy - 0.3 * s),
               (cx + 0.55 * s, cy + 0.05 * s), (cx + 0.75 * s, cy + 0.3 * s),
               (cx + 0.35 * s, cy + 0.25 * s), (cx - 0.1 * s, cy + 0.35 * s),
               (cx - 0.5 * s, cy + 0.3 * s)], fill=NAVY)
    d.ellipse([cx - 1.05 * s, cy - 1.05 * s, cx + 1.05 * s, cy + 1.05 * s],
              outline=BRICK, width=4)
    d.line([cx - 0.75 * s, cy + 0.75 * s, cx + 0.75 * s, cy - 0.75 * s],
           fill=BRICK, width=4)


def pic_door_check(d, cx, cy, s):
    d.rectangle([cx - 0.7 * s, cy - 0.8 * s, cx + 0.1 * s, cy + 0.8 * s],
                outline=NAVY, width=3)
    d.polygon([(cx - 0.7 * s, cy - 0.8 * s), (cx + 0.1 * s, cy - 0.55 * s),
               (cx + 0.1 * s, cy + 0.8 * s), (cx - 0.7 * s, cy + 0.8 * s)],
              fill=(200, 210, 225))
    d.line([cx + 0.25 * s, cy + 0.1 * s, cx + 0.55 * s, cy + 0.45 * s,
            cx + 1.05 * s, cy - 0.35 * s], fill=(30, 140, 60), width=5)


def pic_rocket(d, cx, cy, s):
    d.polygon([(cx, cy - 1.0 * s), (cx + 0.35 * s, cy - 0.2 * s),
               (cx + 0.3 * s, cy + 0.5 * s), (cx, cy + 0.65 * s),
               (cx - 0.3 * s, cy + 0.5 * s), (cx - 0.35 * s, cy - 0.2 * s)],
              fill=(200, 60, 40))
    d.ellipse([cx - 0.14 * s, cy - 0.45 * s, cx + 0.14 * s, cy - 0.17 * s],
              fill=(180, 220, 235))
    flame(d, cx, cy + 0.65 * s, 12)
    d.polygon([(cx + 1.05 * s, cy - 0.85 * s), (cx + 1.2 * s, cy - 0.6 * s),
               (cx + 1.05 * s, cy - 0.55 * s), (cx + 0.9 * s, cy - 0.7 * s)],
              fill=GOLD)


def pic_train(d, cx, cy, s):
    d.rounded_rectangle([cx - 0.8 * s, cy - 0.7 * s, cx + 0.8 * s, cy + 0.6 * s],
                        radius=10, fill=NAVY)
    d.rectangle([cx - 0.55 * s, cy - 0.5 * s, cx - 0.05 * s, cy - 0.05 * s],
                fill=(180, 220, 235))
    d.rectangle([cx + 0.05 * s, cy - 0.5 * s, cx + 0.55 * s, cy - 0.05 * s],
                fill=(180, 220, 235))
    d.ellipse([cx - 0.45 * s, cy + 0.2 * s, cx - 0.15 * s, cy + 0.5 * s],
              fill=(250, 220, 80))
    d.ellipse([cx + 0.15 * s, cy + 0.2 * s, cx + 0.45 * s, cy + 0.5 * s],
              fill=(250, 220, 80))
    d.line([cx - 0.9 * s, cy + 0.85 * s, cx + 0.9 * s, cy + 0.85 * s],
           fill=(60, 60, 60), width=3)


def pic_flags(d, cx, cy, s):
    d.line([cx - 0.45 * s, cy - 0.8 * s, cx - 0.45 * s, cy + 0.8 * s],
           fill=(60, 60, 60), width=3)
    d.line([cx + 0.45 * s, cy - 0.8 * s, cx + 0.45 * s, cy + 0.8 * s],
           fill=(60, 60, 60), width=3)
    d.polygon([(cx - 0.45 * s, cy - 0.8 * s), (cx + 0.1 * s, cy - 0.65 * s),
               (cx - 0.45 * s, cy - 0.45 * s)], fill=(30, 120, 80))
    d.polygon([(cx + 0.45 * s, cy - 0.8 * s), (cx + 1.0 * s, cy - 0.65 * s),
               (cx + 0.45 * s, cy - 0.45 * s)], fill=GOLD)


def pic_tower_flame(d, cx, cy, s):
    d.rectangle([cx - 0.35 * s, cy - 0.6 * s, cx + 0.35 * s, cy + 0.7 * s],
                fill=(90, 100, 115))
    d.polygon([(cx - 0.35 * s, cy - 0.6 * s), (cx, cy - 0.95 * s),
               (cx + 0.35 * s, cy - 0.6 * s)], fill=(60, 68, 82))
    flame(d, cx + 0.65 * s, cy + 0.7 * s, 13)


# ---------------------------------------------------------------- world map
# Rough continent outlines in (lon, lat). Simplified but recognisable.
CONTINENTS = [
    # North America
    [(-168, 66), (-158, 58), (-140, 60), (-135, 58), (-128, 49), (-124, 42),
     (-120, 34), (-114, 29), (-110, 24), (-105, 20), (-97, 16), (-92, 15),
     (-86, 12), (-83, 9), (-79, 9), (-77, 7), (-75, 10), (-72, 12),
     (-68, 12), (-64, 10), (-61, 9), (-59, 8), (-55, 6), (-52, 5),
     (-54, 2), (-50, 0), (-44, 3), (-40, 5), (-44, 8), (-48, 10),
     (-50, 12), (-55, 16), (-58, 20), (-60, 25), (-62, 30), (-66, 32),
     (-70, 36), (-74, 39), (-75, 35), (-80, 32), (-81, 26), (-84, 30),
     (-89, 30), (-91, 29), (-94, 29), (-97, 26), (-97, 21), (-94, 18),
     (-90, 21), (-86, 21), (-90, 14), (-92, 15), (-97, 16), (-105, 20),
     (-110, 23), (-114, 28), (-117, 33), (-122, 37), (-124, 40),
     (-124, 48), (-130, 54), (-140, 60), (-152, 58), (-158, 56),
     (-162, 55), (-168, 66)],
    # Greenland
    [(-58, 64), (-52, 60), (-43, 60), (-40, 65), (-32, 68), (-25, 70),
     (-20, 74), (-25, 76), (-35, 78), (-50, 76), (-58, 72), (-60, 68),
     (-58, 64)],
    # South America
    [(-77, 7), (-72, 11), (-64, 10), (-60, 8), (-55, 6), (-52, 5),
     (-50, 0), (-44, -3), (-38, -5), (-35, -8), (-39, -13), (-40, -20),
     (-41, -23), (-48, -27), (-52, -33), (-58, -38), (-62, -41),
     (-65, -45), (-67, -50), (-68, -54), (-71, -54), (-73, -50),
     (-73, -44), (-73, -37), (-72, -30), (-70, -23), (-70, -18),
     (-75, -15), (-77, -12), (-81, -6), (-81, -1), (-80, 1), (-77, 4),
     (-77, 7)],
    # Africa
    [(-17, 15), (-16, 20), (-15, 27), (-10, 31), (-6, 34), (0, 36),
     (10, 37), (11, 34), (15, 32), (20, 32), (25, 32), (30, 31),
     (32, 31), (34, 28), (35, 28), (37, 24), (39, 20), (39, 16),
     (41, 12), (44, 11), (48, 11), (51, 12), (51, 10), (48, 5),
     (46, 2), (42, -1), (40, -5), (40, -10), (39, -15), (36, -18),
     (35, -22), (33, -26), (31, -29), (28, -33), (25, -34), (20, -35),
     (17, -33), (15, -27), (12, -18), (12, -13), (9, -4), (9, 0),
     (9, 4), (4, 6), (-2, 5), (-8, 5), (-13, 8), (-17, 12), (-17, 15)],
    # Eurasia (one outline, Iberia -> Pacific -> SE Asia -> India -> Arabia)
    [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-1, 49),
     (2, 51), (4, 53), (7, 54), (8, 57), (10, 59), (12, 58),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (30, 66),
     (32, 70), (40, 68), (45, 68), (50, 69), (55, 69), (60, 70),
     (68, 72), (75, 72), (80, 73), (90, 75), (100, 76), (110, 74),
     (120, 73), (130, 72), (140, 72), (150, 70), (158, 69), (162, 66),
     (170, 66), (178, 65), (178, 62), (170, 60), (163, 60), (160, 56),
     (157, 52), (150, 45), (142, 40), (140, 38), (135, 35), (130, 34),
     (127, 35), (126, 38), (122, 38), (120, 32), (122, 28), (118, 24),
     (112, 22), (108, 18), (105, 10), (103, 8), (100, 8), (98, 12),
     (97, 16), (94, 17), (92, 21), (89, 22), (86, 20), (83, 18),
     (80, 15), (80, 10), (77, 8), (75, 12), (73, 16), (72, 20),
     (70, 22), (68, 24), (66, 25), (62, 25), (58, 25), (56, 26),
     (54, 26), (52, 27), (50, 29), (48, 30), (46, 29), (43, 28),
     (41, 29), (39, 28), (38, 24), (36, 22), (35, 20), (35, 18),
     (38, 16), (40, 15), (42, 15), (44, 13), (45, 12), (48, 14),
     (51, 14), (55, 17), (57, 19), (59, 22), (58, 24), (56, 26),
     (54, 26), (52, 25), (50, 26), (48, 28), (44, 29), (40, 31),
     (36, 36), (34, 36), (30, 36), (27, 37), (26, 38), (23, 36),
     (23, 40), (20, 40), (19, 42), (16, 41), (14, 42), (12, 44),
     (8, 44), (6, 43), (3, 42), (0, 39), (-2, 37), (-6, 36), (-9, 37)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-2, 50), (-5, 50)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (137, 35), (139, 36), (140, 38),
     (141, 40), (142, 42), (144, 44), (143, 42), (141, 39), (139, 36),
     (136, 34), (133, 34), (131, 33), (130, 31)],
    # Australia
    [(114, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38),
     (150, -37), (153, -32), (153, -27), (150, -23), (146, -19),
     (142, -15), (142, -11), (137, -12), (135, -12), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20), (114, -22)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (50, -20), (47, -24), (45, -25),
     (43, -22), (44, -18), (44, -16)],
    # New Zealand
    [(167, -45), (170, -43), (173, -41), (175, -38), (178, -38),
     (176, -40), (174, -42), (171, -44), (167, -45)],
]

# pins: (number, true lon, true lat, display lon, display lat)
# display positions are nudged so neighbours do not collide; a thin
# leader line joins each pin to its true location (small navy dot).
PINS = [
    (1, 50.0, 26.6, 42.0, 31.0),   # Ras Tanura
    (2, -77.0, 38.9, -84.0, 33.0),  # Washington (tariffs)
    (3, 56.6, 26.6, 64.0, 34.0),   # Hormuz
    (4, 34.5, 31.4, 26.0, 40.0),   # Gaza
    (5, 32.0, 49.5, 31.0, 57.0),   # Ukraine refineries
    (6, 35.0, 48.0, 48.0, 44.0),   # Ukraine drones
    (7, 31.2, 30.0, 24.0, 23.0),   # Cairo
    (8, -74.0, 40.7, -68.0, 45.0),  # New York (Huawei trial)
    (9, 19.0, 52.0, 12.0, 60.0),   # Poland
    (10, -74.0, 4.6, -74.0, 4.6),  # Colombia
    (11, 69.0, 30.0, 80.0, 40.0),  # Pakistan
    (12, 2.0, 50.5, -6.0, 58.0),   # London-Paris
    (13, 160.0, -9.5, 160.0, -9.5),  # Solomon Islands
]


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- top bar
    y = 14
    f_top_l = font(15, bold=True)
    f_top_r = font(13, bold=True)
    d.text((MARGIN, y), "THE DAY IN WORLD NEWS", font=f_top_l, fill=NAVY)
    right = "35 STORIES \u00b7 6 CONTINENTS \u00b7 ONE DAY"
    d.text((W - MARGIN, y), right, font=f_top_r, fill=BRICK, anchor="ra")

    # ---- masthead
    f_mast = font(56, bold=True, serif=True)
    mast = "Thursday 26 November 2026"
    mw = text_w(d, mast, f_mast)
    if mw > CW:
        warn(f"masthead too wide: {mw:.0f}px > {CW}px")
    d.text((W / 2, 40), mast, font=f_mast, fill=INK, anchor="ma")
    d.line([MARGIN, 106, W - MARGIN, 106], fill=NAVY, width=3)
    d.line([MARGIN, 110, W - MARGIN, 110], fill=NAVY, width=1)

    # ---- hero row
    heroes = [
        ("1 \u00b7 MIDDLE EAST \u00b7 CONFLICT",
         "HOUTHIS HIT SAUDI'S BIGGEST REFINERY",
         "Ras Tanura attacked; fires and black smoke over 600 sq km. Brent jumps to $93.60.",
         draw_refinery),
        ("2 \u00b7 MIDDLE EAST \u00b7 DISASTER",
         "CAIRO TANKER FIRE KILLS 30",
         "Fuel tanker overturns on a Cairo ring road; 30 dead, 25 injured.",
         draw_tanker),
        ("3 \u00b7 WORLD \u00b7 TRADE",
         "US PROPOSES TARIFFS ON 14 ECONOMIES",
         "China capped at 20%, EU at 15%, India 17%; hearing 25 January 2027.",
         draw_bars),
    ]
    hx, hy, hw, hh = MARGIN, 120, 314, 240
    gap = 13
    for i, (tag, head, cap, drawer) in enumerate(heroes):
        x = hx + i * (hw + gap)
        d.rectangle([x, hy, x + hw, hy + hh], fill=CARD, outline=RULE, width=1)
        d.rectangle([x, hy, x + hw, hy + 3], fill=NAVY)
        drawer(d, x + 8, hy + 12, hw - 16, 102)
        d.text((x + 12, hy + 122), tag, font=font(12, bold=True), fill=BRICK)
        draw_fit(d, x + 12, hy + 140, head, font(22, bold=True), hw - 24, 2, 27, INK)
        draw_fit(d, x + 12, hy + 200, cap, font(13), hw - 24, 2, 17, MUTED)

    # ---- medium rows (stories 4-13)
    medium = [
        ("4 \u00b7 MIDDLE EAST", "HAMAS COLONEL KILLED IN GAZA",
         "Ceasefire under strain.", pic_burst),
        ("5 \u00b7 EUROPE", "UKRAINE STRIKES RUSSIAN OIL",
         "Five jets hit at Savasleyka.", pic_tower_flame),
        ("6 \u00b7 EUROPE", "RUSSIAN DRONES KILL SEVEN",
         "Six regions hit overnight.", pic_drone),
        ("7 \u00b7 MIDDLE EAST", "TWO TANKERS HIT MINES IN HORMUZ",
         "IRGC: unauthorised route.", pic_mine),
        ("8 \u00b7 AMERICAS", "HUAWEI CONVICTED",
         "Guilty on 10 counts.", pic_chip),
        ("9 \u00b7 EUROPE", "POLAND PLANS NO-FLY ZONE",
         "Eastern border, early 2027.", pic_no_fly),
        ("10 \u00b7 AMERICAS", "COLOMBIA HOSTAGES FREED",
         "20 freed after 17 hours.", pic_door_check),
        ("11 \u00b7 ASIA-PACIFIC", "FIRST PAKISTANI ASTRONAUT",
         "Flies on Shenzhou-24.", pic_rocket),
        ("12 \u00b7 EUROPE", "EUROSTAR STRIKE CANCELS TRAINS",
         "London\u2013Paris halted.", pic_train),
        ("13 \u00b7 ASIA-PACIFIC", "SOLOMON IS. TREATY",
         "Security pact signed.", pic_flags),
    ]
    mw_, mh = 185, 140
    mgap = 10
    for r in range(2):
        for c in range(5):
            i = r * 5 + c
            tag, head, cap, pic = medium[i]
            x = MARGIN + c * (mw_ + mgap)
            y = 372 + r * (mh + 10)
            d.rectangle([x, y, x + mw_, y + mh], fill=CARD, outline=RULE, width=1)
            pic(d, x + mw_ / 2, y + 32, 26)
            d.text((x + 8, y + 66), tag, font=font(12, bold=True), fill=BRICK)
            draw_fit(d, x + 8, y + 82, head, font(15, bold=True), mw_ - 16, 2, 19, INK)
            draw_fit(d, x + 8, y + 122, cap, font(12), mw_ - 16, 1, 15, MUTED)

    # ---- BY THE NUMBERS strip
    sy, sh = 664, 84
    d.rectangle([MARGIN, sy, W - MARGIN, sy + sh], fill=NAVY)
    d.text((W / 2, sy + 6), "B Y   T H E   N U M B E R S",
           font=font(12, bold=True), fill=GOLD, anchor="ma")
    stats = [
        ("30", "killed in the Cairo tanker fire"),
        ("$93.60", "Brent crude per barrel"),
        ("14", "economies face proposed US tariffs"),
        ("204", "runs off 53 balls \u2014 Sooryavanshi, 15"),
    ]
    cell_w = CW / 4
    for i, (num, cap) in enumerate(stats):
        cx = MARGIN + cell_w * i + cell_w / 2
        d.text((cx, sy + 24), num, font=font(30, bold=True), fill=(255, 255, 255),
               anchor="ma")
        draw_fit(d, MARGIN + cell_w * i + 8, sy + 60, cap, font(12),
                 cell_w - 16, 1, 15, (210, 214, 226), align="center")

    # ---- bottom: map (left) + ALSO list (right)
    by = 760
    map_x, map_w = MARGIN, 420
    list_x, list_w = MARGIN + map_w + 16, CW - map_w - 16  # 532
    f_sec = font(13, bold=True)
    d.text((map_x, by), "WHERE IT HAPPENED \u2014 13 STORIES MAPPED",
           font=f_sec, fill=NAVY)
    d.text((list_x, by), "ALSO ON THURSDAY 26 NOVEMBER",
           font=f_sec, fill=NAVY)
    d.line([map_x, by + 18, map_x + map_w, by + 18], fill=NAVY, width=2)
    d.line([list_x, by + 18, list_x + list_w, by + 18], fill=NAVY, width=2)

    # map box
    mx0, my0 = map_x, by + 26
    mx1, my1 = map_x + map_w, 978
    d.rectangle([mx0, my0, mx1, my1], fill=MAP_BG, outline=RULE, width=1)

    def proj(lon, lat):
        px = mx0 + (lon + 170) / 360.0 * (mx1 - mx0)
        py = my0 + (75 - lat) / 135.0 * (my1 - my0)
        return (px, py)

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    f_pin = font(12, bold=True)
    for num, lon, lat, dlon, dlat in PINS:
        tx, ty = proj(lon, lat)
        px, py = proj(dlon, dlat)
        if (lon, lat) != (dlon, dlat):
            d.line([tx, ty, px, py], fill=(90, 84, 70), width=1)
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=NAVY)
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=BRICK,
                  outline=(255, 255, 255), width=2)
        d.text((px, py), str(num), font=f_pin, fill=(255, 255, 255),
               anchor="mm")

    # ALSO list: 2 columns x 11 rows, 13px minimum
    also = [
        (14, "Washington", "GDP revised up"),
        (15, "LAX", "Thanksgiving crowds"),
        (16, "Mumbai", "26/11 anniversary"),
        (17, "London", "Poundland collapses"),
        (18, "Sudan", "Drone strikes kill 19"),
        (19, "Niger", "Saudi man kidnapped"),
        (20, "Pyongyang", "Swiss office shut"),
        (21, "West Java", "Mine flood traps 23"),
        (22, "Puerto Rico", "Miss Universe win"),
        (23, "Sooryavanshi", "204 off 53 balls"),
        (24, "Gukesh", "Draws game 2 in 20"),
        (25, "SpaceX", "1m satellites OK'd"),
        (26, "New York", "Nvidia-led sell-off"),
        (27, "Nepal", "Quake M5.6 hits Koshi"),
        (28, "UN", "Tribunal backs aid workers"),
        (29, "BBC", "Appeals Trump $10bn suit"),
        (30, "Duran Duran", "Taylor, 65, dies"),
        (31, "Mississippi", "Crash kills six"),
        (32, "Berlin", "Guns up, aid down"),
        (33, "Russia", "War dead near 500,000"),
        (34, "Asteroid", "New crater revealed"),
        (35, "Cameroon", "Elephant kills tourist"),
    ]
    col_w = (list_w - 12) / 2
    f_num = font(13, bold=True)
    f_city = font(13, bold=True)
    f_phrase = font(13)
    row_h = 15.4
    ly0 = by + 26
    for idx, (num, city, phrase) in enumerate(also):
        col = idx // 11
        row = idx % 11
        x = list_x + col * (col_w + 12)
        y = ly0 + row * row_h
        # measure full line; warn if it overflows the column
        num_s = f"{num} "
        city_s = city + " \u2014 "
        total = (text_w(d, num_s, f_num) + text_w(d, city_s, f_city)
                 + text_w(d, phrase, f_phrase))
        if total > col_w:
            warn(f"ALSO row {num} too wide ({total:.0f}px > {col_w:.0f}px): "
                 f"{city} \u2014 {phrase}")
        d.text((x, y), num_s, font=f_num, fill=BRICK)
        nx = x + text_w(d, num_s, f_num)
        d.text((nx, y), city_s, font=f_city, fill=NAVY)
        nx += text_w(d, city_s, f_city)
        d.text((nx, y), phrase, font=f_phrase, fill=INK)

    # ---- footer
    foot = ("Every story was reported on Thursday 26 November 2026; disputed "
            "claims are attributed. Sources: Reuters \u00b7 AP \u00b7 BBC. "
            "Original drawings. Press time 00:30 GMT, 26 Nov 2026.")
    f_foot = font(11)
    fw = text_w(d, foot, f_foot)
    if fw > CW:
        warn(f"footer too wide: {fw:.0f}px > {CW}px")
    d.text((W / 2, 992), foot, font=f_foot, fill=MUTED, anchor="ma")

    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = render()
    img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    sha = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"wrote {out} {img.size[0]}x{img.size[1]} {size} bytes sha256={sha}")
    if WARNINGS:
        print(f"WARNINGS: {len(WARNINGS)}", file=sys.stderr)
        sys.exit(1)
    print("no warnings")


if __name__ == "__main__":
    main()
