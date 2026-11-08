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
  (root/"guides"/"index.html",base+"/guides/"),
  (root/"about.html",base+"/about"),
  (root/"privacy.html",base+"/privacy"),
]
GUIDES=("unix-timestamp-milliseconds","unix-time-javascript","unix-time-python")
def breadcrumbs(html):
 blocks=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',html,re.S)]
 return [x for x in blocks if x["@type"]=="BreadcrumbList"]
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
  crumbs=breadcrumbs(html)
  assert len(crumbs)==1,file
  items=crumbs[0]["itemListElement"]
  assert [i["position"] for i in items]==[1,2,3],file
  assert [i["item"] for i in items]==[base+"/",base+"/guides/",canonical],file
  assert items[2]["name"]==re.search(r"<h1>(.*?)</h1>",html).group(1),file
  assert '<a href="/guides/">Guides</a></p>' in html,file
 if file.name!="index.html" or file.parent.name in GUIDES:
  assert re.search(r'<footer class="guide-footer">.*?href="/guides/".*?</footer>',html,re.S),file
 print("PASS canonical, heading, description:",canonical)
hub=(root/"guides"/"index.html").read_text(encoding="utf-8")
for slug in GUIDES:
 assert '<a href="/'+slug+'/">' in hub,slug
hub_ld=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',hub,re.S)]
assert [x["@type"] for x in hub_ld]==["CollectionPage","BreadcrumbList"]
assert hub_ld[0]["url"]==base+"/guides/"
assert [i["item"] for i in hub_ld[1]["itemListElement"]]==[base+"/",base+"/guides/"]
print("PASS guides hub links every guide and has breadcrumb JSON-LD")
for lang in ("nl","fr","de","es","pt"):
 assert '<a href="/guides/">' in (root/lang/"index.html").read_text(encoding="utf-8"),lang
assert '<a href="/guides/">' in (root/"index.html").read_text(encoding="utf-8")
print("PASS guides hub linked from every locale footer")
ns={"s":"http://www.sitemaps.org/schemas/sitemap/0.9"}
urlroot=ET.parse(root/"sitemap.xml").getroot()
urls=[x.text for x in urlroot.findall("s:url/s:loc",ns)]
for _,url in paths:assert url in urls,url
assert len(urls)==len(paths),(len(urls),len(paths))
print("PASS all",len(paths),"canonical URLs in sitemap")
for slug in (*GUIDES,"guides"):
 assert (root/"dist"/slug/"index.html").is_file(),slug
print("PASS all three guides and the hub included in deployable dist")
