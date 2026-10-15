"""Anatomical miniature horse studies, authored mesh, cm units.
blender -b -t 4 --python-exit-code 1 --python .../sculpt_horses.py -- --hero
Omit --hero for the complete three-pose library.
"""
import bpy, math, json, sys
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix

OUT=Path(__file__).resolve().parents[1]
HERO='--hero' in sys.argv
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene; sc.name='02_HORSE_ATELIER'
sc.unit_settings.system='METRIC'; sc.unit_settings.scale_length=.01
sc.unit_settings.length_unit='CENTIMETERS'
sc.render.engine='CYCLES'; sc.cycles.samples=40; sc.cycles.use_denoising=False
sc.render.threads_mode='FIXED'; sc.render.threads=4
sc.view_settings.view_transform='AgX'
sc.world=bpy.data.worlds.new('Atelier atmosphere'); sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.17,.21,.24,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
sc.render.image_settings.file_format='PNG'
current=None; horses=[]

def material(name,color,rough=.45,metallic=0):
    m=bpy.data.materials.new(name); m.use_nodes=True; m.diffuse_color=(*color,1)
    p=m.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metallic
    return m
ivory=material('01 | warm ivory clay',(.75,.72,.64),.42)
hair=material('02 | carved warm ivory mane',(.63,.58,.48),.46)
hoofmat=material('03 | natural warm horn',(.26,.22,.16),.40)
eyemat=material('04 | deep umber eye',(.023,.013,.007),.22)
socketmat=material('05 | recessed skin',(.15,.10,.065),.58)
nostrilmat=material('05b | unlit depth of nostril',(.040,.024,.014),.78)
earmat=material('06 | ear inner clay',(.40,.31,.23),.56)
base=material('07 | charcoal atelier',(.028,.043,.046),.58)
for m in [ivory,hair]:
    nt=m.node_tree; n=nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=190
    n.inputs['Detail'].default_value=2; b=nt.nodes.new('ShaderNodeBump')
    b.inputs['Strength'].default_value=.10; b.inputs['Distance'].default_value=.006
    nt.links.new(n.outputs['Fac'],b.inputs['Height']); nt.links.new(b.outputs['Normal'],nt.nodes['Principled BSDF'].inputs['Normal'])

def col(name):
    c=bpy.data.collections.new(name); sc.collection.children.link(c); return c
def attach(o,mat=None):
    for c in list(o.users_collection): c.objects.unlink(o)
    current.objects.link(o)
    if mat: o.data.materials.append(mat)
    return o
def smooth(o):
    for p in o.data.polygons: p.use_smooth=True
    return o
def mesh(name,vs,fs,mat):
    d=bpy.data.meshes.new(name); d.from_pydata(vs,[],fs); d.update()
    o=bpy.data.objects.new(name,d); current.objects.link(o)
    if mat: d.materials.append(mat)
    return smooth(o)
def uv(name,loc,scale,mat,rotation=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=24,location=loc)
    o=attach(bpy.context.object,mat); o.name=name; o.scale=scale
    if rotation is not None: o.rotation_euler=rotation
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return smooth(o)
def curve(name,points,radius,mat,radii=None):
    d=bpy.data.curves.new(name,'CURVE'); d.dimensions='3D'; d.resolution_u=12
    d.bevel_depth=radius; d.bevel_resolution=3; d.use_fill_caps=True
    s=d.splines.new('BEZIER'); s.bezier_points.add(len(points)-1)
    for i,(b,p) in enumerate(zip(s.bezier_points,points)):
        b.co=p; b.handle_left_type='AUTO'; b.handle_right_type='AUTO'
        if radii: b.radius=radii[i]
    o=bpy.data.objects.new(name,d); current.objects.link(o)
    if mat: d.materials.append(mat)
    return o
def cat(values,steps=7):
    vs=[np.asarray(v,dtype=float) for v in values]; out=[]
    for i in range(len(vs)-1):
        a=vs[max(0,i-1)]; b=vs[i]; c=vs[i+1]; d=vs[min(i+2,len(vs)-1)]
        for j in range(steps):
            t=j/steps
            out.append((2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)*.5)
    out.append(vs[-1]); return out
def loft(name,points,widths,depths,mat,sides=40,corrugation=0):
    rows=cat([(*p,w,d) for p,w,d in zip(points,widths,depths)],6)
    vs=[]; fs=[]
    for i,row in enumerate(rows):
        p=Vector(row[:3]); t=Vector(rows[min(i+1,len(rows)-1)][:3])-Vector(rows[max(i-1,0)][:3]); t.normalize()
        y=Vector((0,1,0)); y=(y-y.dot(t)*t).normalized(); n=t.cross(y).normalized()
        for j in range(sides):
            a=2*math.pi*j/sides; ripple=1+corrugation*math.cos(a*11+i*.05)
            vs.append(p+y*math.cos(a)*row[3]*ripple+n*math.sin(a)*row[4]*ripple)
    for i in range(len(rows)-1):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides; fs.append((a,b,b+sides,a+sides))
    fs.extend([tuple(reversed(range(sides))),tuple(range((len(rows)-1)*sides,len(rows)*sides))])
    return mesh(name,vs,fs,mat)
def fuse(objects,name,voxel=.026):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects: o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.convert(target='MESH'); bpy.ops.object.join(); o=bpy.context.object; o.name=name
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
    # All sources are authored with consistently oriented loft cross sections.
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    r=o.modifiers.new('Continuous sculpt volume','REMESH'); r.mode='VOXEL'; r.voxel_size=voxel; r.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=r.name)
    s=o.modifiers.new('Relax sculpt surface','SMOOTH'); s.factor=.65; s.iterations=4
    bpy.ops.object.modifier_apply(modifier=s.name)
    return smooth(o)
def boolean(ob,cutter):
    bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('Carve anatomical recess','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(cutter,do_unlink=True)

def body_barrel():
    # Dorsal and ventral profiles are independently designed, not a chain of balls.
    rows=cat([(-1.65,.26,3.48,2.63),(-1.40,.53,3.98,2.35),(-1.07,.65,4.10,2.28),(-.65,.71,4.00,2.18),(0,.73,3.94,2.14),(.55,.69,3.97,2.27),(1.05,.64,4.08,2.48),(1.50,.52,3.96,2.63),(1.78,.30,3.65,2.78),(1.88,.04,3.23,3.10)],6)
    vs=[]; fs=[]; sides=56
    for x,w,top,bottom in rows:
        cz=(top+bottom)/2
        for j in range(sides):
            a=j*2*math.pi/sides
            # Slightly narrow back and fuller lower ribs, taper toward the flank.
            y=math.sin(a)*w*(1-.10*max(0,math.cos(a)))
            z=cz+(top-cz)*math.cos(a)
            vs.append((x*1.13,y,z))
    for i in range(len(rows)-1):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides; fs.append((a,b,b+sides,a+sides))
    fs.extend([tuple(reversed(range(sides))),tuple(range((len(rows)-1)*sides,len(rows)*sides))])
    return mesh('01 | ribcage, back and abdominal tuck',vs,fs,ivory)

def hoof(name,foot):
    # Sloping hoof wall: the coronet sits behind the broad toe, not on a cube.
    vs=[]; fs=[]; sides=48
    for z,rx,ry,shift in [(0,.255,.185,-.055),(.045,.25,.183,-.045),(.26,.17,.15,.05),(.30,.145,.135,.065)]:
        for j in range(sides):
            a=2*math.pi*j/sides
            vs.append((foot[0]+shift+rx*math.cos(a),foot[1]+ry*math.sin(a),z))
    for i in range(3):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides; fs.append((a,b,b+sides,a+sides))
    fs.extend([tuple(reversed(range(sides))),tuple(range(3*sides,4*sides))])
    o=mesh(name,vs,fs,hoofmat)
    b=o.modifiers.new('Rounded horn wall edges','BEVEL'); b.width=.018; b.segments=3
    bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=b.name)
    return o

def lock(name,points,widths,mat,thick=.055,grooves=3,facing=None):
    """Closed lenticular hair lock with longitudinal grooves cut into its surface."""
    rows=cat([(*p,w) for p,w in zip(points,widths)],7)
    vs=[]; fs=[]; cols=20
    for i,row in enumerate(rows):
        p=Vector(row[:3]); tangent=Vector(rows[min(i+1,len(rows)-1)][:3])-Vector(rows[max(i-1,0)][:3]); tangent.normalize()
        # Front-facing hair ribbons expose broad sculpted surfaces to side views.
        forward=Vector((0,-1,0)) if facing is None else Vector(facing)
        across=tangent.cross(forward).normalized()
        normal=across.cross(tangent).normalized()
        for back in [False,True]:
            for j in range(cols+1):
                s=-1+2*j/cols
                arch=math.sqrt(max(0,1-s*s))
                groove=sum(math.exp(-((s-k/(grooves/2))/.075)**2) for k in range(-grooves//2,grooves//2+1))
                h=(-thick*.45 if back else thick*(arch-.20*groove*arch))
                vs.append(p+across*s*row[3]+normal*h)
    stride=2*(cols+1)
    for i in range(len(rows)-1):
        for layer in [0,1]:
            for j in range(cols):
                k=i*stride+layer*(cols+1)+j
                face=(k,k+1,k+1+stride,k+stride)
                fs.append(face if layer==0 else tuple(reversed(face)))
        for j in [0,cols]:
            k=i*stride+j; fs.append((k,k+stride,k+stride+cols+1,k+cols+1))
    for i in [0,len(rows)-1]:
        k=i*stride
        for j in range(cols): fs.append((k+j,k+cols+1+j,k+cols+2+j,k+j+1))
    return mesh(name,vs,fs,mat)

def ear(name,basepoint,axis,F,side):
    vs=[]; fs=[]; nl=20; nw=16
    for layer in [0,1]:
        for i in range(nl+1):
            t=i/nl; centre=basepoint+axis*.46*t+Vector((0,side*.04*t*t,0))
            width=.04*(1-t)+.105*math.sin(math.pi*t)**.8+.003
            for j in range(nw+1):
                s=-1+2*j/nw
                depth=(.045+.035*abs(s)**1.4-.045*(1-s*s)*math.sin(math.pi*t)) if layer==0 else -.045
                vs.append(centre+Vector((0,s*width,0))+F*depth)
    stride=(nl+1)*(nw+1)
    for layer in [0,1]:
        for i in range(nl):
            for j in range(nw):
                k=layer*stride+i*(nw+1)+j; face=(k,k+1,k+nw+2,k+nw+1)
                fs.append(face if layer==0 else tuple(reversed(face)))
    edge=list(range(nw+1))+[i*(nw+1)+nw for i in range(1,nl+1)]+[nl*(nw+1)+j for j in range(nw-1,-1,-1)]+[i*(nw+1) for i in range(nl-1,0,-1)]
    for k,j in zip(edge,edge[1:]+edge[:1]): fs.append((k,j,j+stride,k+stride))
    o=mesh(name,vs,fs,ivory); o.data.materials.append(earmat)
    for p in o.data.polygons:
        if p.index<nl*nw:
            i=p.index//nw; j=p.index%nw
            if 3<i<nl-3 and 3<j<nw-3: p.material_index=1
    return o

def build_horse(code,pose,station):
    global current
    current=col(code+'_'+pose)
    skin=[body_barrel()]
    # Defined but restrained muscle volumes, blended into a continuous skin.
    for side in [-1,1]:
        skin.append(uv('Scapular plane',(-1.28,side*.43,3.20),(.49,.30,.65),ivory,(0,-.36,0)))
        skin.append(uv('Gluteal plane',(1.24,side*.39,3.37),(.64,.30,.57),ivory))
        skin.append(uv('Pectoral mass',(-1.60,side*.22,3.00),(.30,.25,.38),ivory,(0,.2,0)))
    if pose=='standing':
        neck=[(-1.20,0,3.38),(-1.62,0,3.94),(-1.98,0,4.49),(-2.22,0,4.94),(-2.34,0,5.22)]
        poll=Vector((-2.34,0,5.22)); F=Vector((-.80,0,-.60)).normalized()
    elif pose=='grazing':
        neck=[(-1.20,0,3.4),(-1.72,0,3.10),(-2.23,0,2.54),(-2.57,0,1.98),(-2.65,0,1.63)]
        poll=Vector((-2.65,0,1.63)); F=Vector((-.18,0,-.984)).normalized()
    else:
        neck=[(-1.20,0,3.4),(-1.82,0,3.13),(-2.40,0,2.55),(-2.72,0,1.92),(-2.80,0,1.50)]
        poll=Vector((-2.80,0,1.50)); F=Vector((-.05,0,-.999)).normalized()
    N=Vector((F.z,0,-F.x)).normalized(); Y=Vector((0,1,0))
    headrot=Matrix((F,Y,N)).transposed().to_euler()
    def hp(u,y,n): return poll+F*u+Y*y+N*n
    skin.append(loft('02 | neck arch and throat',neck,[.51,.46,.35,.265,.22],[.71,.62,.47,.32,.25],ivory))
    # Long facial planes, flared nostril region and angular lower jaw.
    profile=[(-.12,.12,.17,.14),(.05,.22,.24,.23),(.27,.305,.25,.32),(.48,.275,.22,.34),(.70,.21,.18,.25),(.96,.18,.135,.21),(1.14,.22,.15,.22),(1.32,.285,.18,.20),(1.43,.25,.14,.17),(1.49,.10,.06,.08)]
    rows=cat(profile,6); vs=[]; fs=[]; sides=56
    for u,w,up,down in rows:
        for j in range(sides):
            a=j*2*math.pi/sides; c=math.cos(a)
            # A flatter nasal plane than the rounded cheeks and muzzle.
            height=(up if c>=0 else down)*c
            yy=w*math.sin(a)
            vs.append(hp(u,yy,height))
    for i in range(len(rows)-1):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides; fs.append((a,b,b+sides,a+sides))
    fs.extend([tuple(reversed(range(sides))),tuple(range((len(rows)-1)*sides,len(rows)*sides))])
    skin.append(mesh('03 | skull, nasal bridge and muzzle',vs,fs,ivory))
    skin.append(uv('04 | defined mandibular cheek',hp(.37,0,-.18),(.35,.29,.25),ivory,headrot))
    for side in [-1,1]:
        skin.append(uv('Ear root',hp(-.01,side*.20,.19),(.105,.09,.09),ivory,headrot))
        skin.append(uv('Orbital bone and eyelid support',hp(.28,side*.265,.105),(.15,.065,.105),ivory,headrot))
    feet=[]
    for rear in [False,True]:
        for side in [-1,1]:
            y=side*.48; offset=.22 if side==1 else -.12
            if not rear:
                pts=[(-1.10,y*.60,3.61),(-1.34,y,3.02),(-.94+offset*.4,y,2.53),(-1.12+offset,y,1.78),(-1.18+offset,y,1.48),(-1.22+offset,y,.67),(-1.22+offset,y,.47),(-1.39+offset,y,.27)]
                ws=[.18,.27,.235,.145,.16,.105,.14,.125]
                ds=[.25,.32,.25,.19,.17,.12,.16,.12]
            else:
                offset=.27 if side==1 else -.08
                pts=[(1.15,y*.60,3.70),(1.02,y,3.20),(.79+offset*.3,y,2.78),(.66+offset*.6,y,2.51),(1.29+offset,y,1.72),(1.47+offset,y,1.35),(1.19+offset,y,.64),(1.12+offset,y,.45),(.99+offset,y,.27)]
                ws=[.18,.29,.28,.24,.18,.16,.11,.14,.12]
                ds=[.24,.40,.33,.27,.245,.17,.12,.15,.12]
            pts=[(p[0]*1.13,p[1],p[2]) for p in pts]
            skin.append(loft(('Hind' if rear else 'Fore')+' limb anatomical taper',pts,ws,ds,ivory,36))
            foot=Vector(pts[-1]); foot.x-=.045; feet.append(foot)
            hoof(('Hind' if rear else 'Fore')+' hoof '+str(side),foot)
            # Tendon planes and fetlock transition, blended before remeshing.
            skin.append(curve('Flexor tendon ridge',[Vector(pts[-4])+Vector((.09,0,0)),Vector(pts[-3])+Vector((.09,0,0)),Vector(pts[-2])+Vector((.08,0,0))],.034,ivory,[.7,1,.35]))
            skin.append(uv('Fetlock bone',Vector(pts[-2])+Vector((.035,0,.015)),(.155,.14,.17),ivory))
            if not rear:
                skin.append(uv('Carpus | defined front knee',Vector(pts[4])+Vector((-.018,0,0)),(.18,.165,.165),ivory))
    body=fuse(skin,'BODY | continuous anatomical sculpt')
    def face_width(u,n):
        w=float(np.interp(u,[p[0] for p in profile],[p[1] for p in profile]))
        radius=float(np.interp(u,[p[0] for p in profile],[p[2] if n>=0 else p[3] for p in profile]))
        return w*math.sqrt(max(.02,1-(n/radius)**2))
    # Actual recessed eye sockets and nostrils, not painted black dots.
    for side in [-1,1]:
        ec=hp(.28,side*.285,.105)
        offsets=[-.12,-.08,0,.08,.12]
        cutter=loft('Almond eye opening carving tool',[ec+F*u for u in offsets],[.015,.12,.14,.12,.015],[.004,.041,.058,.041,.004],None,40)
        boolean(body,cutter)
        eyept=hp(.28,side*.287,.105)
        uv('EYE | inset globe under integrated lids',eyept,(.082,.050,.046),eyemat,headrot)
        nc=hp(1.24,side*.24,.025)
        boolean(body,uv('Nostril carving tool',nc,(.14,.10,.080),None,headrot))
        uv('NOSTRIL | deep cavity liner',hp(1.24,side*.165,.018),(.112,.025,.060),nostrilmat,headrot)
        points=[]
        for t in range(17):
            ang=t*math.pi/16; u=1.24+math.cos(ang)*.14; nn=.025+math.sin(ang)*.082
            yy=face_width(u,nn)
            points.append(hp(u,side*(yy-.012),nn))
        curve('Alar rim | attached to muzzle',points,.018,ivory,[.2]+[1]*15+[.2])
        # Subtle mouth slit and short lower lip follow the flared muzzle.
        seam=[(1.06,-.13),(1.26,-.135),(1.42,-.11),(1.48,-.055)]
        curve('MOUTH | recessed lip seam',[hp(u,side*(face_width(u,n)-.005),n) for u,n in seam],.010,socketmat,[.25,1,.7,.2])
        lower=[(1.20,-.163),(1.34,-.16),(1.44,-.13)]
        curve('Lower lip edge',[hp(u,side*(face_width(u,n)-.008),n) for u,n in lower],.016,ivory,[.3,1,.3])
        if pose=='standing':
            axis=(-F*.23+N*.90).normalized(); front=F
        else:
            axis=Vector((-.35,side*.15,.925)).normalized()
            front=(F-axis*F.dot(axis)).normalized()
        ear('EAR | concave shell '+str(side),hp(-.015,side*.21,.20),axis,front,side)
    # Mane: a continuous draped volume, covered in broad overlapping carved locks.
    neckrows=cat([(*p,w,d) for p,w,d in zip(neck,[.51,.46,.35,.265,.22],[.71,.62,.47,.32,.25])],12)
    def mane_point(t,v):
        f=max(0,min(.9999,t))*(len(neckrows)-1); k=int(f); row=neckrows[k]*(1-(f-k))+neckrows[min(k+1,len(neckrows)-1)]*(f-k)
        p=Vector(row[:3]); tangent=(Vector(neckrows[min(k+1,len(neckrows)-1)][:3])-Vector(neckrows[max(k-1,0)][:3])).normalized()
        normal=tangent.cross(Y)
        if normal.z<0: normal=-normal
        if pose!='standing':
            # A hanging mane follows gravity rather than rigidly rotating with
            # the neck's local transverse frame.
            return p+normal*(row[4]-.02)-Y*(row[3]-.02)*math.sin(min(1,v)*math.pi/2)+Vector((-.065*v+.025*math.sin(t*15+v*4)*v,0,-(.72-.30*t)*v))
        angle=v*1.70
        return p+normal*(row[4]-.02)*math.cos(angle)-Y*(row[3]-.02)*math.sin(angle)+Vector((.05*math.sin(t*15+v*4)*v,0,-.18*v*v))
    vs=[]; fs=[]; nt=64; nv=18
    for i in range(nt+1):
        t=i/nt
        for j in range(nv+1):
            v=j/nv*(1.02+.06*math.sin(t*23))
            if pose!='standing': v*=1-.40*t
            vs.append(mane_point(t,v))
    for i in range(nt):
        for j in range(nv):
            k=i*(nv+1)+j; fs.append((k,k+1,k+nv+2,k+nv+1))
    cap=mesh('MANE | continuous draped underlayer',vs,fs,hair)
    sol=cap.modifiers.new('Mane underlayer thickness','SOLIDIFY'); sol.thickness=.045
    for j,t in enumerate([.08,.22,.38,.53,.68,.83,.98]):
        drift=[.08,.16,.23,.29,.24,.27,.30][j]; end=[1.2,1.4,1.25,1.5,1.32,1.4,1.3][j]
        if pose!='standing': drift=-.06; end*=.80*(1-.35*t)
        points=[mane_point(t-drift*v**1.15+.02*math.sin(v*5),v*end) for v in [0,.18,.38,.61,.82,1]]
        widths=[.09,.17,.185,.16,.10,.009]
        lock('MANE | swept primary lock %02d'%j,points,widths,hair,.055,4)
    for j,t in enumerate([.15,.31,.46,.61,.76,.91]):
        drift=.24 if pose=='standing' else -.06
        end=1.1 if pose=='standing' else 1.1*(1-.35*t)
        points=[mane_point(t-drift*v**1.2,v*end)+Vector((0,-.025,0)) for v in [0,.25,.5,.8,1]]
        lock('MANE | interleaved secondary curl',points,[.065,.115,.12,.08,.006],hair,.045,3)
    # Forelock drapes from between the ears down the frontal plane.
    for j in range(4):
        yy=(j-1.5)*.075
        end=[.48,.78,.62,.55][j]
        lock('FORELOCK | forehead curl', [hp(-.08,yy,.24),hp(.12,yy-.035,.255),hp(.35,yy-.06,.24),hp(end,yy-.025,.17)], [.065,.095,.07,.005],hair,.045,2,facing=N)
    # A dimensional dock and flowing tail core, with sculpted surface channels.
    tailpoints=[(1.92,0,3.65),(2.30,-.02,3.69),(2.75,-.10,3.21),(2.83,-.15,2.28),(2.95,-.23,1.30),(3.18,-.25,.64)]
    loft('TAIL | flowing fluted core',tailpoints,[.16,.235,.24,.21,.16,.018],[.17,.23,.23,.20,.14,.018],hair,64,.07)
    for j in range(7):
        s=(j-3)/3
        points=[(2.02,-.11+s*.08,3.68),(2.36+s*.08,-.20+s*.07,3.55),(2.70+s*.09,-.29,2.95),(2.74+s*.09,-.30,2.1),(2.92+s*.11,-.32,1.27),(3.20+s*.15,-.35,.82+abs(s)*.10),(3.10+s*.14,-.31,.58+abs(s)*.14)]
        lock('TAIL | long carved lock %02d'%j,points,[.065,.10,.105,.10,.07,.05,.005],hair,.045,3)
    # Bake everything to mesh and use one UNIFORM scale for all poses.
    bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
    objects=list(current.objects); baked=[]; scale=1.08
    for o in objects:
        d=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg)
        d.transform(Matrix.Scale(scale,4)@o.matrix_world)
        n=bpy.data.objects.new(o.name,d); current.objects.link(n); baked.append(n)
    for o in objects: bpy.data.objects.remove(o,do_unlink=True)
    bpy.context.view_layer.update()
    pts=[v.co for o in baked for v in o.data.vertices]
    lo=Vector([min(v[i] for v in pts) for i in range(3)]); hi=Vector([max(v[i] for v in pts) for i in range(3)])
    offset=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    for o in baked:
        for v in o.data.vertices: v.co-=offset
    root=bpy.data.objects.new(code+'_DATUM_CM',None); current.objects.link(root)
    for o in baked: o.parent=root
    root['uniform_scale']=scale; root['units']='cm'; root['pose']=pose
    root['body_features']='ribcage/scapula/gluteal planes/mandible/carved nostrils/eyelids/concave ears/fetlocks/sloped hooves/carved hair locks'
    current.asset_mark()
    bpy.data.libraries.write(str(OUT/'assets'/(code+'_'+pose+'.blend')),{current},fake_user=True,compress=True)
    root.location=station
    dims=[round(x,4) for x in hi-lo]
    report=dict(id=code,pose=pose,dimensions_cm=dims,uniform_scale=scale,station_cm=station,
                withers_height_cm=round(4.10*scale-offset.z,3),body_vertices=sum(len(o.data.vertices) for o in baked),
                mesh_objects=len(baked),collection=current.name,hoof_coronet_centers_cm=[[round((f*scale-offset)[i],4) for i in range(3)] for f in feet])
    horses.append((report,current,root)); print('HORSE_READY',report,flush=True)

build_horse('H01','standing',(0,0,0))
if not HERO:
    build_horse('H02','grazing',(11,0,0)); build_horse('H03','drinking',(22,0,0))

current=col('ZZ_STUDIO_NOT_PART_OF_MODEL')
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.015)); attach(bpy.context.object,base).name='Atelier floor'
def area(name,loc,power,size,target,color):
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size; d.color=color
    o=bpy.data.objects.new(name,d); current.objects.link(o); o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Sculpt raking softbox',(-7,-8,12),1100,7,(-.5,0,3),(1,.93,.82))
area('Cool contour softbox',(5,5,9),1350,6,(0,0,3),(.66,.81,1))
area('Face bounce',(-8,4,6),550,5,(-2,0,4),(1,.96,.88))
cd=bpy.data.cameras.new('Atelier camera'); cam=bpy.data.objects.new('Atelier camera',cd); current.objects.link(cam)
cd.type='ORTHO'; cd.clip_end=500; sc.camera=cam
def aim(loc,target,scale):
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cd.ortho_scale=scale
aim((-9,-15,8),(-.3,0,3.1),10.5)
sc.render.resolution_x=1800; sc.render.resolution_y=1450; sc.render.resolution_percentage=100
sc['stage']='02 — horse anatomy and carved mane studies; no scene assembly'
sc['final_scene_footprint_cm']=[20,20]
sc['authorship']='Procedurally authored meshes; no downloaded third-party model.'
manifest={'units':'cm','all_poses_same_uniform_scale':True,'horses':[r for r,c,o in horses],
          'not_verified':['clay process or strength','final terrain contacts','watertight manufacturing mesh']}
(OUT/'measurements'/'horses.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
filename='Horse_hero_working.blend' if HERO else 'Nuong_dong_binh_yen_horses_v02.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/filename),compress=True)
if '--no-render' not in sys.argv:
    sc.render.filepath=str(OUT/'renders'/'01_hero_three_quarter.png'); bpy.ops.render.render(write_still=True)
print('SCULPT_BUILD_COMPLETE',flush=True)
