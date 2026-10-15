"""Frame broad base modules with sufficient margin around projected corners."""
import bpy, json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Nuong_dong_binh_yen_components_v01.blend'))
sc=bpy.context.scene; cam=sc.camera
for o in bpy.data.collections['ZZ_PRESENTATION_ONLY'].objects:
    if o.type=='FONT': o.hide_render=True
for a in json.loads((OUT/'measurements'/'components.json').read_text())['assets'][:2]:
    for c in bpy.data.collections:
        if c.name.startswith('A'): c.hide_render=c.name[:3]!=a['id']
    x,y,z=a['station_cm']; dx,dy,dz=a['target_cm']; target=Vector((x,y,dz*.45))
    cam.location=target+Vector((dx*.65+4,-max(dx,dy)*1.5-5,max(dx,dy,dz)*.95+3))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    corners=[Vector((x+sx*dx/2,y+sy*dy/2,zz)) for sx in [-1,1] for sy in [-1,1] for zz in [0,dz]]
    inv=cam.rotation_euler.to_matrix().transposed(); pts=[inv@(v-target) for v in corners]
    cam.data.ortho_scale=max(max(v[i] for v in pts)-min(v[i] for v in pts) for i in [0,1])*1.16
    sc.cycles.samples=20; sc.cycles.use_denoising=False
    sc.render.resolution_x=720; sc.render.resolution_y=720
    sc.render.filepath=str(OUT/'renders'/(a['id']+'.png'))
    bpy.ops.render.render(write_still=True)
