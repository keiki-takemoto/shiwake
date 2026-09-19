#!/usr/bin/env python3
"""アプリアイコンを生成する（外部ライブラリ不要）。
  python3 make_icons.py [Z|A|B|C|D] … 選んだ案で icons/ を作り直す（既定はZ＝ZIPANGの頭文字）
  python3 make_icons.py sheet       … 候補を並べた比較用の1枚を作る
"""
import struct, zlib, os, sys

INK   = (0x1E, 0x4D, 0x57)   # 藍鉄（地）
PAPER = (0xF2, 0xEA, 0xDB)   # 生成り
CATS  = [(0xE0,0xA1,0x71),   # 改善点
         (0x78,0xC6,0xAC),   # 購入品
         (0x9A,0xB0,0xE4),   # 共有事項
         (0xD7,0x9B,0xC2)]   # 商品開発提案
BAR   = (0xF0,0xEA,0xDC)
ENJI  = (0x8C, 0x23, 0x31)   # 店の卓布の臙脂
KURO  = (0x00, 0x00, 0x00)   # 黒（現行の地）
KINU  = (0xF4, 0xEC, 0xDC)   # 生成り（文字）

def blend(d, s, a): return tuple(round(x*(1-a) + y*a) for x, y in zip(d, s))

def rrect(px, w, h, x0, y0, x1, y1, r, color, alpha=1.0):
    for y in range(max(0,int(y0)), min(h,int(y1)+1)):
        for x in range(max(0,int(x0)), min(w,int(x1)+1)):
            cx = x0+r if x < x0+r else (x1-r if x > x1-r else x)
            cy = y0+r if y < y0+r else (y1-r if y > y1-r else y)
            if (x-cx)**2 + (y-cy)**2 > r*r: continue
            px[y][x] = blend(px[y][x], color, alpha)

def canvas(s, bg): return [[bg]*s for _ in range(s)]

def art_A(px, s):            # 4区分が行で並ぶ（表のしるし）
    top, gap = 0.235*s, 0.045*s
    rowh = (0.53*s - gap*3)/4
    tagw, x0 = 0.115*s, 0.20*s
    for i, col in enumerate(CATS):
        y = top + i*(rowh+gap)
        rrect(px, s, s, x0, y, x0+tagw, y+rowh, rowh*0.34, col)
        bx1 = x0 + 0.60*s - (0.055*s if i % 2 else 0)
        rrect(px, s, s, x0+tagw+0.045*s, y+rowh*0.22, bx1, y+rowh*0.78, rowh*0.28, BAR, 0.82-i*0.06)

def art_B(px, s):            # 4区分のタイル（2×2）
    m, g = 0.215*s, 0.055*s
    t = (s - m*2 - g)/2
    for i, col in enumerate(CATS):
        x = m + (i % 2)*(t+g); y = m + (i//2)*(t+g)
        rrect(px, s, s, x, y, x+t, y+t, t*0.28, col)

def art_C(px, s):            # 貼り紙に4色のふせん
    rrect(px, s, s, 0.20*s, 0.165*s, 0.80*s, 0.835*s, 0.075*s, PAPER)
    for i, col in enumerate(CATS):
        y = 0.245*s + i*0.155*s
        rrect(px, s, s, 0.255*s, y, 0.355*s, y+0.095*s, 0.026*s, col)
        rrect(px, s, s, 0.385*s, y+0.028*s, (0.735 - (0.09 if i % 2 else 0))*s, y+0.067*s, 0.02*s, INK, 0.30)

def art_D(px, s):            # 4区分の積み上がり（件数のしるし）
    base, bw, g = 0.775*s, 0.125*s, 0.048*s
    total = bw*4 + g*3
    x0 = (s-total)/2
    for i, (col, hh) in enumerate(zip(CATS, [0.30, 0.46, 0.22, 0.38])):
        x = x0 + i*(bw+g)
        rrect(px, s, s, x, base-hh*s, x+bw, base, bw*0.36, col)
    rrect(px, s, s, x0-0.02*s, base+0.028*s, x0+total+0.02*s, base+0.062*s, 0.017*s, BAR, 0.55)

def fill_polys(s, polys, ss=3):
    """多角形を塗る。ss倍で描いてから縮めるので、斜めの線がなめらかになる。
    戻り値は 0.0〜1.0 の濃さの表。"""
    S = s*ss
    cov = [bytearray(S) for _ in range(S)]
    for poly in polys:
        pts = [(x*ss, y*ss) for x, y in poly]
        ys = [p[1] for p in pts]
        for y in range(max(0, int(min(ys))), min(S, int(max(ys))+1)):
            yc, xs = y+0.5, []
            for i in range(len(pts)):
                x1, y1 = pts[i]; x2, y2 = pts[(i+1) % len(pts)]
                if (y1 <= yc < y2) or (y2 <= yc < y1):
                    xs.append(x1 + (yc-y1)*(x2-x1)/(y2-y1))
            xs.sort()
            row = cov[y]
            for i in range(0, len(xs)-1, 2):
                for x in range(max(0, int(xs[i]+0.5)), min(S, int(xs[i+1]+0.5))):
                    row[x] = 1
    out = []
    inv = 1.0/(ss*ss)
    for y in range(s):
        rows = cov[y*ss:(y+1)*ss]
        out.append([sum(r[x*ss:(x+1)*ss].count(1) for r in rows)*inv for x in range(s)])
    return out

def art_Z(px, s):            # ZIPANGの頭文字
    x0, x1 = 0.215*s, 0.785*s
    y0, y1 = 0.235*s, 0.765*s
    t  = 0.108*s             # 横棒の太さ
    wd = 0.205*s             # 斜め棒の（横方向の）太さ
    polys = [
        [(x0, y0), (x1, y0), (x1, y0+t), (x0, y0+t)],
        [(x0, y1-t), (x1, y1-t), (x1, y1), (x0, y1)],
        [(x1, y0+t), (x1-wd, y0+t), (x0, y1-t), (x0+wd, y1-t)],
    ]
    cov = fill_polys(s, polys)
    for y in range(s):
        for x in range(s):
            a = cov[y][x]
            if a > 0: px[y][x] = blend(px[y][x], KINU, a)

ART = {"Z": (art_Z, KURO), "A": (art_A, INK), "B": (art_B, INK), "C": (art_C, INK), "D": (art_D, INK)}

def png(px, s):
    raw = b"".join(b"\x00" + bytes(v for p in row for v in p) for row in px)
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", s, s, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))

def render(plan, s):
    fn, bg = ART[plan]
    px = canvas(s, bg); fn(px, s); return px

HERE = os.path.dirname(os.path.abspath(__file__))

def write_set(plan):
    d = os.path.join(HERE, "icons"); os.makedirs(d, exist_ok=True)
    for name, size in [("icon-192.png",192), ("icon-512.png",512), ("apple-touch-icon.png",180), ("favicon-32.png",32)]:
        open(os.path.join(d, name), "wb").write(png(render(plan, size), size))
    print("案", plan, "でアイコンを作り直しました")

def write_sheet():
    tile, pad, s = 330, 40, 40
    W = pad*2 + tile*2 + s
    sheet = canvas(W, (0x9A, 0x96, 0x8E))
    for i, plan in enumerate("ZBCD"):
        src = render(plan, tile)
        ox = pad + (i % 2)*(tile+s); oy = pad + (i//2)*(tile+s)
        r = tile*0.225
        for y in range(tile):
            for x in range(tile):
                cx = r if x < r else (tile-1-r if x > tile-1-r else x)
                cy = r if y < r else (tile-1-r if y > tile-1-r else y)
                if (x-cx)**2 + (y-cy)**2 > r*r: continue
                sheet[oy+y][ox+x] = src[y][x]
    out = os.path.join(HERE, "icon-candidates.png")
    open(out, "wb").write(png(sheet, W)); print(out)

arg = (sys.argv[1] if len(sys.argv) > 1 else "Z").upper()
write_sheet() if arg == "SHEET" else write_set(arg)
