"""Reversible selective-contour render study on the original Blender model."""
import bpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from render_ink import install
s=bpy.context.scene;install(s.render.resolution_x/720);s.eevee.taa_render_samples=24
s.render.filepath=str(root/'renders/studies/T04-clean-contours.png')
bpy.ops.render.render(write_still=True)
print('SELECTIVE_CONTOUR_STUDY_COMPLETE',s.render.filepath)
