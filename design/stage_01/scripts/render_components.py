"""Repeat presentation renders without rebuilding measured mesh libraries."""
import bpy, json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Nuong_dong_binh_yen_components_v01.blend'))
scene=bpy.context.scene
scene.cycles.use_denoising=False
scene.cycles.samples=32
cam=scene.camera
assets=json.loads((OUT/'measurements'/'components.json').read_text())['assets']
for a in assets: a['collection']=bpy.data.collections[a['id']+'__'+a['name']]
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Nuong_dong_binh_yen_components_v01.blend'),compress=True)
source=(OUT/'scripts'/'build_components.py').read_text()
start=source.index("scene.render.filepath=str(OUT/'renders'/'01_component_library.png')")
exec(compile(source[start:],str(OUT/'scripts'/'build_components.py'),'exec'))
