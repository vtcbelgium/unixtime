// Zero-dependency converter correctness tests.
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const path=require('node:path');
const file=fs.readFileSync(path.join(__dirname,'..','app.js'),'utf8');
const pattern=/\}\)\(\);\s*$/;
assert(pattern.test(file),'Expected a self-invoking module');
const testFile=file.replace(pattern,'globalThis.__unixTest={nsOf,fmtPart,dateFromNs,floorDiv};})();');
const context={
  document:{documentElement:{lang:'en'},readyState:'loading',addEventListener(){}},
  window:{UNIXTIME_TEXT:{}},
  console
};
vm.runInNewContext(testFile,context);
const {nsOf,fmtPart,dateFromNs,floorDiv}=context.__unixTest;
const sec=1735689600n;
assert.equal(nsOf('1735689600','s').ns,sec*1000000000n);
assert.equal(nsOf('1735689600000','ms').ns,sec*1000000000n);
assert.equal(nsOf('1735689600000000','us').ns,sec*1000000000n);
assert.equal(nsOf('1735689600000000000','ns').ns,sec*1000000000n);
assert.equal(nsOf('1735689600','auto').unit,'s');
assert.equal(nsOf('1735689600000','auto').unit,'ms');
assert.equal(nsOf('1735689600000000','auto').unit,'us');
assert.equal(nsOf('1735689600000000000','auto').unit,'ns');
assert.equal(dateFromNs(sec*1000000000n).toISOString(),'2025-01-01T00:00:00.000Z');
assert.equal(dateFromNs(0n).toISOString(),'1970-01-01T00:00:00.000Z');
assert.equal(dateFromNs(-1000000000n).toISOString(),'1969-12-31T23:59:59.000Z');
assert.equal(fmtPart(nsOf('-1.5','s').ns,1000000000n,9),'-1.5');
assert.equal(fmtPart(nsOf('-0.000000001','s').ns,1000000000n,9),'-0.000000001');
assert.equal(fmtPart(nsOf('0.000000001','s').ns,1000000000n,9),'0.000000001');
assert.equal(fmtPart(nsOf('1.000001','ms').ns,1000000n,6),'1.000001');
assert.equal(floorDiv(-1n,1000000n),-1n);
assert.throws(()=>nsOf('garbage','s'));
assert.throws(()=>nsOf('1.1234567','ms'));
assert.throws(()=>dateFromNs(900000000000000000000000n));
console.log('PASS: 19 converter precision and range assertions');

