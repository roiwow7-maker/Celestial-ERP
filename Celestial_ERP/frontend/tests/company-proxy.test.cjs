/* eslint-disable @typescript-eslint/no-require-imports -- Harness Node para probar el handler sin iniciar Next. */
const { test, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
const { NextRequest } = require('next/server');
const companies = [{id:'default',name:'Actual',backend:'http://127.0.0.1:8000'}, {id:'alpha',name:'Alpha',backend:'http://127.0.0.1:8001'}, {id:'beta',name:'Beta',backend:'http://127.0.0.1:8002'}];
function route() {
  const file = path.resolve(__dirname, '../src/app/backend/[[...path]]/route.ts');
  const source = ts.transpileModule(fs.readFileSync(file,'utf8'), {compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
  const exports = {};
  vm.runInNewContext(source, {exports, require:()=>({companyRegistry:()=>companies}), URL, Headers, Response, Buffer, AbortSignal, process, fetch:(...args)=>global.fetch(...args)});
  return exports;
}
const savedFetch = global.fetch;
afterEach(()=>{global.fetch=savedFetch;});
function request(method='GET', headers={}) {
  return new NextRequest('http://localhost:3000/backend/company/alpha/api/v1/session/', {method, headers});
}
const context = {params:Promise.resolve({path:['company','alpha','api','v1','session']})};
test('forwards only selected company cookies and strips forged forwarding headers',async()=>{
  global.fetch=async(url,options)=>{
    assert.equal(url.origin,'http://127.0.0.1:8001');
    assert.equal(options.headers.get('cookie'),'sessionid=ALPHA; csrftoken=CSRF');
    assert.equal(options.headers.get('x-forwarded-host'),null);
    assert.equal(options.headers.get('x-forwarded-proto'),'http');
    return new Response('{}',{headers:{'X-ERP-Company':'alpha','Content-Type':'application/json','Set-Cookie':'sessionid=new; Path=/; HttpOnly; SameSite=Lax','X-Frame-Options':'DENY'}});
  };
  const result=await route().GET(request('GET',{'Cookie':'erp_alpha_sessionid=ALPHA; erp_alpha_csrftoken=CSRF; erp_beta_sessionid=BETA; sessionid=LEGACY','X-Forwarded-Host':'evil','X-Forwarded-Proto':'https'}),context);
  assert.equal(result.status,200);
  assert.match(result.headers.get('set-cookie'),/^erp_alpha_sessionid=new/);
  assert.match(result.headers.get('set-cookie'),/HttpOnly/);
  assert.equal(result.headers.get('x-frame-options'),'DENY');
  assert.equal(result.headers.get('cache-control'),'no-store, private');
});
test('rejects cross origin mutation before contacting backend',async()=>{
  global.fetch=()=>assert.fail('must not contact backend');
  const result=await route().POST(request('POST',{Origin:'https://evil.example'}),context);
  assert.equal(result.status,403);
});
test('same origin mutation retains CSRF header',async()=>{
  global.fetch=async(url,options)=>{
    assert.equal(options.headers.get('origin'),'http://127.0.0.1:8001');
    assert.equal(options.headers.get('x-csrftoken'),'token');
    return new Response('{}',{headers:{'X-ERP-Company':'alpha'}});
  };
  assert.equal((await route().POST(request('POST',{Origin:'http://localhost:3000','X-CSRFToken':'token'}),context)).status,200);
});
test('unknown company never falls back to another database',async()=>{
  global.fetch=()=>assert.fail('must not contact backend');
  assert.equal((await route().GET(request(),{params:Promise.resolve({path:['company','missing','api']})})).status,404);
});
test('rejects a backend connected to another company',async()=>{
  global.fetch=async()=>new Response('private beta data',{headers:{'X-ERP-Company':'beta'}});
  const result=await route().GET(request(),context);
  assert.equal(result.status,502);
  assert.doesNotMatch(await result.text(),/private beta data/);
});
test('rewrites downloads and redirects within the company',async()=>{
  global.fetch=async()=>new Response(null,{status:302,headers:{'X-ERP-Company':'alpha',Location:'/login/'}});
  const result=await route().GET(request(),context);
  assert.equal(result.headers.get('location'),'/backend/company/alpha/login/');
});
test('root company path stays on its configured backend',async()=>{
  global.fetch=async(url)=>{
    assert.equal(url.href,'http://127.0.0.1:8001/');
    return new Response('ok',{headers:{'X-ERP-Company':'alpha'}});
  };
  assert.equal((await route().GET(request(),{params:Promise.resolve({path:['company','alpha']})})).status,200);
});

test('legacy session is migrated only for default company', async()=>{
  global.fetch=async(url,options)=>{
    assert.equal(url.origin,'http://127.0.0.1:8000');
    assert.equal(options.headers.get('cookie'),'sessionid=legacy');
    return new Response('{}',{headers:{'X-ERP-Company':'default'}});
  };
  const result=await route().GET(request('GET',{'Cookie':'sessionid=legacy; erp_beta_sessionid=BETA'}), {params:Promise.resolve({path:['company','default','api','v1','session']})});
  assert.equal(result.status,200);
});
