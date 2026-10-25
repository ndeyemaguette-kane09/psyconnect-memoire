import json, sys, subprocess
from html import escape

FONT = "DejaVu Sans"
FS = 9

def node(c):
    svc = f'<BR/><FONT POINT-SIZE="{FS-1.5}" COLOR="#2E4D8A">«{escape(c["service"])}»</FONT>' if c.get("service") else ""
    rows = [f'<TR><TD BGCOLOR="#E8EEF6" BORDER="1" SIDES="B"><FONT POINT-SIZE="{FS+1}"><B>{escape(c["name"])}</B></FONT>{svc}</TD></TR>']
    if c.get("stub"):
        rows.append(f'<TR><TD ALIGN="LEFT" BALIGN="LEFT"><FONT POINT-SIZE="{FS-1}" COLOR="#555555"><I>{escape(c["stub"])}</I></FONT></TD></TR>')
    else:
        body = "<BR ALIGN=\"LEFT\"/>".join(escape(a) for a in c["attrs"]) + '<BR ALIGN="LEFT"/>'
        rows.append(f'<TR><TD ALIGN="LEFT" BALIGN="LEFT">{body}</TD></TR>')
    color = "#888888" if c.get("stub") else "#222222"
    return f'"{c["name"]}" [label=<<TABLE BORDER="1" COLOR="{color}" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4" BGCOLOR="white">{"".join(rows)}</TABLE>>];'

def build(spec):
    out = ["digraph G {", f'graph [rankdir={spec.get("rankdir","TB")}, fontname="{FONT}", fontsize={FS+1}, nodesep={spec.get("nodesep",0.25)}, ranksep={spec.get("ranksep",0.45)}, splines={spec.get("splines","ortho")}, pad=0.05, newrank=true];',
           f'node [shape=plaintext, fontname="{FONT}", fontsize={FS}, margin=0];',
           f'edge [fontname="{FONT}", fontsize={FS-1}, arrowsize=0.7, color="#333333"];']
    for i, cl in enumerate(spec.get("clusters", [])):
        out.append(f'subgraph cluster_{i} {{ label=<<B>{escape(cl["label"])}</B>>; labeljust=l; style="rounded,dashed"; color="#9AA7B8"; fontcolor="#2E4D8A"; margin=10;')
        for c in cl["classes"]:
            out.append(node(c))
        out.append("}")
    for c in spec.get("free", []):
        out.append(node(c))
    for e in spec["edges"]:
        a, b, kind = e[0], e[1], e[2]
        attrs = []
        if kind == "assoc":
            attrs.append('dir=none')
        elif kind == "invis":
            out.append(f'"{a}" -> "{b}" [style=invis];'); continue
        elif kind == "refback":
            attrs += ['style=dashed', 'dir=back', 'arrowtail=vee']
        elif kind == "use":
            attrs += ['style=dashed', 'arrowhead=vee', 'xlabel=" «utilise» "']
        elif kind == "ref":
            attrs += ['style=dashed', 'arrowhead=vee']
        if len(e) > 3 and e[3]: attrs.append(f'taillabel=" {e[3]} "')
        if len(e) > 4 and e[4]: attrs.append(f'headlabel=" {e[4]} "')
        if len(e) > 5 and e[5]: attrs.append(f'xlabel=" {e[5]} "')
        if len(e) > 6 and e[6] == "noconstraint": attrs.append("constraint=false")
        attrs.append('labeldistance=1.6')
        out.append(f'"{a}" -> "{b}" [{", ".join(attrs)}];')
    for r in spec.get("ranks", []):
        out.append("{rank=same; " + " ".join(f'"{x}";' for x in r) + "}")
    out.append("}")
    return "\n".join(out)

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf8"))
    dot = build(spec)
    open(sys.argv[1].replace(".json", ".dot"), "w").write(dot)
    subprocess.run(["dot", "-Tpng", "-Gdpi=300", "-o", sys.argv[2]], input=dot.encode(), check=True)
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open(sys.argv[2]).convert("RGB")
    legend = []
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
    lh = 46; pad = 24
    W = max(im.size[0], 1795)
    out = Image.new("RGB", (W, im.size[1] + (pad * 3 + lh * len(legend) if legend else 0)), "white")
    out.paste(im, ((W - im.size[0]) // 2, 0))
    d = ImageDraw.Draw(out)
    y0 = im.size[1] + pad
    if legend:
        d.rectangle([10, y0, W - 10, y0 + pad + lh * len(legend)], outline=(150, 150, 150), width=2, fill=(255, 252, 238))
    for i, line in enumerate(legend):
        d.text((34, y0 + pad // 2 + i * lh + 4), line, font=f, fill=(34, 32, 28))
    out.save(sys.argv[2], dpi=(300, 300))
    im = out; w, h = im.size
    print(sys.argv[2], im.size, "%.1f x %.1f cm" % (w / 300 * 2.54, h / 300 * 2.54))
