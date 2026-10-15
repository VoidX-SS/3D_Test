"""Comparable cameras, profile and close-ups of the same saved horse geometry."""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
source=OUT/('Horse_hero_working.blend' if '--hero' in sys.argv else 'Nuong_dong_binh_yen_horses_v02.blend')
bpy.ops.wm.open_mainfile(filepath=str(source))
sc=bpy.context.scene; cam=sc.camera
only=next((arg.split('=',1)[1].split(',') for arg in sys.argv if arg.startswith('--only=')),None)
sc.cycles.samples=32; sc.cycles.use_denoising=False
if '--draft' in sys.argv: sc.cycles.samples=10
lights=[o for o in sc.objects if o.type=='LIGHT']; origins={o.name:o.location.copy() for o in lights}
def show(code):
    for c in bpy.data.collections:
        if c.name.startswith('H0'): c.hide_render=not c.name.startswith(code)
def shot(name,loc,target,scale,size=(1800,1450),offset=0):
    if only is not None and name not in only: return
    for l in lights: l.location=origins[l.name]+Vector((offset,0,0))
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=scale
    sc.render.resolution_x,sc.render.resolution_y=size
    if '--draft' in sys.argv:
        sc.render.resolution_percentage=45
        sc.render.filepath='/tmp/horse_draft_'+name+'.png'
    else: sc.render.filepath=str(OUT/'renders'/(name+'.png'))
    bpy.ops.render.render(write_still=True)
show('H01')
shot('01_hero_three_quarter',(-9,-15,8),(-.3,0,3.1),10.5,(1800,1450))
views=[
 ('02_profile_left',(0,-18,3.3),(0,0,3.3),9.1,(1800,1450)),
 ('03_front',(-18,0,3.3),(-.4,0,3.3),7.8,(1000,1450)),
 ('04_opposite_three_quarter',(3,18,7),(0,0,3.0),10.2,(1800,1450)),
 ('05_head_detail',(-8,-12,7.0),(-2.85,-.02,4.95),3.6,(1600,1600)),
 ('06_mane_detail',(-1,-12,7.4),(-1.90,-.15,4.45),4.1,(1600,1600)),
 ('07_leg_and_hoof_detail',(-6,-10,3.0),(-.55,0,1.2),5.2,(1800,1200)),
 ('08_tail_detail',(5,-12,6),(2.5,-.1,2.4),4.5,(1300,1600)),
]
for name,loc,target,scale,size in views:
    if '--quick' in sys.argv and name not in {'02_profile_left','05_head_detail'}: continue
    shot(name,loc,target,scale,size)
if '--hero' not in sys.argv:
    show('H02'); shot('09_grazing',(2,-15,7),(10.6,0,2.2),10.6,(1800,1300),11)
    show('H03'); shot('10_drinking',(13,-15,7),(21.6,0,2.2),10.6,(1800,1300),22)
    # Old geometry under precisely the same profile camera and lighting.
    for c in bpy.data.collections:
        if c.name.startswith('H0'): c.hide_render=True
    old=OUT.parents[0]/'stage_01'/'assets'/'A06_Horse_standing.blend'
    with bpy.data.libraries.load(str(old),link=False) as (src,dst): dst.collections=[src.collections[0]]
    oldcol=dst.collections[0]; sc.collection.children.link(oldcol)
    shot('before_v01_profile',(0,-18,3.3),(0,0,3.3),9.1,(1800,1450))
print('REVIEW_RENDERS_COMPLETE')
