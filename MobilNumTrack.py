#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  ███╗   ███╗ ██████╗ ██████╗ ██╗██╗      ███╗  ██╗██╗   ██╗███╗   ███╗
#  ████╗ ████║██╔═══██╗██╔══██╗██║██║     ████╗  ██║██║   ██║████╗ ████║
#  ██╔████╔██║██║   ██║██████╔╝██║██║     ██╔██╗ ██║██║   ██║██╔████╔██║
#  ██║╚██╔╝██║██║   ██║██╔══██╗██║██║     ██║╚██╗██║██║   ██║██║╚██╔╝██║
#  ██║ ╚═╝ ██║╚██████╔╝██████╔╝██║███████╗██║ ╚████║╚██████╔╝██║ ╚═╝ ██║
#  ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝
#
#  MobilNumTrack v4.1
#  NO username prompt  •  NO password prompt  •  NO token  •  EVER
#  Run:  python3 MobilNumTrack.py
# ─────────────────────────────────────────────────────────────────────────────

import sys, os, time, shutil, tempfile, stat
from datetime import datetime

VERSION       = "4.1"

# Auto-detect GitHub remote from local git config — never hardcoded, never prompts
def _detect_github_info():
    """Read git remote URL from .git/config — no network, no credentials."""
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        cfg  = os.path.join(base, ".git", "config")
        if not os.path.exists(cfg):
            return None, None
        with open(cfg) as f:
            content = f.read()
        import re
        # Match SSH:   git@github.com:user/repo.git
        m = re.search(r'git@github\.com[:/]([^/]+)/([^."\n]+)', content)
        if m:
            return m.group(1), m.group(2).rstrip(".git")
        # Match HTTPS: https://github.com/user/repo.git
        m = re.search(r'github\.com[:/]([^/]+)/([^."\n]+)', content)
        if m:
            return m.group(1), m.group(2).rstrip(".git")
    except Exception:
        pass
    return None, None

GITHUB_USER, GITHUB_REPO = _detect_github_info()
GITHUB_BRANCH = "main"

def _raw_base():
    if GITHUB_USER and GITHUB_REPO:
        return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
    return None

# ── Dependency check ──────────────────────────────────────────────────────────
def _check():
    import importlib.util
    missing = [p for p in ("phonenumbers","requests","pytz")
               if not importlib.util.find_spec(p)]
    if missing:
        print(f"\033[91m[!] Missing: {', '.join(missing)}\033[0m")
        print(f"\033[93m[*] Fix: pip3 install {' '.join(missing)} --break-system-packages\033[0m\n")
        sys.exit(1)
_check()

import phonenumbers, requests, pytz
from phonenumbers import geocoder, carrier
from phonenumbers import timezone as pn_tz
from phonenumbers import number_type, PhoneNumberType
from phonenumbers import is_valid_number, is_possible_number
from phonenumbers import format_number, PhoneNumberFormat

# ── Colours ───────────────────────────────────────────────────────────────────
R='\033[91m';G='\033[92m';Y='\033[93m';B='\033[94m'
M='\033[95m';C='\033[96m';W='\033[97m';BD='\033[1m'
DM='\033[2m';UL='\033[4m';RS='\033[0m'

# ── Country centroids ─────────────────────────────────────────────────────────
COORDS={
    "AF":(33.93,67.70),"AL":(41.15,20.17),"DZ":(28.03,1.66),"AR":(-38.42,-63.62),
    "AU":(-25.27,133.78),"AT":(47.52,14.55),"AZ":(40.14,47.58),"BD":(23.69,90.36),
    "BE":(50.50,4.47),"BR":(-14.24,-51.93),"BG":(42.73,25.49),"CA":(56.13,-106.35),
    "CL":(-35.68,-71.54),"CN":(35.86,104.20),"CO":(4.57,-74.30),"HR":(45.10,15.20),
    "CZ":(49.82,15.47),"DK":(56.26,9.50),"EG":(26.82,30.80),"ET":(9.15,40.49),
    "FI":(61.92,25.75),"FR":(46.23,2.21),"GH":(7.95,-1.02),"DE":(51.17,10.45),
    "GR":(39.07,21.82),"GT":(15.78,-90.23),"HK":(22.32,114.17),"HU":(47.16,19.50),
    "IN":(20.59,78.96),"ID":(-0.79,113.92),"IQ":(33.22,43.68),"IR":(32.43,53.69),
    "IE":(53.41,-8.24),"IL":(31.05,34.85),"IT":(41.87,12.57),"JP":(36.20,138.25),
    "JO":(30.59,36.24),"KZ":(48.02,66.92),"KE":(-0.02,37.91),"KR":(35.91,127.77),
    "KW":(29.31,47.48),"LB":(33.85,35.86),"LY":(26.34,17.23),"MY":(4.21,101.98),
    "MX":(23.63,-102.55),"MA":(31.79,-7.09),"NL":(52.13,5.29),"NZ":(-40.90,174.89),
    "NG":(9.08,8.68),"NO":(60.47,8.47),"PK":(30.38,69.35),"PH":(12.88,121.77),
    "PL":(51.92,19.15),"PT":(39.40,-8.22),"QA":(25.35,51.18),"RO":(45.94,24.97),
    "RU":(61.52,105.32),"SA":(23.89,45.08),"ZA":(-30.56,22.94),"ES":(40.46,-3.75),
    "LK":(7.87,80.77),"SE":(60.13,18.64),"CH":(46.82,8.23),"SY":(34.80,38.997),
    "TW":(23.70,120.96),"TZ":(-6.37,34.89),"TH":(15.87,100.99),"TN":(33.89,9.54),
    "TR":(38.96,35.24),"UG":(1.37,32.29),"UA":(48.38,31.17),"AE":(23.42,53.85),
    "GB":(55.38,-3.44),"US":(37.09,-95.71),"UZ":(41.38,64.59),"VE":(6.42,-66.59),
    "VN":(14.06,108.28),"YE":(15.55,48.52),"ZW":(-19.02,29.15),"MG":(-18.77,46.87),
    "CM":(3.85,11.50),"SN":(14.50,-14.45),"CI":(7.54,-5.55),"TG":(8.62,0.82),
    "BJ":(9.31,2.32),"ML":(17.57,-4.0),"BF":(12.36,-1.57),"NE":(17.61,8.08),
    "TD":(15.45,18.73),"SO":(5.15,46.20),"SD":(12.86,30.22),"CF":(6.61,20.94),
    "GN":(11.74,-15.31),"SL":(8.46,-11.78),"LR":(6.43,-9.43),"MZ":(-18.67,35.53),
    "ZM":(-13.13,27.85),"AO":(-11.20,17.87),"BW":(-22.33,24.68),"NA":(-22.96,18.49),
    "RW":(-1.94,29.87),"BI":(-3.37,29.92),"DJ":(11.83,42.59),"ER":(15.18,39.78),
    "JM":(18.11,-77.30),"TT":(10.69,-61.22),"CU":(21.52,-77.78),"DO":(18.74,-70.16),
    "HT":(18.97,-72.29),"NI":(12.87,-85.21),"HN":(15.20,-86.24),"SV":(13.79,-88.90),
    "BZ":(17.19,-88.50),"PA":(8.54,-80.78),"CR":(9.75,-83.75),"BO":(-16.29,-63.59),
    "PY":(-23.44,-58.44),"UY":(-32.52,-55.77),"EC":(-1.83,-78.18),"PE":(-9.19,-75.02),
    "GY":(4.86,-58.93),"MN":(46.86,103.85),"KG":(41.20,74.77),"TJ":(38.86,71.28),
    "TM":(38.97,59.56),"AM":(40.07,45.04),"GE":(42.31,43.36),"CY":(35.13,33.43),
    "MT":(35.94,14.38),"IS":(64.96,-19.02),"LU":(49.82,6.13),"BA":(44.17,17.68),
    "RS":(44.02,21.01),"ME":(42.71,19.37),"MK":(41.61,21.74),"SK":(48.67,19.70),
    "SI":(46.15,14.99),"EE":(58.60,25.01),"LV":(56.88,24.60),"LT":(55.17,23.88),
    "BY":(53.71,27.95),"MD":(47.41,28.37),"KP":(40.34,127.51),
}

TYPE_MAP={
    PhoneNumberType.MOBILE:"Mobile",PhoneNumberType.FIXED_LINE:"Fixed Line",
    PhoneNumberType.FIXED_LINE_OR_MOBILE:"Fixed Line or Mobile",
    PhoneNumberType.TOLL_FREE:"Toll Free",PhoneNumberType.PREMIUM_RATE:"Premium Rate",
    PhoneNumberType.SHARED_COST:"Shared Cost",PhoneNumberType.VOIP:"VoIP / Internet",
    PhoneNumberType.PERSONAL_NUMBER:"Personal Number",PhoneNumberType.PAGER:"Pager",
    PhoneNumberType.UAN:"UAN",PhoneNumberType.VOICEMAIL:"Voicemail",
    PhoneNumberType.UNKNOWN:"Unknown",
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def clr():   os.system('clear' if os.name=='posix' else 'cls')
def ln(ch="─",w=74,col=C): print(f"{col}{ch*w}{RS}")
def sec(t):  print();ln();print(f"{C}  ◈  {W}{BD}{t}{RS}");ln();print()
def row(l,v,lc=C,vc=W): print(f"  {lc}{BD}{l:<26}{RS} {vc}{v}{RS}")
def maps_url(a,o): return f"https://www.google.com/maps?q={a},{o}&z=6"
def osm_url(a,o):  return f"https://www.openstreetmap.org/?mlat={a}&mlon={o}&zoom=5"

def spin(msg, dur=0.8):
    f="⣾⣽⣻⢿⡿⣟⣯⣷"; t=time.time()+dur; i=0
    while time.time()<t:
        sys.stdout.write(f"\r  {C}{f[i%8]}{RS} {Y}{msg}{RS}   ")
        sys.stdout.flush(); time.sleep(0.07); i+=1
    sys.stdout.write(f"\r  {G}✔{RS} {msg:<52}\n")

# ── Auto-update — no credentials, no git, pure HTTPS requests ─────────────────
def _remote_version():
    base = _raw_base()
    if not base:
        return None
    try:
        r = requests.get(f"{base}/MobilNumTrack.py", timeout=5,
                         headers={"User-Agent":f"MobilNumTrack/{VERSION}"})
        if r.status_code == 200:
            for line in r.text.splitlines():
                if line.strip().startswith("VERSION") and "=" in line:
                    return line.split("=")[1].strip().strip('"\'')
    except Exception:
        pass
    return None

def _silent_update_check():
    """Runs silently at startup. Never blocks. Never asks anything."""
    try:
        remote = _remote_version()
        if remote and float(remote) > float(VERSION):
            print(f"\n  {Y}{BD}[UPDATE]{RS} {Y}v{remote} available"
                  f" — select {W}[3]{Y} to update.{RS}\n")
    except Exception:
        pass

def apply_update():
    base = _raw_base()
    FILES = ["MobilNumTrack.py","requirements.txt","install.sh"]
    print(f"\n  {C}{BD}── AUTO-UPDATE (HTTPS only — no git, no password) ───────{RS}\n")
    if not base:
        print(f"  {Y}[!]{RS} No GitHub remote detected in .git/config.")
        print(f"  {DM}Run the SSH setup first, then push to GitHub.{RS}\n"); return
    spin("Checking latest version ...", 1.0)
    remote = _remote_version()
    if not remote:
        print(f"\n  {R}[!]{RS} Cannot reach GitHub. Check internet.\n"); return
    print(f"  {DM}Local: {VERSION}   Remote: {remote}{RS}\n")
    try:
        newer = float(remote) > float(VERSION)
    except ValueError:
        newer = remote != VERSION
    if not newer:
        print(f"  {G}✔{RS}  Already on latest version ({VERSION}).\n"); return
    print(f"  {G}★{RS}  v{remote} found — downloading ...\n")
    tmp = tempfile.mkdtemp(prefix="mnt_upd_")
    try:
        for fname in FILES:
            spin(f"Downloading {fname} ...", 0.8)
            r = requests.get(f"{base}/{fname}", timeout=15,
                             headers={"User-Agent":f"MobilNumTrack/{VERSION}"})
            r.raise_for_status()
            with open(os.path.join(tmp,fname),"wb") as fh: fh.write(r.content)
        spin("Applying ...", 0.5)
        bdir = os.path.dirname(os.path.abspath(__file__))
        for fname in FILES:
            src=os.path.join(tmp,fname); dst=os.path.join(bdir,fname)
            if os.path.exists(src):
                shutil.copy2(src,dst)
                if fname.endswith((".py",".sh")):
                    st=os.stat(dst)
                    os.chmod(dst,st.st_mode|stat.S_IEXEC|stat.S_IXGRP|stat.S_IXOTH)
        print(f"\n  {G}{BD}✔  Updated to v{remote}! Restart:{RS}")
        print(f"  {C}  python3 MobilNumTrack.py{RS}\n")
    except Exception as e:
        print(f"\n  {R}[!] Update failed: {e}{RS}\n")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

# ── Free public APIs ──────────────────────────────────────────────────────────
def _restcountries(code):
    try:
        r=requests.get(f"https://restcountries.com/v3.1/alpha/{code}",timeout=6,
                       headers={"User-Agent":f"MobilNumTrack/{VERSION}"})
        if r.status_code==200: return r.json()[0]
    except Exception: pass
    return None

def _nominatim(lat,lon):
    try:
        r=requests.get("https://nominatim.openstreetmap.org/reverse",
                       params={"lat":lat,"lon":lon,"format":"json","zoom":10},
                       headers={"User-Agent":f"MobilNumTrack/{VERSION} (OSINT tool)"},
                       timeout=6)
        if r.status_code==200: return r.json()
    except Exception: pass
    return None

# ── Core tracker ──────────────────────────────────────────────────────────────
def track(raw):
    print()
    spin("Parsing number ...",           0.4)
    spin("Querying carrier database ...", 0.5)
    spin("Fetching country data ...",    0.8)
    spin("Address lookup ...",           1.0)
    spin("Building report ...",          0.3)
    print()
    try:
        parsed=phonenumbers.parse("+"+raw.lstrip("+"))
    except Exception:
        try: parsed=phonenumbers.parse(raw,None)
        except Exception as e:
            print(f"\n  {R}[ERROR]{RS} {e}")
            print(f"  {Y}Include country code — e.g.  +44 7700 900000{RS}\n"); return

    valid   =is_valid_number(parsed)
    possible=is_possible_number(parsed)
    e164    =format_number(parsed,PhoneNumberFormat.E164)
    intl    =format_number(parsed,PhoneNumberFormat.INTERNATIONAL)
    national=format_number(parsed,PhoneNumberFormat.NATIONAL)
    rfc3966 =format_number(parsed,PhoneNumberFormat.RFC3966)
    cc      =parsed.country_code
    region  =phonenumbers.region_code_for_number(parsed)
    geo_desc=geocoder.description_for_number(parsed,"en") or ""
    carrier_=carrier.name_for_number(parsed,"en") or "Unknown"
    timezones=list(pn_tz.time_zones_for_number(parsed))
    ptype   =TYPE_MAP.get(number_type(parsed),"Unknown")
    coords  =COORDS.get(region)
    lat=coords[0] if coords else 0.0; lon=coords[1] if coords else 0.0

    rc=_restcountries(region) if region else None
    country_name=capital=sub_region=continent=population=""
    currencies_s=languages_s=flag=borders_s=""
    if rc:
        try: country_name=rc["name"]["common"]
        except: pass
        try: capital=rc["capital"][0]
        except: pass
        try: sub_region=rc.get("subregion","")
        except: pass
        try: continent=rc.get("region","")
        except: pass
        try: population=f"{rc['population']:,}"
        except: pass
        try: currencies_s=", ".join(f"{v['name']} ({k})"for k,v in rc.get("currencies",{}).items())
        except: pass
        try: languages_s=", ".join(rc.get("languages",{}).values())
        except: pass
        try: flag=rc.get("flag","")
        except: pass
        try:
            b=rc.get("borders",[]); borders_s=", ".join(b) if b else "None / Island"
        except: pass

    nom=_nominatim(lat,lon) if coords else None
    nom_state=nom_county=nom_city=nom_postcode=nom_suburb=""
    if nom and "address" in nom:
        a=nom["address"]
        nom_state   =a.get("state","")
        nom_county  =a.get("county","") or a.get("district","")
        nom_city    =a.get("city","") or a.get("town","") or a.get("village","")
        nom_postcode=a.get("postcode","")
        nom_suburb  =a.get("suburb","") or a.get("neighbourhood","")

    ln("═"); print()
    print(f"  {(G+BD+'  ✔  VALID  '+RS) if valid else (Y+BD+'  ⚠  POSSIBLY VALID  '+RS) if possible else (R+BD+'  ✘  INVALID  '+RS)}")
    sec("NUMBER FORMATS")
    row("E.164",        e164,    C,G);row("International",intl,C,W)
    row("National",     national,C,W);row("RFC 3966",rfc3966,C,W)
    row("Dial Code",    f"+{cc}",C,Y)
    sec("CARRIER & LINE TYPE")
    row("Carrier / Operator",carrier_,C,G)
    row("Line Type",ptype,C,Y)
    row("Valid","YES" if valid else "NO",C,G if valid else R)
    sec("ADDRESS INTELLIGENCE")
    if country_name: row("Country",f"{flag}  {country_name}",C,W)
    elif region:     row("Country Code",region,C,W)
    if geo_desc and geo_desc!=country_name: row("Area",geo_desc,C,Y)
    if capital:      row("Capital City",capital,C,W)
    if sub_region:   row("Sub-Region",sub_region,C,W)
    if continent:    row("Continent",continent,C,W)
    if nom_state:    row("State / Province",nom_state,C,G)
    if nom_county:   row("County",nom_county,C,W)
    if nom_city:     row("Nearest City",nom_city,C,Y)
    if nom_suburb:   row("Suburb",nom_suburb,C,W)
    if nom_postcode: row("Postcode",nom_postcode,C,M)
    if population:   row("Population",population,C,DM+W)
    if currencies_s: row("Currency",currencies_s,C,DM+W)
    if languages_s:  row("Languages",languages_s,C,DM+W)
    if borders_s:    row("Borders",borders_s,C,DM+W)
    sec("TIMEZONE & LOCAL TIME")
    for i,tz in enumerate(timezones,1):
        row(f"Timezone {i}",tz,C,Y)
        try:
            now=datetime.now(pytz.timezone(tz))
            row(f"  Local Time {i}",now.strftime("%A, %d %B %Y  —  %H:%M:%S %Z"),C,G)
        except Exception: pass
    if not timezones: row("Timezone","Unknown",C,R)
    sec("MAP COORDINATES & LINKS")
    if coords:
        ns="N" if lat>=0 else "S"; ew="E" if lon>=0 else "W"
        row("Latitude",f"{abs(lat):.4f}° {ns}",C,W)
        row("Longitude",f"{abs(lon):.4f}° {ew}",C,W)
        print()
        print(f"  {Y}{BD}  ▶  Google Maps:{RS}\n     {UL}{B}{maps_url(lat,lon)}{RS}")
        print()
        print(f"  {Y}{BD}  ▶  OpenStreetMap:{RS}\n     {UL}{B}{osm_url(lat,lon)}{RS}")
    else:
        row("Coordinates","Not available",C,R)
    print(); ln("═")

# ── Banner ────────────────────────────────────────────────────────────────────
def banner():
    clr()
    print(f"""{C}{BD}
╔═══════════════════════════════════════════════════════════════════════════╗
║  ███╗   ███╗ ██████╗ ██████╗ ██╗██╗      ███╗  ██╗██╗   ██╗███╗   ███╗  ║
║  ████╗ ████║██╔═══██╗██╔══██╗██║██║     ████╗  ██║██║   ██║████╗ ████║  ║
║  ██╔████╔██║██║   ██║██████╔╝██║██║     ██╔██╗ ██║██║   ██║██╔████╔██║  ║
║  ██║╚██╔╝██║██║   ██║██╔══██╗██║██║     ██║╚██╗██║██║   ██║██║╚██╔╝██║  ║
║  ██║ ╚═╝ ██║╚██████╔╝██████╔╝██║███████╗██║ ╚████║╚██████╔╝██║ ╚═╝ ██║  ║
║  ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝  ║
║                                                                           ║
║   ████████╗██████╗  █████╗  ██████╗██╗  ██╗  v{VERSION}                     ║
║   ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝                              ║
║      ██║   ██████╔╝███████║██║     █████╔╝                               ║
║      ██║   ██╔══██╗██╔══██║██║     ██╔═██╗                               ║
║      ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗                              ║
║      ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝                             ║{RS}
{Y}{BD}║   NO username  •  NO password  •  NO token  •  Direct launch           ║{RS}
{C}{BD}╚═══════════════════════════════════════════════════════════════════════════╝{RS}
""")

# ── Menu ──────────────────────────────────────────────────────────────────────
MENU=[
    ("Track a Mobile Number",  "Single number — full address report"),
    ("Bulk Track Numbers",     "Many numbers in one session"),
    ("Check / Apply Update",   f"HTTPS update — no git, no password (v{VERSION})"),
    ("About","APIs and tool info"),
    ("Exit","Quit"),
]

def show_menu():
    ln("─"); print(f"  {W}{BD}MAIN MENU{RS}"); ln("─")
    for i,(n,d) in enumerate(MENU,1):
        print(f"  {Y}[{i}]{RS}  {W}{BD}{n:<30}{RS}  {DM}{d}{RS}")
    ln("─")

def opt_single():
    sec("TRACK A MOBILE NUMBER")
    print(f"  {C}Include country code. Examples:{RS}")
    print(f"    {Y}+44 7700 900000{RS}   UK     {Y}+1 202 555 0147{RS}  USA")
    print(f"    {Y}+91 98765 43210{RS}   India  {Y}+92 300 1234567{RS}  Pakistan\n")
    raw=input(f"  {G}{BD}Phone number  ➜  {RS}").strip()
    if not raw: print(f"\n  {R}No number entered.{RS}\n"); return
    track(raw)

def opt_bulk():
    sec("BULK TRACKER")
    print(f"  {C}One number per line. Type {Y}DONE{C} to finish.{RS}\n")
    nums=[]
    while True:
        r=input(f"  {G}{BD}  ➜  {RS}").strip()
        if r.upper() in ("DONE",""): break
        if r: nums.append(r)
    if not nums: print(f"\n  {R}No numbers entered.{RS}\n"); return
    for i,n in enumerate(nums,1):
        print(f"\n{M}{BD}  ── [ {i} / {len(nums)} ] ─────────────────────────────────{RS}")
        track(n)
        if i<len(nums): time.sleep(1.2)

def opt_update(): apply_update()

def opt_about():
    sec("ABOUT")
    rb=_raw_base()
    print(f"""
  {C}{BD}MobilNumTrack v{VERSION}{RS}
  {W}GitHub remote : {Y}{rb if rb else "Not set — run SSH setup first"}{RS}
  {W}Update method : {Y}HTTPS download — no git, no login, no password{RS}

  {W}{BD}Free APIs:{RS}
    {G}✔{RS}  phonenumbers (Google) — offline
    {G}✔{RS}  restcountries.com — no key
    {G}✔{RS}  nominatim.openstreetmap.org — no key
""")
    ln()

HANDLERS=[opt_single,opt_bulk,opt_update,opt_about,lambda:sys.exit(0)]

def main():
    banner()
    _silent_update_check()
    while True:
        show_menu()
        try:
            ch=input(f"\n  {G}{BD}Select  ➜  {RS}").strip()
            if not ch: continue
            idx=int(ch)-1
            if 0<=idx<len(HANDLERS): print(); HANDLERS[idx]()
            else: print(f"\n  {R}Enter 1–{len(HANDLERS)}.{RS}\n")
        except ValueError: print(f"\n  {R}Enter a number.{RS}\n")
        except KeyboardInterrupt: print(f"\n\n  {C}Goodbye!{RS}\n"); sys.exit(0)

if __name__=="__main__":
    main()
