import csv,json,re,sys,datetime,pathlib,subprocess
root=pathlib.Path(sys.argv[1]); out=pathlib.Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)
def rows(kind):
    files=list((root/kind/'schema-01').rglob('*.csv'))
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
for r in rows('routes'):
    call=code(val(r,'callsign')); carrier=code(val(r,'airlinecode','code')); num=code(val(r,'number'))
    path=[code(a) for a in re.split(r'[-,; /]+',val(r,'airportcodes')) if a.strip()]
    if not call or len(path)<2 or any(len(a) not in (3,4) for a in path): continue
    if len(carrier)!=3: carrier=call[:3]
    routes.add((call,carrier,num,tuple(path)))
if len(routes)<10000 or len(airports)<1000 or len(airlines)<100 or sum(bool(a[0]) for a in airlines.values())<100: raise ValueError(f'Unexpected source/schema: {len(routes)} routes, {len(airports)} airports, {len(airlines)} airlines')
try: revision=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
except Exception: revision=''
obj={'schema':1,'builtAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':revision,'source':'Virtual Radar Server standing-data (CC0-1.0)','airlines':airlines,'airports':airports,'routes':sorted(routes)}
tmp=out/'db.tmp'; tmp.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')),encoding='utf-8'); tmp.replace(out/'db.json');print(len(routes),len(airports),len(airlines), (out/'db.json').stat().st_size)
