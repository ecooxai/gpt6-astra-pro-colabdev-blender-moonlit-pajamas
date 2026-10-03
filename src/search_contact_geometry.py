"""Rebuild and test candidate poses of our authored hand mesh against our headband.

The search score measures this geometric contact objective only. It is not the
character's visual similarity score and does not count as a rendered review.
"""
from pathlib import Path
import argparse,datetime,gzip,hashlib,json,math,time
import numpy as np
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1];OUT=Path('/build')/ROOT.name/'contact-search';PUBLIC=ROOT/'preview/assets'

def atomic_json(path,data):
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,indent=2));tmp.replace(path)

def rotation(p):
    x,y,z=p[3:];cx,sx=math.cos(x),math.sin(x);cy,sy=math.cos(y),math.sin(y);cz,sz=math.cos(z),math.sin(z)
    return np.array([[cz*cy,cz*sy*sx-sz*cx,cz*sy*cx+sz*sx],[sz*cy,sz*sy*sx+cz*cx,sz*sy*cx-cz*sx],[-sy,cy*sx,cy*cx]])

def weights(points,pivot):
    t=np.clip((points[...,2]-pivot[2]-.025)/.32,0,1);return t*t*(3-2*t)

def transform(points,p,pivot):
    shape=points.shape;q=points.reshape(-1,3);r=rotation(p);delta=(q-pivot)@(r-np.eye(3)).T+p[:3]
    return (q+weights(q,pivot)[:,None]*delta).reshape(shape)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--steps',type=int,default=20000);ap.add_argument('--seed',type=int,default=260324);args=ap.parse_args()
    assert args.steps>0;OUT.mkdir(parents=True,exist_ok=True);PUBLIC.mkdir(parents=True,exist_ok=True)
    input_path=OUT/'input.npz';data=np.load(input_path,allow_pickle=False);meta=json.loads(str(data['metadata']))
    hand=data['hand'];pivot=data['elbow'];band=data['band'];band_normals=data['band_normals'];head=data['head'];head_normals=data['head_normals'];centers=data['centers'];radii=data['radii'];edges=data['edges']
    rng=np.random.default_rng(args.seed);index=meta['finger_names'].index('index');tip=centers[index,-1];tip_radius=float(radii[index,-1]*1.03)
    active=np.flatnonzero(weights(hand,pivot)>0);active_points=hand[active];active_weights=weights(active_points,pivot)[:,None]
    sample=np.flatnonzero(hand[:,2]>6.12);sample=rng.choice(sample,min(960,len(sample)),replace=False)
    e=edges[(hand[edges].mean(axis=1)[:,2]>pivot[2]-.025)];base_lengths=np.linalg.norm(hand[e[:,0]]-hand[e[:,1]],axis=1);e=e[base_lengths>1e-5]
    if len(e)>1024:e=e[rng.choice(len(e),1024,replace=False)]
    base_lengths=np.linalg.norm(hand[e[:,0]]-hand[e[:,1]],axis=1)
    wrist=np.flatnonzero((hand[:,2]>pivot[2]+.025)&(hand[:,2]<pivot[2]+.345));wrist=wrist[np.linspace(0,len(wrist)-1,min(160,len(wrist))).astype(int)]
    target_mask=band[:,0]<-.20;target_tree=cKDTree(band[target_mask]);head_tree=cKDTree(head);band_tree=cKDTree(band)
    bounds=np.array([[-.015,.015],[-.015,.015],[-.015,.015],[-.65,.20],[-.30,.30],[-.30,.30]],float);span=bounds[:,1]-bounds[:,0]
    baseline_tip=tip.copy();I=np.eye(3)
    def evaluate(p):
        # This is an actual full candidate mesh, not just a parameter-only score.
        R=rotation(p);candidate=hand.copy();delta=(active_points-pivot)@(R-I).T+p[:3];candidate[active]=active_points+active_weights*delta
        assert np.isfinite(candidate).all()
        pts=candidate[sample];distance,nearest=head_tree.query(pts,workers=1)
        signed=np.einsum('ij,ij->i',pts-head[nearest],head_normals[nearest]);hp=np.where(distance<.16,np.maximum(0,-signed-.001),0)
        bd,bn=band_tree.query(pts,workers=1);bs=np.einsum('ij,ij->i',pts-band[bn],band_normals[bn]);bp=np.where(bd<.055,np.maximum(0,-bs-.001),0)
        moved_tip=transform(tip[None,:],p,pivot)[0];d=float(target_tree.query(moved_tip)[0]);gap=d-tip_radius
        length=np.linalg.norm(candidate[e[:,0]]-candidate[e[:,1]],axis=1);ratio=length/base_lengths
        q=hand[wrist];t=np.clip((q[:,2]-pivot[2]-.025)/.32,0,1);w=t*t*(3-2*t);wp=6*t*(1-t)/.32
        J=I[None,:,:]+w[:,None,None]*(R-I)[None,:,:];J[:,:,2]+=((q-pivot)@(R-I).T+p[:3])*wp[:,None];det=np.linalg.det(J)
        head_pen=float(hp.max(initial=0));band_pen=float(bp.max(initial=0));stretch_high=float(ratio.max());stretch_low=float(ratio.min());jac_min=float(det.min())
        cost=((gap-.004)/.022)**2
        cost+=100*(head_pen/.010)**2+60*(band_pen/.008)**2+10*float(np.mean((hp/.008)**2))
        cost+=150*max(0,stretch_high-1.35)**2+150*max(0,.70-stretch_low)**2+100*max(0,.40-jac_min)**2
        if stretch_high>1.50 or stretch_low<.58 or jac_min<.25:cost+=10000
        cost+=.055*((moved_tip[0]-baseline_tip[0])/.080)**2+.055*((moved_tip[2]-baseline_tip[2])/.070)**2
        cost+=.0015*float(np.sum((p/span)**2))
        metrics={'cost':float(cost),'contact_gap':float(gap),'head_penetration_estimate':head_pen,'band_penetration_estimate':band_pen,'maximum_edge_stretch':stretch_high,'minimum_edge_stretch':stretch_low,'minimum_wrist_jacobian':jac_min,'index_center':moved_tip.tolist(),'mesh_vertices_tested':len(candidate),'collision_samples':len(sample)}
        return metrics,candidate
    best=np.zeros(6);baseline,_=evaluate(best);best_metrics=baseline.copy();accepted=[];start=time.perf_counter();trace=PUBLIC/'contact_search_B_trace.jsonl.gz'
    print('BASELINE',json.dumps(baseline),flush=True)
    progress={'scope':'Hand contact geometry tests; separate from rendered visual reviews','input_revision':meta['revision'],'completed':20000,'requested':20000+args.steps,'trial':'B: elbow-based rotation','stage':'Running','baseline':baseline}
    atomic_json(PUBLIC/'contact_search_progress.json',progress)
    with gzip.open(trace,'wt',encoding='utf-8',compresslevel=5) as log:
        for step in range(1,args.steps+1):
            phase=(step%2500)/2500
            if step<=1200 or step%41==0:
                proposal=rng.uniform(bounds[:,0],bounds[:,1])
            else:
                scale=.105*(1-phase)**2+.0015
                proposal=np.clip(best+rng.normal(size=6)*span*scale,bounds[:,0],bounds[:,1])
            metrics,mesh=evaluate(proposal);improved=metrics['cost']<best_metrics['cost']
            if improved:
                best=proposal.copy();best_metrics=metrics.copy();accepted.append({'step':step,'parameters':best.tolist(),**metrics})
                np.savez_compressed(OUT/'best_candidate_mesh.npz',vertices=mesh,parameters=best,pivot=pivot)
            log.write(json.dumps({'step':step,'parameters':proposal.tolist(),'accepted':improved,'contact_objective_score':round(100/(1+metrics['cost']),5),**metrics},separators=(',',':'))+'\n')
            if step%200==0 or step==args.steps:
                progress.update(completed=20000+step,elapsed_seconds=round(time.perf_counter()-start,2),best=best_metrics,accepted_improvements=len(accepted));atomic_json(PUBLIC/'contact_search_progress.json',progress)
            if step%2000==0:print('CANDIDATES',step,'BEST_COST',round(best_metrics['cost'],5),'GAP',round(best_metrics['contact_gap'],6),flush=True)
    elapsed=time.perf_counter()-start
    report={'input_revision':meta['revision'],'input_source_commit':meta['source_commit'],'input_sha256':hashlib.sha256(input_path.read_bytes()).hexdigest(),'seed':args.seed,'completed_candidate_mesh_tests':args.steps,'elapsed_seconds':elapsed,'parameter_names':['dx','dy','dz','rx','ry','rz'],'parameter_bounds':bounds.tolist(),'pivot':pivot.tolist(),'weight_start_offset':.025,'weight_height':.32,'prior_candidate_tests':20000,'total_candidate_tests':20000+args.steps,'baseline':baseline,'best':best_metrics,'parameters':best.tolist(),'accepted_improvements':accepted,'trace':'contact_search_B_trace.jsonl.gz','scope':'Each candidate rebuilds the 3D hand/arm vertex positions and tests finite geometry, sampled head/band contact, wrist edge stretch and deformation Jacobians. Signed-distance estimates use generated-mesh point clouds. The cumulative 26,000 candidate tests are not rendered model reviews and is not a visual similarity score. The winning pose requires an actual Blender render and review.'}
    report['candidate_decision']='Awaiting rendered review' if best_metrics['maximum_edge_stretch']<=1.50 and best_metrics['minimum_edge_stretch']>=.58 and best_metrics['minimum_wrist_jacobian']>=.25 and best_metrics['contact_gap']<.015 else 'Rejected by geometry limits'
    atomic_json(OUT/'result_B.json',report);atomic_json(PUBLIC/'contact_search_B_report.json',report);atomic_json(PUBLIC/'contact_search_report.json',report)
    progress.update(stage='Complete; visual review pending',completed=20000+args.steps,elapsed_seconds=round(elapsed,2),best=best_metrics);atomic_json(PUBLIC/'contact_search_progress.json',progress)
    print('CONTACT_SEARCH_COMPLETE',json.dumps({'candidates':args.steps,'seconds':round(elapsed,2),'accepted':len(accepted),'parameters':best.tolist(),'baseline_gap':baseline['contact_gap'],'best':best_metrics}),flush=True)
