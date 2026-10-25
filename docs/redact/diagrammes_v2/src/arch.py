import math, html, sys
from PIL import Image, ImageDraw, ImageFont
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W=1795; INK=(20,20,20); TEAL=(0,92,110)
F={"t":ImageFont.truetype(B,34),"n":ImageFont.truetype(B,31),"p":ImageFont.truetype(B,27),"d":ImageFont.truetype(R,26),"c":ImageFont.truetype(B,24),"h":ImageFont.truetype(B,30)}
COL={"app":((226,237,250),(25,45,95)),"gw":((232,236,246),(25,45,95)),"infra":((255,250,235),(150,120,40)),"svc":((226,242,240),TEAL),"ext":((255,255,255),(110,110,110)),"db":((240,240,240),(80,80,80))}
nodes=[]; edges=[]
def box(id,x,y,w,h,title,sub="",kind="svc",port=""):
    nodes.append(dict(id=id,x=x,y=y,w=w,h=h,title=title,sub=sub,kind=kind,port=port))
def edge(a,b,label="",dashed=False,pa=None,pb=None):
    edges.append(dict(a=a,b=b,label=label,dashed=dashed,pa=pa,pb=pb))
box("app",380,30,1035,170,"Application mobile PsyConnect","Flutter — iOS et Android\nPatient · Psychologue · Administrateur","app")
box("gw",380,300,1035,120,"API Gateway","Spring Cloud Gateway — point d'entrée unique","gw","8080")
box("zip",30,290,300,140,"Zipkin","port 9411\ntraçage distribué","infra")
box("eur",1465,290,300,140,"Eureka Server","port 8761\nregistre des services","infra")
CX=30; CW=1735; CY=500; GAPX=26; BW=(CW-40-3*GAPX)//4; BH=225
box("ms",CX,CY,CW,580,"Microservices — conteneurs Docker Compose","", "ms")
row1=[("user","user-service","8082","profils, disponibilités,\nsolde, notes cliniques,\nsignalements, annonces"),
      ("appt","appointment-service","8083","rendez-vous, messagerie,\nquestionnaires,\néchéances automatiques"),
      ("pay","payment-service","8085","paiements, commissions,\nremboursements,\nretraits"),
      ("notif","notification-service","8086","notifications\nin-app, par profil\net par rôle")]
row2=[("auth","auth-service","8081","comptes, connexion,\njetons JWT, mot de\npasse oublié"),
      ("sess","session-service","8089","sessions et salons\nvidéo, clôture\nautomatique"),
      ("ai","ai-companion-service","8087","compagnon Xalaat,\ngarde-fou de crise"),
      ("ml","ml-service","8000","recommandations\nTF-IDF\n(Python / FastAPI)")]
for r,row in enumerate((row1,row2)):
    for i,(id,t,p,s) in enumerate(row):
        box(id,CX+20+i*(BW+GAPX),CY+70+r*(BH+40),BW,BH,t,s,"svc",p)
BY=CY+580+90
ext=[("mail","Mailpit","serveur d'e-mails\n(code de réinitialisation)","ext"),
     ("jit","Jitsi Meet","salons de\nvisioconférence","ext"),
     ("oll","Ollama","modèle qwen2.5:3b\nexécuté en local","ext"),
     ("pg","PostgreSQL","6 bases distinctes,\nune par service","db")]
for i,(id,t,s,k) in enumerate(ext):
    box(id,CX+20+i*(BW+GAPX),BY,BW,170,t,s,k,"5434" if id=="pg" else "")
edge("app","gw","HTTPS / REST + jeton JWT")
edge("gw","eur","",True)
edge("gw","ms","")
edge("ms","zip","traces",True)
edge("auth","mail","envoie le code")
edge("sess","jit","crée le salon")
edge("ai","oll","prompt")
edge("ms","pg","données",True)
NOTE="Les services s'appellent entre eux en REST ; Resilience4j protège ces appels (nouvelles tentatives, disjoncteur).\nChaque service vérifie lui-même le jeton JWT."
def node(i): return next(n for n in nodes if n["id"]==i)
def render(out):
    H=BY+170+40+120
    img=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(img)
    for n in nodes:
        x,y,w,h=n["x"],n["y"],n["w"],n["h"]
        if n["kind"]=="ms":
            d.rounded_rectangle([x,y,x+w,y+h],radius=18,fill=(247,250,253),outline=(120,135,160),width=4)
            d.text((x+24,y+20),n["title"],font=F["h"],fill=(25,45,95)); continue
        fill,stroke=COL[n["kind"]]
        if n["kind"]=="db":
            e=36; d.rectangle([x,y+e/2,x+w,y+h-e/2],fill=fill); d.ellipse([x,y+h-e,x+w,y+h],fill=fill,outline=stroke,width=3)
            d.line([(x,y+e/2),(x,y+h-e/2)],fill=stroke,width=3); d.line([(x+w,y+e/2),(x+w,y+h-e/2)],fill=stroke,width=3)
            d.rectangle([x+3,y+h-e,x+w-3,y+h-e/2],fill=fill); d.arc([x,y+h-e,x+w,y+h],0,180,fill=stroke,width=3)
            d.ellipse([x,y,x+w,y+e],fill=fill,outline=stroke,width=3); ty=y+e+8
        else:
            d.rounded_rectangle([x,y,x+w,y+h],radius=16,fill=fill,outline=stroke,width=4 if n["kind"] in("app","gw","svc") else 3); ty=y+16
        t=n["title"]+(f"  ({n['port']})" if n["port"] and n["kind"]!="svc" else "")
        fnt=F["t"] if n["kind"] in("app","gw") else F["n"]
        d.text((x+w/2,ty),t,font=fnt,fill=INK,anchor="ma")
        yy=ty+46
        if n["kind"]=="svc": d.text((x+w/2,yy),"port "+n["port"],font=F["p"],fill=TEAL,anchor="ma"); yy+=40
        d.multiline_text((x+w/2,yy),n["sub"],font=F["d"],fill=INK,anchor="ma",align="center",spacing=6)
    def arrow(p,q,dashed,label):
        if dashed:
            L=math.hypot(q[0]-p[0],q[1]-p[1]); k=max(1,int(L//16))
            for j in range(0,k,2):
                a,b=j/k,min(1,(j+1)/k); d.line([(p[0]+(q[0]-p[0])*a,p[1]+(q[1]-p[1])*a),(p[0]+(q[0]-p[0])*b,p[1]+(q[1]-p[1])*b)],fill=INK,width=3)
        else: d.line([p,q],fill=INK,width=4)
        ang=math.atan2(q[1]-p[1],q[0]-p[0])
        d.polygon([q,(q[0]-24*math.cos(ang-0.4),q[1]-24*math.sin(ang-0.4)),(q[0]-24*math.cos(ang+0.4),q[1]-24*math.sin(ang+0.4))],fill=INK)
        if label:
            mx,my=(p[0]+q[0])/2,(p[1]+q[1])/2
            bb=d.textbbox((mx+14,my),label,font=F["c"],anchor="lm"); d.rectangle([bb[0]-4,bb[1]-3,bb[2]+4,bb[3]+3],fill="white")
            d.text((mx+14,my),label,font=F["c"],fill=INK,anchor="lm")
    for e in edges:
        a,b=node(e["a"]),node(e["b"])
        if abs((a["y"]+a["h"]/2)-(b["y"]+b["h"]/2))<40 and e["a"]!="zip":
            p=(a["x"]+a["w"],a["y"]+a["h"]/2); q=(b["x"],b["y"]+b["h"]/2)
            arrow(p,q,e["dashed"],""); 
            if e["label"]:
                bb=d.textbbox(((p[0]+q[0])/2,p[1]-10),e["label"],font=F["c"],anchor="mb"); d.rectangle([bb[0]-4,bb[1]-3,bb[2]+4,bb[3]+3],fill="white"); d.text(((p[0]+q[0])/2,p[1]-10),e["label"],font=F["c"],fill=INK,anchor="mb")
        else:
            x=a["x"]+a["w"]/2 if e["a"] not in("ms",) else (b["x"]+b["w"]/2)
            if e["a"]=="gw": x=a["x"]+a["w"]/2
            if a["y"]>b["y"]: p=(x,a["y"]); q=(x,b["y"]+b["h"])
            else: p=(x,a["y"]+a["h"]); q=(x,b["y"])
            arrow(p,q,e["dashed"],e["label"])
    ny=BY+170+40
    d.rectangle([CX,ny,CX+CW,ny+100],fill=(255,252,238),outline=(120,135,160),width=2)
    d.multiline_text((CX+20,ny+50),NOTE,font=ImageFont.truetype(R,27),fill=INK,anchor="lm",spacing=8)
    img.save(out,dpi=(300,300)); print(out,img.size)
def drawio(out):
    S=0.5; cells=['<mxCell id="0"/>','<mxCell id="1" parent="0"/>']
    hx=lambda c:"#%02X%02X%02X"%c
    for n in nodes:
        k=n["kind"]
        if k=="ms": st="rounded=1;arcSize=3;whiteSpace=wrap;html=1;fillColor=#F7FAFD;strokeColor=#7887A0;strokeWidth=2;verticalAlign=top;align=left;spacingLeft=10;fontStyle=1;fontSize=15;fontColor=#192D5F;"; v=n["title"]
        else:
            fill,stroke=COL[k]
            shape="shape=cylinder3;boundedLbl=1;size=10;" if k=="db" else "rounded=1;arcSize=10;"
            st=f"{shape}whiteSpace=wrap;html=1;fillColor={hx(fill)};strokeColor={hx(stroke)};strokeWidth=2;fontSize=12;verticalAlign=top;"
            port=(f"<br><font color='#005C6E'><b>port {n['port']}</b></font>" if k=="svc" else (f" ({n['port']})" if n["port"] else ""))
            v=f"<b style='font-size:15px'>{html.escape(n['title'])}</b>{port}<br>"+html.escape(n["sub"]).replace("\n","<br>")
        cells.append(f'<mxCell id="{n["id"]}" value="{html.escape(v,quote=True)}" style="{st}" vertex="1" parent="1"><mxGeometry x="{n["x"]*S}" y="{n["y"]*S}" width="{n["w"]*S}" height="{n["h"]*S}" as="geometry"/></mxCell>')
    for i,e in enumerate(edges):
        st="html=1;endArrow=block;endFill=1;strokeWidth=2;fontStyle=1;fontSize=11;labelBackgroundColor=#FFFFFF;"+("dashed=1;" if e["dashed"] else "")
        cells.append(f'<mxCell id="e{i}" value="{html.escape(e["label"])}" style="{st}" edge="1" parent="1" source="{e["a"]}" target="{e["b"]}"><mxGeometry relative="1" as="geometry"/></mxCell>')
    ny=(BY+170+40)*S
    cells.append(f'<mxCell id="note" value="{html.escape(NOTE.replace(chr(10),"<br>"),quote=True)}" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFCEE;strokeColor=#7887A0;align=left;spacingLeft=8;fontSize=12;" vertex="1" parent="1"><mxGeometry x="{CX*S}" y="{ny}" width="{CW*S}" height="50" as="geometry"/></mxCell>')
    open(out,"w",encoding="utf8").write('<mxfile host="app.diagrams.net"><diagram id="arch" name="Architecture"><mxGraphModel grid="1" gridSize="10" guides="1" connect="1" arrows="1" page="1" pageWidth="900" pageHeight="1000"><root>'+"".join(cells)+'</root></mxGraphModel></diagram></mxfile>')
render(sys.argv[1]); drawio(sys.argv[2])
