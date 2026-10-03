"""Validate generated exports. These checks do not measure visual similarity."""
from pathlib import Path
import json,struct,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'preview/assets'
TYPES={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}
SIZES={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}

def validate(path):
    raw=path.read_bytes();magic,version,size=struct.unpack_from('<4sII',raw)
    assert magic==b'glTF' and version==2 and size==len(raw),'Invalid GLB header'
    offset=12;doc=None;binary=None
    while offset<len(raw):
        length,kind=struct.unpack_from('<II',raw,offset);offset+=8;chunk=raw[offset:offset+length];offset+=length
        if kind==0x4e4f534a:doc=json.loads(chunk)
        elif kind==0x004e4942:binary=chunk
    assert doc is not None and binary is not None and offset==len(raw)
    def accessor(index):
        a=doc['accessors'][index];b=doc['bufferViews'][a['bufferView']];dtype=np.dtype(TYPES[a['componentType']]);n=SIZES[a['type']]
        start=b.get('byteOffset',0)+a.get('byteOffset',0);stride=b.get('byteStride',n*dtype.itemsize)
        assert start+(a['count']-1)*stride+n*dtype.itemsize<=len(binary)
        return np.ndarray((a['count'],n),dtype=dtype,buffer=binary,offset=start,strides=(stride,dtype.itemsize))
    triangles=0;vertices=0;largest=[]
    for mesh in doc.get('meshes',[]):
        count=0
        for p in mesh['primitives']:
            xyz=accessor(p['attributes']['POSITION']);assert np.isfinite(xyz).all();vertices+=len(xyz)
            if 'indices' in p:
                idx=accessor(p['indices']);assert idx.min()>=0 and idx.max()<len(xyz);count+=len(idx)//3
            else:count+=len(xyz)//3
            if 'NORMAL' in p['attributes']:assert np.isfinite(accessor(p['attributes']['NORMAL'])).all()
        triangles+=count;largest.append((count,mesh.get('name','mesh')))
    assert all('uri' not in i for i in doc.get('images',[])),'External texture URL'
    assert all('uri' not in b for b in doc.get('buffers',[])),'External buffer URL'
    return dict(file=path.name,result='PASS',bytes=len(raw),triangles=triangles,vertex_entries=vertices,embedded_images=len(doc.get('images',[])),largest_meshes=sorted(largest,reverse=True)[:6])

if __name__=='__main__':
    stats=json.loads((ASSETS/'model_stats.json').read_text());legs={}
    for name,leg in stats['legs'].items():
        h,k,a=[np.array(leg[x],float) for x in ('hip','knee','ankle')];upper=float(np.linalg.norm(h-k));lower=float(np.linalg.norm(k-a))
        assert abs(upper-stats['upper_leg_length'])<1e-6 and abs(lower-stats['lower_leg_length'])<1e-6
        legs[name]={'upper':upper,'lower':lower}
    results=[validate(ASSETS/(ROOT.name+suffix+'.glb')) for suffix in ('','_web')]
    assert results[0]['triangles']==stats['triangles'] and results[1]['triangles']==stats['web_triangles']
    report={'revision':stats['revision'],'result':'PASS','exports':results,'authored_leg_center_lengths':legs,'scope':'Finite mesh data, valid indices, embedded textures, triangle-count agreement, and matching authored leg-center segment lengths. Not a visual score or animation-rig test.'}
    (ASSETS/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
