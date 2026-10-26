// MIT · HouseNimble public plugin SDK. No private core implementation.
const encoder=new TextEncoder();
export class LuaUsb {
 constructor(port,{timeout=5000}={}){this.port=port;this.timeout=timeout;this.sequence=0;this.token=null;this.pending=new Map();this.queue=Promise.resolve();this.queued=0;this.closed=true;}
 async open(){
  await this.port.open({baudRate:115200,bufferSize:8192});this.closed=false;
  this.reader=this.port.readable.getReader();this.writer=this.port.writable.getWriter();this.reading=this.readLoop();
 }
 async readLoop(){
  const decoder=new TextDecoder();let line='',discard=false;
  try{
   while(!this.closed){const {value,done}=await this.reader.read();if(done)break;
    for(const ch of decoder.decode(value,{stream:true})){
     if(ch==='\n'){
      if(!discard){const at=line.indexOf('@HN1 ');if(at>=0){try{const reply=JSON.parse(line.slice(at+5));const slot=this.pending.get(reply.id);if(slot){this.pending.delete(reply.id);clearTimeout(slot.timer);if(reply.ok===true)slot.resolve(reply);else slot.reject(new Error('Skærmen afviste handlingen. Kontrollér udviklings-core og USB-koden.'));}}catch{}}}
      line='';discard=false;
     }else if(!discard){line+=ch;if(line.length>2048){line='';discard=true;}}
    }
   }
  }catch{}finally{this.closed=true;for(const slot of this.pending.values()){clearTimeout(slot.timer);slot.reject(new Error('USB-forbindelsen blev afbrudt.'));}this.pending.clear();this.reader.releaseLock();}
 }
 request(op,fields={}){
  if(this.closed||this.queued>=8)return Promise.reject(new Error('USB-forbindelsen er lukket eller optaget.'));
  this.queued++;
  const run=async()=>{
   if(this.closed)throw new Error('USB-forbindelsen er lukket.');
   const id=++this.sequence;const message={id,op,...fields};if(this.token)message.token=this.token;
   const bytes=encoder.encode('@HN1 '+JSON.stringify(message)+'\n');if(bytes.length>1800)throw new Error('USB-meddelelsen er for stor.');
   // Arm the response before writing: a fast device may acknowledge immediately.
   let slot;const response=new Promise((resolve,reject)=>{slot={resolve,reject,timer:setTimeout(()=>{this.pending.delete(id);reject(new Error('Skærmen svarede ikke. Kontrollér kabel og Flight-kompatibel udviklings-core.'));},this.timeout)};this.pending.set(id,slot);});
   try{await Promise.race([this.writer.write(bytes),response]);}catch{clearTimeout(slot.timer);this.pending.delete(id);slot.resolve(null);throw new Error('Kunne ikke skrive til USB-porten.');}
   return response;
  };
  const result=this.queue.then(run);this.queue=result.catch(()=>{});return result.finally(()=>{this.queued--;});
 }
 async hello({wait=20000}={}){
  const until=Date.now()+wait;let status;
  for(;;){try{status=await this.request('hello');break;}catch(error){if(this.closed||Date.now()>=until)throw error;}}
  if(status.protocol!==1||status.coreApi!==1||status.development!==true||status.capabilities?.httpFlight!==true)throw new Error('Skærmen kræver en Flight-kompatibel Lua-udviklings-core. Den nuværende firmware blev ikke ændret.');
  return status;
 }
 async pair(pin){
  if(!/^[0-9]{6}$/.test(pin))throw new Error('Indtast de seks tal fra USB · par enhed.');
  const result=await this.request('pair',{pin});if(!/^[0-9a-f]{64}$/.test(result.token||''))throw new Error('USB-parringen kunne ikke bekræftes.');
  this.token=result.token;return {paired:true};
 }
 async upload(bytes,config,onProgress=()=>{}){
  if(!this.token)throw new Error('Par USB-forbindelsen først.');
  if(!(bytes instanceof Uint8Array)||bytes.length<22||bytes.length>147456)throw new Error('Ugyldig pluginpakke.');
  if(!config||typeof config!=='object'||Array.isArray(config)||encoder.encode(JSON.stringify(config)).length>768)throw new Error('Ugyldige pluginindstillinger.');
  const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
  await this.request('begin',{size:bytes.length,sha256:hash,isolated:true,config});
  for(let offset=0;offset<bytes.length;offset+=768){
   const part=bytes.subarray(offset,offset+768);const data=btoa(String.fromCharCode(...part));
   const result=await this.request('chunk',{offset,data});if(result.received!==offset+part.length)throw new Error('Skærmen bekræftede et forkert antal bytes.');
   onProgress((offset+part.length)/bytes.length);
  }
  const result=await this.request('commit');if(result.active!==true||result.plugin!=='housenimble.flight')throw new Error('Flight kunne ikke startes.');return result;
 }
 status(){return this.request('status');}
 async close({stop=true}={}){
  let stopped=!this.token;
  try{if(stop&&this.token&&!this.closed){await this.request('stop');stopped=true;}}
  catch{}finally{
   this.token=null;this.closed=true;
   try{await this.reader?.cancel();}catch{}
   try{await this.reading;}catch{}
   try{this.writer?.releaseLock();}catch{}
   try{await this.port.close();}catch{}
  }
  return stopped;
 }
}
