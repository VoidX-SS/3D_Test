"""Stage 01: dimensioned, separate sculpting studies; 1 Blender unit = 1 cm.
Run: blender -b -t 4 --python design/stage_01/scripts/build_components.py
No assembled diorama is produced in this stage.
"""
import bpy
import math
import random
import json
import csv
from pathlib import Path
from mathutils import Vector, Matrix

OUT = Path(__file__).resolve().parents[1]
random.seed(27)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = '01_COMPONENT_LIBRARY_CM'
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01
scene.unit_settings.length_unit = 'CENTIMETERS'
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = False  # Debian Blender build has no OpenImageDenoise.
scene.render.threads_mode = 'FIXED'
scene.render.threads = 4
scene.view_settings.view_transform = 'AgX'
scene.world = bpy.data.worlds.new('Warm studio')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.56,.61,.66,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .45

def mat(name, color, rough=.6, metallic=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metallic
    return m

ivory=mat('Warm porcelain clay',(.78,.72,.59),.44)
mane=mat('Cream mane',(.61,.51,.35),.5)
hoof=mat('Warm grey hoof',(.26,.24,.20))
eye=mat('Dark brown eyes',(.035,.023,.014),.28)
rockm=[mat('Slate %02d'%i,c) for i,c in enumerate([(.25,.28,.25),(.32,.34,.29),(.39,.38,.30),(.21,.25,.24),(.44,.43,.34)])]
for m in rockm:
    nt=m.node_tree; n=nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=8
    n.inputs['Detail'].default_value=3; b=nt.nodes.new('ShaderNodeBump')
    b.inputs['Strength'].default_value=.27; b.inputs['Distance'].default_value=.045
    nt.links.new(n.outputs['Fac'],b.inputs['Height'])
    nt.links.new(b.outputs['Normal'],nt.nodes['Principled BSDF'].inputs['Normal'])
soil=mat('Earth on terraces',(.29,.27,.17))
greens=[mat('Leaf green %02d'%i,c) for i,c in enumerate([(.12,.23,.07),(.22,.34,.09),(.33,.42,.12),(.08,.19,.10),(.42,.47,.17)])]
bark=mat('Bark clay',(.25,.15,.075))
water=mat('River glazed teal',(.035,.28,.31),.24,.12)
foam=mat('Water ridges pale blue',(.48,.74,.71),.34)
gold=mat('Ochre sun',(.83,.43,.065),.4,.45)
cloudmat=mat('Ivory clouds',(.78,.76,.66),.72)
moonmat=mat('Pearl moon',(.74,.79,.76),.24,.15)
black=mat('Charcoal plinth',(.035,.045,.044))
labelmat=mat('Label dark green',(.08,.15,.13))
boardmat=mat('Sand studio',(.65,.64,.58))
assets=[]; current=None

def collection(name):
    c=bpy.data.collections.new(name); scene.collection.children.link(c); return c

def attach(o, material=None):
    for c in list(o.users_collection): c.objects.unlink(o)
    current.objects.link(o)
    if material: o.data.materials.append(material)
    return o

def smooth(o):
    if o.type=='MESH':
        for p in o.data.polygons: p.use_smooth=True
    return o

def uv(name, loc, scale, material, segments=24, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return smooth(attach(o,material))

def cube(name, loc, dims, material, bevel=.08):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    attach(o,material)
    if bevel:
        m=o.modifiers.new('Soft hand finished edge','BEVEL'); m.width=bevel; m.segments=3
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=m.name)
    return o

def mesh(name, verts, faces, material):
    m=bpy.data.meshes.new(name); m.from_pydata(verts,[],faces); m.update()
    o=bpy.data.objects.new(name,m); current.objects.link(o)
    if material: m.materials.append(material)
    return o

def tube(name, points, radius, material, radii=None, res=3):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.resolution_u=12
    c.bevel_depth=radius; c.bevel_resolution=res; c.use_fill_caps=True
    s=c.splines.new('BEZIER'); s.bezier_points.add(len(points)-1)
    for i,(b,p) in enumerate(zip(s.bezier_points,points)):
        b.co=p; b.handle_left_type='AUTO'; b.handle_right_type='AUTO'
        if radii: b.radius=radii[i]
    o=bpy.data.objects.new(name,c); current.objects.link(o)
    if material: c.materials.append(material)
    return o

def loft(name, points, widths, depths, material, sides=14):
    verts=[]; faces=[]
    for i,p in enumerate(points):
        p=Vector(p)
        t=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])
        t.normalize(); a=Vector((0,1,0)); a=(a-t*a.dot(t)).normalized(); b=t.cross(a).normalized()
        for j in range(sides):
            ang=2*math.pi*j/sides
            verts.append(p+a*math.cos(ang)*widths[i]+b*math.sin(ang)*depths[i])
    for i in range(len(points)-1):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            faces.append((a,b,b+sides,a+sides))
    faces.extend([tuple(reversed(range(sides))),tuple(range((len(points)-1)*sides,len(points)*sides))])
    return smooth(mesh(name,verts,faces,material))

def bbox(objects):
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    coords=[]
    for ob in objects:
        if ob.type not in {'MESH','CURVE','SURFACE','FONT'}: continue
        e=ob.evaluated_get(dg)
        # Rotated object bounding-box corners exaggerate an oval's true size.
        # Measure actual evaluated vertices instead of transformed box corners.
        me=e.to_mesh()
        coords.extend(e.matrix_world@v.co for v in me.vertices)
        e.to_mesh_clear()
    lo=Vector(tuple(min(v[i] for v in coords) for i in range(3)))
    hi=Vector(tuple(max(v[i] for v in coords) for i in range(3)))
    return lo,hi

def begin(code, name, target, planned, note):
    global current
    current=collection(code+'__'+name)
    current['asset_id']=code
    current['target_cm']=target
    current['note']=note
    return dict(id=code,name=name,collection=current,target_cm=target,planned_origin_cm=planned,note=note)

def finish(a, station):
    obs=list(current.objects); lo,hi=bbox(obs)
    # Normalize the complete evaluated component, then set its datum at bottom centre.
    target=Vector(a['target_cm']); size=hi-lo
    s=Vector(tuple(target[i]/size[i] for i in range(3)))
    centre=Vector(((hi.x+lo.x)/2,(hi.y+lo.y)/2,lo.z))
    # Bake evaluated curves and bevels before world-axis scaling. Object-local
    # scale cannot correctly normalize rotated ears, discs, or curve bevels.
    dg=bpy.context.evaluated_depsgraph_get()
    bake=Matrix.Diagonal((*s,1)) @ Matrix.Translation(-centre)
    baked=[]
    for o in obs:
        data=bpy.data.meshes.new_from_object(o.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
        data.transform(bake @ o.matrix_world)
        n=bpy.data.objects.new(o.name+'_mesh',data); current.objects.link(n)
        n.location=station; baked.append(n)
    for o in obs: bpy.data.objects.remove(o,do_unlink=True)
    obs=baked
    lo,hi=bbox(obs)
    root=bpy.data.objects.new(a['id']+'_DATUM',None); current.objects.link(root)
    root.location=station; root.empty_display_size=.7; root['unit']='cm'
    for o in obs:
        o.parent=root; o.location=(0,0,0)
    a.update(root=root,station_cm=station,actual_cm=[round(x,4) for x in hi-lo],objects=obs)
    root['design_size_cm']=a['target_cm']; root['planned_origin_cm']=a['planned_origin_cm']
    assets.append(a)
    print('ASSET',a['id'],a['actual_cm'],flush=True)

def rock(name, loc, dims, material=None):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=loc)
    o=attach(bpy.context.object,material or random.choice(rockm)); o.name=name
    for v in o.data.vertices:
        v.co*=random.uniform(.85,1.13)
    o.scale=Vector(dims)/2
    b=o.modifiers.new('Worn stone edges','BEVEL'); b.width=.06; b.segments=2
    return o

# Separate base and terrain modules, with flat landings reserved for later hoof placement.
a=begin('A01','Base_20x20',(20,20,1.2),(0,0,0),'Exact final outside footprint; no element may project beyond this outline.')
cube('Black plinth',(0,0,.6),(20,20,1.2),black,.16)
finish(a,(-31,22,0))

def terrain(code,name,dims,planned,station):
    a=begin(code,name,dims,planned,'Separate rock terrace. Top landing is flat; water channel and final supports remain assembly-stage work.')
    w,d,h=dims; n=28; verts=[]; faces=[]
    # Squircle rings retain useful shelf area instead of converging to a point.
    for k,(z,shrink) in enumerate([(0,.95),(.18,1),(h*.73,.87),(h,.80)]):
        for j in range(n):
            t=j*2*math.pi/n
            x=math.copysign(abs(math.cos(t))**.63,math.cos(t))*w/2
            y=math.copysign(abs(math.sin(t))**.63,math.sin(t))*d/2
            jag=1+(.025*math.sin(j*2.6) if k not in (0,3) else 0)
            verts.append((x*shrink*jag*.88,y*shrink*jag*.88,z))
    for k in range(3):
        for j in range(n):
            p=k*n+j; q=k*n+(j+1)%n; faces.append((p,q,q+n,p+n))
    faces.extend([tuple(reversed(range(n))),tuple(range(3*n,4*n))])
    if code=='A02':
        # Low front shore, higher rear landing. A grid gives a genuinely flat
        # front bank rather than triangulating a non-planar giant ngon.
        verts=[]; faces=[]; nx=24; ny=24
        def top(y): return .34+(h-.34)*max(0,min(1,(y+d*.17)/(d*.35)))
        for iy in range(ny+1):
            y=-d/2+d*iy/ny
            for ix in range(nx+1): verts.append(((-w/2+w*ix/nx)*.9,y*.9,top(y)))
        for iy in range(ny):
            for ix in range(nx):
                k=iy*(nx+1)+ix; faces.append((k,k+1,k+nx+2,k+nx+1))
        edge=list(range(nx+1))+[iy*(nx+1)+nx for iy in range(1,ny+1)]+[ny*(nx+1)+ix for ix in range(nx-1,-1,-1)]+[iy*(nx+1) for iy in range(ny-1,0,-1)]
        bottom=[]
        for k in edge:
            bottom.append(len(verts)); verts.append((verts[k][0],verts[k][1],0))
        for j,k in enumerate(edge):
            jj=(j+1)%len(edge); faces.append((k,bottom[j],bottom[jj],edge[jj]))
        faces.append(tuple(reversed(bottom)))
    ob=mesh(name+'_core',verts,faces,soil)
    for j in range(36):
        t=2*math.pi*j/36; rr=random.uniform(.94,1.02)
        x=math.copysign(abs(math.cos(t))**.63,math.cos(t))*w*.43*rr
        y=math.copysign(abs(math.sin(t))**.63,math.sin(t))*d*.43*rr
        localh=top(y) if code=='A02' else h
        height=random.uniform(.62,.95)*localh
        rock('Stratified column_%02d'%j,(x,y,height/2+.06),(random.uniform(1.2,2.2),random.uniform(1.0,1.9),height))
        if j%2==0:
            rock('Cap stone',(x*.98,y*.98,localh*.83),(1.4,1.2,min(.45,localh*.3)))
    # Small moss patches explicitly kept separate from load-bearing stones.
    for j in range(16):
        t=random.uniform(0,2*math.pi)
        my=.39*d*math.sin(t); mz=top(my) if code=='A02' else h
        uv('Moss',(.39*w*math.cos(t),my,mz*.98),(.45,.32,.11),random.choice(greens),16,10)
    finish(a,station)

terrain('A02','Mountain_tier_1',(19,18.8,4.0),(0,0,1.2),(-7,22,0))
terrain('A03','Mountain_tier_2',(14.2,12.8,6.0),(-1.8,2.3,5.2),(14,22,0))
terrain('A04','Mountain_tier_3',(9.2,8.5,6.0),(0,4.1,11.2),(31,22,0))
a=begin('A05','Mountain_summit',(4.2,3.6,8.3),(.2,7,17.2),'Rear summit; final altitude 25.5 cm. Reserve upper horse shelf in front.')
for j in range(7):
    x=random.uniform(-1.2,1.2); y=random.uniform(-.9,.9); h=random.uniform(4,8.3)
    rock('Summit needle',(x,y,h/2),(random.uniform(.9,1.6),random.uniform(.8,1.4),h))
finish(a,(43,22,0))

def horse(code,name,target,planned,station,pose):
    a=begin(code,name,target,planned,'Sculpted horse study, not a scan. Thin legs/ears need material-specific review. Comparable body scale across all three poses.')
    skin=[]
    def flesh(n,p,s):
        o=uv(n,p,s,ivory,32,20); skin.append(o); return o
    flesh('Barrel ribcage',(.15,0,3.1),(1.45,.59,.82))
    flesh('Shoulder',(-.91,0,3.20),(.65,.61,.76))
    flesh('Hindquarter',(1.12,0,3.17),(.74,.63,.78))
    flesh('Chest',(-1.27,0,2.98),(.40,.45,.68))
    # Tapered neck with a wide chest root, narrower throat and defined poll.
    if pose=='stand':
        neck=[(-1.05,0,3.38),(-1.52,0,3.97),(-1.76,0,4.6),(-1.93,0,5.08)]
        head=Vector((-2.18,0,5.04)); muzzle=Vector((-2.75,0,4.6)); poll=Vector((-1.95,0,5.25))
    else:
        # Lower neck follows an arch into the downward head, not an elbow bend.
        low=.47 if pose=='drink' else .72
        neck=[(-1.06,0,3.4),(-1.65,0,2.95),(-2.14,0,2.13),(-2.32,0,1.46)]
        head=Vector((-2.55,0,1.15)); muzzle=Vector((-2.72,0,low)); poll=Vector((-2.38,0,1.51))
    skin.append(loft('Neck',neck,[.49,.43,.32,.25],[.64,.51,.37,.3],ivory,20))
    # Cheek, nasal bridge and muzzle flow as one continuous skin after voxel fusion.
    flesh('Cheek',head,(.39,.29,.41))
    axis=muzzle-head
    bridge=flesh('Nasal bridge',(head+muzzle)/2,(.28,.22,axis.length*.66))
    bridge.rotation_euler=axis.to_track_quat('Z','Y').to_euler()
    flesh('Soft muzzle',muzzle,(.26,.245,.23))
    # Four distinct legs with elbows/hocks, fine cannons and wider hooves.
    for rear in [False,True]:
        for side in [-1,1]:
            y=side*.40
            if rear:
                pts=[(1.14,y,3.05),(1.4,y,2.26),(.99,y,1.49),(1.24,y,.43),(1.31,y,.20)]
            else:
                shift=.22 if side==1 else -.12
                pts=[(-.97,y,3.03),(-.84+shift,y,2.14),(-.99+shift,y,1.34),(-1.04+shift,y,.42),(-1.08+shift,y,.20)]
            skin.append(loft(('Hind' if rear else 'Fore')+' leg',pts,[.27,.20,.14,.105,.12],[.31,.23,.14,.115,.12],ivory,16))
            flesh('Fetlock',pts[-2],(.135,.145,.17))
            cube('Hoof',Vector(pts[-1])+Vector((-.04,0,-.07)),(.36,.30,.27),hoof,.065)
    # Ears attached at the poll: thick bases, rounded pointed tips.
    for side in [-1,1]:
        earbase=poll+Vector((.06,side*.18,.15))
        e=flesh('Ear',earbase+Vector((.02,side*.04,.19)),(.10,.12,.26))
        e.rotation_euler[1]=-.23 if pose=='stand' else .25
        # Eyes and nostrils remain visible but deliberately enlarged for hand sculpting.
        eyept=head+Vector((-.16,side*.264,.13))
        uv('Eye',eyept,(.055,.035,.061),eye,16,12)
        uv('Nostril',muzzle+Vector((-.13,side*.21,.04)),(.065,.026,.048),eye,16,10)
    bpy.ops.object.select_all(action='DESELECT')
    for o in skin: o.select_set(True)
    bpy.context.view_layer.objects.active=skin[0]
    bpy.ops.object.join(); body=bpy.context.object; body.name='Horse continuous clay skin'
    rem=body.modifiers.new('Fuse anatomy','REMESH'); rem.mode='VOXEL'; rem.voxel_size=.055; rem.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=rem.name)
    sm=body.modifiers.new('Soften sculpt transitions','SMOOTH'); sm.factor=1.25; sm.iterations=5
    bpy.ops.object.modifier_apply(modifier=sm.name)
    smooth(body)
    # Raised cheek/jaw line and mane locks are modeled geometry, not textures.
    crest=[]
    for j in range(16):
        f=j/15*2.99; k=int(f); t=f-k
        p=Vector(neck[k]).lerp(Vector(neck[k+1]),t)
        tangent=(Vector(neck[k+1])-Vector(neck[k])).normalized()
        normal=tangent.cross(Vector((0,1,0)))
        if normal.z<0: normal=-normal
        depth=[.64,.51,.37,.3][k]*(1-t)+[.64,.51,.37,.3][k+1]*t
        width=[.49,.43,.32,.25][k]*(1-t)+[.49,.43,.32,.25][k+1]*t
        start=p+normal*depth*.95
        crest.append(start)
        pts=[start,p+normal*depth*.74+Vector((0,-width*.65,0)),p+normal*depth*.18+Vector((0,-width*.97,0))+tangent*.12]
        tube('Mane attached sculpt lock',pts,.065,mane,[1,.9,.22])
    tube('Continuous mane crest',crest,.10,mane)
    for j in range(8):
        y=(j-3.5)*.065
        tube('Tail lock',[(1.65,y,3.65),(2.12,y*.9,3.40),(2.35,y*.7,2.35),(2.25,y*.4,1.35),(2.40,y*.12,.72)],.075,mane,[1,.9,.8,.6,.18])
    # A few readable rib/haunch surface planes are formed by the body, no engraved noise.
    finish(a,station)

horse('A06','Horse_standing',(6.7,2.15,6.3),(-.3,2,17.2),(-30,0,0),'stand')
horse('A07','Horse_grazing',(7.1,2.2,4.8),(-4.1,-1.9,11.2),(-18,0,0),'graze')
horse('A08','Horse_drinking',(7.1,2.2,4.65),(3.6,-6.2,1.54),(-6,0,0),'drink')

def leaf(name,p,length,width,material,angle=0):
    verts=[]; faces=[]
    for i in range(9):
        t=i/8; x=length*t; w=width*.5*math.sin(math.pi*t)**.72
        z=.09*math.sin(math.pi*t)
        for yy,zz in [(-w,z),(0,z+.045),(w,z)]:
            verts.append((p[0]+x*math.cos(angle)-yy*math.sin(angle),p[1]+x*math.sin(angle)+yy*math.cos(angle),p[2]+zz))
    for i in range(8):
        for j in range(2):
            k=i*3+j; faces.append((k,k+1,k+4,k+3))
    o=smooth(mesh(name,verts,faces,material))
    solid=o.modifiers.new('Sculptable leaf thickness','SOLIDIFY'); solid.thickness=.09
    return o

a=begin('A09','Pine_tree',(3.6,3.4,7.2),(-7.3,3,5.2),'One reusable pine; final quantity and placement deferred. Leaves grouped into sculptable clusters.')
tube('Pine trunk',[(0,0,0),(.02,0,2.8),(-.1,0,5.8),(0,0,7.2)],.18,bark,[1,.8,.4,.05])
for level in range(8):
    z=1+level*.73; radius=(7.2-z)*.25
    for j in range(7):
        ang=j*2*math.pi/7+level*.7
        end=(radius*math.cos(ang),radius*math.sin(ang),z-.22)
        tube('Pine branch',[(0,0,z+.2),end],.075,bark,[1,.35])
        for s in [.48,.79,1]:
            uv('Pine needle cluster',(end[0]*s,end[1]*s,z+.04),(.40,.33,.32),random.choice(greens),16,10)
finish(a,(8,0,0))

a=begin('A10','Bonsai_tree',(6.2,4.6,5.8),(-6.6,4.5,11.2),'Broad calm canopy. Root spread included in width. Branches need support review after clay is identified.')
tube('Twisting trunk',[(0,0,0),(-.45,.05,1),(-.16,0,2.3),(-.45,0,3.4),(.15,0,4.8)],.35,bark,[1.3,1,.85,.6,.3])
for j,(end,z) in enumerate([((-2,0,3.7),2.4),((1.7,.7,4.5),3),((-.2,-1.3,5.1),3.6),((.5,.5,5.6),4)]):
    tube('Bonsai branch',[(-.2,0,z),((end[0]-.2)*.5,end[1]*.5,end[2]-.3),end],.16,bark,[1,.7,.3])
    for k in range(9):
        ang=k*2.4; r=.25*math.sqrt(k)
        uv('Canopy pad',(end[0]+r*math.cos(ang),end[1]+r*math.sin(ang),end[2]+random.uniform(-.07,.15)),(.64,.54,.27),random.choice(greens),20,12)
for j in range(6):
    t=j*2*math.pi/6
    tube('Exposed root',[(0,0,.45),(.55*math.cos(t),.55*math.sin(t),.12),(.86*math.cos(t),.86*math.sin(t),.06)],.13,bark,[1,.7,.2])
finish(a,(20,0,0))

a=begin('A11','Sun_disc',(6.2,.45,6.2),(-3.8,7,24.8-3.1),'Bottom datum at z21.7. Disc requires hidden rear support; no floating attachment implied.')
bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=3.1,depth=.45,location=(0,0,3.1),rotation=(math.pi/2,0,0))
o=attach(bpy.context.object,gold); o.name='Sun disc'
b=o.modifiers.new('Rounded disc edge','BEVEL'); b.width=.08; b.segments=3
bpy.ops.object.modifier_apply(modifier=b.name); smooth(o)
for j in range(14):
    t=2*math.pi*j/14
    tube('Sun engraved-look rays',[(2.5*math.cos(t),-.235,3.1+2.5*math.sin(t)),(2.8*math.cos(t),-.235,3.1+2.8*math.sin(t))],.025,gold)
finish(a,(32,0,0))

a=begin('A12','Moon_pearl',(2.6,2.6,2.6),(4.7,7,24.4),'Optional pearl moon from reference. Additional rear pin required. Can omit for simpler peaceful composition.')
uv('Moon',(0,0,1.3),(1.3,1.3,1.3),moonmat,40,24)
finish(a,(42,0,0))

a=begin('A13','Cloud_bank',(6,1.4,1.8),(-4.5,5,20.2),'Single clay cloud module; repetitions must stay inside the 20cm square and use concealed supports.')
for j in range(10):
    x=-2.7+j*.60; z=.4+.45*math.exp(-(x/.95)**2)+random.uniform(-.1,.1)
    uv('Cloud coil',(x,0,z),(.52,.37,.25+random.uniform(0,.18)),cloudmat,20,12)
tube('Long cloud base',[(-3,0,.25),(-1.5,-.03,.2),(0,0,.2),(1.8,0,.2),(3,0,.3)],.16,cloudmat,[.2,1,1,.8,.2])
finish(a,(-31,-15,0))

a=begin('A14','Grass_tuft',(2.2,1.8,1.1),(-7,-6.8,1.2),'Grass is represented as thick grouped blades; do not reproduce every fine strand in fragile clay.')
for j in range(18):
    ang=j*2.4; r=random.uniform(.02,.55); p=(r*math.cos(ang),r*math.sin(ang),.06)
    tube('Grass blade',[p,(p[0]*1.35,p[1]*1.35,.55),(p[0]*1.8,p[1]*1.8,random.uniform(.6,1.15))],.055,random.choice(greens),[1,.7,.15])
uv('Tuft moss base',(0,0,.1),(.65,.50,.14),greens[1],20,12)
finish(a,(-20,-15,0))

a=begin('A15','Leaf_sprig',(2.8,1.8,.6),(-7.4,-4.5,5.2),'Standalone sprig for hand study; leaf minimum nominal thickness 0.9mm before normalization, final thickness must be measured locally.')
tube('Leaf stem',[(-1.2,0,.08),(0,0,.1),(1.2,0,.14)],.055,bark)
for j in range(5):
    x=-.9+j*.42
    for side in [-1,1]: leaf('Rounded leaf',(x,0,.12),.78,.34,greens[(j+2)%5],side*.9)
finish(a,(-11,-15,0))

def ribbon(name, points, widths, material):
    verts=[]
    for i,(p,w) in enumerate(zip(points,widths)):
        tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])
        side=Vector((1,0,0)) if abs(tangent.y)<.01 else Vector((tangent.y,-tangent.x,0)).normalized()
        for j in range(9):
            t=(j/8-.5)*2
            v=Vector(p)+side*w/2*t
            v.z+=.025*math.sin(i*2.2+j*1.3)+.025*math.cos(j*2)
            verts.append(v)
    faces=[]
    for i in range(len(points)-1):
        for j in range(8):
            k=i*9+j; faces.append((k,k+1,k+10,k+9))
    o=smooth(mesh(name,verts,faces,material))
    sol=o.modifiers.new('Water slab thickness','SOLIDIFY'); sol.thickness=.16
    return o

a=begin('A16','River_lower',(5.6,7.6,.32),(1.5,-5.5,1.24),'Lower water slab only. Opaque glazed-clay study; resin is not assumed.')
pts=[(.3,-3.8,.17),(-.25,-2.6,.18),(-.7,-1.3,.2),(.1,0,.19),(.8,1.2,.22),(.5,2.4,.24),(.1,3.8,.25)]
ribbon('River surface',pts,[3.8,4.8,4.3,3.7,3.0,2.5,2.3],water)
for j in range(18):
    y=random.uniform(-3.2,3.2); x=random.uniform(-1.2,1.2)
    tube('River ripple',[(x-.24,y,.28),(x,y+.07,.29),(x+.25,y,.28)],.026,foam)
finish(a,(0,-15,0))

def fall(code,name,height,station,planned):
    a=begin(code,name,(2.2,2.6,height),planned,'Separate waterfall module, downward flow. Final end interfaces and bank clearance are deferred to assembly.')
    pts=[(0,1.3,height),(.12,.6,height*.90),(-.12,.3,height*.65),(.14,-.10,height*.36),(0,-.65,.25),(.05,-1.3,.12)]
    ribbon('Waterfall sheet',pts,[1.5,1.65,1.35,1.4,1.8,2.2],water)
    for j in range(7):
        x=-.6+j*.2
        tube('Raised fall streak',[(x,1.1,height-.08),(x+.07,.61,height*.88),(x-.06,.29,height*.64),(x+.05,-.1,height*.36),(x,-.7,.30)],.032,foam,[.6,1,1,.8,.1])
    for j in range(7):
        uv('Splash cushion',(-.9+j*.3,-1.1,.16),(.22,.30,.11),foam,16,10)
    finish(a,station)

fall('A17','Fall_lower',4.0,(11,-15,0),(2.6,-4.0,1.3))
fall('A18','Fall_middle',6.0,(18,-15,0),(3.4,-.6,5.3))
fall('A19','Fall_upper',6.0,(25,-15,0),(3.7,3.3,11.3))

a=begin('A20','Flower_and_moss_patch',(2.2,1.8,.6),(-4.3,-5.7,5.2),'Optional grouped flowers; full-size standalone study, not a promise of individually modeled tiny petals in final clay.')
uv('Moss pad',(0,0,.12),(1,.75,.16),greens[1])
for j in range(6):
    t=j*2.4; x=.65*math.cos(t); y=.5*math.sin(t)
    tube('Flower stem',[(x,y,.12),(x,y,.42)],.045,greens[0])
    for k in range(5):
        t=k*2*math.pi/5
        uv('Petal',(x+.13*math.cos(t),y+.13*math.sin(t),.45),(.13,.09,.065),cloudmat,12,8)
    uv('Flower heart',(x,y,.48),(.07,.07,.06),gold,12,8)
finish(a,(34,-15,0))

# Asset libraries are independent and centered on their own bottom datum.
for a in assets:
    for o in a['collection'].all_objects: o.asset_mark() if o==a['root'] else None
    a['collection'].asset_mark()
    a['root'].location=Vector((0,0,0)); bpy.context.view_layer.update()
    bpy.data.libraries.write(str(OUT/'assets'/(a['id']+'_'+a['name']+'.blend')),{a['collection']},fake_user=True,compress=True)
    a['root'].location=a['station_cm']

# All technical dimensions are measured from evaluated geometry, including bevels/curves.
rows=[]
for a in assets:
    lo,hi=bbox(a['objects']); dims=hi-lo
    assert all(abs(dims[i]-a['target_cm'][i])<.008 for i in range(3)),(a['id'],dims)
    rows.append({k:v for k,v in a.items() if k not in {'collection','root','objects'}})
(OUT/'measurements'/'components.json').write_text(json.dumps({'units':'cm','stage':'01 separated component studies','assembly_verified':False,'concept':'Nuong dong binh yen','assets':rows},ensure_ascii=False,indent=2))
with (OUT/'measurements'/'components.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['id','component','length_X_cm','width_Y_cm','height_Z_cm','planned_x_cm','planned_y_cm','planned_bottom_z_cm'])
    for a in assets: w.writerow([a['id'],a['name'],*a['actual_cm'],*a['planned_origin_cm']])

# Presentation geometry is never included in asset dimensions.
current=collection('ZZ_PRESENTATION_ONLY')
def text(name,body,loc,size=.56):
    c=bpy.data.curves.new(name,'FONT'); c.body=body; c.size=size; c.extrude=.001
    c.align_x='CENTER'; c.align_y='CENTER'
    o=bpy.data.objects.new(name,c); current.objects.link(o); o.location=loc; c.materials.append(labelmat)
    return o
for a in assets:
    x,y,z=a['station_cm']; d=a['target_cm']
    text(a['id']+' label',a['id']+' / '+a['name'].replace('_',' '),(x,y-d[1]/2-1.1,.03),.44)
    text(a['id']+' dimensions',' × '.join(f'{v:g}' for v in d)+' cm',(x,y-d[1]/2-1.9,.03),.40)
cube('Backdrop',(5,6,-.32),(102,72,.4),boardmat,.15)

def camera(name,loc,target,ortho):
    c=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,c); current.objects.link(o)
    o.location=loc; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    c.type='ORTHO'; c.ortho_scale=ortho; c.lens=50; c.clip_end=500
    return o
cam=camera('Library overview',(48,-76,108),(5,5,1.4),108)
scene.camera=cam
def area(name,loc,power,size,target):
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size
    o=bpy.data.objects.new(name,d); current.objects.link(o); o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler(); return o
area('Large soft key',(-24,-30,65),42000,38,(2,4,0))
area('Cool rim',(44,35,40),28000,30,(4,5,0))
scene.render.resolution_x=2000; scene.render.resolution_y=1450; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
for screen in bpy.data.screens:
    for ar in screen.areas:
        if ar.type=='VIEW_3D':
            ar.spaces.active.region_3d.view_perspective='CAMERA'
scene['stage']='01: separate components; NOT assembled'
scene['units']='1 Blender unit = 1 cm. Measurement CSV includes evaluated world-space bounding boxes.'
scene['final_envelope_cm']=[20,20,27.9]
scene['concept']='Nương dòng bình yên / Resting by the quiet stream'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Nuong_dong_binh_yen_components_v01.blend'),compress=True)
scene.render.filepath=str(OUT/'renders'/'01_component_library.png')
bpy.ops.render.render(write_still=True)

# Detail plates: isolated components in their stations, with presentation lights.
for filename,ids,loc,target,scale in [
    ('02_horses',['A06','A07','A08'],(-22,-22,12),(-18,0,2.3),33),
    ('03_mountain_modules',['A02','A03','A04','A05'],(16,-34,55),(13,22,2),78),
    ('04_botanical_and_sky',['A09','A10','A11','A12'],(34,-23,17),(25,0,2.6),46),
    ('05_water_and_small_details',['A13','A14','A15','A16','A17','A18','A19','A20'],(5,-52,45),(3,-15,1),78),
]:
    for a in assets: a['collection'].hide_render=a['id'] not in ids
    for o in bpy.data.collections['ZZ_PRESENTATION_ONLY'].objects:
        if o.type=='FONT': o.hide_render=o.name[:3] not in ids
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=scale
    scene.render.resolution_x=1800; scene.render.resolution_y=1050
    scene.render.filepath=str(OUT/'renders'/(filename+'.png'))
    bpy.ops.render.render(write_still=True)

# Individual geometry thumbnails have consistent orientation and no unrelated labels.
for a in assets:
    for b in assets: b['collection'].hide_render=b['id']!=a['id']
    for o in bpy.data.collections['ZZ_PRESENTATION_ONLY'].objects:
        if o.type=='FONT': o.hide_render=True
    x,y,z=a['station_cm']; dx,dy,dz=a['target_cm']; target=Vector((x,y,dz*.45))
    cam.location=target+Vector((dx*.65+4,-max(dx,dy)*1.5-5,max(dx,dy,dz)*.95+3))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    corners=[Vector((x+sx*dx/2,y+sy*dy/2,zz)) for sx in [-1,1] for sy in [-1,1] for zz in [0,dz]]
    inv=cam.rotation_euler.to_matrix().transposed()
    projected=[inv@(v-target) for v in corners]
    cam.data.ortho_scale=max(max(v[i] for v in projected)-min(v[i] for v in projected) for i in [0,1])*1.16
    scene.render.resolution_x=720; scene.render.resolution_y=720
    scene.cycles.samples=20
    scene.render.filepath=str(OUT/'renders'/(a['id']+'.png'))
    bpy.ops.render.render(write_still=True)
print('STAGE_01_COMPLETE',flush=True)
