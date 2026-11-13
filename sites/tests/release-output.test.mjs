import test from 'node:test';
import {execFileSync} from 'node:child_process';
import assert from 'node:assert/strict';
import {readFileSync, readdirSync, statSync, existsSync} from 'node:fs';
import {resolve, relative} from 'node:path';
import {equivalentPeers, versionOptions, publications} from '../astro/components/ReleasePresentation.mjs';
const root = resolve(import.meta.dirname, '../..');
const dist = resolve(root, 'sites/dist');
const read = path => readFileSync(resolve(dist, path), 'utf8');
const scopes = JSON.parse(read('versions.json'));
const publicRoot = resolve(root, 'sites/static');
const evidencePath = resolve(publicRoot, 'release-equivalence.json');
const prefix = new URL(readFileSync(resolve(root, '.project/docs/config.yaml'),'utf8').match(/base_url: (.*)/)[1]).pathname.replace(/\/$/,'');
const html = href => read(href.slice(prefix.length).replace(/^\//,'') + 'index.html');
const options = page => [...page.matchAll(/<select[^>]*aria-label="(?:Version|Versión)"[^>]*>([\s\S]*?)<\/select>/g)][0]?.[1] || '';
const destination = (scope, guide) => scope.pages.find(page=>page.slug===guide)?.href || scope.root;
const walk = path => readdirSync(path).flatMap(name => {const file=resolve(path,name); return statSync(file).isDirectory()?walk(file):[file];});
test('Astro latest release entry, exact versions, separate Development and scoped search',()=>{
 const released=scopes.filter(scope=>scope.language==='en'&&!scope.development).sort((a,b)=>{
  const av=a.version.split('-')[0].split('.').map(Number),bv=b.version.split('-')[0].split('.').map(Number);
  for(let i=0;i<3;i++)if(av[i]!==bv[i])return av[i]-bv[i];
  return Number(a.version.endsWith('-maven-central'))-Number(b.version.endsWith('-maven-central'));
 });
 const latest=released.at(-1);
 assert.ok(read('index.html').includes(`url=${latest.root}`));
 for(const scope of scopes){
  const page=html(scope.root), select=options(page);
  assert.ok(select.includes('Development')||select.includes('Desarrollo'));
  assert.ok(page.includes(`version:${scope.version}`));
  assert.ok(page.includes('data-filters=')&&page.includes('data-doc-navigation'));
  assert.ok(page.includes('Site build revision')||page.includes('Revisión de compilación'));
  for(const image of scope.images || []) assert.ok(readFileSync(resolve(dist,image.src.slice(prefix.length).replace(/^\//,''))).length>0);
  for(const guide of scope.pages){assert.ok(read(guide.raw.slice(prefix.length).replace(/^\//,'')).length>0);}
  const guide=scope.pages.find(page=>page.slug&&page.slug!=='installation');
  if(guide){const output=html(guide.href);for(const match of options(output).matchAll(/<option value="([^"]+)"/g)){const target=scopes.find(peer=>match[1].startsWith(peer.root));assert.ok(target);assert.equal(target.language,scope.language);assert.equal(target.module,scope.module);if(target.pages.some(page=>page.slug===guide.slug)){assert.equal(match[1],destination(target,guide.slug));}else{const fallback=new URL(match[1],'https://fixture.invalid');assert.equal(fallback.pathname,destination(target,''));assert.equal(fallback.searchParams.get('guide-unavailable'),guide.slug);assert.equal(fallback.hash,'#guide-unavailable');}}const other=scopes.find(peer=>peer.language!==scope.language&&peer.version===scope.version);if(other?.pages.some(page=>page.slug===guide.slug))assert.ok(output.includes(destination(other,guide.slug)));}
 }
 for(const endpoint of ['IMPORT.md','llms.txt','agents/index.md'])assert.ok(read(endpoint).length>0);
});
test('all retained static aliases and screenshot URLs survive byte-for-byte',()=>{
 for(const source of walk(resolve(root,'sites/static'))){const path=relative(resolve(root,'sites/static'),source);assert.deepEqual(readFileSync(resolve(dist,path)),readFileSync(source),path);}
});
test('same version text never establishes provider equivalence',()=>{
 const sources={'maven-central':'a'.repeat(40),jitpack:'b'.repeat(40)};
 const pair=Object.entries(sources).map(([name,source])=>({module:'demo-common',language:'en',version:`0.1.2-${name}`,source,root:`/${name}/`,pages:[]}));
 const evidence=[{module:'demo-common',version:'0.1.2',sources,sha256:Object.fromEntries(['.aar','-sources.jar','-javadoc.jar'].map(key=>[key,'c'.repeat(64)]))}];
 assert.equal(versionOptions(pair,pair[0],'',destination,[]).length,2);
 assert.equal(publications(pair,pair[0],[]).length,1);
 assert.equal(equivalentPeers(pair,pair[0],evidence).length,2);
 assert.equal(versionOptions(pair,pair[1],'',destination,evidence).length,1);
 assert.ok(versionOptions(pair,pair[1],'',destination,evidence)[0].selected);
 assert.equal(publications(pair,pair[0],evidence).length,2);
 assert.equal(equivalentPeers([pair[0],{...pair[1],source:'unverified'}],pair[0],evidence).length,1);
 assert.equal(equivalentPeers(pair,pair[0],[{...evidence[0],sha256:{}}]).length,1);
});

test('reviewed 0.1.2 equivalence matches both immutable publication records and hashes',()=>{
 const evidence=JSON.parse(readFileSync(evidencePath,'utf8'));
 const record=evidence.find(record=>record.version==='0.1.2');
 for(const provider of ['maven-central','jitpack']){
  const history=JSON.parse(readFileSync(resolve(root,`docs/releases/history/demo-common/0.1.2-${provider}.json`),'utf8'));
  assert.equal(history.source,record.sources[provider]);
  for(const [key,hash] of Object.entries(record.sha256))assert.equal(history.destinations[provider].sha256[key],hash);
 }
 for(const language of ['en','es']){
  const central=scopes.find(scope=>scope.language===language&&scope.version==='0.1.2-maven-central');
  const jitpack=scopes.find(scope=>scope.language===language&&scope.version==='0.1.2-jitpack');
  assert.equal(equivalentPeers(scopes,central,evidence).length,2);
  for(const scope of [central,jitpack]){
   const page=html(scope.root),select=options(page);
   assert.equal((select.match(/>0\.1\.2<\/option>/g)||[]).length,1);
   assert.ok(page.includes(record.sources['maven-central'])&&page.includes(record.sources.jitpack));
   assert.ok(page.includes(central.root+'installation/')&&page.includes(jitpack.root+'installation/'));
   assert.ok(page.includes(scope.documentation_ref));
  }
 }
});

test('catalog screenshots retain the selected immutable documentation revision',()=>{
 for(const scope of scopes){
  for(const image of scope.images || []){
   const filename=image.src.split('/').at(-1);
   const expected=scope.development ? readFileSync(resolve(root,'docs/screenshots',filename)) : execFileSync('git',['show',`${scope.documentation_ref}:docs/screenshots/${filename}`],{cwd:root});
   assert.deepEqual(readFileSync(resolve(dist,image.src.slice(prefix.length).replace(/^\//,''))),expected,`${scope.version}/${filename}`);
  }
 }
});

test('translated Markdown links use the actual translated source directory',()=>{
 for(const file of walk(resolve(root,'docs/es')).filter(file=>file.endsWith('.md'))){
  for(const match of readFileSync(file,'utf8').matchAll(/\]\(([^\s)]+)/g)){
   const path=match[1].split('#')[0];
   if(!path || path.startsWith('/') || /^[a-z]+:/i.test(path))continue;
   assert.ok(existsSync(resolve(file,'..',path)),`${relative(root,file)}: ${path}`);
  }
 }
 const release=scopes.find(scope=>scope.language==='es'&&scope.development);
 const guide=release.pages.find(page=>page.slug==='releases');
 const page=html(guide.href);
 assert.ok(!page.includes('/docs/sites/README.md'));
 assert.ok(!page.includes('/docs/IMPORT.md'));
});
