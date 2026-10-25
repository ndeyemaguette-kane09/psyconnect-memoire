import json, sys, math
from PIL import Image, ImageDraw, ImageFont
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FI = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"
f_act = ImageFont.truetype(F, 33); f_lane = ImageFont.truetype(FB, 36); f_g = ImageFont.truetype(FI, 30); f_dec = ImageFont.truetype(F, 29)
INK = (34, 32, 28); LINE = (60, 60, 60); FILL = (244, 247, 251); LANEH = (232, 238, 246)
W = 1795

def wrap(text, font, maxw):
    out = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split(" "):
            t = (cur + " " + w).strip()
            if font.getlength(t) <= maxw or not cur: cur = t
            else: out.append(cur); cur = w
        out.append(cur)
    return out

def render(spec, out):
    lanes = spec["lanes"]; n = len(lanes); lw = W / n
    ROW = spec.get("row", 175); TOP = 120
    nodes = {}
    for nd in spec["nodes"]:
        x = lw * nd["lane"] + lw / 2 + nd.get("dx", 0)
        y = TOP + 60 + nd["row"] * ROW
        t = nd["type"]
        if t in ("start", "end"): w = h = 56
        elif t in ("bstart", "bend"): w = h = 70; lines = wrap(nd.get("text",""), f_dec, 330)
        elif t == "timer": w = 60; h = 80; lines = wrap(nd.get("text",""), f_dec, 400)
        elif t == "gateway": w = h = 120; lines = wrap(nd.get("text",""), f_dec, 380)
        elif t == "decision":
            lines = wrap(nd["text"], f_dec, nd.get("tw", 250)); w = nd.get("w", 430); h = max(120, 44 * len(lines) + 70)
        elif t == "merge": w = h = 60; lines = []
        else:
            lines = wrap(nd["text"], f_act, nd.get("w", lw - 110) - 40); w = max(f_act.getlength(l) for l in lines) + 50; h = 44 * len(lines) + 34
        nodes[nd["id"]] = dict(nd, x=x, y=y, w=w, h=h, lines=lines if t not in ("start", "end") else [])
    H = int(max(v["y"] + v["h"] / 2 for v in nodes.values()) + 70)
    img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
    for i, name in enumerate(lanes):
        x0 = i * lw
        d.rectangle([x0, 0, x0 + lw, TOP], fill=LANEH, outline=INK, width=3)
        d.text((x0 + lw / 2, TOP / 2), name, font=f_lane, fill=INK, anchor="mm")
        d.rectangle([x0, TOP, x0 + lw, H - 2], outline=INK, width=3)
    def port(nd, side):
        x, y, w, h = nd["x"], nd["y"], nd["w"], nd["h"]
        return {"top": (x, y - h / 2), "bottom": (x, y + h / 2), "left": (x - w / 2, y), "right": (x + w / 2, y)}[side]
    labels = []
    for e in spec["edges"]:
        a, b = nodes[e["from"]], nodes[e["to"]]
        if "path" in e:
            s = port(a, e.get("out", "bottom")); t = port(b, e.get("in", "top"))
            pts = [s] + [tuple(p) if not isinstance(p, str) else None for p in []]
            pts = [s]
            for p in e["path"]:
                px = p[0] if p[0] is not None else pts[-1][0]
                py = p[1] if p[1] is not None else pts[-1][1]
                if isinstance(px, str): px = eval(px, {}, {"tx": t[0], "sx": s[0], "lw": lw})
                if isinstance(py, str): py = eval(py, {}, {"ty": t[1], "sy": s[1]})
                pts.append((px, py))
            pts.append(t)
        elif abs(a["x"] - b["x"]) < 2:
            pts = [port(a, "bottom"), port(b, "top")] if b["y"] > a["y"] else [port(a, "top"), port(b, "bottom")]
        elif abs(a["y"] - b["y"]) < 2:
            pts = [port(a, "right"), port(b, "left")] if b["x"] > a["x"] else [port(a, "left"), port(b, "right")]
        else:
            side = e.get("out", "right" if b["x"] > a["x"] else "left")
            s = port(a, side) if a["type"] == "decision" or e.get("out") else port(a, "bottom")
            t = port(b, "top")
            if s[1] == a["y"]:
                pts = [s, (t[0], s[1]), t]
            else:
                my = t[1] - 34
                pts = [s, (s[0], my), (t[0], my), t]
        d.line(pts, fill=LINE, width=3, joint="curve")
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        ang = math.atan2(y2 - y1, x2 - x1)
        d.polygon([(x2, y2), (x2 - 24 * math.cos(ang - 0.4), y2 - 24 * math.sin(ang - 0.4)), (x2 - 24 * math.cos(ang + 0.4), y2 - 24 * math.sin(ang + 0.4))], fill=LINE)
        if e.get("label"):
            (lx, ly), (mx, my2) = pts[0], pts[1]
            if abs(mx - lx) > abs(my2 - ly):
                labels.append(((lx + mx) / 2, ly - 6, "[" + e["label"] + "]", "mb"))
            else:
                labels.append((lx + 12, (ly + my2) / 2, "[" + e["label"] + "]", "lm"))
    for v in nodes.values():
        x, y, w, h, t = v["x"], v["y"], v["w"], v["h"], v["type"]
        if t == "start":
            d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=INK)
        elif t == "end":
            d.ellipse([x - 30, y - 30, x + 30, y + 30], outline=INK, width=4, fill="white"); d.ellipse([x - 18, y - 18, x + 18, y + 18], fill=INK)
        elif t == "timer":
            d.polygon([(x - 30, y - 40), (x + 30, y - 40), (x - 30, y + 40), (x + 30, y + 40)], outline=INK, fill="white", width=3)
            d.line([(x - 30, y - 40), (x + 30, y - 40)], fill=INK, width=4); d.line([(x - 30, y + 40), (x + 30, y + 40)], fill=INK, width=4)
            d.line([(x - 30, y - 40), (x + 30, y + 40)], fill=INK, width=3); d.line([(x + 30, y - 40), (x - 30, y + 40)], fill=INK, width=3)
            for i, l in enumerate(v["lines"]):
                d.text((x + 50, y - (len(v["lines"]) - 1) * 18 + i * 36), l, font=f_dec, fill=INK, anchor="lm")
        elif t in ("bstart", "bend"):
            wd = 3 if t == "bstart" else 9
            d.ellipse([x - 35, y - 35, x + 35, y + 35], outline=INK, width=wd, fill="white")
            for i, l in enumerate(v["lines"]):
                if v.get("tpos") == "below":
                    d.text((x, y + 50 + i * 36), l, font=f_dec, fill=INK, anchor="mt")
                else:
                    d.text((x + 50, y - (len(v["lines"]) - 1) * 18 + i * 36), l, font=f_dec, fill=INK, anchor="lm")
        elif t == "gateway":
            d.polygon([(x, y - 60), (x + 60, y), (x, y + 60), (x - 60, y)], fill="white", outline=INK, width=3)
            d.line([(x - 22, y - 22), (x + 22, y + 22)], fill=INK, width=5); d.line([(x - 22, y + 22), (x + 22, y - 22)], fill=INK, width=5)
            side = v.get("tside", "left")
            for i, l in enumerate(v["lines"]):
                if side == "left":
                    d.text((x - 72, y - 40 - (len(v["lines"]) - 1 - i) * 36), l, font=f_dec, fill=INK, anchor="rb")
                else:
                    d.text((x + 72, y - 40 - (len(v["lines"]) - 1 - i) * 36), l, font=f_dec, fill=INK, anchor="lb")
        elif t in ("decision", "merge"):
            d.polygon([(x, y - h / 2), (x + w / 2, y), (x, y + h / 2), (x - w / 2, y)], fill="white", outline=INK, width=3)
            for i, l in enumerate(v["lines"]):
                d.text((x, y - (len(v["lines"]) - 1) * 22 + i * 44), l, font=f_dec, fill=INK, anchor="mm")
        else:
            d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], radius=28, fill=FILL, outline=INK, width=3)
            for i, l in enumerate(v["lines"]):
                d.text((x, y - (len(v["lines"]) - 1) * 22 + i * 44), l, font=f_act, fill=INK, anchor="mm")
    for lx, ly, txt, anc in labels:
        bb = d.textbbox((lx, ly), txt, font=f_g, anchor=anc)
        d.rectangle([bb[0] - 4, bb[1] - 2, bb[2] + 4, bb[3] + 2], fill="white")
        d.text((lx, ly), txt, font=f_g, fill=INK, anchor=anc)
    img.save(out, dpi=(300, 300))
    print(out, img.size, "%.1f x %.1f cm" % (W / 300 * 2.54, H / 300 * 2.54))

if __name__ == "__main__":
    render(json.load(open(sys.argv[1], encoding="utf8")), sys.argv[2])
