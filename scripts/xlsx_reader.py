import zipfile,xml.etree.ElementTree as E,re,collections,json
N={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def rows(path,sheet=1):
 z=zipfile.ZipFile(path); ss=[]
 if 'xl/sharedStrings.xml' in z.namelist():ss=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml'))]
 out=[]
 for r in E.fromstring(z.read(f'xl/worksheets/sheet{sheet}.xml')).findall('.//m:sheetData/m:row',N):
  d={}
  for c in r:
   v=c.find('m:v',N); inline=c.find('m:is',N); val=v.text if v is not None else ''.join(inline.itertext()) if inline is not None else ''
   if c.get('t')=='s':val=ss[int(val)]
   d[re.sub('[0-9]','',c.get('r'))]=val
  out.append((int(r.get('r')),d))
 return out
