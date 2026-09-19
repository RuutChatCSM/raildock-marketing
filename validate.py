from pathlib import Path
from html.parser import HTMLParser
import json, re, sys, yaml
ROOT=Path(__file__).parent
errors=[]

# OpenAPI structural checks
spec=yaml.safe_load((ROOT/'openapi/raildock.openapi.yaml').read_text())
if spec.get('openapi')!='3.1.0': errors.append('OpenAPI version is not 3.1.0')
valid_methods={'get','post','put','patch','delete','head','options','trace'}
operation_ids=[]
for path,item in spec['paths'].items():
    placeholders=set(re.findall(r'\{([^}]+)\}',path))
    for method,op in item.items():
        if method not in valid_methods: continue
        operation_ids.append(op.get('operationId'))
        declared={p['name'] for p in op.get('parameters',[]) if p.get('in')=='path'}
        if placeholders != declared:
            errors.append(f'{method.upper()} {path}: path params {placeholders} != declared {declared}')
if len(operation_ids)!=len(set(operation_ids)): errors.append('Duplicate operationId values')
text=(ROOT/'openapi/raildock.openapi.yaml').read_text()
for ref in re.findall(r"#/components/schemas/([A-Za-z0-9_-]+)",text):
    if ref not in spec['components']['schemas']: errors.append(f'Missing schema ref {ref}')

# Docs navigation + links
cfg=json.loads((ROOT/'docs/docs.json').read_text())
nav_slugs=[]
def walk(x):
    if isinstance(x,list):
        for y in x: walk(y)
    elif isinstance(x,dict):
        if 'pages' in x: walk(x['pages'])
        if 'groups' in x: walk(x['groups'])
    elif isinstance(x,str): nav_slugs.append(x)
walk(cfg['navigation']['tabs'])
for slug in nav_slugs:
    if not (ROOT/'docs'/f'{slug}.mdx').exists(): errors.append(f'docs.json references missing page: {slug}')
known={'/api-reference/','/'}
all_slugs={ '/' + p.relative_to(ROOT/'docs').with_suffix('').as_posix() for p in (ROOT/'docs').rglob('*.mdx') }
for p in (ROOT/'docs').rglob('*.mdx'):
    body=p.read_text()
    for href in re.findall(r'\[[^\]]+\]\((/[^) #]+)',body):
        h=href.rstrip('/') if href!='/' else href
        doc_target=h
        if h.startswith('/api-reference'): continue
        if doc_target not in all_slugs and href not in known:
            errors.append(f'{p.relative_to(ROOT)} links to missing docs route {href}')

# Marketing route/link + metadata checks
marketing_routes={'/'}
for p in (ROOT/'marketing').glob('*/index.html'):
    marketing_routes.add('/'+p.parent.name+'/')
doc_routes={'/docs/'+s.lstrip('/') for s in all_slugs}
class PageParser(HTMLParser):
    def __init__(self): super().__init__(); self.title=False; self.h1=0; self.desc=False; self.links=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='title': self.title=True
        if tag=='h1': self.h1+=1
        if tag=='meta' and d.get('name')=='description' and d.get('content'): self.desc=True
        if tag=='a' and d.get('href'): self.links.append(d['href'])
for p in (ROOT/'marketing').rglob('*.html'):
    q=PageParser(); q.feed(p.read_text())
    if not q.title or not q.desc or q.h1<1: errors.append(f'{p.relative_to(ROOT)} missing title/description/h1')
    for href in q.links:
        if not href.startswith('/') or href.startswith('//'): continue
        clean=href.split('#')[0]
        if clean.startswith('/docs/') or clean=='/docs/': continue
        if clean.startswith('/api-reference'): continue
        if clean not in marketing_routes and clean not in {'/404'}:
            errors.append(f'{p.relative_to(ROOT)} links to unknown marketing route {href}')

print(f"OpenAPI: {len(spec['paths'])} paths / {len(operation_ids)} operations")
print(f"Docs: {len(nav_slugs)} navigation pages / {len(all_slugs)} MDX files")
print(f"Marketing: {len(marketing_routes)} routes")
if errors:
    print('\nVALIDATION FAILED')
    for e in errors: print('-',e)
    sys.exit(1)
print('Validation passed.')
