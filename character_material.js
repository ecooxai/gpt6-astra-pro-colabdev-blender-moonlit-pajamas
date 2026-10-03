import * as THREE from 'three';
export const characterLight={value:new THREE.Vector3(-.45,.8,.9).normalize()};
const cache=new Map();
export function illustrationMaterial(source){
 if(cache.has(source.uuid))return cache.get(source.uuid);
 const name=source.name.toLowerCase(),flat=/iris|eyewhite|lash|mouth|halo|pinklight/.test(name),skin=/skin|face/.test(name),hair=/hair/.test(name);
 const mat=new THREE.ShaderMaterial({name:source.name+' illustration',side:THREE.DoubleSide,
 uniforms:{albedo:{value:source.map||null},hasMap:{value:!!source.map},color:{value:source.color.clone()},lightDirection:characterLight,low:{value:new THREE.Vector3(...(skin?[.78,.52,.55]:hair?[.55,.54,.71]:[.62,.76,.85]))},unshaded:{value:flat},skin:{value:skin}},
 vertexShader:`varying vec2 vUv;varying vec3 vN;void main(){vUv=uv;vN=normalize(normalMatrix*normal);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
 fragmentShader:`uniform vec3 color,lightDirection,low;uniform sampler2D albedo;uniform bool hasMap,unshaded,skin;varying vec2 vUv;varying vec3 vN;
 void main(){vec4 base=hasMap?texture2D(albedo,vUv):vec4(color,1.0);vec3 n=normalize(vN);if(!gl_FrontFacing)n=-n;
 float l=dot(n,normalize(lightDirection));float level=smoothstep(-.13,.16,l)*.63+smoothstep(.40,.59,l)*.37;
 if(skin)level=.65+.35*smoothstep(-.42,.02,l);vec3 shade=unshaded?vec3(1.0):mix(low,vec3(1.0),level);gl_FragColor=vec4(base.rgb*shade,base.a);
 #include <colorspace_fragment>
 }`});cache.set(source.uuid,mat);return mat;
}
export function clearMaterialCache(){cache.clear();}
