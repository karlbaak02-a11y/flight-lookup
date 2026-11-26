import csv,json,re,sys,datetime,pathlib,subprocess,hashlib,gzip,urllib.request,io,os,time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
root=pathlib.Path(sys.argv[1]); out=pathlib.Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)
def rows(kind):
    files=sorted((root/kind/'schema-01').rglob('*.csv'))
    if not files: raise ValueError('No CSVs for '+kind)
    for p in files:
        with p.open(encoding='utf-8-sig',newline='') as f:
            for row in csv.DictReader(f):
                yield {re.sub('[^a-z0-9]','',k.lower()): (v or '').strip() for k,v in row.items() if k}
def val(r,*keys): return next((r[k] for k in keys if r.get(k)), '')
def code(s): return re.sub('[^A-Z0-9]','',s.upper())
airlines={}; airports={}; routes=set()
for r in rows('airlines'):
    icao=code(val(r,'icao','icaocode','airlineicao','code')); iata=code(val(r,'iata','iatacode','airlineiata'))
    if len(icao)!=3 or not icao.isalpha(): continue
    a=[iata if len(iata)==2 else '',val(r,'name','airlinename','operatorname'),val(r,'callsign','telephony','radiocallsign')]
    if icao not in airlines or sum(bool(x) for x in a)>sum(bool(x) for x in airlines[icao]): airlines[icao]=a
for r in rows('airports'):
    icao=code(val(r,'icao','icaocode','code')); iata=code(val(r,'iata','iatacode'))
    if len(icao)!=4: continue
    airports[icao]=[iata if len(iata)==3 else '',val(r,'name'),val(r,'location','city','municipality'),val(r,'countryiso2','country')]
# Join the MIT-licensed airportsdata IANA timezone mapping at build time only.
# The existing workflow needs no changes or new dependencies.
TZ_ROOT='https://raw.githubusercontent.com/mborsetti/airportsdata/main/'
def tz_fetch(name, env):
    local=os.environ.get(env)
    if local: return pathlib.Path(local).read_bytes()
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(TZ_ROOT+name,headers={'User-Agent':'FlightLookup-builder/1.4'}),timeout=45) as f:
                return f.read(20_000_001)
        except Exception:
            if attempt==2: raise
            time.sleep(2**attempt)
def timezone_data():
    raw=tz_fetch('airportsdata/airports.csv','FLIGHTLOOKUP_TZ_CSV')
    license_text=tz_fetch('LICENSE','FLIGHTLOOKUP_TZ_LICENSE').decode('utf-8')
    if len(raw)>20_000_000 or 'Permission is hereby granted' not in license_text: raise ValueError('Invalid timezone source or MIT license')
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    if not {'icao','iata','country','tz'}.issubset(reader.fieldnames or []): raise ValueError('Unexpected airport timezone schema')
    result={}; checked={}
    for r in reader:
        z=r['tz'].strip(); ident=code(r['icao']); iata=code(r['iata']); country=code(r['country'])
        if not z or not ident: continue
        if z not in checked:
            try: ZoneInfo(z); checked[z]=True
            except (ZoneInfoNotFoundError,ValueError): checked[z]=False
        if checked[z]: result[ident]=(iata,country,z)
    if len(result)<10000: raise ValueError('Airport timezone source unexpectedly small')
    return result,license_text
zones,tz_license=timezone_data()
for ident,a in airports.items():
    record=zones.get(ident)
    if record:
        iata,country,z=record
        # Reject explicit code/country conflicts instead of guessing a timezone.
        if a[0] and iata and a[0]!=iata: continue
        if len(a[3])==2 and country and a[3].upper()!=country: continue
        a.append(z)
matched=sum(len(a)>4 for a in airports.values())
for ident in ('RKSI','KJFK','EGLL','YSSY'):
    if ident in airports and len(airports[ident])<5: raise ValueError('Missing major airport timezone: '+ident)
if matched<1000: raise ValueError('Too few matched airport timezones: '+str(matched))
print(f'Airport timezone coverage: {matched}/{len(airports)}')

for r in rows('routes'):
    call=code(val(r,'callsign')); carrier=code(val(r,'airlinecode','code')); num=code(val(r,'number'))
    path=[code(a) for a in re.split(r'[-,; /]+',val(r,'airportcodes')) if a.strip()]
    if not call or len(path)<2 or any(len(a) not in (3,4) for a in path): continue
    if len(carrier)!=3: carrier=call[:3]
    routes.add((call,carrier,num,tuple(path)))
if len(routes)<10000 or len(airports)<1000 or len(airlines)<100 or sum(bool(a[0]) for a in airlines.values())<100: raise ValueError(f'Unexpected source/schema: {len(routes)} routes, {len(airports)} airports, {len(airlines)} airlines')
try: revision=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
except Exception: revision=''
# Fingerprint route content, not the time of the daily rebuild or upstream commit.
content={'schema':1,'airlines':airlines,'airports':airports,'routes':sorted(routes),'timezoneSource':'airportsdata (MIT; IANA timezone names)','timezoneLicense':tz_license}
def encode(obj): return json.dumps(obj,ensure_ascii=False,separators=(',',':'),sort_keys=True).encode('utf-8')
version=hashlib.sha256(encode(content)).hexdigest()
built=datetime.datetime.now(datetime.timezone.utc).isoformat()
obj={**content,'builtAt':built,'revision':revision,'source':'Virtual Radar Server standing-data (CC0-1.0); airportsdata (MIT)','contentVersion':version}
raw=encode(obj); compressed=gzip.compress(raw,compresslevel=9,mtime=0)
meta={'schema':1,'contentVersion':version,'builtAt':built,'bytes':len(raw),'gzipBytes':len(compressed),'routeCount':len(routes)}
for name,data in [('db.json',raw),('db.json.gz',compressed),('db-meta.json',encode(meta)),('airportsdata-LICENSE.txt',tz_license.encode('utf-8'))]:
    tmp=out/(name+'.tmp'); tmp.write_bytes(data); tmp.replace(out/name)
print(f'{len(routes)} routes, {len(airports)} airports, {len(airlines)} airlines; JSON {len(raw)} bytes, gzip {len(compressed)} bytes; content {version}')
