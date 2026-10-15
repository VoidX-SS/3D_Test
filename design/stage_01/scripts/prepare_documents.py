"""Vietnamese review packet; measured design dimensions, not inferred AI dimensions."""
from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color

OUT=Path(__file__).resolve().parents[1]
assets=json.loads((OUT/'measurements'/'components.json').read_text())['assets']
names=['Đế vuông','Núi — tầng 1','Núi — tầng 2','Núi — tầng 3','Cụm đỉnh núi','Ngựa đứng thư thái','Ngựa gặm cỏ','Ngựa uống nước','Cây tùng','Cây tán rộng','Đĩa mặt trời','Ngọc / mặt trăng','Cụm mây','Cụm cỏ','Cành lá','Mặt suối thấp','Thác thấp','Thác giữa','Thác trên','Hoa và rêu']
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
boldpath='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('DV',fontpath))
pdfmetrics.registerFont(TTFont('DVB',boldpath))

# Legible contact sheet: one isolated Blender render per cell, no invented views.
im=Image.new('RGB',(2000,2670),'#eeeade'); d=ImageDraw.Draw(im)
f=ImageFont.truetype(fontpath,26); fb=ImageFont.truetype(boldpath,44)
d.text((55,35),'NƯƠNG DÒNG BÌNH YÊN',font=fb,fill='#243f34')
d.text((55,100),'Giai đoạn 01 · 20 thành phần riêng · Kích thước X × Y × Z (cm)',font=f,fill='#4a5b4c')
for i,a in enumerate(assets):
    col=i%4; row=i//4; x=35+col*493; y=170+row*490
    thumb=Image.open(OUT/'renders'/(a['id']+'.png')).convert('RGB')
    thumb.thumbnail((460,380),Image.Resampling.LANCZOS)
    im.paste(thumb,(x+(460-thumb.width)//2,y+(380-thumb.height)//2))
    d.text((x+10,y+388),a['id']+'  '+names[i],font=f,fill='#203c30')
    dims=' × '.join(f'{v:g}' for v in a['actual_cm'])+' cm'
    d.text((x+10,y+426),dims,font=f,fill='#4e5e50')
d.text((55,2630),'Bộ mẫu rời để duyệt tỉ lệ — chưa ghép cảnh, chưa phải bản thi công.',font=f,fill='#4e5e50')
im.save(OUT/'renders'/'00_component_catalog.png')

pdf=canvas.Canvas(str(OUT/'Phieu_thiet_ke_giai_doan_01.pdf'),pagesize=(210*mm,297*mm))
pdf.setTitle('Nương dòng bình yên — thành phần và kích thước v01')
W,H=210*mm,297*mm; page=0

def header(title,sub='Giai đoạn 01 · Thư viện thành phần rời · Đơn vị cm'):
    global page
    page+=1
    pdf.setFillColor(HexColor('#203c30')); pdf.setFont('DVB',17)
    pdf.drawString(15*mm,280*mm,title)
    pdf.setFont('DV',8.5); pdf.drawString(15*mm,272*mm,sub)
    pdf.setStrokeColor(HexColor('#adc0ac')); pdf.line(15*mm,267*mm,195*mm,267*mm)

def paragraph(body,x,y,width=180*mm,size=9.5,leading=15):
    pdf.setFont('DV',size); pdf.setFillColor(HexColor('#25392f'))
    for para in body.split('\n'):
        words=para.split(); line=''
        for word in words:
            test=(line+' '+word).strip()
            if pdfmetrics.stringWidth(test,'DV',size)>width:
                pdf.drawString(x,y,line); y-=leading; line=word
            else: line=test
        if line: pdf.drawString(x,y,line); y-=leading
        y-=leading*.4
    return y

def footer():
    pdf.setFont('DV',8); pdf.setFillColor(HexColor('#647364'))
    pdf.drawString(15*mm,10*mm,'V01 · Mẫu thiết kế, chưa kiểm tiếp xúc và kết cấu của cảnh lắp')
    pdf.drawRightString(195*mm,10*mm,str(page)); pdf.showPage()

header('Nương dòng bình yên')
y=paragraph('Một tiểu cảnh 20 × 20 cm về thiên nhiên và sự bình yên. Ba chú ngựa cùng nghỉ bên dòng suối liên tục; núi và cây tạo sự che chở.\nBốn góc trong ảnh tham khảo là các góc nhìn của cùng một ý tưởng. Giai đoạn này chỉ dựng riêng các bộ phận, chưa ghép toàn cảnh.',15*mm,255*mm)
pdf.drawImage(str(OUT/'renders'/'01_component_library.png'),10*mm,76*mm,width=190*mm,height=138*mm,preserveAspectRatio=True,anchor='c')
paragraph('Đã dựng 20 mô-đun Blender. Bộ mặt bằng hoàn thiện giữ trong 20 × 20 cm, kể cả tán cây, mây, đuôi ngựa và mặt trời. Chiều cao thiết kế ban đầu: 27,9 cm.\nẢnh AI không cho phép xác định kích thước thật. Các số đo ở đây là quyết định thiết kế mới, được kiểm từ hình học Blender, không phải phép đo một vật thể tồn tại.',15*mm,68*mm,size=9)
footer()

header('Bảng kích thước thành phần')
pdf.setFont('DVB',9); pdf.drawString(15*mm,255*mm,'Mã / Thành phần'); pdf.drawString(110*mm,255*mm,'X × Y × Z (cm)')
y=247*mm
for a,name in zip(assets,names):
    pdf.setFillColor(HexColor('#eef1e7') if int(a['id'][1:])%2 else HexColor('#ffffff'))
    pdf.rect(14*mm,y-2.2*mm,181*mm,8.4*mm,stroke=0,fill=1)
    pdf.setFillColor(HexColor('#25392f')); pdf.setFont('DV',9)
    pdf.drawString(16*mm,y,a['id']+'  '+name)
    pdf.drawString(110*mm,y,' × '.join(f'{v:g}' for v in a['actual_cm']))
    y-=8.4*mm
paragraph('X = trái–phải; Y = trước–sau; Z = cao. Gốc mỗi mô-đun ở tâm đáy. 1 đơn vị tọa độ Blender = 1 cm (Unit Scale = 0,01).\nHộp bao gồm cả bờm, đuôi, tán, gợn nước. Chưa đo độ dày nhỏ nhất để xác nhận độ bền. Các bậc núi là mô-đun ghép, không cộng tất cả chiều cao của mọi món.',15*mm,65*mm,size=9)
footer()

header('Mặt bằng thử 1:1 — chưa lắp', 'In Actual size / 100%. Hình dưới là hộp bao dự kiến, không phải đường cắt đất.')
bx=5*mm; by=49*mm; side=200*mm
pdf.setLineWidth(.25); pdf.setStrokeColor(HexColor('#d7ddd1'))
for i in range(21):
    pdf.line(bx+i*10*mm,by,bx+i*10*mm,by+side)
    pdf.line(bx,by+i*10*mm,bx+side,by+i*10*mm)
pdf.setStrokeColor(HexColor('#203c30')); pdf.setLineWidth(1)
pdf.rect(bx,by,side,side)
palette={'A02':'#938575','A03':'#6e8170','A04':'#466f5b','A05':'#32483d','A06':'#965b37','A07':'#965b37','A08':'#965b37','A16':'#258d9d'}
for a in assets:
    if a['id'] not in palette: continue
    x,y,z=a['planned_origin_cm']; dx,dy,dz=a['target_cm']
    xx=bx+(x-dx/2+10)*10*mm; yy=by+(y-dy/2+10)*10*mm
    pdf.setStrokeColor(HexColor(palette[a['id']])); pdf.setLineWidth(.8)
    pdf.setDash(3,2) if a['id'].startswith('A0') and int(a['id'][1:])>=6 else pdf.setDash()
    pdf.rect(xx,yy,dx*10*mm,dy*10*mm)
    pdf.setDash(); pdf.setFont('DVB',8); pdf.setFillColor(HexColor(palette[a['id']]))
    pdf.drawCentredString(xx+dx*5*mm,yy+dy*5*mm,a['id'])
pdf.setFillColor(HexColor('#203c30')); pdf.setFont('DV',9)
pdf.drawCentredString(105*mm,254*mm,'PHÍA SAU (+Y)')
pdf.drawCentredString(105*mm,42*mm,'PHÍA TRƯỚC (−Y) · cạnh ngoài = 200 mm')
pdf.setLineWidth(1); pdf.line(15*mm,29*mm,65*mm,29*mm)
pdf.line(15*mm,27*mm,15*mm,31*mm); pdf.line(65*mm,27*mm,65*mm,31*mm)
pdf.setFont('DV',8); pdf.drawString(72*mm,28*mm,'Thước kiểm 50 mm — đo lại sau khi in')
footer()

header('Cao độ và khoảng không dự kiến')
paragraph('Sơ đồ kiểm chiều cao 1:2; không phải bản vẽ mặt đứng cuối. Ngựa và cây chưa được đặt lên mô hình núi. Vị trí dự kiến chỉ được kiểm hộp bao trong 20 × 20 × 27,9 cm.',15*mm,255*mm,size=9)
ox=25*mm; oy=72*mm; scale=5*mm
for z,label in [(0,'Đáy đế'),(1.2,'Mặt đế'),(5.2,'Mặt tầng 1 phía sau'),(11.2,'Mặt tầng 2'),(17.2,'Mặt tầng 3'),(25.5,'Đỉnh núi'),(27.9,'Mép mặt trời')]:
    yy=oy+z*scale
    pdf.setLineWidth(.3); pdf.setStrokeColor(HexColor('#a5b8a6')); pdf.line(ox,yy,188*mm,yy)
    pdf.setFillColor(HexColor('#203c30')); pdf.setFont('DV',8)
    pdf.drawString(ox,yy+1.5*mm,f'Z = {z:g} cm')
    pdf.drawRightString(188*mm,yy+1.5*mm,label)
for x,y,w,h,col in [(65,0,60,1.2,'#353f39'),(68,1.2,54,4,'#9b927b'),(75,5.2,40,6,'#7c846a'),(81,11.2,27,6,'#66765f'),(92,17.2,12,8.3,'#4c5d4f')]:
    pdf.setStrokeColor(HexColor(col)); pdf.setFillColor(HexColor(col)); pdf.rect(x*mm,oy+y*scale,w*mm,h*scale,fill=1,stroke=0)
pdf.setStrokeColor(HexColor('#ae7e24')); pdf.circle(79*mm,oy+24.8*scale,3.1*scale,stroke=1,fill=0)
paragraph('Bờ trước tầng 1 hạ thấp để làm khu vực ngựa uống nước. Cao độ chân dự kiến khoảng 1,54 cm, mặt nước dưới khoảng 1,56 cm. Còn phải chỉnh đầu và mép nước khi lắp; hai giá trị gần nhau không tự chứng minh miệng đã chạm nước.\nKhông chi tiết nào được vượt ra ngoài mép đế. Mặt trời/mây/ngọc cần điểm nối cơ học thật, dự kiến giấu phía sau núi; chưa dựng chốt ở giai đoạn này.',15*mm,58*mm,size=9)
footer()

header('Chuẩn bị nặn — phần có thể chốt')
paragraph('Đã chốt: kích thước hoàn thiện ngoài 20 × 20 cm; ba tầng địa hình; ba ngựa cùng quy mô; bố cục và màu hướng về sự bình yên.\nChưa chốt: loại đất, quy trình nung/khô, lõi núi, độ dày vỏ, gia cường chân ngựa, độ co và thứ tự dán/ghép. Chưa nên làm cả khối bằng đất trước khi chốt các mục này.\nBước 1 — Hỏi người trực tiếp nặn tên đất và yêu cầu môn học. Nếu không nung, chọn vật liệu lõi tương thích với đất/keo. Nếu là đất gốm, thống nhất cấu trúc rỗng và quy trình với giảng viên hoặc xưởng; không mặc định cho lõi xốp hay giấy vào lò.\nBước 2 — Làm thử một chân ngựa, một nhánh cây và một đoạn bờm ở đúng tỉ lệ. Nếu dễ gãy, tăng tiết diện, gộp chi tiết hoặc đổi tư thế trước khi nặn toàn bộ.\nBước 3 — Đo thử độ co của vật liệu theo đúng quy trình, ưu tiên thêm thông số nhà sản xuất. Với độ co dài s, kích thước ướt tham khảo = kích thước hoàn thiện / (1 − s). Không áp hệ số co tùy đoán cho đất chưa biết loại.\nBước 4 — Chỉ sau khi duyệt mô-đun mới ghép một cảnh thử; kiểm móng–đá, miệng–nước, đường chảy và vị trí chốt đỡ. Chụp bốn góc từ cùng một cảnh để tránh lặp lại mâu thuẫn của ảnh AI.\nBước 5 — Khi cảnh lắp ổn, khóa bộ kích thước thi công và thứ tự nặn: lõi/bệ → tầng đá → ngựa/cây → nước → mây/mặt trời → chi tiết nhỏ và sơn. Trình tự này còn tùy vật liệu.\nBộ v01 là công cụ trao đổi với người nặn. Chưa đánh giá độ bền, khối lượng, cân bằng trọng tâm hay chất lượng nung. Không phải bộ file in 3D sẵn dùng.',15*mm,254*mm,size=10,leading=16)
footer()
pdf.save()
print('DOCUMENTS_OK')
