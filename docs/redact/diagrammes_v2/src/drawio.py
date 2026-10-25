import json, sys, html
import usecase2 as U
S = 0.5
def esc(t): return html.escape(t, quote=True).replace("\n", "&#xa;")
def layout(spec):
    U.AZ = max(195, int(U.f_act.getlength(spec["actor"])) + 70); U.X0, U.X1 = U.AZ, U.W - U.AZ
    U.PKW = (U.X1 - U.X0 - 40 - U.GAP) // 2
    U.COLS = [(U.X0 + 20, U.X0 + 20 + U.PKW), (U.X1 - 20 - U.PKW, U.X1 - 20)]
    U.EW = min(610, U.PKW - 74)
    pos = {}; boxes = []; ends = []
    top = 100
    for ci, col in enumerate(spec["columns"]):
        px0, px1 = U.COLS[ci]; ex0 = px0 + 22 if ci == 0 else px1 - 22 - U.EW; y = top
        for g in col:
            gy = y; y += U.HEAD
            for it in g["items"]:
                lab = it if isinstance(it, str) else it["label"]
                link = True if isinstance(it, str) else it.get("actor", True)
                h = U.eh(lab); pos[lab] = (ex0, y, U.EW, h, link, ci); y += h + U.VG
            y += U.PAD - U.VG; boxes.append((px0, gy, px1, y, g["title"])); y += 26
        ends.append(y - 26)
    return pos, boxes, max(ends) + 24
def page(spec, name, pid):
    pos, boxes, sys_y1 = layout(spec)
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    n = [2]
    def nid():
        n[0] += 1; return f"{pid}_{n[0]}"
    def v(style, x, y, w, h, value=""):
        i = nid(); cells.append(f'<mxCell id="{i}" value="{esc(value)}" style="{style}" vertex="1" parent="1"><mxGeometry x="{x*S:.1f}" y="{y*S:.1f}" width="{w*S:.1f}" height="{h*S:.1f}" as="geometry"/></mxCell>'); return i
    def e(style, s, t, value=""):
        i = nid(); cells.append(f'<mxCell id="{i}" value="{esc(value)}" style="{style}" edge="1" parent="1" source="{s}" target="{t}"><mxGeometry relative="1" as="geometry"/></mxCell>'); return i
    v("rounded=0;whiteSpace=wrap;html=1;fillColor=#E2EDFA;strokeColor=#141414;strokeWidth=3;verticalAlign=top;fontStyle=1;fontSize=21;spacingTop=4;", U.X0, 20, U.X1 - U.X0, sys_y1 - 20, "Système PsyConnect")
    for px0, gy, px1, gy1, t in boxes:
        v("rounded=1;arcSize=4;whiteSpace=wrap;html=1;fillColor=#F8FAFD;strokeColor=#7887A0;strokeWidth=1.5;verticalAlign=top;align=left;spacingLeft=8;fontStyle=1;fontSize=16;fontColor=#192D5F;", px0, gy, px1 - px0, gy1 - gy, t)
    ids = {}
    for lab, (ex, ey, ew, h, link, ci) in pos.items():
        ids[lab] = v("ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#141414;strokeWidth=1.5;fontStyle=1;fontSize=15;", ex, ey, ew, h, lab)
    for ci in range(len(spec["columns"])):
        ys = [p[1] + p[3] / 2 for p in pos.values() if p[5] == ci and p[4]]
        if not ys: continue
        ay = (min(ys) + max(ys)) / 2; ax = U.X0 - 112 if ci == 0 else U.X1 + 112
        a = v("shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;strokeWidth=3;fontStyle=1;fontSize=14;", ax - 62, ay - 160, 124, 255, spec["actor"])
        for lab, p in pos.items():
            if p[5] == ci and p[4]:
                side = "exitX=1;exitY=0.35;entryX=0;entryY=0.5;" if ci == 0 else "exitX=0;exitY=0.35;entryX=1;entryY=0.5;"
                e("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=none;strokeColor=#005C6E;strokeWidth=2;" + side, a, ids[lab])
    for rel in spec.get("relations", []):
        fr, to, kind = (rel["from"], rel["to"], rel["kind"]) if isinstance(rel, dict) else ([rel[0]], [rel[1]], rel[2])
        for a in fr:
            for b in to:
                ci = pos[a][5]
                side = "exitX=1;exitY=0.5;entryX=1;entryY=0.5;" if ci == 0 else "exitX=0;exitY=0.5;entryX=0;entryY=0.5;"
                e("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;endArrow=open;endSize=10;strokeWidth=1.5;fontStyle=1;fontSize=12;labelBackgroundColor=#FFFFFF;" + side, ids[a], ids[b], "«" + kind + "»")
    note = spec.get("note")
    if note:
        v("rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFCEE;strokeColor=#7887A0;align=left;spacingLeft=10;fontSize=13;", U.X0, sys_y1 + 30, U.X1 - U.X0, 150, note.replace("\n", " "))
    return f'<diagram id="{pid}" name="{esc(name)}"><mxGraphModel dx="1000" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="900" pageHeight="1400" math="0" shadow="0"><root>{"".join(cells)}</root></mxGraphModel></diagram>'
pages = [page(json.load(open(f"uc2_{k}.json", encoding="utf8")), t, k) for k, t in (("patient", "Patient"), ("psy", "Psychologue"), ("admin", "Administrateur"))]
open(sys.argv[1], "w", encoding="utf8").write('<mxfile host="app.diagrams.net">' + "".join(pages) + "</mxfile>")
print("ok")
