"""Validate UnixTime static SEO, readable guides, final canonical URLs and sitemap."""
from pathlib import Path
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
import json,re
root=Path(__file__).resolve().parents[1]
base="https://unixtime.othrys.be"
paths=[
  (root/"index.html",base+"/"),
  *[(root/lang/"index.html",base+"/"+lang+"/") for lang in ("nl","fr","de","es","pt")],
  *[(root/slug/"index.html",base+"/"+slug+"/") for slug in
    ("unix-timestamp-milliseconds","unix-time-javascript","unix-time-python")],
  (root/"about.html",base+"/about"),
  (root/"privacy.html",base+"/privacy"),
]
class Tags(HTMLParser):
 def __init__(self):
  super().__init__();self.attrs=[];self.h1=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);self.attrs.append((tag,a))
  if tag=='h1':self.h1+=1
for file,canonical in paths:
 assert file.exists(),file
 html=file.read_text(encoding="utf-8")
 p=Tags();p.feed(html)
 assert p.h1==1,(file,p.h1)
 assert any(t=="link" and a.get("rel")=="canonical" and a.get("href")==canonical for t,a in p.attrs),file
 assert any(t=="meta" and a.get("name")=="description" and len(a.get("content",""))>80 for t,a in p.attrs),file
 assert not re.search(r"href=['\"]/(?:about|privacy)\.html",html),file
 if "unix-time-" in str(file) or "unix-timestamp-milliseconds" in str(file):
  assert re.search(r'<h2[^>]*>',html),file
  assert len(re.findall(r'<p(?:\s[^>]*)?>',html))>=6,file
  ld=re.search(r'<script type="application/ld\+json">(.*?)</script>',html,re.S)
  assert ld,file
  data=json.loads(ld.group(1))
  assert data["@type"]=="WebPage",file
 print("PASS canonical, heading, description:",canonical)
ns={"s":"http://www.sitemaps.org/schemas/sitemap/0.9"}
urlroot=ET.parse(root/"sitemap.xml").getroot()
urls=[x.text for x in urlroot.findall("s:url/s:loc",ns)]
for _,url in paths:assert url in urls,url
assert len(urls)==len(paths),(len(urls),len(paths))
print("PASS all",len(paths),"canonical URLs in sitemap")
for slug in ("unix-timestamp-milliseconds","unix-time-javascript","unix-time-python"):
 assert (root/"dist"/slug/"index.html").is_file(),slug
print("PASS all three guides included in deployable dist")
