"""Read a saved Blender scene and audit only its two hand/arm mesh surfaces."""
import bpy,bmesh,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
if not bpy.data.filepath:raise RuntimeError('Load the saved model before auditing it')
out=Path(bpy.data.filepath).resolve().parent;out.mkdir(parents=True,exist_ok=True)
reports=[]
for name in ('Body_raised_arm_five_fingers','Body_relaxed_arm_five_fingers'):
    ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);seen=set();counts=[]
    for v in bm.verts:
        if v in seen:continue
        stack=[v];seen.add(v);n=0
        while stack:
            q=stack.pop();n+=1
            for edge in q.link_edges:
                other=edge.other_vert(q)
                if other not in seen:seen.add(other);stack.append(other)
        counts.append(n)
    boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges)
    reports.append({'object':name,'vertices':len(bm.verts),'components':sorted(counts,reverse=True),'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'result':'PASS' if len(counts)==1 and nonmanifold==0 else 'FAIL'});bm.free()
report={'revision':bpy.context.scene.get('revision'),'result':'PASS' if all(r['result']=='PASS' for r in reports) else 'FAIL','hands':reports,'scope':'Surface connectivity and closedness, not a claim that anatomy or pose is perfect.'}
(out/'hand_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if report['result']!='PASS':raise RuntimeError('Hand surface audit found a defect')
