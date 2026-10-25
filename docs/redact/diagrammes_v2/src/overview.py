import subprocess
from html import escape
FONT="DejaVu Sans"
pk={
 "auth-service":["User","PasswordResetCode"],
 "user-service":["UserProfile","PatientProfile","PsychologistProfile","PsychologistAvailability","MedicalHistory","JournalEntry","WalletTransaction","ClinicalNote","PsyPatientLink","Review","PsychologistReport","SupportMessage","Broadcast"],
 "appointment-service":["Appointment","Questionnaire","SessionRecommendation","Conversation","Message"],
 "session-service":["Session"],
 "payment-service":["Payment","PsychologistWithdrawal","PlatformSettings"],
 "notification-service":["Notification"]}
deps=[("user-service","auth-service","authUserId"),
 ("appointment-service","user-service","patientId, psychologistId"),
 ("user-service","appointment-service","appointmentId\n(ClinicalNote)"),
 ("session-service","appointment-service","appointmentId"),
 ("session-service","user-service","emergencyPatientId,\nemergencyPsychologistId"),
 ("payment-service","appointment-service","appointmentId"),
 ("payment-service","user-service","patientId, psychologistId"),
 ("notification-service","user-service","userId")]
def node(name, classes):
    rows="".join(f'<TR><TD ALIGN="LEFT">{escape(c)}</TD></TR>' for c in classes)
    tab=f'<TR><TD ALIGN="LEFT" BGCOLOR="#E8EEF6" BORDER="1" SIDES="LTR"><B>{escape(name)}</B></TD><TD BORDER="0"></TD></TR>'
    body=f'<TR><TD COLSPAN="2" BORDER="1" BALIGN="LEFT"><TABLE BORDER="0" CELLPADDING="1" CELLSPACING="0">{rows}</TABLE></TD></TR>'
    return f'"{name}" [label=<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4" COLOR="#222222">{tab}{body}</TABLE>>];'
L=['digraph G {',f'graph [rankdir=TB, fontname="{FONT}", nodesep=0.35, ranksep=0.6, splines=spline, pad=0.05];',
   f'node [shape=plaintext, fontname="{FONT}", fontsize=10];',f'edge [fontname="{FONT}", fontsize=9, color="#333333", style=dashed, arrowhead=vee, arrowsize=0.8];']
for k,v in pk.items(): L.append(node(k,v))
for a,b,lab in deps:
    L.append(f'"{a}" -> "{b}" [label="{lab}"];')
L.append('{rank=min; "notification-service"; "session-service"; "payment-service";}')
L.append('{rank=same; "user-service"; "appointment-service";}')
L.append('{rank=max; "auth-service";}')
L.append('}')
dot="\n".join(L); open('overview.dot','w').write(dot)
subprocess.run(["dot","-Tpng","-Gdpi=300","-o","overview.png"],input=dot.encode(),check=True)
from PIL import Image; im=Image.open('overview.png'); print(im.size,"%.1f x %.1f cm"%(im.size[0]/300*2.54,im.size[1]/300*2.54))
