#!/usr/bin/env python3
"""Generate static, indexable UnixTime translations from one reviewed template.
No runtime database, network request or external JS package is needed.
"""
from pathlib import Path
from html import escape, unescape
import json, re, datetime
from xml.sax.saxutils import escape as xml_escape

ROOT=Path(__file__).resolve().parent
BASE='https://unixtime.othrys.be'
languages={'en':'English','nl':'Nederlands','fr':'Français','de':'Deutsch','es':'Español','pt':'Português'}
locales=json.loads((ROOT/'translations.json').read_text(encoding='utf-8-sig'))
template=(ROOT/'template.html').read_text(encoding='utf-8')
assert set(locales)==set(languages)
keys=set(re.findall(r'@@([A-Z][A-Z_]+)@@',template))
generated={'ALTERNATES','LANG','DIRECTION','CANONICAL','LANG_CHOICES','LANG_LINKS','SCHEMA','CLIENT_TEXT'}
fields=keys-generated
for lang,data in locales.items():
    assert fields<=set(data), (lang,fields-set(data))
    assert len(data['WHAT_P1'])>90 and len(data['WHAT_P2'])>90, lang

def canonical(code):
    return BASE+'/' if code=='en' else BASE+'/'+code+'/'

alternates='\n'.join('<link rel="alternate" hreflang="'+code+'" href="'+canonical(code)+'">' for code in languages)
alternates+='\n<link rel="alternate" hreflang="x-default" href="'+canonical('en')+'">'
for code,data in locales.items():
    choices='\n'.join('<option value="'+('/' if c=='en' else '/'+c+'/')+'"'+(' selected' if c==code else '')+'>'+escape(name)+'</option>' for c,name in languages.items())
    links='\n'.join('<a href="'+('/' if c=='en' else '/'+c+'/')+'"'+(' aria-current="page"' if c==code else '')+'>'+escape(name)+'</a>' for c,name in languages.items())
    schema={'@context':'https://schema.org','@type':'WebApplication','name':'UnixTime','url':canonical(code),
        'description':data['SEO_DESC'],'applicationCategory':'UtilitiesApplication','operatingSystem':'Any',
        'inLanguage':code,'isAccessibleForFree':True,'offers':{'@type':'Offer','price':'0','priceCurrency':'EUR'}}
    script_data={k:data[k] for k in ('invalid','precision','outOfRange','invalidDate','enterUnix','copied','detected','autoNotice','datePrecision','seconds','milliseconds','microseconds','nanoseconds') if k in data}
    script_data.update({'seconds':data['SECONDS'],'milliseconds':data['MILLISECONDS'],'microseconds':data['MICROSECONDS'],'nanoseconds':data['NANOSECONDS']})
    page=template
    special={'ALTERNATES':alternates,'LANG':code,'DIRECTION':'ltr','CANONICAL':canonical(code),
        'LANG_CHOICES':choices,'LANG_LINKS':links,'SCHEMA':json.dumps(schema,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'),
        'CLIENT_TEXT':json.dumps(script_data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')}
    for key,val in {**data,**special}.items():
        page=page.replace('@@'+key+'@@',escape(val,quote=True) if key not in special else val)
    assert '@@' not in page,(code,[x for x in re.findall(r'@@\w+@@',page)])
    path=(ROOT if code=='en' else ROOT/code)
    path.mkdir(exist_ok=True)
    (path/'index.html').write_text(page,encoding='utf-8')

GUIDES=('unix-timestamp-milliseconds','unix-time-javascript','unix-time-python')
GUIDES_URL=BASE+'/guides/'

def ld_script(data):
    return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+'</script>'

def breadcrumbs(*trail):
    return {'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[
        {'@type':'ListItem','position':i,'name':name,'item':url} for i,(name,url) in enumerate(trail,1)]}

# Guide pages are hand-written; only their breadcrumb is generated, so a rebuild replaces it in place.
breadcrumb_script=re.compile(r'<script type="application/ld\+json">\{"@context":"https://schema\.org","@type":"BreadcrumbList".*?</script>\n')
guide_cards=[]
for guide in GUIDES:
    file=ROOT/guide/'index.html'
    page=file.read_text(encoding='utf-8')
    heading=re.search(r'<h1>(.*?)</h1>',page).group(1)
    deck=re.search(r'<p class="guide-deck">(.*?)</p>',page).group(1)
    trail=breadcrumbs(('UnixTime',BASE+'/'),('Guides',GUIDES_URL),(unescape(heading),BASE+'/'+guide+'/'))
    page=breadcrumb_script.sub('',page).replace('</head>',ld_script(trail)+'\n</head>',1)
    file.write_text(page,encoding='utf-8')
    guide_cards.append('<h2><a href="/'+guide+'/">'+heading+'</a></h2>\n<p>'+deck+'</p>')

HUB_TITLE='Unix Time Guides and Timestamp References | UnixTime'
HUB_DESC='Practical Unix time guides: work with timestamps in JavaScript and Python, tell seconds from milliseconds and avoid common timezone mistakes.'
hub_schema={'@context':'https://schema.org','@type':'CollectionPage','url':GUIDES_URL,'name':HUB_TITLE,'description':HUB_DESC,
    'isPartOf':{'@type':'WebSite','name':'UnixTime','url':BASE+'/'},'inLanguage':'en'}
hub='''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>'''+HUB_TITLE+'''</title>
<meta name="description" content="'''+HUB_DESC+'''">
<meta name="robots" content="index,follow,max-snippet:-1">
<link rel="canonical" href="'''+GUIDES_URL+'''">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="stylesheet" href="/styles.css?v=3">
<script src="/fleet-spotlight.js" defer></script>
<meta property="og:type" content="website">
<meta property="og:title" content="'''+HUB_TITLE+'''">
<meta property="og:description" content="'''+HUB_DESC+'''">
<meta property="og:url" content="'''+GUIDES_URL+'''">
'''+ld_script(hub_schema)+'\n'+ld_script(breadcrumbs(('UnixTime',BASE+'/'),('Guides',GUIDES_URL)))+'''
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><nav class="topbar container" aria-label="Main navigation">
<a href="/" class="brand"><span class="brand-main"><strong>UNIX</strong>TIME</span><small class="brand-signature">an OTHRYS utility</small></a>
<div class="nav-links"><a href="/">Converter</a><a href="/about">About UnixTime</a></div>
<span aria-hidden="true"></span></nav></header>
<main class="guide-main" id="main">
<p class="guide-eyebrow"><a href="/">UnixTime</a> / Guides</p>
<h1>Unix time guides</h1>
<p class="guide-deck">Short, tested references for reading, converting and debugging Unix timestamps.</p>

'''+'\n'.join(guide_cards)+'''

<p>For a quick interactive check, use the <a href="/">UnixTime converter</a>.</p>
</main>
<footer class="guide-footer"><a href="/">UnixTime converter</a><a href="/about">About</a><a href="/privacy">Privacy</a><a href="https://othrys.be/" rel="noopener" target="_blank">OTHRYS</a></footer>
</body>
</html>
'''
(ROOT/'guides').mkdir(exist_ok=True)
(ROOT/'guides'/'index.html').write_text(hub,encoding='utf-8')

# Clean and small sitemap: one canonical entry per genuinely translated page.
out=['<?xml version="1.0" encoding="UTF-8"?>',
'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for code in languages:
    out+=['  <url>','    <loc>'+xml_escape(canonical(code))+'</loc>']
    out+=['    <xhtml:link rel="alternate" hreflang="'+alt+'" href="'+xml_escape(canonical(alt))+'"/>' for alt in languages]
    out+=['    <xhtml:link rel="alternate" hreflang="x-default" href="'+xml_escape(canonical('en'))+'"/>','  </url>']
for guide in GUIDES:
    out+=['  <url><loc>'+BASE+'/'+guide+'/</loc><lastmod>2026-10-23</lastmod></url>']
out+=['  <url><loc>'+GUIDES_URL+'</loc></url>','  <url><loc>'+BASE+'/about</loc></url>','  <url><loc>'+BASE+'/privacy</loc></url>','</urlset>']
(ROOT/'sitemap.xml').write_text('\n'.join(out)+'\n',encoding='utf-8')
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n',encoding='utf-8')
print('Generated',len(languages),'fully localized indexable pages and sitemap')
# Produce a clean deployable directory: exclude template, translations, tests and README.
import shutil
output=ROOT/'dist'
if output.exists(): shutil.rmtree(output)
output.mkdir()
for filename in ('index.html','styles.css','app.js','favicon.svg','fleet-spotlight.js','robots.txt','sitemap.xml','about.html','privacy.html','404.html','_headers','stats.js'):
    shutil.copy2(ROOT/filename,output/filename)
for lang in languages:
    if lang=='en':continue
    target=output/lang
    target.mkdir()
    shutil.copy2(ROOT/lang/'index.html',target/'index.html')
for guide in (*GUIDES,'guides'):
    shutil.copytree(ROOT/guide,output/guide)
print('Built dist/ —',len(list(output.rglob('*'))),'files/directories (ready for commercial-permitted static hosting).')
