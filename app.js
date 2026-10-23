/* UnixTime: local-only, precision-safe Unix date converter. */
(()=>{
'use strict';
const $=id=>document.getElementById(id);
const T=window.UNIXTIME_TEXT||{};
const locale=document.documentElement.lang==='en'?'en-GB':document.documentElement.lang||'en-GB';
const NS=1000000000n,MAX_MS=8640000000000000n;
const POW={s:1000000000n,ms:1000000n,us:1000n,ns:1n};
const safeSet=(id,value)=>{const el=$(id);if(el)el.textContent=value;};
const word=(key,fallback)=>T[key]||fallback;
const floorDiv=(a,b)=>a>=0n?a/b:-((-a+b-1n)/b);
function fmtPart(ns,divisor,decimals){
 const negative=ns<0n,absolute=negative?-ns:ns;
 const whole=absolute/divisor,remainder=absolute%divisor;
 const sign=(negative?'-':'')+String(whole);
 if(!decimals||remainder===0n)return sign;
 return sign+'.'+String(remainder).padStart(decimals,'0').replace(/0+$/,'');
}
function nsOf(text,unit){
 const raw=String(text).trim().replace(/\s/g,'');
 if(!/^[+-]?\d{1,25}(?:\.\d{1,9})?$/.test(raw))throw Error(word('invalid','Enter a numeric timestamp.'));
 const negative=raw.startsWith('-'),unsigned=raw.replace(/^[+-]/,'');
 const parts=unsigned.split('.'),whole=parts[0],decimal=parts[1]||'';
 const chosen=unit==='auto'?(whole.length>=19?'ns':whole.length>=16?'us':whole.length>=13?'ms':'s'):unit;
 if(!POW[chosen])throw Error(word('invalid','Unsupported precision.'));
 const mult=POW[chosen],places=String(mult).length-1;
 if(decimal.length>places)throw Error(word('precision','Too many decimal places.'));
 const n=BigInt(whole)*mult+BigInt(decimal.padEnd(places,'0')||'0');
 return{ns:negative?-n:n,unit:chosen};
}
function dateFromNs(ns){
 const millis=floorDiv(ns,1000000n);
 if(millis>MAX_MS||millis<(-MAX_MS))throw Error(word('outOfRange','Timestamp outside date range.'));
 const date=new Date(Number(millis));
 if(!Number.isFinite(date.getTime()))throw Error(word('invalidDate','Invalid date.'));
 return date;
}
function formatReadable(date){
 return new Intl.DateTimeFormat(locale,{weekday:'long',day:'numeric',month:'long',year:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23',timeZone:'UTC'}).format(date).replace(', ',' · ').replace(' at ',' · ')+' UTC';
}
function formatUTC(date){
 return new Intl.DateTimeFormat(locale,{day:'numeric',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23',timeZone:'UTC'}).format(date).replace(', ',' · ').replace(' at ',' · ')+' UTC';
}
function copy(text,button){
 if(!text||text==='—')return;
 const ok=()=>{
  const original=button.getAttribute('aria-label')||button.textContent.trim();
  button.setAttribute('aria-label',word('copied','Copied!'));
  button.setAttribute('title',word('copied','Copied!'));
  window.setTimeout(()=>{button.setAttribute('aria-label',original);button.removeAttribute('title');},1400);
 };
 const fallback=()=>{
  const el=document.createElement('textarea');el.value=text;el.style.cssText='position:fixed;opacity:0';
  document.body.appendChild(el);el.select();
  const done=document.execCommand('copy');el.remove();if(done)ok();
 };
 if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(text).then(ok).catch(fallback);
 else fallback();
}
function convertUnix(){
 const notice=$('inputNotice');
 try{
  const parsed=nsOf($('unixInput').value,$('unitSelector').value);
  const date=dateFromNs(parsed.ns);
  safeSet('unixUtc',formatUTC(date));
  safeSet('unixIso',date.toISOString());
  notice.textContent='';notice.classList.remove('error');
 }catch(e){
  safeSet('unixUtc','—');safeSet('unixIso','—');
  notice.textContent=e.message;notice.classList.add('error');
 }
}
function zoneParts(instant,zone){
 const items=new Intl.DateTimeFormat('en-US',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'}).formatToParts(instant);
 const p=Object.fromEntries(items.filter(v=>v.type!=='literal').map(v=>[v.type,Number(v.value)]));
 const two=x=>String(x).padStart(2,'0');
 return String(p.year).padStart(4,'0')+'-'+two(p.month)+'-'+two(p.day)+'T'+two(p.hour)+':'+two(p.minute)+':'+two(p.second);
}
function parseDateInput(day,time,zone){
 const stamp=day+'T'+(time.length===5?time+':00':time);
 if(!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(stamp))throw Error(word('invalidDate','Enter a date and time.'));
 const utc=new Date(stamp+'Z');
 if(!Number.isFinite(utc.getTime())||utc.toISOString().slice(0,19)!==stamp)throw Error(word('invalidDate','Invalid calendar date.'));
 if(zone==='UTC')return utc;
 if(zone==='local'){
  const d=new Date(stamp),two=x=>String(x).padStart(2,'0');
  const local=String(d.getFullYear()).padStart(4,'0')+'-'+two(d.getMonth()+1)+'-'+two(d.getDate())+'T'+two(d.getHours())+':'+two(d.getMinutes())+':'+two(d.getSeconds());
  if(!Number.isFinite(d.getTime())||local!==stamp)throw Error(word('invalidDate','Invalid or nonexistent local time.'));
  return d;
 }
 let millis=utc.getTime();
 for(let i=0;i<5;i++){
  const actual=zoneParts(new Date(millis),zone),diff=utc.getTime()-Date.parse(actual+'Z');
  if(diff===0)break;
  millis+=diff;
 }
 const d=new Date(millis);
 if(!Number.isFinite(d.getTime())||zoneParts(d,zone)!==stamp)throw Error(word('invalidDate','Invalid or nonexistent local time.'));
 return d;
}
function convertDate(){
 const notice=$('dateNotice');
 try{
  const d=parseDateInput($('dateInput').value,$('timeInput').value,$('dateZoneSelect').value);
  safeSet('dateSec',String(Math.floor(d.getTime()/1000)));
  notice.textContent='';notice.classList.remove('error');
 }catch(e){
  safeSet('dateSec','—');notice.textContent=e.message;notice.classList.add('error');
 }
}
function updateClock(){
 const now=Date.now(),date=new Date(now);
 safeSet('liveSeconds',String(Math.floor(now/1000)));
 safeSet('liveMilliseconds',String(now));
 safeSet('liveIso',date.toISOString());
 safeSet('liveLocal',date.toLocaleString());
 safeSet('liveReadable',formatReadable(date));
}
function init(){
 const q=new URLSearchParams(location.search),shared=q.get('ts');
 $('unixInput').value=shared&&/^[+-]?\d{1,25}(?:\.\d{1,9})?$/.test(shared)?shared:String(Math.floor(Date.now()/1000));
 const unit=q.get('unit');if(['s','ms','us','ns'].includes(unit))$('unitSelector').value=unit;
 const sync=()=>{
  const chosen=$('unitSelector').value;
  document.querySelectorAll('.unit-choice').forEach(btn=>{
   const active=btn.dataset.unit===chosen;
   btn.classList.toggle('is-active',active);btn.setAttribute('aria-pressed',String(active));
  });
  convertUnix();
 };
 document.querySelectorAll('.unit-choice').forEach(btn=>btn.addEventListener('click',()=>{$('unitSelector').value=btn.dataset.unit;sync();}));
 $('unitSelector').addEventListener('change',sync);
 $('unixInput').addEventListener('input',convertUnix);
 const iso=new Date().toISOString();$('dateInput').value=iso.slice(0,10);$('timeInput').value=iso.slice(11,19);
 for(const id of ['dateInput','timeInput'])$(id).addEventListener('input',convertDate);
 $('dateZoneSelect').addEventListener('change',convertDate);
 $('langSelect').addEventListener('change',e=>location.assign(e.target.value));
 const syncNavigation=()=>{
  const active=location.hash==='#about'?'#about':'#converter';
  document.querySelectorAll('.nav-links a').forEach(link=>{
   const selected=link.getAttribute('href')===active;
   link.classList.toggle('active',selected);
   if(selected)link.setAttribute('aria-current','location');
   else link.removeAttribute('aria-current');
  });
 };
 window.addEventListener('hashchange',syncNavigation);
 syncNavigation();
 document.addEventListener('click',e=>{
  const btn=e.target.closest('[data-copy]');
  if(btn){const target=$(btn.dataset.copy);if(target)copy(target.textContent,btn);}
 });
 updateClock();sync();convertDate();
 window.setInterval(updateClock,1000);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);
else init();
})();