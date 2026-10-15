"""Reopen saved horse meshes; measure geometry and contact planes independently."""
import bpy, bmesh, json, math, csv
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Nuong_dong_binh_yen_horses_v02.blend'))
manifest=json.loads((OUT/'measurements'/'horses.json').read_text())
results=[]; crossrows=[]
for h in manifest['horses']:
    c=bpy.data.collections[h['collection']]
    meshes=[o for o in c.objects if o.type=='MESH']
    bpy.context.view_layer.update()
    root=next(o for o in c.objects if o.type=='EMPTY')
    assert all(abs(s-1)<1e-8 for s in root.scale)
    pts=[o.matrix_world@v.co-root.location for o in meshes for v in o.data.vertices]
    assert all(math.isfinite(x) for p in pts for x in p)
    lo=[min(p[i] for p in pts) for i in range(3)]; hi=[max(p[i] for p in pts) for i in range(3)]
    dims=[hi[i]-lo[i] for i in range(3)]
    assert max(abs(dims[i]-h['dimensions_cm'][i]) for i in range(3))<.001
    assert abs(lo[2])<.001
    hoofs=[o for o in meshes if ' hoof ' in o.name]
    assert len(hoofs)==4
    contact_heights=[min((o.matrix_world@v.co-root.location).z for v in o.data.vertices) for o in hoofs]
    assert all(abs(z)<.001 for z in contact_heights),(h['id'],contact_heights)
    body=next(o for o in meshes if o.name.startswith('BODY |'))
    bm=bmesh.new(); bm.from_mesh(body.data)
    nonmanifold=sum(not e.is_manifold for e in bm.edges)
    seen=set(); islands=[]
    for v in bm.verts:
        if v.index in seen: continue
        stack=[v]; size=0; seen.add(v.index)
        while stack:
            p=stack.pop(); size+=1
            for e in p.link_edges:
                q=e.other_vert(p)
                if q.index not in seen: seen.add(q.index); stack.append(q)
        islands.append(size)
    # Sample actual cannon cross-sections, excluding all decorative hair objects.
    min_sections={k:float('inf') for k in ['fore_near','fore_far','hind_near','hind_far']}
    keys=['fore_near','fore_far','hind_near','hind_far']
    centres=[Vector(p[:2]) for p in h['hoof_coronet_centers_cm']]
    for z in [.65,.75,.85,.95,1.05,1.15]:
        groups={k:[] for k in min_sections}
        for e in bm.edges:
            a,b=[v.co for v in e.verts]
            if (a.z-z)*(b.z-z)<0:
                p=a.lerp(b,(z-a.z)/(b.z-a.z))
                distances=[(Vector((p.x,p.y))-centre).length for centre in centres]
                nearest=min(range(4),key=lambda i:distances[i])
                # Low heads also cross these planes in grazing/drinking poses.
                # Restrict each section to the anatomical leg neighborhood.
                if distances[nearest]>.9: continue
                key=keys[nearest]
                groups[key].append(p)
        for key,section in groups.items():
            if not section: continue
            dx=max(p.x for p in section)-min(p.x for p in section)
            dy=max(p.y for p in section)-min(p.y for p in section)
            minimum=min(dx,dy)*10
            min_sections[key]=min(min_sections[key],minimum)
            crossrows.append([h['id'],key,z,round(dx*10,3),round(dy*10,3)])
    bm.free()
    assert nonmanifold==0,(h['id'],'skin has open or nonmanifold edges',nonmanifold)
    assert len(islands)==1,(h['id'],'skin has detached fragments',sorted(islands,reverse=True))
    results.append(dict(id=h['id'],dimensions_cm=[round(x,4) for x in dims],vertices=len(pts),
                        hoof_contacts_z_cm=contact_heights,body_nonmanifold_edges=nonmanifold,
                        body_connected_components=len(islands),body_component_vertex_counts=sorted(islands,reverse=True),
                        sampled_cannon_min_xy_width_mm={k:round(v,3) for k,v in min_sections.items()}))
assert len(results)==3
report={'saved_file_reopened':True,'units':'cm','same_uniform_scale_for_all_poses':True,
        'passed':['three saved poses','finite nonempty geometry','measured bounding boxes','all twelve hoof soles on Z=0','scale preserved across poses'],
        'body_topology':results,
        'not_verified':['final terrain contacts','muzzle water contact after assembly','clay material strength','whole asset union or manufacturing readiness'],
        'section_note':'Six horizontal samples between Z=0.65 and 1.15cm on the skin mesh only. X/Y spans are not a certified minimum diameter or strength test.'}
(OUT/'measurements'/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
with (OUT/'measurements'/'leg_sections.csv').open('w',newline='') as f:
    w=csv.writer(f,lineterminator='\n'); w.writerow(['horse','limb','z_cm','span_x_mm','span_y_mm']); w.writerows(crossrows)
with (OUT/'measurements'/'horse_dimensions.csv').open('w',newline='') as f:
    w=csv.writer(f,lineterminator='\n'); w.writerow(['horse','pose','length_X_cm','width_Y_cm','height_Z_cm','approx_withers_cm'])
    for h in manifest['horses']: w.writerow([h['id'],h['pose'],*h['dimensions_cm'],h['withers_height_cm']])
print('HORSE_VALIDATION_OK',json.dumps(results),flush=True)
