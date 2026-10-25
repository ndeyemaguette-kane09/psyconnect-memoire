import json, sys
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
INK, LINE, FILL, GROUP_FILL, ACCENT = (34, 32, 28), (70, 70, 70), (244, 247, 251), (250, 250, 248), (46, 77, 138)

W = 1795
f_uc = ImageFont.truetype(BOLD, 38)
f_grp = ImageFont.truetype(BOLD, 40)
f_sys = ImageFont.truetype(BOLD, 42)
f_act = ImageFont.truetype(BOLD, 44)
f_note = ImageFont.truetype(FONT, 34)
f_rel = ImageFont.truetype(FONT, 32)

def render(spec, out):
    groups = spec["groups"]
    UC_H, UC_H2, UC_GAP, GRP_HEAD, GRP_PAD = 96, 132, 18, 74, 22
    sys_x0, sys_x1 = max(380, int(f_act.getlength(spec["actor"])) + 50), W - 14
    uc_w = spec.get("width", 960)
    uc_cx = (sys_x0 + sys_x1) // 2 + 20 + spec.get("shift", 0)
    y = 20
    sys_y0 = y
    y += 90
    layout = []
    for g in groups:
        gy0 = y
        y += GRP_HEAD
        items = []
        for it in g["items"]:
            label = it if isinstance(it, str) else it["label"]
            linked = True if isinstance(it, str) else it.get("actor", True)
            h = UC_H if "\n" not in label else UC_H2
            items.append((label, y, h, linked))
            y += h + UC_GAP
        y += GRP_PAD - UC_GAP
        layout.append((g["title"], gy0, y, items))
        y += 34
    sys_y1 = y - 10
    note = spec.get("note")
    H = sys_y1 + (150 if note else 30)
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    d.rectangle([sys_x0, sys_y0, sys_x1, sys_y1], outline=INK, width=4)
    d.text(((sys_x0 + sys_x1) // 2, sys_y0 + 46), "Système PsyConnect", font=f_sys, fill=INK, anchor="mm")

    ax, ay = max(180, int(f_act.getlength(spec["actor"]) / 2) + 14), (sys_y0 + sys_y1) // 2
    hand = (ax + 70, ay - 40)
    for title, gy0, gy1, items in layout:
        d.rounded_rectangle([sys_x0 + 40, gy0, sys_x1 - 40, gy1], radius=18, outline=(150, 150, 150), width=3, fill=GROUP_FILL)
        d.text((sys_x1 - 70, gy0 + 22), title, font=f_grp, fill=ACCENT, anchor="ra")
    for title, gy0, gy1, items in layout:
        for label, uy, h, linked in items:
            if not linked:
                continue
            d.line([hand, (uc_cx - uc_w // 2 + 4, uy + h // 2)], fill=LINE, width=3)
    pos = {}
    for title, gy0, gy1, items in layout:
        for label, uy, h, linked in items:
            pos[label] = (uy, h)
    rel_labels = []
    for rel in spec.get("relations", []):
        a, b, kind = rel[:3]; off = rel[3] if len(rel) > 3 else 90
        ya, ha = pos[a]; yb, hb = pos[b]
        xr = uc_cx + uc_w // 2
        pa = (xr, ya + ha // 2)
        pb = (xr, yb + hb // 2)
        bend = xr + off
        pts = [pa, (bend, pa[1]), (bend, pb[1]), pb]
        import math
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]; x1, y1 = pts[i + 1]
            L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L // 16))
            for k in range(0, n, 2):
                t0, t1 = k / n, min(1, (k + 1) / n)
                d.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)], fill=INK, width=3)
        x0, y0 = pts[-2]; x1, y1 = pts[-1]
        ang = math.atan2(y1 - y0, x1 - x0)
        for da in (2.6, -2.6):
            d.line([(x1, y1), (x1 + 26 * math.cos(ang + da), y1 + 26 * math.sin(ang + da))], fill=INK, width=3)
        rel_labels.append((bend + 12, (pa[1] + pb[1]) // 2, "«" + kind + "»"))
    for title, gy0, gy1, items in layout:
        for label, uy, h, linked in items:
            d.ellipse([uc_cx - uc_w // 2, uy, uc_cx + uc_w // 2, uy + h], fill=FILL, outline=INK, width=3)
            d.multiline_text((uc_cx, uy + h // 2), label, font=f_uc, fill=INK, anchor="mm", align="center", spacing=6)
    for lx, ly, lt in rel_labels:
        bb = d.textbbox((lx, ly), lt, font=f_rel, anchor="lm")
        d.rectangle([bb[0] - 6, bb[1] - 4, bb[2] + 6, bb[3] + 4], fill="white")
        d.text((lx, ly), lt, font=f_rel, fill=INK, anchor="lm")
    d.ellipse([ax - 34, ay - 170, ax + 34, ay - 102], outline=INK, width=6, fill="white")
    d.line([(ax, ay - 102), (ax, ay + 10)], fill=INK, width=6)
    d.line([(ax - 70, ay - 40), (ax + 70, ay - 40)], fill=INK, width=6)
    d.line([(ax, ay + 10), (ax - 55, ay + 100)], fill=INK, width=6)
    d.line([(ax, ay + 10), (ax + 55, ay + 100)], fill=INK, width=6)
    d.text((ax, ay + 140), spec["actor"], font=f_act, fill=INK, anchor="mm")

    if note:
        nx0, ny0 = sys_x0, sys_y1 + 30
        d.rectangle([nx0, ny0, sys_x1, ny0 + 100], outline=(150, 150, 150), width=2, fill=(255, 252, 238))
        d.multiline_text((nx0 + 24, ny0 + 50), note, font=f_note, fill=INK, anchor="lm", spacing=6)
    img.save(out, dpi=(300, 300))
    print(out, img.size, "%.1f x %.1f cm" % (W / 300 * 2.54, H / 300 * 2.54))

if __name__ == "__main__":
    render(json.load(open(sys.argv[1], encoding="utf8")), sys.argv[2])
