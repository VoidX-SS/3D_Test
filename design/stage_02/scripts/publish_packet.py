"""Generate lightweight review images, Vietnamese PDF and model ZIP locally."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from zipfile import ZipFile, ZIP_DEFLATED
import re

OUT=Path(__file__).resolve().parents[1]; R=OUT/'renders'
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
boldpath='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
f=ImageFont.truetype(fontpath,29); fb=ImageFont.truetype(boldpath,44)

def contain(path,size):
    im=Image.open(path).convert('RGB'); im.thumbnail(size,Image.Resampling.LANCZOS); return im
hero=contain(R/'01_hero_three_quarter.png',(1600,1400)); hero.save(R/'hero_preview.jpg',quality=92,optimize=True)
compare=Image.new('RGB',(2000,1000),'#132125'); d=ImageDraw.Draw(compare)
d.text((55,28),'NGỰA V01 → V02',font=fb,fill='#eee8dc')
d.text((55,88),'Cùng camera góc nghiêng và đơn vị cm · Hình từ mesh Blender',font=f,fill='#aebeb8')
for x,path,label in [(35,R/'before_v01_profile.png','V01 — mẫu ban đầu'),(1020,R/'02_profile_left.png','V02 — dựng lại hình khối và chi tiết')]:
    im=contain(path,(945,770)); compare.paste(im,(x+(945-im.width)//2,145+(770-im.height)//2))
    d.text((x+20,945),label,font=f,fill='#eee8dc')
compare.save(R/'comparison_v01_v02.jpg',quality=92,optimize=True)

board=Image.new('RGB',(2000,2160),'#132125'); d=ImageDraw.Draw(board)
d.text((55,30),'CHI TIẾT NGỰA V02',font=fb,fill='#eee8dc')
d.text((55,95),'Các góc cận từ cùng một ngựa đứng · Tượng cách điệu',font=f,fill='#aebeb8')
for i,(fn,label) in enumerate([('05_head_detail','Hốc mắt, sống mũi, lỗ mũi và tai'),('06_mane_detail','Bờm chồng lớp, rãnh chạy dọc'),('07_leg_and_hoof_detail','Khớp chân, gân và vách móng nghiêng'),('08_tail_detail','Đuôi có lõi và lọn tóc cong')]):
    x=35+(i%2)*990; y=160+(i//2)*990
    im=contain(R/(fn+'.png'),(930,870)); board.paste(im,(x+(930-im.width)//2,y+(870-im.height)//2))
    d.text((x+10,y+905),label,font=f,fill='#eee8dc')
board.save(R/'detail_board.jpg',quality=92,optimize=True)

poses=Image.new('RGB',(2400,1000),'#132125'); d=ImageDraw.Draw(poses)
d.text((45,25),'MỘT THIẾT KẾ NGỰA — BA NHỊP SỐNG',font=fb,fill='#eee8dc')
for i,(fn,label) in enumerate([('01_hero_three_quarter','Đứng nghỉ'),('09_grazing','Gặm cỏ'),('10_drinking','Uống nước')]):
    im=contain(R/(fn+'.png'),(770,780)); x=20+i*795
    poses.paste(im,(x+(770-im.width)//2,120+(780-im.height)//2)); d.text((x+25,932),label,font=f,fill='#eee8dc')
poses.save(R/'three_poses.jpg',quality=91,optimize=True)

manifest=json.loads((OUT/'measurements'/'horses.json').read_text())
val=json.loads((OUT/'measurements'/'validation.json').read_text())
old=json.loads((OUT.parent/'stage_01'/'measurements'/'components.json').read_text())
lookup={a['id']:a for a in old['assets']}; replacements=[]
for h,aid in zip(manifest['horses'],['A06','A07','A08']):
    p=lookup[aid]['planned_origin_cm']; sz=h['dimensions_cm']
    low=[p[0]-sz[0]/2,p[1]-sz[1]/2,p[2]]; high=[p[0]+sz[0]/2,p[1]+sz[1]/2,p[2]+sz[2]]
    assert min(low[:2])>=-10 and max(high[:2])<=10 and high[2]<=27.9
    replacements.append(dict(horse=h['id'],replaces=aid,planned_origin_cm=p,bounds_cm=[low,high]))
(OUT/'measurements'/'replacement_plan.json').write_text(json.dumps({'status':'planned AABB only; final contacts and collisions not checked','replacements':replacements},indent=2))

pdfmetrics.registerFont(TTFont('DV',fontpath)); pdfmetrics.registerFont(TTFont('DVB',boldpath))
pdf=canvas.Canvas(str(OUT/'Horse_design_review_v02.pdf'),pagesize=(210*mm,297*mm)); pdf.setTitle('Nương dòng bình yên — Ngựa v02')
page=0
def header(title):
    global page
    page+=1; pdf.setFillColor(HexColor('#203c36')); pdf.setFont('DVB',17); pdf.drawString(15*mm,279*mm,title)
    pdf.setFont('DV',9); pdf.drawString(15*mm,269*mm,'Giai đoạn 02 · Ngựa là chủ thể · Số đo mesh tính bằng cm')
def para(body,y,size=9.5):
    pdf.setFont('DV',size); pdf.setFillColor(HexColor('#203c36'))
    for p in body.split('\n'):
        line=''
        for word in p.split():
            t=(line+' '+word).strip()
            if pdfmetrics.stringWidth(t,'DV',size)>180*mm:
                pdf.drawString(15*mm,y,line); y-=15; line=word
            else: line=t
        if line: pdf.drawString(15*mm,y,line); y-=15
        y-=5
    return y
def footer():
    pdf.setFont('DV',8); pdf.drawString(15*mm,10*mm,'V02 · Chưa ghép cảnh, chưa xác nhận vật liệu và độ bền khi nặn')
    pdf.drawRightString(195*mm,10*mm,str(page)); pdf.showPage()
header('Nương dòng bình yên — ngựa v02')
para('Ngựa là nhân vật chính của bài chọn một loài vật. Ba tư thế giữ cùng một thiết kế, kể nhịp sống tự nhiên: đứng nghỉ, gặm cỏ, uống nước. Cây, núi và dòng suối ở bước sau sẽ nâng đỡ nhân vật, không lấn át ngựa.',253*mm)
pdf.drawImage(str(R/'hero_preview.jpg'),15*mm,73*mm,width=180*mm,height=155*mm,preserveAspectRatio=True,anchor='c')
para('Đã dựng lại hình khối thân, đầu, chân và móng; bờm và đuôi dùng các lọn có rãnh hình học. Có hốc mắt và lỗ mũi lõm thật. Đây là tượng ngựa cách điệu có cơ sở giải phẫu, không phải bản quét một con ngựa thật.\nẢnh trong phiếu được render từ cùng các mesh lưu trong file Blender; không dùng hình AI làm sản phẩm thay thế.',60*mm)
footer()
header('Từ khối mẫu đến tượng có chi tiết')
pdf.drawImage(str(R/'comparison_v01_v02.jpg'),10*mm,153*mm,width=190*mm,height=95*mm,preserveAspectRatio=True)
para('1. Tỉ lệ: kéo dài thân, đầu có sống mũi và mặt phẳng hàm; giữ cùng quy mô thân/chân ở ba tư thế.\n2. Thân: lồng ngực, bụng, vai và hông nối thành một khối da. Loại bỏ phần nắp khối đùi lộ ra ngoài ở bản sửa đầu tiên.\n3. Mặt: mắt nhỏ và sâu trong khe hình hạnh nhân; mép lỗ mũi và môi bám vào bề mặt, tránh cảm giác viền dây trang trí.\n4. Tóc: thay bờm răng lược bằng nền liền và lọn chồng lớp. Với ngựa cúi đầu, bờm có đường rủ riêng theo trọng lực.\n5. Chân và móng: khớp, gân, đốt nghiêng và vách móng có hình khối; cả bốn móng đặt trên mặt phẳng nghiên cứu.\nBản v01 được giữ nguyên để đối chiếu. Không đồng nhất số đa giác với chất lượng thẩm mỹ; quá trình sửa dựa trên ảnh toàn thân và cận cảnh từ nhiều góc.',140*mm)
footer()
header('Đầu, bờm, chân và đuôi')
pdf.drawImage(str(R/'detail_board.jpg'),15*mm,48*mm,width=180*mm,height=194*mm,preserveAspectRatio=True)
para('Các ảnh cận không cùng tỉ lệ phóng đại. Khi nặn nhỏ, rãnh tóc/mí/môi có thể khắc lên mảng lớn; không cần nặn và dán từng sợi rời như một cấu trúc độc lập.',37*mm,size=9)
footer()
header('Kích thước và điều kiện chuyển sang đất')
y=252*mm
for h in manifest['horses']:
    text=h['id']+' / '+h['pose']+': '+' × '.join(f'{x:.2f}' for x in h['dimensions_cm'])+' cm'
    y=para(text,y,size=10)
y=para('X = dài trái–phải; Y = bề ngang; Z = cao. Hộp bao gồm cả bờm và đuôi. Cao vai xấp xỉ 4,43 cm ở cả ba con. Đế tác phẩm vẫn là 20 × 20 cm, chiều cao cảnh dự kiến vẫn trong 27,9 cm. Vị trí thay thế các ngựa v01 được kiểm hộp bao; chưa kiểm tiếp xúc với địa hình.',y-3*mm)
pdf.drawImage(str(R/'three_poses.jpg'),10*mm,125*mm,width=190*mm,height=79*mm,preserveAspectRatio=True)
mins=[v for h in val['body_topology'] for v in h['sampled_cannon_min_xy_width_mm'].values()]
para(f'Đọc lại file: đủ ba tư thế, 12 đáy móng đồng phẳng Z = 0; khối da chính mỗi con là một phần liên tục và không có biên hở ở phép kiểm mesh. Mắt, tai, bờm, đuôi và móng vẫn được giữ thành các mesh để chỉnh sửa.\nMột số lát cắt cẳng chân cho bề ngang X/Y nhỏ khoảng {min(mins):.2f}–{max(mins):.2f} mm. Đây không phải kiểm độ bền hoặc đường kính nhỏ nhất toàn bộ chân.\nChưa chốt loại đất: cần thử chi tiết ở đúng kích thước trước khi nặn toàn bộ; chưa quyết định lõi kim loại, keo, quy trình nung hay hệ số co. Chân mảnh và đầu lọn tóc cần được người nặn cân nhắc gia cường/gộp chi tiết theo vật liệu.\nBước sau: đặt ba ngựa lên cảnh, chỉnh tiếp xúc móng–đá và miệng–nước, chừa khoảng trống quanh đầu/thân để người xem nhận ra ngựa trước các chi tiết nền.',113*mm,size=9)
footer(); pdf.save()

archive=OUT.parent/'Nuong_dong_binh_yen_horses_v02.zip'
files=[OUT/'Nuong_dong_binh_yen_horses_v02.blend',OUT/'Horse_design_review_v02.pdf',OUT/'README.md']
files+=list((OUT/'assets').glob('*.blend'))+list((OUT/'measurements').glob('*'))+list((OUT/'scripts').glob('*.py'))
files+=list(R.glob('*.jpg'))
with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=6) as z:
    for f in files:
        path=Path('stage_02')/f.relative_to(OUT)
        if f==OUT/'README.md':
            body=re.sub(r'\]\((renders/[^)]+\.png)\)',r'](https://github.com/VoidX-SS/3D_Test/blob/main/design/stage_02/\1)',f.read_text())
            z.writestr(str(path),body)
        else: z.write(f,path)
    z.writestr('stage_02/DOWNLOAD_README.txt','Open Nuong_dong_binh_yen_horses_v02.blend in Blender 4.3+. Units: 1 unit = 1 cm. ZIP includes full models, measurement reports, PDF and lightweight review images. Full-resolution PNG review images are available in the GitHub repository under design/stage_02/renders/. This is an editable sculpture study, not a manufacturing-certified print file.\n')
with ZipFile(archive) as z: assert z.testzip() is None
assert archive.stat().st_size<100*1024*1024
print('PACKET_OK',round(archive.stat().st_size/1024/1024,1),'MiB')
