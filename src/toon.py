import bpy

def install():
    for mat in bpy.data.materials:
        if not mat.use_nodes:continue
        n=mat.node_tree.nodes;links=mat.node_tree.links
        p=n.get('Principled BSDF');output=n.get('Material Output')
        if p is None or output is None:continue
        emit=n.new('ShaderNodeEmission');emit.name='Illustration surface'
        emit.inputs['Strength'].default_value=1
        texture=next((x for x in n if x.type=='TEX_IMAGE'),None)
        color=p.inputs['Base Color'].default_value[:]
        if mat.name in ['Original violet iris','eyeWhite','lash','mouth','pinkLight','Cyan halo inlay']:
            if texture:links.new(texture.outputs['Color'],emit.inputs['Color'])
            else:emit.inputs['Color'].default_value=color
        else:
            diffuse=n.new('ShaderNodeBsdfDiffuse')
            diffuse.inputs['Color'].default_value=(1,1,1,1)
            diffuse.inputs['Roughness'].default_value=1
            rgb=n.new('ShaderNodeShaderToRGB');links.new(diffuse.outputs[0],rgb.inputs[0])
            bw=n.new('ShaderNodeRGBToBW');links.new(rgb.outputs['Color'],bw.inputs[0])
            ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='EASE'
            name=mat.name.lower()
            dark=(.69,.40,.43,1) if 'skin' in name or 'face' in name else ((.43,.49,.66,1) if 'hair' in name else (.47,.63,.76,1))
            ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
            e=ramp.color_ramp.elements[0];e.position=.16;e.color=dark
            e=ramp.color_ramp.elements.new(.39);e.color=(.81,.84,.91,1)
            e=ramp.color_ramp.elements.new(.63);e.color=(1,1,1,1)
            links.new(bw.outputs[0],ramp.inputs[0])
            mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY'
            mix.inputs[0].default_value=1;mix.inputs[1].default_value=color
            if texture:links.new(texture.outputs['Color'],mix.inputs[1])
            links.new(ramp.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],emit.inputs['Color'])
        links.new(emit.outputs[0],output.inputs['Surface'])

def export_fallback():
    for mat in bpy.data.materials:
        if not mat.use_nodes:continue
        n=mat.node_tree.nodes;p=n.get('Principled BSDF');out=n.get('Material Output')
        if p and out:
            p.inputs['Emission Strength'].default_value=.02
            mat.node_tree.links.new(p.outputs[0],out.inputs['Surface'])
