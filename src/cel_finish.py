"""Selected original cel finish: clear cotton folds, soft white-fabric highlights."""
import bpy

def install():
    cotton={'Original cat-print cotton','fabricShade','cuffCotton','collarShade'}
    soft={'white','pillowBack'}
    for mat in bpy.data.materials:
        if not mat.use_nodes or mat.name not in cotton|soft:continue
        hard=mat.name in cotton
        for node in mat.node_tree.nodes:
            if node.type!='VALTORGB':continue
            ramp=node.color_ramp;ramp.interpolation='CONSTANT' if hard else 'EASE'
            positions=[.18,.43,.69] if hard else [.30,.48,.54]
            colors=[(.47,.65,.79,1),(.82,.89,.97,1),(1,1,1,1)] if hard else [(.52,.71,.84,1),(.87,.94,.99,1),(1,1,1,1)]
            for element,position,color in zip(ramp.elements,positions,colors):element.position=position;element.color=color
