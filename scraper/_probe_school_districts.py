"""
Probe FL school districts for their agenda platform.

Checks:
  - BoardDocs  : https://go.boarddocs.com/fl/{slug}/Board.nsf/Public
  - NovusAgenda: https://{slug}.novusagenda.com/agendapublic/
  - Legistar   : https://{slug}.legistar.com/Calendar.aspx

Prints seed-ready lines for confirmed districts.
Usage:
    python _probe_school_districts.py
"""
import asyncio
import re
import sys
import truststore; truststore.inject_into_ssl()

import httpx

TIMEOUT = 15.0

# ---------------------------------------------------------------------------
# FL school districts: (display_name, county, [boarddocs_slugs], [novus_slugs])
# ---------------------------------------------------------------------------
DISTRICTS = [
    # large / metro
    ("Miami-Dade County Schools",    "Miami-Dade",  ["fldade","mdcps","flmiamidade","dade"],                    ["miamidadeschools","mdcps"]),
    ("Broward County Schools",       "Broward",     ["flbroward","bcsb","broward","flbrow"],                    ["browardschools","bcps"]),
    ("Palm Beach County Schools",    "Palm Beach",  ["flpb","flpalmbeach","palmbeach","pbcsd"],                 ["palmbeachschools","pbcs"]),
    ("Hillsborough County Schools",  "Hillsborough",["flhills","flhillsborough","hillsborough","hcsb"],         ["hillsboroughschools","hcps"]),
    ("Orange County Schools",        "Orange",      ["florange","ocps","orangecounty","florangecounty"],        ["orangeschools","ocps"]),
    ("Pinellas County Schools",      "Pinellas",    ["flpinellas","pinellas","pcsd"],                           ["pinellasschools","pcps"]),
    ("Duval County Schools",         "Duval",       ["flduval","duval","dcps"],                                 ["duvalschools","dcps"]),
    ("Polk County Schools",          "Polk",        ["flpolk","polk","pcsd2"],                                  ["polkschools","pcsb"]),
    ("Brevard County Schools",       "Brevard",     ["flbre","flbrevard","brevard","bcps"],                     ["brevardschools","bcps2"]),
    ("Volusia County Schools",       "Volusia",     ["flvolusia","volusia","vcsd"],                             ["volusiaschools","vcps"]),
    ("Pasco County Schools",         "Pasco",       ["flpasco","pasco"],                                        ["paschools","pasco"]),
    ("Seminole County Schools",      "Seminole",    ["flseminole","seminole"],                                   ["seminoleschools","scps"]),
    ("Sarasota County Schools",      "Sarasota",    ["flsarasota","sarasota","scsb"],                           ["sarasotaschools","scps2"]),
    ("Manatee County Schools",       "Manatee",     ["flmanatee","manatee","mcsb"],                             ["manateeschools","mcps"]),
    ("Collier County Schools",       "Collier",     ["flcollier","collier"],                                     ["collierschools","ccps"]),
    ("Osceola County Schools",       "Osceola",     ["flosceola","osceola"],                                     ["osceolschools","ocps2"]),
    ("Alachua County Schools",       "Alachua",     ["flalachua","alachua"],                                     ["alachuaschools","acps"]),
    ("St. Johns County Schools",     "St. Johns",   ["flstjohns","stjohns","flsaintjohns"],                     ["stjohnsschools","sjcsd"]),
    ("Lee County Schools",           "Lee",         ["fllee","lee","lcsd"],                                      ["leeschools","lcps"]),
    ("Marion County Schools",        "Marion",      ["flmarion","marion","mcsb2"],                               ["marionschools","mcps2"]),
    ("St. Lucie County Schools",     "St. Lucie",   ["flstlucie","stlucie","slcsb","flsl"],                     ["stlucieschools","slcsd"]),
    ("Okaloosa County Schools",      "Okaloosa",    ["flokaloosa","okaloosa"],                                   ["okaloosaschools","ocsd"]),
    ("Charlotte County Schools",     "Charlotte",   ["flcharlotte","charlotte"],                                 ["charlotteschools","ccps2"]),
    ("Indian River County Schools",  "Indian River",["flindianriver","indianriver","flir","ircsb"],              ["indianriverschools","ircs"]),
    ("Clay County Schools",          "Clay",        ["flclay","clay"],                                           ["clayschools","ccps3"]),
    ("Flagler County Schools",       "Flagler",     ["flflagler","flagler"],                                     ["flaglerschools","fcsd"]),
    ("Hernando County Schools",      "Hernando",    ["flhernando","hernando"],                                   ["hernandoschools","hcps2"]),
    ("Santa Rosa County Schools",    "Santa Rosa",  ["flsantarosa","santarosa","flsr","srcsb"],                 ["santarosaschools","srcs"]),
    ("Leon County Schools",          "Leon",        ["flleon","leon"],                                           ["leonschools","lcps2"]),
    ("Escambia County Schools",      "Escambia",    ["flescambia","escambia"],                                   ["escambiaschools","ecsd"]),
    ("Bay County Schools",           "Bay",         ["flbay","bay","bcsb2"],                                    ["bayschools","bcps3"]),
    ("Martin County Schools",        "Martin",      ["flmartin","martin"],                                       ["martinschools","mcps3"]),
    ("Citrus County Schools",        "Citrus",      ["flcitrus","citrus"],                                       ["citrusschools","ccps4"]),
    ("Nassau County Schools",        "Nassau",      ["flnassau","nassau"],                                       ["nassauschools","ncsd"]),
    ("Putnam County Schools",        "Putnam",      ["flputnam","putnam"],                                       ["putnamschools","pcps2"]),
    ("Highlands County Schools",     "Highlands",   ["flhighlands","highlands"],                                 ["highlandsschools","hcps3"]),
    ("Walton County Schools",        "Walton",      ["flwalton","walton"],                                       ["waltonschools","wcsb"]),
    ("Columbia County Schools",      "Columbia",    ["flcolumbia","columbia"],                                   ["columbiaschools","ccps5"]),
    ("Hendry County Schools",        "Hendry",      ["flhendry","hendry"],                                       ["hendryschools","hcps4"]),
    ("Okeechobee County Schools",    "Okeechobee",  ["flokeechobee","okeechobee"],                               ["okeechobeeschools","ocsd2"]),
    ("Suwannee County Schools",      "Suwannee",    ["flsuwannee","suwannee"],                                   ["suwanneeschools","scps3"]),
    ("Sumter County Schools",        "Sumter",      ["flsumter","sumter"],                                       ["sumterschools","scsb2"]),
    ("Gadsden County Schools",       "Gadsden",     ["flgadsden","gadsden"],                                     ["gadsdenschools","gcsd"]),
    ("Jackson County Schools",       "Jackson",     ["fljackson","jackson","jcsb"],                             ["jacksonschools","jcps"]),
    ("DeSoto County Schools",        "DeSoto",      ["fldesoto","desoto"],                                       ["desotoschools","dcps2"]),
    ("Levy County Schools",          "Levy",        ["fllevy","levy"],                                           ["levyschools","lcps3"]),
    ("Hardee County Schools",        "Hardee",      ["flhardee","hardee"],                                       ["hardeeschools","hcps5"]),
    ("Monroe County Schools",        "Monroe",      ["flmonroe","monroe"],                                       ["monroeschools","mcps4"]),
    ("Baker County Schools",         "Baker",       ["flbaker","baker"],                                         ["bakerschools","bcps4"]),
    ("Wakulla County Schools",       "Wakulla",     ["flwakulla","wakulla"],                                     ["wakullaschools","wcps"]),
    ("Washington County Schools",    "Washington",  ["flwashington","washington"],                               ["washingtonschools","wcps2"]),
    ("Madison County Schools",       "Madison",     ["flmadison","madison"],                                     ["madisonschools","mcps5"]),
    ("Taylor County Schools",        "Taylor",      ["fltaylor","taylor"],                                       ["taylorschools","tcps"]),
    ("Holmes County Schools",        "Holmes",      ["flholmes","holmes"],                                       ["holmesschools","hcps6"]),
    ("Jefferson County Schools",     "Jefferson",   ["fljefferson","jefferson"],                                  ["jeffersonschools","jcps2"]),
    ("Gilchrist County Schools",     "Gilchrist",   ["flgilchrist","gilchrist"],                                  ["gilchristschools","gcps"]),
    ("Hamilton County Schools",      "Hamilton",    ["flhamilton","hamilton"],                                    ["hamiltonschools","hcps7"]),
    ("Lafayette County Schools",     "Lafayette",   ["fllafayette","lafayette"],                                  ["lafayetteschools","lcps4"]),
    ("Calhoun County Schools",       "Calhoun",     ["flcalhoun","calhoun"],                                     ["calhounschools","ccps6"]),
    ("Union County Schools",         "Union",       ["flunion","union"],                                         ["unionschools","ucps"]),
    ("Franklin County Schools",      "Franklin",    ["flfranklin","franklin"],                                    ["franklinschools","fcps2"]),
    ("Liberty County Schools",       "Liberty",     ["flliberty","liberty"],                                     ["libertyschools","lcps5"]),
    ("Glades County Schools",        "Glades",      ["flglades","glades"],                                       ["gladesschools","gcps2"]),
    ("Gulf County Schools",          "Gulf",        ["flgulf","gulf"],                                           ["gulfschools","gcps3"]),
    ("Bradford County Schools",      "Bradford",    ["flbradford","bradford"],                                   ["bradfordschools","bcps5"]),
    ("Dixie County Schools",         "Dixie",       ["fldixie","dixie"],                                         ["dixieschools","dcps3"]),
    ("Lake County Schools",          "Lake",        ["fllake","lake","lakecounty"],                              ["lakeschools","lcps6"]),
]

BD_BASE    = "https://go.boarddocs.com/fl/{slug}/Board.nsf/Public"
NOVUS_BASE = "https://{slug}.novusagenda.com/agendapublic/"


def _bd_url(slug: str) -> str:
    return BD_BASE.format(slug=slug)


def _novus_url(slug: str) -> str:
    return NOVUS_BASE.format(slug=slug)


async def probe_boarddocs(client: httpx.AsyncClient, slug: str) -> bool:
    url = _bd_url(slug)
    try:
        r = await client.get(url, timeout=TIMEOUT, follow_redirects=True)
        text = r.text.lower()
        if r.status_code == 200 and ("boarddocs" in text or "board.nsf" in text):
            return True
    except Exception:
        pass
    return False


async def probe_novus(client: httpx.AsyncClient, slug: str) -> bool:
    url = _novus_url(slug)
    try:
        r = await client.get(url, timeout=TIMEOUT, follow_redirects=True)
        text = r.text.lower()
        if r.status_code == 200 and len(r.text) > 5_000 and "http error occurred" not in text:
            if "novusagenda" in text or "ddldaterange" in text or "agendapublic" in text:
                return True
    except Exception:
        pass
    return False


async def probe_district(client: httpx.AsyncClient, name: str, county: str, bd_slugs: list, novus_slugs: list):
    # Try BoardDocs slugs concurrently
    bd_tasks = [probe_boarddocs(client, s) for s in bd_slugs]
    bd_results = await asyncio.gather(*bd_tasks)
    for slug, ok in zip(bd_slugs, bd_results):
        if ok:
            return (name, county, "boarddocs", _bd_url(slug), slug)

    # Try NovusAgenda slugs concurrently
    n_tasks = [probe_novus(client, s) for s in novus_slugs]
    n_results = await asyncio.gather(*n_tasks)
    for slug, ok in zip(novus_slugs, n_results):
        if ok:
            return (name, county, "novusagenda", _novus_url(slug), slug)

    return (name, county, None, None, None)


async def main():
    found = []
    not_found = []

    limits = httpx.Limits(max_connections=40, max_keepalive_connections=20)
    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0 (compatible; flock-off-probe/1.0)"},
        limits=limits,
        verify=True,
    ) as client:
        tasks = [
            probe_district(client, name, county, bd_slugs, novus_slugs)
            for name, county, bd_slugs, novus_slugs in DISTRICTS
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results):
        name, county, *_ = DISTRICTS[i]
        if isinstance(result, Exception):
            not_found.append((name, county, f"ERROR: {result}"))
            continue
        r_name, r_county, platform, url, slug = result
        if platform:
            found.append((r_name, r_county, platform, url, slug))
        else:
            not_found.append((name, county, "not found"))

    print("\n" + "="*70)
    print(f"FOUND ({len(found)}):")
    print("="*70)
    for name, county, platform, url, slug in sorted(found, key=lambda x: x[0]):
        print(f"  dict(name={name!r:<45} county={county!r:<20} platform={platform!r}, calendar_url={url!r}, entity_type='school_district'),")

    print(f"\nNOT FOUND ({len(not_found)}):")
    print("="*70)
    for name, county, reason in sorted(not_found, key=lambda x: x[0]):
        print(f"  {name:<50}  {reason}")

    print(f"\nSeed-ready count: {len(found)}")


if __name__ == "__main__":
    asyncio.run(main())
