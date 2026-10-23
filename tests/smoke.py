"""Build/SEO smoke tests: no external packages."""
import json, re
from pathlib import Path
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'translations.json').read_text(encoding='utf-8-sig'))
class Check(HTMLParser):
 def __init__(self):
  super().__init__();self.tags=[];self.alts=[];self.attrs=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);self.tags.append(tag);self.attrs.append((tag,a))
  if tag=='link' and a.get('rel')=='alternate':self.alts.append(a)
for code in d:
 p=(ROOT/'index.html' if code=='en' else ROOT/code/'index.html')
 assert p.is_file(),p
 s=p.read_text(encoding='utf-8')
 assert '@@' not in s
 c=Check();c.feed(s)
 attrs=c.attrs
 assert any(t=='html' and a.get('lang')==code for t,a in attrs)
 assert c.tags.count('h1')==1
 assert any(t=='meta' and a.get('name')=='description' and len(a.get('content',''))>95 for t,a in attrs)
 assert any(t=='link' and a.get('rel')=='canonical' and a.get('href')=='https://unixtime.othrys.be/'+('' if code=='en' else code+'/') for t,a in attrs)
 assert len(c.alts)==len(d)+1,(code,c.alts)
 assert all(x in s for x in ('id="unixInput"','id="dateInput"','id="liveSeconds"','application/ld+json','/app.js','/styles.css'))
 assert '<script src="https://' not in s
 print('PASS',code,'HTML, SEO and locale')
tree=ET.parse(ROOT/'sitemap.xml')
root=tree.getroot()
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
assert len(root.findall('s:url',ns))==len(d)+2
assert 'Sitemap: https://unixtime.othrys.be/sitemap.xml' in (ROOT/'robots.txt').read_text()
print('PASS sitemap.xml, robots.txt, all locales')
