"""Wider mountain plate so no module is clipped by the frame."""
import bpy
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Nuong_dong_binh_yen_components_v01.blend'))
sc=bpy.context.scene; ids={'A02','A03','A04','A05'}
for c in bpy.data.collections:
    if c.name.startswith('A'): c.hide_render=c.name[:3] not in ids
for o in bpy.data.collections['ZZ_PRESENTATION_ONLY'].objects:
    if o.type=='FONT': o.hide_render=o.name[:3] not in ids
cam=sc.camera; cam.location=(16,-34,55)
cam.rotation_euler=(Vector((13,22,2))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.ortho_scale=78
sc.cycles.use_denoising=False; sc.cycles.samples=24
sc.render.threads_mode='FIXED'; sc.render.threads=1
sc.render.resolution_x=1800; sc.render.resolution_y=1050
sc.render.filepath=str(OUT/'renders'/'03_mountain_modules.png')
bpy.ops.render.render(write_still=True)
