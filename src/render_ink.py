"""Thin, colored silhouette lines on selected original meshes."""
import bpy

def install(scale=1.0):
    s=bpy.context.scene;s.render.use_freestyle=True;s.render.line_thickness=1.0
    settings=bpy.context.view_layer.freestyle_settings
    for line in list(settings.linesets):settings.linesets.remove(line)
    specs=[('Hair ink',(.075,.062,.135),.80),('Skin ink',(.22,.12,.15),.60),('Cotton ink',(.14,.23,.29),.72)]
    collections={}
    for name,color,width in specs:
        collection=bpy.data.collections.new(name);s.collection.children.link(collection);collections[name]=collection
        line=settings.linesets.new(name);line.linestyle=bpy.data.linestyles.new(name)
        line.linestyle.color=color;line.linestyle.alpha=.80;line.linestyle.thickness=width*scale
        line.select_by_collection=True;line.collection=collection
        for key,value in {'select_silhouette':name!='Cotton ink','select_external_contour':True,'select_contour':False,'select_border':False,'select_crease':False,'select_material_boundary':False,'select_edge_mark':False}.items():
            if hasattr(line,key):setattr(line,key,value)
    for ob in list(s.objects):
        if ob.type!='MESH':continue
        name=ob.name;group=None
        if name.startswith(('HairTop_','HairLong_')):group='Hair ink'
        elif name.startswith(('Body_raised_arm_five','Body_relaxed_arm_five','Body_front_leg','Body_rear_leg','Head_original')):group='Skin ink'
        elif name.startswith(('Clothes_pajama_shirt','Clothes_soft_pajama_shorts','Accessory_inflated_cotton_pillow','HeadWear_bow_')):group='Cotton ink'
        if group:collections[group].objects.link(ob)
