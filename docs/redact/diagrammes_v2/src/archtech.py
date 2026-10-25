import math, html, sys
from PIL import Image, ImageDraw, ImageFont
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W=1795; INK=(20,20,20)
F={"t":ImageFont.truetype(B,32),"n":ImageFont.truetype(B,28),"d":ImageFont.truetype(R,24),"c":ImageFont.truetype(B,23),"h":ImageFont.truetype(B,29)}
COL={"client":((226,237,250),(25,45,95)),"infra":((255,250,235),(150,120,40)),"svc":((226,242,240),(0,92,110)),"py":((236,240,252),(60,70,150)),"ext":((255,255,255),(110,110,110)),"db":((240,240,240),(80,80,80)),"layer":((255,255,255),(0,92,110))}
nodes=[]; edges=[]; frames=[]
def box(id,x,y,w,h,title,sub="",kind="svc"): nodes.append(dict(id=id,x=x,y=y,w=w,h=h,title=title,sub=sub,kind=kind))
def frame(id,x,y,w,h,title,fill=(247,250,253)): frames.append(dict(id=id,x=x,y=y,w=w,h=h,title=title,fill=fill))
def edge(a,b,label="",dashed=False,side=None): edges.append(dict(a=a,b=b,label=label,dashed=dashed,side=side))
frame("phone",30,20,1180,250,"Smartphone (iOS / Android)",(240,245,252))
box("app",60,80,1120,165,"Application Flutter (Dart)","Provider (gestion d'état) · http (REST / JSON)\nJitsi Meet SDK (vidéo) · jeton JWT conservé sur l'appareil","client")
box("jitsi",1290,60,475,170,"Serveur Jitsi public","meet.ffmuc.net\nsalons vidéo (WebRTC)","ext")
frame("docker",30,380,1735,800,"Serveur — Docker Compose")
box("gw",60,450,820,140,"api-gateway  (8080)","Spring Cloud Gateway — route vers le bon service","infra")
box("eur",910,450,410,140,"eureka-server  (8761)","Spring Cloud Netflix Eureka","infra")
box("zip",1350,450,385,140,"zipkin  (9411)","traces Micrometer Tracing","infra")
SW=(1675-6*22)//7
svcs=[("auth","auth","8081"),("user","user","8082"),("appt","appointment","8083"),("sess","session","8089"),("pay","payment","8085"),("notif","notification","8086"),("ai","ai-companion","8087")]
for i,(id,n,p) in enumerate(svcs): box(id,60+i*(SW+22),660,SW,130,n,p,"svc")
box("stack",60,815,1675,95,"Socle commun des 7 microservices Java (nom-service)","Spring Boot 3.5 · Java 17 · Spring Security (filtre JWT) · Spring Data JPA / Hibernate · Resilience4j · Micrometer Tracing","svc")
box("ml",60,960,520,150,"ml-service  (8000)","Python 3 · FastAPI · NumPy\n(TF-IDF, similarité cosinus)","py")
box("mail",610,960,420,150,"mailpit  (1025 / 8025)","serveur SMTP de développement","ext")
box("pg",1060,960,630,190,"postgres  (5434)","PostgreSQL 16 — 6 bases :\nauth, user, appointment, session,\npayment, notification","db")
box("oll",1060,1240,705,140,"Ollama sur la machine hôte  (11434)","modèle qwen2.5:3b, appelé par Spring AI","ext")
LX=60; LW=950
frame("layers",LX-30,1240,LW+60,560,"Organisation interne d'un service Spring Boot",(250,252,250))
layers=[("ctl","controller","points d'accès REST, DTO"),("srv","service","règles métier"),("rep","repository","Spring Data JPA"),("ent","entity","classes JPA ↔ tables")]
for i,(id,t,s) in enumerate(layers): box(id,LX+30,1305+i*118,560,92,t,s,"layer")
box("sec",LX+620,1305,330,92,"security","filtre JWT","layer")
box("cli",LX+620,1423,330,120,"client","appels REST\n+ Resilience4j","layer")
edge("app","gw","HTTPS · REST/JSON · Bearer JWT")
edge("app","jitsi","WebRTC")
edge("gw","eur","",True)
edge("ctl","srv"); edge("srv","rep"); edge("rep","ent")
NOTE="Chaque service s'enregistre auprès d'Eureka et envoie ses traces à Zipkin. Les 7 services Java partagent le même socle\ntechnique ; ai-companion-service n'a pas de base de données, ml-service non plus."
def node(i): return next(n for n in nodes+frames if n["id"]==i)
def render(out):
    H=1830
    img=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(img)
    for f in frames:
        d.rounded_rectangle([f["x"],f["y"],f["x"]+f["w"],f["y"]+f["h"]],radius=18,fill=f["fill"],outline=(120,135,160),width=4)
        d.text((f["x"]+22,f["y"]+16),f["title"],font=F["h"],fill=(25,45,95))
    def arrow(p,q,dashed=False,label="",lside="r"):
        if dashed:
            L=math.hypot(q[0]-p[0],q[1]-p[1]); k=max(1,int(L//16))
            for j in range(0,k,2):
                a,b=j/k,min(1,(j+1)/k); d.line([(p[0]+(q[0]-p[0])*a,p[1]+(q[1]-p[1])*a),(p[0]+(q[0]-p[0])*b,p[1]+(q[1]-p[1])*b)],fill=INK,width=3)
        else: d.line([p,q],fill=INK,width=4)
        ang=math.atan2(q[1]-p[1],q[0]-p[0])
        d.polygon([q,(q[0]-22*math.cos(ang-0.4),q[1]-22*math.sin(ang-0.4)),(q[0]-22*math.cos(ang+0.4),q[1]-22*math.sin(ang+0.4))],fill=INK)
        if label:
            mx,my=(p[0]+q[0])/2,(p[1]+q[1])/2
            anc="lm" if lside=="r" else "mb"; pos=(mx+14,my) if lside=="r" else (mx,my-8)
            bb=d.textbbox(pos,label,font=F["c"],anchor=anc); d.rectangle([bb[0]-4,bb[1]-3,bb[2]+4,bb[3]+3],fill="white"); d.text(pos,label,font=F["c"],fill=INK,anchor=anc)
    gw=node("gw"); app=node("app")
    arrow((700,app["y"]+app["h"]),(700,gw["y"]))
    lab="HTTPS · REST / JSON · Authorization: Bearer JWT"; bb=d.textbbox((716,318),lab,font=F["c"],anchor="lm"); d.rectangle([bb[0]-4,bb[1]-3,bb[2]+4,bb[3]+3],fill="white"); d.text((716,318),lab,font=F["c"],fill=INK,anchor="lm")
    arrow((app["x"]+app["w"],app["y"]+app["h"]/2),(node("jitsi")["x"],app["y"]+app["h"]/2),label="WebRTC",lside="t")
    arrow((gw["x"]+gw["w"],gw["y"]+gw["h"]/2),(node("eur")["x"],gw["y"]+gw["h"]/2),True)
    arrow((700,gw["y"]+gw["h"]),(700,660))
    ai=node("ai"); oll=node("oll")
    pts=[(ai["x"]+ai["w"],ai["y"]+ai["h"]/2),(1748,ai["y"]+ai["h"]/2),(1748,oll["y"])]
    for k in range(len(pts)-2): 
        p,q=pts[k],pts[k+1]
        L=math.hypot(q[0]-p[0],q[1]-p[1]); n=max(1,int(L//16))
        for j in range(0,n,2):
            a,b=j/n,min(1,(j+1)/n); d.line([(p[0]+(q[0]-p[0])*a,p[1]+(q[1]-p[1])*a),(p[0]+(q[0]-p[0])*b,p[1]+(q[1]-p[1])*b)],fill=INK,width=3)
    arrow(pts[-2],pts[-1],True)
    bb=d.textbbox((1740,1205),"HTTP (Spring AI)",font=F["c"],anchor="rm"); d.rectangle([bb[0]-4,bb[1]-3,bb[2]+4,bb[3]+3],fill="white"); d.text((1740,1205),"HTTP (Spring AI)",font=F["c"],fill=INK,anchor="rm")
    pg=node("pg"); arrow((1375,903),(1375,pg["y"]),True,"JDBC")
    for a,b in (("ctl","srv"),("srv","rep"),("rep","ent")):
        A,Bn=node(a),node(b); arrow((A["x"]+A["w"]/2,A["y"]+A["h"]),(Bn["x"]+Bn["w"]/2,Bn["y"]))
    for n in nodes:
        x,y,w,h=n["x"],n["y"],n["w"],n["h"]; fill,stroke=COL[n["kind"]]
        if n["kind"]=="db":
            e=34; d.rectangle([x,y+e/2,x+w,y+h-e/2],fill=fill); d.line([(x,y+e/2),(x,y+h-e/2)],fill=stroke,width=3); d.line([(x+w,y+e/2),(x+w,y+h-e/2)],fill=stroke,width=3)
            d.ellipse([x,y+h-e,x+w,y+h],fill=fill,outline=stroke,width=3); d.rectangle([x+3,y+h-e,x+w-3,y+h-e/2],fill=fill); d.arc([x,y+h-e,x+w,y+h],0,180,fill=stroke,width=3); d.ellipse([x,y,x+w,y+e],fill=fill,outline=stroke,width=3); ty=y+e+6
        else:
            d.rounded_rectangle([x,y,x+w,y+h],radius=14,fill=fill,outline=stroke,width=3); ty=y+14
        fnt=F["t"] if n["id"] in("app",) else F["n"]
        d.text((x+w/2,ty),n["title"],font=fnt,fill=INK,anchor="ma")
        if n["kind"]=="svc" and n["id"]!="stack":
            d.text((x+w/2,ty+50),"port "+n["sub"],font=F["c"],fill=(0,92,110),anchor="ma")
        else:
            d.multiline_text((x+w/2,ty+42),n["sub"],font=F["d"],fill=INK,anchor="ma",align="center",spacing=6)
    ny=H-80
    d.multiline_text((1100,1700),"",font=F["d"])
    d.rectangle([1060,1420,1765,1700],fill=(255,252,238),outline=(120,135,160),width=2)
    txt="• Chaque service s'enregistre\n  auprès d'Eureka et envoie\n  ses traces à Zipkin.\n• Les 7 services Java partagent\n  le même socle technique.\n• ai-companion-service et\n  ml-service n'ont pas de base."
    d.multiline_text((1085,1445),txt,font=ImageFont.truetype(R,26),fill=INK,spacing=10)
    img.save(out,dpi=(300,300)); print(out,img.size)
render(sys.argv[1])
def drawio(out):
    S=0.5; hx=lambda c:"#%02X%02X%02X"%c
    cells=['<mxCell id="0"/>','<mxCell id="1" parent="0"/>']
    for f in frames:
        st=f"rounded=1;arcSize=3;whiteSpace=wrap;html=1;fillColor={hx(f['fill'])};strokeColor=#7887A0;strokeWidth=2;verticalAlign=top;align=left;spacingLeft=10;fontStyle=1;fontSize=15;fontColor=#192D5F;"
        cells.append(f'<mxCell id="{f["id"]}" value="{html.escape(f["title"])}" style="{st}" vertex="1" parent="1"><mxGeometry x="{f["x"]*S}" y="{f["y"]*S}" width="{f["w"]*S}" height="{f["h"]*S}" as="geometry"/></mxCell>')
    for n in nodes:
        fill,stroke=COL[n["kind"]]
        shape="shape=cylinder3;boundedLbl=1;size=10;" if n["kind"]=="db" else "rounded=1;arcSize=10;"
        sub=("port "+n["sub"]) if (n["kind"]=="svc" and n["id"]!="stack") else n["sub"]
        title=n["title"]+("-service" if (n["kind"]=="svc" and n["id"]!="stack") else "")
        v=f"<b style='font-size:14px'>{html.escape(title)}</b><br>"+html.escape(sub).replace("\n","<br>")
        st=f"{shape}whiteSpace=wrap;html=1;fillColor={hx(fill)};strokeColor={hx(stroke)};strokeWidth=2;fontSize=11;verticalAlign=top;"
        cells.append(f'<mxCell id="{n["id"]}" value="{html.escape(v,quote=True)}" style="{st}" vertex="1" parent="1"><mxGeometry x="{n["x"]*S}" y="{n["y"]*S}" width="{n["w"]*S}" height="{n["h"]*S}" as="geometry"/></mxCell>')
    E=[("app","gw","HTTPS · REST/JSON · Bearer JWT",0),("app","jitsi","WebRTC",0),("gw","eur","",1),("gw","appt","",0),("ai","oll","HTTP (Spring AI)",1),("stack","pg","JDBC",1),("ctl","srv","",0),("srv","rep","",0),("rep","ent","",0)]
    for i,(a,b,l,dsh) in enumerate(E):
        st="edgeStyle=orthogonalEdgeStyle;html=1;endArrow=block;endFill=1;strokeWidth=2;fontStyle=1;fontSize=11;labelBackgroundColor=#FFFFFF;"+("dashed=1;" if dsh else "")
        cells.append(f'<mxCell id="e{i}" value="{html.escape(l)}" style="{st}" edge="1" parent="1" source="{a}" target="{b}"><mxGeometry relative="1" as="geometry"/></mxCell>')
    txt="• Chaque service s'enregistre auprès d'Eureka et envoie ses traces à Zipkin.<br>• Les 7 services Java partagent le même socle technique.<br>• ai-companion-service et ml-service n'ont pas de base."
    cells.append(f'<mxCell id="note" value="{html.escape(txt,quote=True)}" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFCEE;strokeColor=#7887A0;align=left;spacingLeft=8;fontSize=12;" vertex="1" parent="1"><mxGeometry x="530" y="710" width="352" height="140" as="geometry"/></mxCell>')
    open(out,"w",encoding="utf8").write('<mxfile host="app.diagrams.net"><diagram id="archtech" name="Architecture technique"><mxGraphModel grid="1" gridSize="10" guides="1" connect="1" arrows="1" page="1" pageWidth="900" pageHeight="950"><root>'+"".join(cells)+'</root></mxGraphModel></diagram></mxfile>')
    print(out)
if len(sys.argv)>2: drawio(sys.argv[2])
