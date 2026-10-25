import json, sys, math
from PIL import Image, ImageDraw, ImageFont
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
INK = (20, 20, 20); ACC = (25, 45, 95); PK = (120, 135, 160); PKF = (248, 250, 253); SYSF = (226, 237, 250); ASSOC = (0, 92, 110)
W = 1795
f_uc = ImageFont.truetype(B, 31); f_pk = ImageFont.truetype(B, 33); f_sys = ImageFont.truetype(B, 42)
f_act = ImageFont.truetype(B, 27); f_rel = ImageFont.truetype(B, 25); f_note = ImageFont.truetype(R, 29)
AZ = 175; X0, X1 = AZ, W - AZ; GAP = 36
PKW = (X1 - X0 - 40 - GAP) // 2
COLS = [(X0 + 20, X0 + 20 + PKW), (X1 - 20 - PKW, X1 - 20)]
EW = 600; HEAD = 64; PAD = 20; VG = 14
LH = 38
def eh(label):
    lines = label.split("\n"); n = len(lines)
    h = max(76, n * LH + 34)
    while True:
        ok = True
        for i, l in enumerate(lines):
            dy = abs((i - (n - 1) / 2) * LH) + LH * 0.36
            avail = EW / 2 * max(0, 1 - (dy / (h / 2)) ** 2) ** 0.5 - 8
            if f_uc.getlength(l) / 2 > avail: ok = False
        if ok or h > 260: return int(h)
        h += 6
def dashed(d, pts):
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L // 14))
        for k in range(0, n, 2):
            a, b = k / n, min(1, (k + 1) / n)
            d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)], fill=INK, width=3)
def render(spec, out):
    global AZ, X0, X1, PKW, COLS, EW
    AZ = max(195, int(f_act.getlength(spec["actor"])) + 70); X0, X1 = AZ, W - AZ
    PKW = (X1 - X0 - 40 - GAP) // 2
    COLS = [(X0 + 20, X0 + 20 + PKW), (X1 - 20 - PKW, X1 - 20)]
    EW = min(610, PKW - 74)
    pos = {}; boxes = []; colspan = []
    top = 100
    for ci, col in enumerate(spec["columns"]):
        px0, px1 = COLS[ci]
        ex0 = px0 + 22 if ci == 0 else px1 - 22 - EW
        y = top
        y0c = y
        for g in col:
            gy = y; y += HEAD
            for it in g["items"]:
                lab = it if isinstance(it, str) else it["label"]
                link = True if isinstance(it, str) else it.get("actor", True)
                h = eh(lab); pos[lab] = (ex0, y, EW, h, link, ci); y += h + VG
            y += PAD - VG
            boxes.append((px0, gy, px1, y, g["title"], ci)); y += 26
        colspan.append((y0c, y - 26))
    sys_y1 = max(c[1] for c in colspan) + 24
    note = spec.get("note"); H = sys_y1 + (40 + 44 * (note.count("\n") + 1) + 40 if note else 30)
    img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
    d.rectangle([X0, 20, X1, sys_y1], outline=INK, width=6, fill=SYSF)
    d.text(((X0 + X1) / 2, 60), "Système PsyConnect", font=f_sys, fill=INK, anchor="mm")
    for px0, gy, px1, gy1, t, ci in boxes:
        d.rounded_rectangle([px0, gy, px1, gy1], radius=16, outline=PK, width=3, fill=PKF)
        d.text((px0 + 18, gy + 16), t, font=f_pk, fill=ACC, anchor="la")
    actors = []
    for ci in range(len(spec["columns"])):
        ys = [v[1] + v[3] / 2 for v in pos.values() if v[5] == ci and v[4]]
        if not ys: continue
        ay = (min(ys) + max(ys)) / 2
        ax = X0 - 112 if ci == 0 else X1 + 112
        actors.append((ax, ay))
        hand = (ax + (62 if ci == 0 else -62), ay - 36)
        tr = X0 - 34 if ci == 0 else X1 + 34
        bys = []
        for lab, (ex, ey, ew, h, link, c) in pos.items():
            if c == ci and link:
                tx = ex if ci == 0 else ex + ew
                by = ey + h / 2; bys.append(by)
                d.line([(tr, by), (tx, by)], fill=ASSOC, width=4)
        d.line([(tr, min(bys + [hand[1]])), (tr, max(bys + [hand[1]]))], fill=ASSOC, width=4)
        d.line([hand, (tr, hand[1])], fill=ASSOC, width=4)
    labels = []
    rels = []
    for rel in spec.get("relations", []):
        if isinstance(rel, dict): rels.append((rel["from"], rel["to"], rel["kind"]))
        else: rels.append(([rel[0]], [rel[1]], rel[2]))
    att = {}
    for fr, to, k in rels:
        for n in fr + to: att.setdefault(n, []).append(id((fr, to)))
    used = {}
    def ay_of(n):
        ex, ey, ew, h, link, c = pos[n]; lst = att[n]; k = used.get(n, 0); used[n] = k + 1
        return ey + h / 2 + (k - (len(lst) - 1) / 2) * 16
    levels = {0: [], 1: []}
    for fr, to, kind in rels:
        ci = pos[fr[0]][5]
        ends = [(n, ay_of(n), n in to) for n in fr + to]
        lo = min(e[1] for e in ends); hi = max(e[1] for e in ends)
        lv = 0
        while any(not (hi + 10 < a or lo - 10 > b) for a, b, l in levels[ci] if l == lv): lv += 1
        levels[ci].append((lo, hi, lv))
        off = 30 + lv * 46
        for n, y, is_t in ends:
            ex, ey, ew, h, link, c = pos[n]
            xe = ex + ew if ci == 0 else ex
            bend = (xe + off) if ci == 0 else (xe - off)
            dashed(d, [(xe, y), (bend, y)])
            if is_t:
                sgn = 1 if ci == 0 else -1
                for da in (0.5, -0.5): d.line([(xe, y), (xe + sgn * 24 * math.cos(da), y + 24 * math.sin(da))], fill=INK, width=3)
        bx = (pos[fr[0]][0] + pos[fr[0]][2] + off) if ci == 0 else (pos[fr[0]][0] - off)
        dashed(d, [(bx, lo), (bx, hi)])
        my = (lo + hi) / 2
        for lab, v in pos.items():
            if v[5] == ci and v[1] < my < v[1] + v[3]:
                gaps = [v[1] - VG / 2, v[1] + v[3] + VG / 2]
                cand = [g for g in gaps if lo < g < hi]
                if cand: my = min(cand, key=lambda g: abs(g - my))
                break
        labels.append((bx, my, "«" + kind + "»"))
    for lab, (ex, ey, ew, h, link, c) in pos.items():
        d.ellipse([ex, ey, ex + ew, ey + h], fill="white", outline=INK, width=3)
        d.multiline_text((ex + ew / 2, ey + h / 2), lab, font=f_uc, fill=INK, anchor="mm", align="center", spacing=LH - 31)
    for lx, ly, t in labels:
        bb = d.textbbox((lx, ly), t, font=f_rel, anchor="mm")
        d.rectangle([bb[0] - 5, bb[1] - 4, bb[2] + 5, bb[3] + 4], fill="white")
        d.text((lx, ly), t, font=f_rel, fill=INK, anchor="mm")
    for ax, ay in actors:
        d.ellipse([ax - 30, ay - 160, ax + 30, ay - 100], outline=INK, width=6, fill="white")
        d.line([(ax, ay - 100), (ax, ay + 10)], fill=INK, width=6)
        d.line([(ax - 62, ay - 36), (ax + 62, ay - 36)], fill=INK, width=6)
        d.line([(ax, ay + 10), (ax - 50, ay + 95)], fill=INK, width=6); d.line([(ax, ay + 10), (ax + 50, ay + 95)], fill=INK, width=6)
        tw = f_act.getlength(spec["actor"]); lx = min(max(ax, tw / 2 + 6), X0 - 50 - tw / 2) if ax < W / 2 else max(min(ax, W - tw / 2 - 6), X1 + 50 + tw / 2)
        d.text((lx, ay + 132), spec["actor"], font=f_act, fill=INK, anchor="mm")
    if note:
        ny = sys_y1 + 30
        d.rectangle([X0, ny, X1, H - 20], outline=PK, width=2, fill=(255, 252, 238))
        d.multiline_text((X0 + 22, (ny + H - 20) / 2), note, font=f_note, fill=INK, anchor="lm", spacing=8)
    img.save(out, dpi=(300, 300)); print(out, img.size, "%.1f x %.1f cm" % (W / 300 * 2.54, H / 300 * 2.54))
if __name__ == "__main__":
    render(json.load(open(sys.argv[1], encoding="utf8")), sys.argv[2])
