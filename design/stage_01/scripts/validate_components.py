"""Independently reopen saved artifacts and inspect actual stored mesh vertices."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
manifest=json.loads((OUT/'measurements'/'components.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Nuong_dong_binh_yen_components_v01.blend'))
sc=bpy.context.scene
assert sc.unit_settings.scale_length == .01 or abs(sc.unit_settings.scale_length-.01)<1e-8
results=[]
for a in manifest['assets']:
    c=bpy.data.collections[a['id']+'__'+a['name']]
    meshes=[o for o in c.objects if o.type=='MESH']
    assert meshes, a['id']
    bpy.context.view_layer.update()
    pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
    assert all(math.isfinite(t) for v in pts for t in v)
    lo=[min(v[i] for v in pts) for i in range(3)]
    hi=[max(v[i] for v in pts) for i in range(3)]
    actual=[hi[i]-lo[i] for i in range(3)]
    err=max(abs(actual[i]-a['target_cm'][i]) for i in range(3))
    assert err<.008, (a['id'],actual)
    assert abs(lo[2])<.005,(a['id'],'bottom datum',lo[2])
    assert max(abs((hi[i]+lo[i])/2-a['station_cm'][i]) for i in [0,1])<.005
    f=OUT/'assets'/(a['id']+'_'+a['name']+'.blend')
    assert f.stat().st_size>1000
    origin=a['planned_origin_cm']; dims=a['target_cm']
    planned_min=[origin[0]-dims[0]/2,origin[1]-dims[1]/2,origin[2]]
    planned_max=[origin[0]+dims[0]/2,origin[1]+dims[1]/2,origin[2]+dims[2]]
    assert planned_min[0]>=-10-1e-5 and planned_max[0]<=10+1e-5,a['id']
    assert planned_min[1]>=-10-1e-5 and planned_max[1]<=10+1e-5,a['id']
    assert planned_max[2]<=27.901,a['id']
    results.append({'id':a['id'],'measured_cm':[round(x,5) for x in actual],
                    'max_error_cm':err,'vertices':len(pts),
                    'faces':sum(len(o.data.polygons) for o in meshes),
                    'planned_bounds_cm':[planned_min,planned_max]})
assert len(results)==20
report={'saved_file_reopened':True,'component_count':len(results),
        'passed':['centimeter unit scale','mesh dimensions within 0.008 cm','bottom-center datums','nonempty finite geometry','20 individual libraries exist','planned axis-aligned envelopes inside 20 x 20 x 27.9 cm'],
        'not_verified':['final assembled intersections','hoof and muzzle contact','clay shrinkage','support strength','watertight printable solids'],
        'assets':results}
(OUT/'measurements'/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('VALIDATION_OK',len(results),'saved component libraries; proposed envelope 20 x 20 x 27.9 cm')
