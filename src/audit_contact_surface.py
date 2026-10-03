"""Check the resulting fingertip-to-headband gap against actual mesh triangles."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[1];out=Path('/build')/root.name/'pending-preview';out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene;assert scene.get('contact_adjustment_applied'),'No contact adjustment in this scene'
ob=bpy.data.objects['HeadWear_soft_headband'];deps=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(deps);me=ev.to_mesh()
points=[ev.matrix_world@v.co for v in me.vertices];faces=[tuple(p.vertices) for p in me.polygons];tree=BVHTree.FromPolygons(points,faces)
center=Vector(scene['contact_index_tip_center']);radius=scene['contact_index_pad_radius'];point,normal,index,distance=tree.find_nearest(center);gap=distance-radius
report={'revision':scene.get('revision'),'result':'PASS' if -.003<=gap<=.015 else 'FAIL','contact_center':list(center),'closest_band_point':list(point),'pad_radius':radius,'triangle_surface_gap':gap,'contact_candidate_tests':scene['contact_candidate_tests'],'units':'Blender authoring units','scope':'Actual triangle-distance check for the authored index pad and headband. Other contacts and overall appearance still require inspection.'}
(out/'contact_search_progress.json').write_text(json.dumps({'completed':scene['contact_candidate_tests'],'requested':scene['contact_candidate_tests'],'stage':'previous search complete; selected pose audited in '+str(scene.get('revision')),'running':False,'scope':'Geometry candidate tests, not build-and-review iterations'},indent=2))
(out/'contact_surface_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));ev.to_mesh_clear()
if report['result']!='PASS':raise RuntimeError('Fingertip contact outside tolerance')
