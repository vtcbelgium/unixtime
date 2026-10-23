// Date input/timezone regression tests (zero third-party dependencies).
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const path=require('node:path');
const original=fs.readFileSync(path.join(__dirname,'..','app.js'),'utf8');
assert(/\}\)\(\);\s*$/.test(original));
const script=original.replace(/\}\)\(\);\s*$/,'globalThis.__test={parseDateInput,zoneParts};})();');
const context={
 document:{documentElement:{lang:'en'},readyState:'loading',addEventListener(){}},
 window:{UNIXTIME_TEXT:{}},
 console
};
vm.runInNewContext(script,context);
const {parseDateInput,zoneParts}=context.__test;
assert.equal(parseDateInput('2025-01-01','00:00:00','UTC').toISOString(),'2025-01-01T00:00:00.000Z');
assert.equal(parseDateInput('1970-01-01','00:00','UTC').getTime(),0);
assert.equal(parseDateInput('1969-12-31','23:59:59','UTC').getTime(),-1000);
assert.equal(parseDateInput('2026-10-23','17:09:21','Europe/Brussels').toISOString(),'2026-10-23T15:09:21.000Z');
assert.equal(parseDateInput('2026-01-23','17:09:21','Europe/Brussels').toISOString(),'2026-01-23T16:09:21.000Z');
assert.equal(parseDateInput('2026-10-23','11:09:21','America/New_York').toISOString(),'2026-10-23T15:09:21.000Z');
assert.equal(parseDateInput('2026-10-23','20:39:21','Asia/Kolkata').toISOString(),'2026-10-23T15:09:21.000Z');
assert.throws(()=>parseDateInput('2025-02-29','12:00','UTC'));
assert.throws(()=>parseDateInput('2026-03-29','02:30','Europe/Brussels'));
assert.equal(zoneParts(new Date('2026-10-23T15:09:21.000Z'),'Europe/Brussels'),'2026-10-23T17:09:21');
console.log('PASS: 10 date-input, leap year, daylight-saving and timezone checks');
