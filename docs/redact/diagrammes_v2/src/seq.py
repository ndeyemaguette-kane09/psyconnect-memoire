import json, sys, math
from PIL import Image, ImageDraw, ImageFont
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FI = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"
f_head = ImageFont.truetype(FB, 36); f_sub = ImageFont.truetype(F, 28)
f_msg = ImageFont.truetype(F, 33); f_tag = ImageFont.truetype(FB, 30); f_guard = ImageFont.truetype(FI, 31); f_note = ImageFont.truetype(F, 31)
INK = (34, 32, 28); LINE = (60, 60, 60); HEAD = (232, 238, 246); ACC = (46, 77, 138); NOTE = (255, 250, 230)
W = 1795; LH = 40

def wrap(text, font, maxw):
    out = []
    for para in text.split("\n"):
        words = para.split(" "); cur = ""
        for w in words:
            t = (cur + " " + w).strip()
            if font.getlength(t) <= maxw or not cur: cur = t
            else: out.append(cur); cur = w
        out.append(cur)
    return out

class Seq:
    def __init__(self, spec):
        self.spec = spec
        ps = spec["participants"]; n = len(ps)
        m = spec.get("margin", 205 if len(spec["participants"]) < 6 else 175)
        self.xs = {p["id"]: int(m + i * (W - 2 * m) / (n - 1)) for i, p in enumerate(ps)}
        self.gap = (W - 2 * m) / (n - 1)
        self.ops = []; self.y = 0

    def layout(self, steps, depth=0):
        for s in steps:
            k = s["t"]
            if k in ("msg", "ret"):
                a, b = self.xs[s["from"]], self.xs[s["to"]]
                lines = wrap(s["text"], f_msg, max(abs(b - a) - 40, 330))
                self.y += 12 + len(lines) * LH
                self.ops.append((k, a, b, self.y, lines)); self.y += 30
            elif k == "self":
                a = self.xs[s["p"]]
                maxw = max(s.get("w", 0), self.gap - 70, 420)
                lines = wrap(s["text"], f_msg, maxw)
                h = max(56, len(lines) * LH + 16)
                self.y += 14
                self.ops.append(("self", a, a, self.y, lines, h)); self.y += h + 24
            elif k == "note":
                x0 = self.xs[s["from"]] - 60; x1 = self.xs[s["to"]] + 60
                lines = wrap(s["text"], f_note, x1 - x0 - 40)
                h = len(lines) * LH + 24
                self.y += 14
                self.ops.append(("note", x0, x1, self.y, lines, h)); self.y += h + 22
            elif k in ("alt", "opt", "loop"):
                x0 = self.xs[s.get("from", self.spec["participants"][0]["id"])] - 70 + depth * 14
                x1 = self.xs[s.get("to", self.spec["participants"][-1]["id"])] + 70 - depth * 14
                top = self.y + 10; self.y += 10
                seps = []
                for i, (guard, sub) in enumerate(s["ops"]):
                    if i: seps.append(self.y); 
                    gy = self.y + 14
                    self.ops.append(("guard", x0, x1, gy, guard, i == 0))
                    self.y += 64
                    self.layout(sub, depth + 1)
                    self.y += 6
                bot = self.y + 6; self.y += 22
                self.ops.append(("frag", x0, x1, top, bot, k, seps))

    def render(self, out):
        ps = self.spec["participants"]
        head_h = 118
        self.y = head_h + 30
        self.layout(self.spec["steps"])
        H = self.y + 40
        img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
        bw = min(self.gap - 24, 380)
        self.fh = f_head
        for sz in (36, 31, 28, 26):
            self.fh = ImageFont.truetype(FB, sz)
            if all(self.fh.getlength(p["label"]) + 24 <= bw for p in ps): break
        for p in ps:
            x = self.xs[p["id"]]
            d.line([(x, head_h), (x, H - 20)], fill=(150, 150, 150), width=3)
        for p in ps:
            x = self.xs[p["id"]]
            fh = self.fh
            w = max(bw, fh.getlength(p["label"]) + 24)
            d.rectangle([x - w / 2, 10, x + w / 2, head_h], fill=HEAD, outline=INK, width=3)
            if p.get("sub"):
                d.text((x, 48), p["label"], font=fh, fill=INK, anchor="mm")
                d.text((x, 90), p["sub"], font=f_sub, fill=ACC, anchor="mm")
            else:
                d.text((x, head_h // 2 + 6), p["label"], font=fh, fill=INK, anchor="mm")
        frags = [o for o in self.ops if o[0] == "frag"]
        for o in frags:
            _, x0, x1, top, bot, kind, seps = o
            d.rectangle([x0, top, x1, bot], outline=INK, width=3)
            tw = f_tag.getlength(kind) + 26
            d.polygon([(x0, top), (x0 + tw, top), (x0 + tw, top + 34), (x0 + tw - 14, top + 46), (x0, top + 46)], fill="white", outline=INK)
            d.text((x0 + 10, top + 22), kind, font=f_tag, fill=INK, anchor="lm")
            for sy in seps:
                for xx in range(int(x0), int(x1), 28):
                    d.line([(xx, sy), (min(xx + 15, x1), sy)], fill=INK, width=2)
        for o in self.ops:
            k = o[0]
            if k == "guard":
                _, x0, x1, gy, guard, first = o
                d.text((x0 + (f_tag.getlength("alt") + 46 if first else 16), gy + 16), "[" + guard + "]", font=f_guard, fill=INK, anchor="lm")
            elif k in ("msg", "ret"):
                _, a, b, y, lines = o
                cx = (a + b) / 2
                for i, l in enumerate(lines):
                    ty = y - 12 - (len(lines) - 1 - i) * LH
                    bb = d.textbbox((cx, ty), l, font=f_msg, anchor="mb")
                    d.rectangle([bb[0] - 6, bb[1] - 3, bb[2] + 6, bb[3] + 3], fill="white")
                    d.text((cx, ty), l, font=f_msg, fill=INK, anchor="mb")
                if k == "ret":
                    step = 20; L = abs(b - a); sgn = 1 if b > a else -1
                    for t in range(0, int(L), step * 2):
                        d.line([(a + sgn * t, y), (a + sgn * min(t + step, L), y)], fill=LINE, width=3)
                else:
                    d.line([(a, y), (b, y)], fill=LINE, width=3)
                sgn = 1 if b > a else -1
                if k == "ret":
                    d.line([(b, y), (b - sgn * 24, y - 12)], fill=LINE, width=3); d.line([(b, y), (b - sgn * 24, y + 12)], fill=LINE, width=3)
                else:
                    d.polygon([(b, y), (b - sgn * 26, y - 12), (b - sgn * 26, y + 12)], fill=LINE)
            elif k == "self":
                _, a, _, y, lines, h = o
                sg = -1 if a > W * 0.8 else 1
                d.line([(a, y), (a + sg * 50, y), (a + sg * 50, y + h), (a, y + h)], fill=LINE, width=3)
                d.polygon([(a, y + h), (a + sg * 24, y + h - 12), (a + sg * 24, y + h + 12)], fill=LINE)
                for i, l in enumerate(lines):
                    tx = a + sg * 64
                    bb = d.textbbox((tx, y + 8 + i * LH), l, font=f_msg, anchor="la" if sg > 0 else "ra")
                    d.rectangle([bb[0] - 4, bb[1] - 2, bb[2] + 4, bb[3] + 2], fill="white")
                    d.text((tx, y + 8 + i * LH), l, font=f_msg, fill=INK, anchor="la" if sg > 0 else "ra")
            elif k == "note":
                _, x0, x1, y, lines, h = o
                d.polygon([(x0, y), (x1 - 22, y), (x1, y + 22), (x1, y + h), (x0, y + h)], fill=NOTE, outline=(120, 120, 120))
                for i, l in enumerate(lines):
                    d.text((x0 + 20, y + 12 + i * LH), l, font=f_note, fill=INK, anchor="la")
        img.save(out, dpi=(300, 300))
        print(out, img.size, "%.1f x %.1f cm" % (W / 300 * 2.54, H / 300 * 2.54))

if __name__ == "__main__":
    Seq(json.load(open(sys.argv[1], encoding="utf8"))).render(sys.argv[2])
