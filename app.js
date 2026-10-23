/* UnixTime — independent, client-side timestamp conversion. No external APIs. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const T = window.UNIXTIME_TEXT || {};
  const locale = document.documentElement.lang || 'en';
  const NS = 1000000000n;
  const MAX_MS = 8640000000000000n;
  const POW = { s:1000000000n, ms:1000000n, us:1000n, ns:1n };
  const safeSet = (id, value) => { const e=$(id); if(e) e.textContent=value; };
  const word = (key, fallback) => T[key] || fallback;
  const digit = v => String(v).padStart(2,'0');
  const nowLocalInput = d => d.getFullYear()+'-'+digit(d.getMonth()+1)+'-'+digit(d.getDate())+'T'+digit(d.getHours())+':'+digit(d.getMinutes())+':'+digit(d.getSeconds());
  const floorDiv = (a,b) => a>=0n ? a/b : -((-a+b-1n)/b);
  const fmtPart = (ns, divisor, decimals) => {
    const negative=ns<0n;
    const absolute=negative?-ns:ns;
    const whole=absolute/divisor;
    const remainder=absolute%divisor;
    const signed=(negative?'-':'')+String(whole);
    if(!decimals || remainder===0n) return signed;
    const frac=String(remainder).padStart(decimals,'0').replace(/0+$/,'');
    return signed+'.'+frac;
  };
  const nsOf = (text,unit) => {
    const raw=String(text).trim().replace(/\s/g,'');
    if(!/^[+-]?\d{1,25}(?:\.\d{1,9})?$/.test(raw)) throw Error(word('invalid','Enter a numeric timestamp.'));
    const negative=raw.startsWith('-');
    const unsigned=raw.replace(/^[+-]/,'');
    const parts=unsigned.split('.');
    const chosen=unit==='auto' ? ((parts[0].length>=19)?'ns':(parts[0].length>=16)?'us':(parts[0].length>=13)?'ms':'s') : unit;
    const multiplier=POW[chosen];
    const maxFrac=String(multiplier).length-1;
    if((parts[1]||'').length>maxFrac) throw Error(word('precision','Too many decimal places for this unit.'));
    const base=BigInt(parts[0])*multiplier;
    const fractional=BigInt((parts[1]||'').padEnd(maxFrac,'0')||'0');
    return { ns:(negative?-1n:1n)*(base+fractional),unit:chosen };
  };
  function dateFromNs(ns){
    const millis=floorDiv(ns,1000000n);
    if(millis>MAX_MS || millis<(-MAX_MS)) throw Error(word('outOfRange','This timestamp is outside JavaScript date range.'));
    const d=new Date(Number(millis));
    if(!Number.isFinite(d.getTime())) throw Error(word('invalidDate','Invalid date.'));
    return d;
  }
  function formatZone(date,zone){
    try {
      const opts={year:'numeric',month:'short',day:'2-digit',weekday:'short',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'};
      if(zone && zone!=='local') opts.timeZone=zone;
      return new Intl.DateTimeFormat(locale,opts).format(date);
    } catch { return date.toUTCString(); }
  }
  function relativeFrom(date){
    const diff=Math.round((date.getTime()-Date.now())/1000);
    const abs=Math.abs(diff);
    const options=abs<90?['second',1]:abs<5400?['minute',60]:abs<129600?['hour',3600]:abs<3888000?['day',86400]:['month',2629800];
    try {return new Intl.RelativeTimeFormat(locale,{numeric:'auto'}).format(Math.round(diff/options[1]),options[0]);}
    catch {return (diff<0?'−':'+')+abs+' s';}
  }
  function copy(str,button) {
    if (!str || str==='—') return;
    const show=()=>{const prev=button.textContent;button.textContent=word('copied','Copied!');window.setTimeout(()=>button.textContent=prev,1400);};
    if(navigator.clipboard && window.isSecureContext){
      navigator.clipboard.writeText(str).then(show).catch(()=>fallback());
    } else fallback();
    function fallback(){
      const area=document.createElement('textarea');area.value=str;area.style.position='fixed';area.style.opacity='0';
      document.body.appendChild(area);area.focus();area.select();
      const ok=document.execCommand('copy');area.remove();if(ok)show();
    }
  }
  function showUnix(){
    const notice=$('inputNotice');
    const val=$('unixInput').value.trim();
    if(!val){notice.textContent=word('enterUnix','Enter a Unix timestamp to convert.');notice.classList.remove('error');return;}
    try {
      const {ns,unit}=nsOf(val,$('unitSelector').value);
      const d=dateFromNs(ns);
      safeSet('unixUtc',formatZone(d,'UTC'));
      safeSet('unixLocal',formatZone(d,$('zoneSelect').value));
      safeSet('unixIso',d.toISOString());
      safeSet('unixSeconds',fmtPart(ns,NS,9));
      safeSet('unixMs',fmtPart(ns,1000000n,6));
      safeSet('unixUs',fmtPart(ns,1000n,3));
      safeSet('unixNs',ns.toString());
      safeSet('unixRelative',relativeFrom(d));
      notice.classList.remove('error');
      notice.textContent=word('detected','Interpreted as')+' '+({s:word('seconds','seconds'),ms:word('milliseconds','milliseconds'),us:word('microseconds','microseconds'),ns:word('nanoseconds','nanoseconds')})[unit]+'. '+word('autoNotice','Choose a unit explicitly for historical or ambiguous values.');
    } catch(e) {
      ['unixUtc','unixLocal','unixIso','unixSeconds','unixMs','unixUs','unixNs','unixRelative'].forEach(x=>safeSet(x,'—'));
      notice.textContent=e.message;notice.classList.add('error');
    }
  }
  function convertDate(){
    const notice=$('dateNotice');
    try {
      const raw=$('dateInput').value;
      if(!raw || !/^\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?$/.test(raw)) throw Error(word('invalidDate','Enter a valid date and time.'));
      const date = new Date(raw+($('dateBasis').value==='utc'?'Z':''));
      if(!Number.isFinite(date.getTime())) throw Error(word('invalidDate','Invalid date.'));
      const ns=BigInt(date.getTime())*1000000n;
      safeSet('dateSec',fmtPart(ns,NS,9));
      safeSet('dateMs',fmtPart(ns,1000000n,6));
      safeSet('dateUs',fmtPart(ns,1000n,3));
      safeSet('dateNs',String(ns));
      notice.classList.remove('error');
      notice.textContent=word('datePrecision','Date input has millisecond precision; finer values are padded with zeros.');
    }catch(e){
      ['dateSec','dateMs','dateUs','dateNs'].forEach(id=>safeSet(id,'—'));
      notice.textContent=e.message;notice.classList.add('error');
    }
  }
  function clock(){
    const ms=Date.now(), d=new Date(ms);
    safeSet('liveSeconds',String(Math.floor(ms/1000)));
    safeSet('liveMilliseconds',String(ms));
    safeSet('liveIso',d.toISOString());
    safeSet('liveLocal',formatZone(d,'local'));
  }
  function init(){
    const q=new URLSearchParams(location.search), from=q.get('ts');
    $('unixInput').value=from&&/^[+\-]?\d{1,25}(?:\.\d{1,9})?$/.test(from)?from:String(Math.floor(Date.now()/1000));
    const u=q.get('unit');
    if(['s','ms','us','ns'].includes(u))$('unitSelector').value=u;
    const langMenu=$('langSelect');
    if(langMenu) langMenu.addEventListener('change',()=>{location.assign(langMenu.value);});
    const n=new Date();
    $('dateInput').value=n.toISOString().slice(0,19);
    $('unixInput').addEventListener('input',showUnix);
    $('unitSelector').addEventListener('change',showUnix);
    $('zoneSelect').addEventListener('change',showUnix);
    $('dateInput').addEventListener('input',convertDate);
    $('dateBasis').addEventListener('change',()=>{
      const old=$('dateBasis').value;
      const date=new Date();
      $('dateInput').value=old==='utc'?date.toISOString().slice(0,19):nowLocalInput(date);
      convertDate();
    });
    document.addEventListener('click',e=>{
      const b=e.target.closest('[data-copy]');
      if(b){ const el=$(b.dataset.copy); copy(el ? el.textContent : '',b); }
      const reset=e.target.closest('[data-now]');
      if(reset){$('unixInput').value=String(Math.floor(Date.now()/1000));$('unitSelector').value='s';showUnix();}
      const share=e.target.closest('[data-share]');
      if(share){
        const v=$('unixInput').value.trim();
        if(!/^[+\-]?\d{1,25}(?:\.\d{1,9})?$/.test(v))return;
        const url=new URL(location.href);url.search='';url.searchParams.set('ts',v);
        if($('unitSelector').value!=='auto')url.searchParams.set('unit',$('unitSelector').value);
        copy(url.toString(),share);
      }
    });
    clock();showUnix();convertDate();
    window.setInterval(clock,1000);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init);
  else init();
})();