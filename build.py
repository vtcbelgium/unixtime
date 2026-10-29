#!/usr/bin/env python3
"""Generate static, indexable UnixTime translations from one reviewed template.
No runtime database, network request or external JS package is needed.
"""
from pathlib import Path
from html import escape
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
    
# Clean and small sitemap: one canonical entry per genuinely translated page.
out=['<?xml version="1.0" encoding="UTF-8"?>',
'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for code in languages:
    out+=['  <url>','    <loc>'+xml_escape(canonical(code))+'</loc>']
    out+=['    <xhtml:link rel="alternate" hreflang="'+alt+'" href="'+xml_escape(canonical(alt))+'"/>' for alt in languages]
    out+=['    <xhtml:link rel="alternate" hreflang="x-default" href="'+xml_escape(canonical('en'))+'"/>','  </url>']
GUIDES=('unix-timestamp-milliseconds','unix-time-javascript','unix-time-python')
for guide in GUIDES:
    out+=['  <url><loc>'+BASE+'/'+guide+'/</loc><lastmod>2026-10-23</lastmod></url>']
out+=['  <url><loc>'+BASE+'/about</loc></url>','  <url><loc>'+BASE+'/privacy</loc></url>','</urlset>']
(ROOT/'sitemap.xml').write_text('\n'.join(out)+'\n',encoding='utf-8')
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n',encoding='utf-8')
print('Generated',len(languages),'fully localized indexable pages and sitemap')
# Produce a clean deployable directory: exclude template, translations, tests and README.
import shutil
output=ROOT/'dist'
if output.exists(): shutil.rmtree(output)
output.mkdir()
for filename in ('index.html','styles.css','app.js','favicon.svg','robots.txt','sitemap.xml','about.html','privacy.html','404.html','_headers'):
    shutil.copy2(ROOT/filename,output/filename)
for lang in languages:
    if lang=='en':continue
    target=output/lang
    target.mkdir()
    shutil.copy2(ROOT/lang/'index.html',target/'index.html')
for guide in GUIDES:
    shutil.copytree(ROOT/guide,output/guide)
print('Built dist/ —',len(list(output.rglob('*'))),'files/directories (ready for commercial-permitted static hosting).')
