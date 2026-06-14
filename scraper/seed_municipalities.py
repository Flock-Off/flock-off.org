"""
Seed the municipalities table with FL cities/counties.
Run once: python seed_municipalities.py

Legistar public slugs verified 2026-06-14 by probing /Bodies endpoint.
Token-gated cities (Tampa, Jacksonville, Miami, etc.) are listed as 'custom'
platform with their web portal URL until we find another scraping approach.

To find a Legistar slug: check if https://{slug}.legistar.com exists, then
verify public API access at https://webapi.legistar.com/v1/{slug}/Bodies
"""
import db

# fmt: off
MUNICIPALITIES = [
    # ── Legistar — publicly accessible API (no token needed) ─────────────────
    {"name": "City of Fort Lauderdale", "county": "Broward",      "platform": "legistar", "legistar_client": "fortlauderdale",  "calendar_url": "https://fortlauderdale.legistar.com/Calendar.aspx"},
    {"name": "Broward County",          "county": "Broward",      "platform": "legistar", "legistar_client": "broward",         "calendar_url": "https://broward.legistar.com/Calendar.aspx"},
    {"name": "City of Gainesville",     "county": "Alachua",      "platform": "legistar", "legistar_client": "gainesville",     "calendar_url": "https://gainesville.legistar.com/Calendar.aspx"},
    {"name": "City of Clearwater",      "county": "Pinellas",     "platform": "legistar", "legistar_client": "clearwater",      "calendar_url": "https://clearwater.legistar.com/Calendar.aspx"},
    {"name": "City of Hollywood",       "county": "Broward",      "platform": "legistar", "legistar_client": "hollywoodfl",     "calendar_url": "https://hollywoodfl.legistar.com/Calendar.aspx"},
    {"name": "City of Miramar",         "county": "Broward",      "platform": "legistar", "legistar_client": "miramar",         "calendar_url": "https://miramar.legistar.com/Calendar.aspx"},
    {"name": "City of Pensacola",       "county": "Escambia",     "platform": "legistar", "legistar_client": "pensacola",       "calendar_url": "https://pensacola.legistar.com/Calendar.aspx"},
    {"name": "City of Delray Beach",    "county": "Palm Beach",   "platform": "legistar", "legistar_client": "delraybeach",     "calendar_url": "https://delraybeach.legistar.com/Calendar.aspx"},
    {"name": "City of Coconut Creek",   "county": "Broward",      "platform": "legistar", "legistar_client": "coconutcreek",    "calendar_url": "https://coconutcreek.legistar.com/Calendar.aspx"},
    {"name": "City of Hallandale Beach","county": "Broward",      "platform": "legistar", "legistar_client": "hallandalebeach", "calendar_url": "https://hallandalebeach.legistar.com/Calendar.aspx"},
    {"name": "Pinellas County",         "county": "Pinellas",     "platform": "legistar", "legistar_client": "pinellas",        "calendar_url": "https://pinellas.legistar.com/Calendar.aspx"},
    {"name": "Alachua County",          "county": "Alachua",      "platform": "legistar", "legistar_client": "alachua",         "calendar_url": "https://alachua.legistar.com/Calendar.aspx"},
    {"name": "City of Ocala",           "county": "Marion",       "platform": "legistar", "legistar_client": "ocala",           "calendar_url": "https://ocala.legistar.com/Calendar.aspx"},
    {"name": "City of Cocoa",           "county": "Brevard",      "platform": "legistar", "legistar_client": "cocoa",           "calendar_url": "https://cocoa.legistar.com/Calendar.aspx"},

    # ── Legistar — token-gated (web portal public, API needs auth) ────────────
    # Marked as 'custom' for now so the Playwright scraper handles them.
    # If you can get API tokens from these municipalities, change to 'legistar'.
    {"name": "City of Miami",           "county": "Miami-Dade",   "platform": "custom",   "legistar_client": "miami",          "calendar_url": "https://miami.legistar.com/Calendar.aspx"},
    {"name": "City of Tampa",           "county": "Hillsborough", "platform": "custom",   "legistar_client": "tampa",          "calendar_url": "https://tampa.legistar.com/Calendar.aspx"},
    {"name": "City of Orlando",         "county": "Orange",       "platform": "custom",   "legistar_client": "orlando",        "calendar_url": "https://orlando.legistar.com/Calendar.aspx"},
    {"name": "City of Jacksonville",    "county": "Duval",        "platform": "custom",   "legistar_client": "jacksonville",   "calendar_url": "https://jacksonville.legistar.com/Calendar.aspx"},
    {"name": "City of Tallahassee",     "county": "Leon",         "platform": "custom",   "legistar_client": "tallahassee",    "calendar_url": "https://tallahassee.legistar.com/Calendar.aspx"},
    {"name": "City of St. Petersburg",  "county": "Pinellas",     "platform": "custom",   "legistar_client": "stpete",         "calendar_url": "https://stpete.legistar.com/Calendar.aspx"},
    {"name": "City of Sarasota",        "county": "Sarasota",     "platform": "custom",   "legistar_client": "sarasota",       "calendar_url": "https://sarasota.legistar.com/Calendar.aspx"},
    {"name": "Palm Beach County",       "county": "Palm Beach",   "platform": "custom",   "legistar_client": "pbcgov",         "calendar_url": "https://pbcgov.legistar.com/Calendar.aspx"},
    {"name": "City of Coral Springs",   "county": "Broward",      "platform": "custom",   "legistar_client": "coralsprings",   "calendar_url": "https://coralsprings.legistar.com/Calendar.aspx"},
    {"name": "City of Boca Raton",      "county": "Palm Beach",   "platform": "custom",   "legistar_client": "bocaraton",      "calendar_url": "https://bocaraton.legistar.com/Calendar.aspx"},
    {"name": "City of Pompano Beach",   "county": "Broward",      "platform": "custom",   "legistar_client": "pompanobeach",   "calendar_url": "https://pompanobeach.legistar.com/Calendar.aspx"},
    {"name": "City of Sunrise",         "county": "Broward",      "platform": "custom",   "legistar_client": "sunrise",        "calendar_url": "https://sunrise.legistar.com/Calendar.aspx"},
    {"name": "City of Palm Bay",        "county": "Brevard",      "platform": "custom",   "legistar_client": "palmbay",        "calendar_url": "https://palmbay.legistar.com/Calendar.aspx"},
    {"name": "City of Pembroke Pines",  "county": "Broward",      "platform": "custom",   "legistar_client": "pembrokepines",  "calendar_url": "https://pembrokepines.legistar.com/Calendar.aspx"},
    {"name": "City of Cape Coral",      "county": "Lee",          "platform": "custom",   "legistar_client": "capecoral",      "calendar_url": "https://capecoral.legistar.com/Calendar.aspx"},
    {"name": "City of Hialeah",         "county": "Miami-Dade",   "platform": "custom",   "legistar_client": "hialeah",        "calendar_url": "https://hialeah.legistar.com/Calendar.aspx"},
    {"name": "City of Lakeland",        "county": "Polk",         "platform": "custom",   "legistar_client": "lakeland",       "calendar_url": "https://lakeland.legistar.com/Calendar.aspx"},
    {"name": "City of Daytona Beach",   "county": "Volusia",      "platform": "custom",   "legistar_client": "daytonabeach",   "calendar_url": "https://daytonabeach.legistar.com/Calendar.aspx"},
    {"name": "City of West Palm Beach", "county": "Palm Beach",   "platform": "custom",   "legistar_client": "westpalmbeach",  "calendar_url": "https://westpalmbeach.legistar.com/Calendar.aspx"},
    {"name": "City of Davie",           "county": "Broward",      "platform": "custom",   "legistar_client": "davie",          "calendar_url": "https://davie.legistar.com/Calendar.aspx"},
    {"name": "City of Deerfield Beach", "county": "Broward",      "platform": "custom",   "legistar_client": "deerfieldbeach", "calendar_url": "https://deerfieldbeach.legistar.com/Calendar.aspx"},
    {"name": "City of Margate",         "county": "Broward",      "platform": "custom",   "legistar_client": "margate",        "calendar_url": "https://margate.legistar.com/Calendar.aspx"},
    {"name": "City of Lauderhill",      "county": "Broward",      "platform": "custom",   "legistar_client": "lauderhill",     "calendar_url": "https://lauderhill.legistar.com/Calendar.aspx"},
    {"name": "City of Tamarac",         "county": "Broward",      "platform": "custom",   "legistar_client": "tamarac",        "calendar_url": "https://tamarac.legistar.com/Calendar.aspx"},
    {"name": "City of North Lauderdale","county": "Broward",      "platform": "custom",   "legistar_client": "northlauderdale","calendar_url": "https://northlauderdale.legistar.com/Calendar.aspx"},
    {"name": "City of Dania Beach",     "county": "Broward",      "platform": "custom",   "legistar_client": "dania",          "calendar_url": "https://dania.legistar.com/Calendar.aspx"},
    {"name": "City of Weston",          "county": "Broward",      "platform": "custom",   "legistar_client": "westonfl",       "calendar_url": "https://westonfl.legistar.com/Calendar.aspx"},
    {"name": "City of Plantation",      "county": "Broward",      "platform": "custom",   "legistar_client": "plantation",     "calendar_url": "https://plantation.legistar.com/Calendar.aspx"},
    {"name": "Hillsborough County",     "county": "Hillsborough", "platform": "custom",   "legistar_client": "hillsborough",   "calendar_url": "https://hillsborough.legistar.com/Calendar.aspx"},
    {"name": "Orange County",           "county": "Orange",       "platform": "custom",   "legistar_client": "orangecountyfl", "calendar_url": "https://orangecountyfl.legistar.com/Calendar.aspx"},
    {"name": "Osceola County",          "county": "Osceola",      "platform": "custom",   "legistar_client": "osceola",        "calendar_url": "https://osceola.legistar.com/Calendar.aspx"},
    {"name": "Polk County",             "county": "Polk",         "platform": "custom",   "legistar_client": "polk",           "calendar_url": "https://polk.legistar.com/Calendar.aspx"},
    {"name": "Brevard County",          "county": "Brevard",      "platform": "custom",   "legistar_client": "brevard",        "calendar_url": "https://brevard.legistar.com/Calendar.aspx"},
    {"name": "Volusia County",          "county": "Volusia",      "platform": "custom",   "legistar_client": "volusia",        "calendar_url": "https://volusia.legistar.com/Calendar.aspx"},
    {"name": "Leon County",             "county": "Leon",         "platform": "custom",   "legistar_client": "leon",           "calendar_url": "https://leon.legistar.com/Calendar.aspx"},
    {"name": "City of Fort Myers",      "county": "Lee",          "platform": "custom",   "legistar_client": "fortmyers",      "calendar_url": "https://fortmyers.legistar.com/Calendar.aspx"},
    {"name": "City of Naples",          "county": "Collier",      "platform": "custom",   "legistar_client": "naples",         "calendar_url": "https://naples.legistar.com/Calendar.aspx"},
    {"name": "City of Kissimmee",       "county": "Osceola",      "platform": "custom",   "legistar_client": "kissimmee",      "calendar_url": "https://kissimmee.legistar.com/Calendar.aspx"},
    {"name": "City of Sanford",         "county": "Seminole",     "platform": "custom",   "legistar_client": "sanford",        "calendar_url": "https://sanford.legistar.com/Calendar.aspx"},
    {"name": "City of Melbourne",       "county": "Brevard",      "platform": "custom",   "legistar_client": "melbournefl",    "calendar_url": "https://melbournefl.legistar.com/Calendar.aspx"},
    {"name": "City of Titusville",      "county": "Brevard",      "platform": "custom",   "legistar_client": "titusville",     "calendar_url": "https://titusville.legistar.com/Calendar.aspx"},

    # ── CivicPlus (AgendaCenter HTML scrape) — verified 2026-06-14 by probe ─────
    {"name": "City of Deltona",              "county": "Volusia",       "platform": "civicplus", "calendar_url": "https://www.deltonafl.gov/AgendaCenter"},
    {"name": "City of Winter Haven",         "county": "Polk",          "platform": "civicplus", "calendar_url": "https://mywinterhaven.com/AgendaCenter"},
    {"name": "City of Homestead",            "county": "Miami-Dade",    "platform": "civicplus", "calendar_url": "https://www.homesteadfl.gov/AgendaCenter"},
    {"name": "City of Vero Beach",           "county": "Indian River",  "platform": "civicplus", "calendar_url": "https://www.covb.org/AgendaCenter"},
    {"name": "City of Sebastian",            "county": "Indian River",  "platform": "civicplus", "calendar_url": "https://www.cityofsebastian.org/AgendaCenter"},
    {"name": "City of Panama City",          "county": "Bay",           "platform": "civicplus", "calendar_url": "https://www.panamacity.gov/AgendaCenter"},
    {"name": "Sumter County",                "county": "Sumter",        "platform": "civicplus", "calendar_url": "https://www.sumtercountyfl.gov/AgendaCenter"},
    {"name": "City of Fernandina Beach",     "county": "Nassau",        "platform": "civicplus", "calendar_url": "https://fl-fernandinabeach2.civicplus.com/AgendaCenter"},
    {"name": "Town of Oakland",              "county": "Orange",        "platform": "civicplus", "calendar_url": "https://oaklandfl.gov/AgendaCenter"},
    {"name": "City of Atlantis",             "county": "Palm Beach",    "platform": "civicplus", "calendar_url": "https://www.atlantisfl.gov/AgendaCenter"},
    {"name": "City of Safety Harbor",        "county": "Pinellas",      "platform": "civicplus", "calendar_url": "https://www.cityofsafetyharbor.com/AgendaCenter"},
    {"name": "City of Temple Terrace",       "county": "Hillsborough",  "platform": "civicplus", "calendar_url": "https://www.templeterrace.com/AgendaCenter"},
    {"name": "City of Fort Walton Beach",    "county": "Okaloosa",      "platform": "civicplus", "calendar_url": "https://www.fwb.org/AgendaCenter"},
    {"name": "City of Destin",               "county": "Okaloosa",      "platform": "civicplus", "calendar_url": "https://www.cityofdestin.com/AgendaCenter"},
    {"name": "City of Crestview",            "county": "Okaloosa",      "platform": "civicplus", "calendar_url": "https://www.cityofcrestview.org/AgendaCenter"},
    {"name": "City of Milton",               "county": "Santa Rosa",    "platform": "civicplus", "calendar_url": "https://www.miltonfl.org/AgendaCenter"},
    {"name": "City of Tavares",              "county": "Lake",          "platform": "civicplus", "calendar_url": "https://www.tavares.org/AgendaCenter"},
    {"name": "City of St. Augustine",        "county": "St. Johns",     "platform": "civicplus", "calendar_url": "https://www.citystaug.com/AgendaCenter"},
    {"name": "City of St. Cloud",            "county": "Osceola",       "platform": "civicplus", "calendar_url": "https://www.stcloudfl.gov/AgendaCenter"},
    {"name": "City of Haines City",          "county": "Polk",          "platform": "civicplus", "calendar_url": "https://www.hainescity.com/AgendaCenter"},
    {"name": "City of Lake Wales",           "county": "Polk",          "platform": "civicplus", "calendar_url": "https://www.lakewalesfl.gov/AgendaCenter"},
    {"name": "City of Palatka",              "county": "Putnam",        "platform": "civicplus", "calendar_url": "https://www.palatka-fl.gov/AgendaCenter"},
    {"name": "City of Green Cove Springs",   "county": "Clay",          "platform": "civicplus", "calendar_url": "https://www.greencovesprings.com/AgendaCenter"},
    {"name": "City of Inverness",            "county": "Citrus",        "platform": "civicplus", "calendar_url": "https://www.inverness-fl.gov/AgendaCenter"},
    {"name": "City of Key West",             "county": "Monroe",        "platform": "civicplus", "calendar_url": "https://www.cityofkeywest-fl.gov/AgendaCenter"},
    {"name": "City of Alachua",              "county": "Alachua",       "platform": "civicplus", "calendar_url": "https://www.cityofalachua.com/AgendaCenter"},
    {"name": "City of Starke",               "county": "Bradford",      "platform": "civicplus", "calendar_url": "https://www.cityofstarke.org/AgendaCenter"},
    {"name": "City of Islamorada",           "county": "Monroe",        "platform": "civicplus", "calendar_url": "https://www.islamorada.fl.us/AgendaCenter"},
    {"name": "City of Belleview",            "county": "Marion",        "platform": "civicplus", "calendar_url": "https://www.belleviewfl.org/AgendaCenter"},
    {"name": "City of Lady Lake",            "county": "Lake",          "platform": "civicplus", "calendar_url": "https://www.ladylake.org/AgendaCenter"},
    {"name": "City of Clewiston",            "county": "Hendry",        "platform": "civicplus", "calendar_url": "https://www.clewiston-fl.gov/AgendaCenter"},
    {"name": "City of Jupiter",              "county": "Palm Beach",    "platform": "civicplus", "calendar_url": "https://www.jupiter.fl.us/AgendaCenter"},
    {"name": "City of Boynton Beach",        "county": "Palm Beach",    "platform": "civicplus", "calendar_url": "https://www.boynton-beach.org/AgendaCenter"},
    {"name": "City of Lantana",              "county": "Palm Beach",    "platform": "civicplus", "calendar_url": "https://www.lantana.org/AgendaCenter"},
    {"name": "City of Manalapan",            "county": "Palm Beach",    "platform": "civicplus", "calendar_url": "https://www.manalapan.org/AgendaCenter"},
    {"name": "Village of North Palm Beach",  "county": "Palm Beach",    "platform": "civicplus", "calendar_url": "https://www.village-npb.org/AgendaCenter"},
    {"name": "Village of Tequesta",          "county": "Palm Beach",    "platform": "civicplus", "calendar_url": "https://www.tequesta.org/AgendaCenter"},
    {"name": "City of Dania Beach",          "county": "Broward",       "platform": "civicplus", "calendar_url": "https://www.daniabeachfl.gov/AgendaCenter"},
    {"name": "City of Lauderdale Lakes",     "county": "Broward",       "platform": "civicplus", "calendar_url": "https://www.lauderdalelakes.org/AgendaCenter"},
    {"name": "City of Lauderdale-by-the-Sea","county": "Broward",       "platform": "civicplus", "calendar_url": "https://www.lauderdalebythesea-fl.gov/AgendaCenter"},
    {"name": "City of Wilton Manors",        "county": "Broward",       "platform": "civicplus", "calendar_url": "https://www.wiltonmanors.com/AgendaCenter"},
    {"name": "City of Lighthouse Point",     "county": "Broward",       "platform": "civicplus", "calendar_url": "https://www.lighthousepoint.com/AgendaCenter"},
    {"name": "City of Parkland",             "county": "Broward",       "platform": "civicplus", "calendar_url": "https://www.cityofparkland.org/AgendaCenter"},
    {"name": "City of Pembroke Pines",       "county": "Broward",       "platform": "civicplus", "calendar_url": "https://www.ppines.com/AgendaCenter"},
    {"name": "City of Opa-locka",            "county": "Miami-Dade",    "platform": "civicplus", "calendar_url": "https://www.opalockafl.gov/AgendaCenter"},
    {"name": "City of Miami Gardens",        "county": "Miami-Dade",    "platform": "civicplus", "calendar_url": "https://www.miamigardens-fl.gov/AgendaCenter"},
    {"name": "City of Sweetwater",           "county": "Miami-Dade",    "platform": "civicplus", "calendar_url": "https://www.cityofsweetwater.fl.gov/AgendaCenter"},
    {"name": "City of South Miami",          "county": "Miami-Dade",    "platform": "civicplus", "calendar_url": "https://www.southmiamifl.gov/AgendaCenter"},
    {"name": "City of Florida City",         "county": "Miami-Dade",    "platform": "civicplus", "calendar_url": "https://www.floridacityfl.gov/AgendaCenter"},
    {"name": "City of Aventura",             "county": "Miami-Dade",    "platform": "civicplus", "calendar_url": "https://www.cityofaventura.com/AgendaCenter"},
    {"name": "City of North Miami",          "county": "Miami-Dade",    "platform": "civicplus", "calendar_url": "https://www.northmiamifl.gov/AgendaCenter"},
    {"name": "City of North Miami Beach",    "county": "Miami-Dade",    "platform": "civicplus", "calendar_url": "https://www.citynmb.com/AgendaCenter"},
    {"name": "City of Sanibel",              "county": "Lee",           "platform": "civicplus", "calendar_url": "https://www.mysanibel.com/AgendaCenter"},
    {"name": "City of Palmetto",             "county": "Manatee",       "platform": "civicplus", "calendar_url": "https://www.palmettofl.org/AgendaCenter"},
    {"name": "City of Anna Maria",           "county": "Manatee",       "platform": "civicplus", "calendar_url": "https://www.cityofannamaria.com/AgendaCenter"},
    {"name": "City of Longboat Key",         "county": "Sarasota",      "platform": "civicplus", "calendar_url": "https://www.longboatkey.org/AgendaCenter"},
]
# fmt: on


def seed() -> None:
    client = db.get_client()
    for row in MUNICIPALITIES:
        row.setdefault("state", "FL")
        row.setdefault("active", True)
        client.table("municipalities").upsert(row, on_conflict="name").execute()
        print(f"  {row['platform']:<10}  {row['name']}")
    print(f"\nDone — {len(MUNICIPALITIES)} municipalities seeded.")


if __name__ == "__main__":
    seed()
