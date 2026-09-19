#!/usr/bin/env python3
"""アプリアイコンを生成する（外部ライブラリ不要）。
濃い藍鉄の地に、4区分の色の行が並ぶ = タスク表のしるし。"""
import struct, zlib, os

BG   = (0x1E, 0x4D, 0x57)
ROWS = [(0xE0,0xA1,0x71), (0x78,0xC6,0xAC), (0x9A,0xB0,0xE4), (0xD7,0x9B,0xC2)]
BAR  = (0xF0,0xEA,0xDC)

def blend(dst, src, a):
    return tuple(round(d*(1-a) + s*a) for d, s in zip(dst, src))

def rrect(px, w, h, x0, y0, x1, y1, r, color, alpha=1.0):
    for y in range(max(0,int(y0)), min(h,int(y1)+1)):
        for x in range(max(0,int(x0)), min(w,int(x1)+1)):
            cx = x0+r if x < x0+r else (x1-r if x > x1-r else x)
            cy = y0+r if y < y0+r else (y1-r if y > y1-r else y)
            if (x-cx)**2 + (y-cy)**2 > r*r:
                continue
            px[y][x] = blend(px[y][x], color, alpha)

def render(size):
    s = size
    px = [[BG]*s for _ in range(s)]
    # 4行。左に区分色のタグ、右に内容を表す明るいバー。
    top, gap = 0.235*s, 0.045*s
    rowh = (0.53*s - gap*3) / 4
    tagw, x0 = 0.115*s, 0.20*s
    for i, col in enumerate(ROWS):
        y = top + i*(rowh+gap)
        rr = rowh*0.34
        rrect(px, s, s, x0, y, x0+tagw, y+rowh, rr, col)
        bx0 = x0 + tagw + 0.045*s
        bx1 = x0 + 0.60*s - (0.055*s if i % 2 else 0)
        rrect(px, s, s, bx0, y+rowh*0.22, bx1, y+rowh*0.78, rowh*0.28, BAR, 0.82 - i*0.06)
    raw = b"".join(b"\x00" + bytes(v for p in row for v in p) for row in px)
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", s, s, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))

here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
for name, size in [("icon-192.png",192), ("icon-512.png",512), ("apple-touch-icon.png",180), ("favicon-32.png",32)]:
    open(os.path.join(here, name), "wb").write(render(size))
    print(name, size)
