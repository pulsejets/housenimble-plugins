import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {webcrypto} from 'node:crypto';
globalThis.crypto??=webcrypto;
const {LuaUsb}=await import('data:text/javascript;base64,'+Buffer.from(await readFile(new URL('../../_sdk/web-usb.js',import.meta.url))).toString('base64'));
function fake({rejectChunk=false,capability=true,plugin="housenimble.flight",schema=1,silent=false}={}){
 let controller;const requests=[];let stopped=false;
 const port={readable:new ReadableStream({start(c){controller=c;}}),writable:new WritableStream({write(bytes){
  const m=JSON.parse(new TextDecoder().decode(bytes).slice(5));requests.push(m);if(silent)return;
  const reply={id:m.id,ok:true,protocol:1,coreApi:1,development:true,capabilities:{httpFlight:capability,settingsSchema:schema}};
  if(m.op==='pair')reply.token='a'.repeat(64);
  if(m.op==='chunk')reply.received=m.offset+Buffer.from(m.data,'base64').length-(rejectChunk?1:0);
  if(m.op==='commit'){reply.active=true;reply.plugin=plugin;}
  if(m.op==='stop')stopped=true;
  controller.enqueue(new TextEncoder().encode('boot log\n@HN1 '+JSON.stringify(reply)+'\n'));
 }}),async open(){},async close(){},requests,get stopped(){return stopped;}};return port;
}
{
 const port=fake(),usb=new LuaUsb(port,{timeout:100});await usb.open();await usb.hello({wait:0});await usb.pair('000001');
 const bytes=new Uint8Array(2000).fill(7);await usb.upload(bytes,{country:'GLOBAL'});await Promise.all([usb.status(),usb.status()]);
 assert.equal(port.requests.filter(r=>r.op==='chunk').length,3);assert.equal(port.requests.find(r=>r.op==='begin').sha256,Buffer.from(await webcrypto.subtle.digest('SHA-256',bytes)).toString('hex'));
 assert.equal(await usb.close(),true);assert(port.stopped);assert.equal(usb.token,null);
}
{
 const port=fake({capability:false}),usb=new LuaUsb(port,{timeout:100});await usb.open();await assert.rejects(usb.hello({wait:0}),/udviklings-core/);assert(!port.requests.some(r=>r.op==='pair'||r.op==='begin'));await usb.close();
}
{
 const port=fake({rejectChunk:true}),usb=new LuaUsb(port,{timeout:100});await usb.open();await usb.hello({wait:0});await usb.pair('123456');await assert.rejects(usb.upload(new Uint8Array(22),{}),/forkert antal/);assert(!port.requests.some(r=>r.op==='commit'));await usb.close();
}
const manifest={id:'housenimble.counter',apiVersion:1,permissions:{network:[],mqttSubscribe:[],mqttPublish:[]}};
{
 const port=fake({capability:false,plugin:manifest.id}),usb=new LuaUsb(port,{manifest,timeout:100});await usb.open();await usb.hello({wait:0});await usb.pair('000001');await usb.upload(new Uint8Array(22),{country:'DK'});assert.equal(port.requests.find(r=>r.op==='begin').config.country,'DK');await usb.close();
}
{
 const port=fake({schema:0}),usb=new LuaUsb(port,{manifest,timeout:100});await usb.open();await usb.hello({wait:0});await usb.pair('000001');await assert.rejects(usb.upload(new Uint8Array(22),{}),/generelle pluginindstillinger/);assert(!port.requests.some(r=>r.op==='begin'));await usb.close();
}
{
 const port=fake({silent:true}),usb=new LuaUsb(port,{manifest,timeout:20});await usb.open();await assert.rejects(usb.hello({wait:0}));assert.equal(usb.pending.size,0);await usb.close();
}
console.log('PASS: public browser USB handshake, capability rejection, pairing, SHA/chunks, serialization and cleanup');
