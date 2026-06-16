"""
Seed the municipalities table with FL cities/counties.
Run once: python seed_municipalities.py

Legistar public slugs verified 2026-06-14 by probing /Bodies endpoint.
NovusAgenda slugs verified 2026-06-14/15 by probing /agendapublic/ pages.
Token-gated Legistar cities that also appear on NovusAgenda use the
NovusAgenda platform for actual scraping; the 'custom' fallback remains
for sites not yet covered by a dedicated scraper.
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
    {"name": "Lake County",             "county": "Lake",         "platform": "legistar", "legistar_client": "lakecounty",      "calendar_url": "https://lakecounty.legistar.com/Calendar.aspx"},
    {"name": "Martin County",           "county": "Martin",       "platform": "legistar", "legistar_client": "martin",          "calendar_url": "https://martin.legistar.com/Calendar.aspx"},
    {"name": "City of Venice",          "county": "Sarasota",     "platform": "legistar", "legistar_client": "venice",          "calendar_url": "https://venice.legistar.com/Calendar.aspx"},
    {"name": "City of Coral Gables",    "county": "Miami-Dade",   "platform": "legistar", "legistar_client": "coralgables",     "calendar_url": "https://coralgables.legistar.com/Calendar.aspx"},
    {"name": "City of Doral",           "county": "Miami-Dade",   "platform": "legistar", "legistar_client": "doral",           "calendar_url": "https://doral.legistar.com/Calendar.aspx"},
    {"name": "City of Pinecrest",       "county": "Miami-Dade",   "platform": "legistar", "legistar_client": "pinecrest",       "calendar_url": "https://pinecrest.legistar.com/Calendar.aspx"},
    {"name": "City of Marco Island",    "county": "Collier",      "platform": "legistar", "legistar_client": "marcoisland",     "calendar_url": "https://marcoisland.legistar.com/Calendar.aspx"},
    {"name": "City of Key West",        "county": "Monroe",       "platform": "legistar", "legistar_client": "keywest",         "calendar_url": "https://keywest.legistar.com/Calendar.aspx"},
    {"name": "City of Pompano Beach",   "county": "Broward",      "platform": "legistar", "legistar_client": "pompano",         "calendar_url": "https://pompano.legistar.com/Calendar.aspx"},

    # ── NovusAgenda (Granicus) — public calendar, verified 2026-06-15 ──────────
    # Cities formerly listed as 'custom' (token-gated Legistar) that have a
    # working public NovusAgenda instance; switched to provide actual scraping.
    {"name": "City of Orlando",         "county": "Orange",       "platform": "novusagenda", "calendar_url": "https://orlando.novusagenda.com/agendapublic/"},
    {"name": "City of Jacksonville",    "county": "Duval",        "platform": "granicus", "calendar_url": "https://jacksonville.novusagenda.com/agendapublic/"},
    {"name": "City of Tallahassee",     "county": "Leon",         "platform": "granicus", "calendar_url": "https://tallahassee.novusagenda.com/agendapublic/"},
    {"name": "City of St. Petersburg",  "county": "Pinellas",     "platform": "novusagenda", "calendar_url": "https://stpete.novusagenda.com/agendapublic/"},
    {"name": "City of Sarasota",        "county": "Sarasota",     "platform": "novusagenda", "calendar_url": "https://sarasota.novusagenda.com/agendapublic/"},
    {"name": "City of Boca Raton",      "county": "Palm Beach",   "platform": "novusagenda", "calendar_url": "https://bocaraton.novusagenda.com/agendapublic/"},
    {"name": "City of Coral Springs",   "county": "Broward",      "platform": "novusagenda", "calendar_url": "https://coralsprings.novusagenda.com/agendapublic/"},
    {"name": "City of Sunrise",         "county": "Broward",      "platform": "novusagenda", "calendar_url": "https://sunrisefl.novusagenda.com/agendapublic/"},
    {"name": "City of Palm Bay",        "county": "Brevard",      "platform": "novusagenda", "calendar_url": "https://palmbay.novusagenda.com/agendapublic/"},
    {"name": "City of Cape Coral",      "county": "Lee",          "platform": "novusagenda", "calendar_url": "https://capecoral.novusagenda.com/agendapublic/"},
    {"name": "City of Fort Myers",      "county": "Lee",          "platform": "novusagenda", "calendar_url": "https://fortmyers.novusagenda.com/agendapublic/"},
    {"name": "City of Lakeland",        "county": "Polk",         "platform": "novusagenda", "calendar_url": "https://lakeland.novusagenda.com/agendapublic/"},
    {"name": "City of West Palm Beach", "county": "Palm Beach",   "platform": "novusagenda", "calendar_url": "https://westpalmbeach.novusagenda.com/agendapublic/"},
    {"name": "City of Kissimmee",       "county": "Osceola",      "platform": "novusagenda", "calendar_url": "https://kissimmee.novusagenda.com/agendapublic/"},
    {"name": "City of Sanford",         "county": "Seminole",     "platform": "novusagenda", "calendar_url": "https://sanford.novusagenda.com/agendapublic/"},
    {"name": "City of Melbourne",       "county": "Brevard",      "platform": "novusagenda", "calendar_url": "https://melbourne.novusagenda.com/agendapublic/"},
    {"name": "City of Titusville",      "county": "Brevard",      "platform": "novusagenda", "calendar_url": "https://titusville.novusagenda.com/agendapublic/"},
    {"name": "City of Weston",          "county": "Broward",      "platform": "novusagenda", "calendar_url": "https://weston.novusagenda.com/agendapublic/"},
    {"name": "Palm Beach County",       "county": "Palm Beach",   "platform": "novusagenda", "calendar_url": "https://pbcgov.novusagenda.com/agendapublic/"},
    {"name": "Hillsborough County",     "county": "Hillsborough", "platform": "novusagenda", "calendar_url": "https://hillsboroughcounty.novusagenda.com/agendapublic/"},
    {"name": "Orange County",           "county": "Orange",       "platform": "novusagenda", "calendar_url": "https://orangecountyfl.novusagenda.com/agendapublic/"},
    {"name": "Brevard County",          "county": "Brevard",      "platform": "novusagenda", "calendar_url": "https://brevardfl.novusagenda.com/agendapublic/"},
    {"name": "Volusia County",          "county": "Volusia",      "platform": "novusagenda", "calendar_url": "https://volusiacounty.novusagenda.com/agendapublic/"},
    {"name": "Polk County",             "county": "Polk",         "platform": "novusagenda", "calendar_url": "https://polkcounty.novusagenda.com/agendapublic/"},
    # Counties with no prior entry
    {"name": "Lee County",              "county": "Lee",          "platform": "novusagenda", "calendar_url": "https://leecounty.novusagenda.com/agendapublic/"},
    {"name": "Charlotte County",        "county": "Charlotte",    "platform": "novusagenda", "calendar_url": "https://charlottecounty.novusagenda.com/agendapublic/"},
    {"name": "Collier County",          "county": "Collier",      "platform": "novusagenda", "calendar_url": "https://colliercountyfl.novusagenda.com/agendapublic/"},
    {"name": "Seminole County",         "county": "Seminole",     "platform": "novusagenda", "calendar_url": "https://seminolecounty.novusagenda.com/agendapublic/"},
    {"name": "St. Johns County",        "county": "St. Johns",    "platform": "novusagenda", "calendar_url": "https://stjohnscounty.novusagenda.com/agendapublic/"},
    {"name": "Flagler County",          "county": "Flagler",      "platform": "novusagenda", "calendar_url": "https://flaglercounty.novusagenda.com/agendapublic/"},
    {"name": "Hernando County",         "county": "Hernando",     "platform": "novusagenda", "calendar_url": "https://hernandocounty.novusagenda.com/agendapublic/"},
    {"name": "Pasco County",            "county": "Pasco",        "platform": "novusagenda", "calendar_url": "https://pascogov.novusagenda.com/agendapublic/"},
    {"name": "Citrus County",           "county": "Citrus",       "platform": "novusagenda", "calendar_url": "https://citruscounty.novusagenda.com/agendapublic/"},
    {"name": "St. Lucie County",        "county": "St. Lucie",    "platform": "novusagenda", "calendar_url": "https://stlucie.novusagenda.com/agendapublic/"},
    {"name": "Indian River County",     "county": "Indian River", "platform": "novusagenda", "calendar_url": "https://indianrivercounty.novusagenda.com/agendapublic/"},
    {"name": "Manatee County",          "county": "Manatee",      "platform": "novusagenda", "calendar_url": "https://manatee.novusagenda.com/agendapublic/"},
    {"name": "Miami-Dade County",       "county": "Miami-Dade",   "platform": "novusagenda", "calendar_url": "https://miamidade.novusagenda.com/agendapublic/"},
    {"name": "Marion County",           "county": "Marion",       "platform": "novusagenda", "calendar_url": "https://marioncounty.novusagenda.com/agendapublic/"},
    {"name": "Clay County",             "county": "Clay",         "platform": "novusagenda", "calendar_url": "https://claycounty.novusagenda.com/agendapublic/"},
    {"name": "Nassau County",           "county": "Nassau",       "platform": "novusagenda", "calendar_url": "https://nassaucounty.novusagenda.com/agendapublic/"},
    {"name": "Putnam County",           "county": "Putnam",       "platform": "novusagenda", "calendar_url": "https://putnamcounty.novusagenda.com/agendapublic/"},
    {"name": "Walton County",           "county": "Walton",       "platform": "novusagenda", "calendar_url": "https://waltoncounty.novusagenda.com/agendapublic/"},
    {"name": "Bay County",              "county": "Bay",          "platform": "novusagenda", "calendar_url": "https://baycounty.novusagenda.com/agendapublic/"},
    {"name": "Okaloosa County",         "county": "Okaloosa",     "platform": "novusagenda", "calendar_url": "https://okaloosacounty.novusagenda.com/agendapublic/"},
    {"name": "Santa Rosa County",       "county": "Santa Rosa",   "platform": "novusagenda", "calendar_url": "https://santarosacounty.novusagenda.com/agendapublic/"},
    {"name": "Escambia County",         "county": "Escambia",     "platform": "novusagenda", "calendar_url": "https://escambiacounty.novusagenda.com/agendapublic/"},
    {"name": "Highlands County",        "county": "Highlands",    "platform": "novusagenda", "calendar_url": "https://highlandscounty.novusagenda.com/agendapublic/"},
    {"name": "Columbia County",         "county": "Columbia",     "platform": "novusagenda", "calendar_url": "https://columbiacounty.novusagenda.com/agendapublic/"},
    {"name": "Sarasota County",         "county": "Sarasota",     "platform": "novusagenda", "calendar_url": "https://sarasotafl.novusagenda.com/agendapublic/"},
    # Cities with no prior entry
    {"name": "City of Port St. Lucie",  "county": "St. Lucie",   "platform": "novusagenda", "calendar_url": "https://portsl.novusagenda.com/agendapublic/"},
    {"name": "City of Palm Beach Gardens","county":"Palm Beach",  "platform": "novusagenda", "calendar_url": "https://pbgfl.novusagenda.com/agendapublic/"},
    {"name": "City of Bradenton",       "county": "Manatee",      "platform": "novusagenda", "calendar_url": "https://bradenton.novusagenda.com/agendapublic/"},

    # ── Legistar — public web API confirmed 2026-06-15 (slug was wrong before) ──
    {"name": "City of Margate",         "county": "Broward",      "platform": "legistar", "legistar_client": "margatefl",      "calendar_url": "https://margatefl.legistar.com/Calendar.aspx"},

    # ── NovusAgenda — confirmed 2026-06-15 (were falsely listed as token-gated) ─
    {"name": "City of Miami",           "county": "Miami-Dade",   "platform": "novusagenda", "calendar_url": "https://miami.novusagenda.com/agendapublic/"},
    {"name": "City of Naples",          "county": "Collier",      "platform": "novusagenda", "calendar_url": "https://naples.novusagenda.com/agendapublic/"},
    {"name": "City of Lauderhill",      "county": "Broward",      "platform": "novusagenda", "calendar_url": "https://lauderhill.novusagenda.com/agendapublic/"},
    {"name": "City of North Lauderdale","county": "Broward",      "platform": "granicus", "calendar_url": "https://northlauderdale.novusagenda.com/agendapublic/"},
    {"name": "City of Plantation",      "county": "Broward",      "platform": "novusagenda", "calendar_url": "https://plantation.novusagenda.com/agendapublic/"},
    {"name": "Osceola County",          "county": "Osceola",      "platform": "novusagenda", "calendar_url": "https://osceolagov.novusagenda.com/agendapublic/"},
    {"name": "Leon County",             "county": "Leon",         "platform": "novusagenda", "calendar_url": "https://leon.novusagenda.com/agendapublic/"},

    # ── CivicPlus — confirmed 2026-06-15 (had wrong platform before) ──────────
    {"name": "City of Hialeah",         "county": "Miami-Dade",   "platform": "civicplus", "calendar_url": "https://www.hialeahfl.gov/AgendaCenter"},
    {"name": "City of Daytona Beach",   "county": "Volusia",      "platform": "civicplus", "calendar_url": "https://www.daytonabeach.gov/AgendaCenter"},
    {"name": "City of Davie",           "county": "Broward",      "platform": "civicplus", "calendar_url": "https://www.davie-fl.gov/AgendaCenter"},
    {"name": "City of Deerfield Beach", "county": "Broward",      "platform": "civicplus", "calendar_url": "https://www.deerfield-beach.com/AgendaCenter"},
    {"name": "City of Tamarac",         "county": "Broward",      "platform": "civicplus", "calendar_url": "https://www.tamarac.gov/AgendaCenter"},

    # ── Tampa — Hyland OnBase AgendaOnline ────────────────────────────────────
    {"name": "City of Tampa",           "county": "Hillsborough", "platform": "hyland",   "calendar_url": "https://tampagov.hylandcloud.com/251agendaonline/"},

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

    # ── NovusAgenda expansion — probe-confirmed 2026-06-16 ───────────────────
    # ── Pinellas ──────────────────────────────────────────────────────────────
    {"name": "City of Largo",               "county": "Pinellas",      "platform": "novusagenda", "calendar_url": "https://largo.novusagenda.com/agendapublic/"},
    {"name": "City of Pinellas Park",       "county": "Pinellas",      "platform": "novusagenda", "calendar_url": "https://pinellaspark.novusagenda.com/agendapublic/"},
    {"name": "City of Dunedin",             "county": "Pinellas",      "platform": "novusagenda", "calendar_url": "https://dunedin.novusagenda.com/agendapublic/"},
    {"name": "City of Tarpon Springs",      "county": "Pinellas",      "platform": "novusagenda", "calendar_url": "https://tarponsprings.novusagenda.com/agendapublic/"},
    {"name": "City of Gulfport",            "county": "Pinellas",      "platform": "novusagenda", "calendar_url": "https://gulfport.novusagenda.com/agendapublic/"},
    {"name": "City of St. Pete Beach",      "county": "Pinellas",      "platform": "novusagenda", "calendar_url": "https://stpetebeach.novusagenda.com/agendapublic/"},
    {"name": "City of Oldsmar",             "county": "Pinellas",      "platform": "novusagenda", "calendar_url": "https://oldsmar.novusagenda.com/agendapublic/"},
    {"name": "City of Seminole",            "county": "Pinellas",      "platform": "novusagenda", "calendar_url": "https://seminole.novusagenda.com/agendapublic/"},
    {"name": "City of Madeira Beach",       "county": "Pinellas",      "platform": "novusagenda", "calendar_url": "https://madeirabeach.novusagenda.com/agendapublic/"},
    {"name": "City of Treasure Island",     "county": "Pinellas",      "platform": "novusagenda", "calendar_url": "https://treasureisland.novusagenda.com/agendapublic/"},
    {"name": "City of Belleair",            "county": "Pinellas",      "platform": "novusagenda", "calendar_url": "https://belleair.novusagenda.com/agendapublic/"},
    # ── Hillsborough ──────────────────────────────────────────────────────────
    {"name": "City of Plant City",          "county": "Hillsborough",  "platform": "novusagenda", "calendar_url": "https://plantcity.novusagenda.com/agendapublic/"},
    # ── Orange ────────────────────────────────────────────────────────────────
    {"name": "City of Apopka",              "county": "Orange",        "platform": "novusagenda", "calendar_url": "https://apopka.novusagenda.com/agendapublic/"},
    {"name": "City of Ocoee",               "county": "Orange",        "platform": "novusagenda", "calendar_url": "https://ocoee.novusagenda.com/agendapublic/"},
    {"name": "City of Winter Park",         "county": "Orange",        "platform": "novusagenda", "calendar_url": "https://winterpark.novusagenda.com/agendapublic/"},
    {"name": "City of Winter Garden",       "county": "Orange",        "platform": "novusagenda", "calendar_url": "https://wintergarden.novusagenda.com/agendapublic/"},
    {"name": "City of Maitland",            "county": "Orange",        "platform": "novusagenda", "calendar_url": "https://maitland.novusagenda.com/agendapublic/"},
    {"name": "City of Edgewood",            "county": "Orange",        "platform": "novusagenda", "calendar_url": "https://edgewood.novusagenda.com/agendapublic/"},
    # ── Seminole ──────────────────────────────────────────────────────────────
    {"name": "City of Altamonte Springs",   "county": "Seminole",      "platform": "novusagenda", "calendar_url": "https://altamontesprings.novusagenda.com/agendapublic/"},
    {"name": "City of Casselberry",         "county": "Seminole",      "platform": "novusagenda", "calendar_url": "https://casselberry.novusagenda.com/agendapublic/"},
    {"name": "City of Winter Springs",      "county": "Seminole",      "platform": "novusagenda", "calendar_url": "https://wintersprings.novusagenda.com/agendapublic/"},
    {"name": "City of Oviedo",              "county": "Seminole",      "platform": "novusagenda", "calendar_url": "https://oviedo.novusagenda.com/agendapublic/"},
    {"name": "City of Lake Mary",           "county": "Seminole",      "platform": "novusagenda", "calendar_url": "https://lakemary.novusagenda.com/agendapublic/"},
    {"name": "City of Longwood",            "county": "Seminole",      "platform": "novusagenda", "calendar_url": "https://longwood.novusagenda.com/agendapublic/"},
    # ── Volusia ───────────────────────────────────────────────────────────────
    {"name": "City of DeLand",              "county": "Volusia",       "platform": "novusagenda", "calendar_url": "https://deland.novusagenda.com/agendapublic/"},
    {"name": "City of Ormond Beach",        "county": "Volusia",       "platform": "novusagenda", "calendar_url": "https://ormondbeach.novusagenda.com/agendapublic/"},
    {"name": "City of Port Orange",         "county": "Volusia",       "platform": "novusagenda", "calendar_url": "https://portorange.novusagenda.com/agendapublic/"},
    {"name": "City of New Smyrna Beach",    "county": "Volusia",       "platform": "novusagenda", "calendar_url": "https://newsmyrnabeach.novusagenda.com/agendapublic/"},
    {"name": "City of Edgewater",           "county": "Volusia",       "platform": "novusagenda", "calendar_url": "https://edgewaterfl.novusagenda.com/agendapublic/"},
    {"name": "City of South Daytona",       "county": "Volusia",       "platform": "novusagenda", "calendar_url": "https://southdaytona.novusagenda.com/agendapublic/"},
    {"name": "City of Holly Hill",          "county": "Volusia",       "platform": "novusagenda", "calendar_url": "https://hollyhill.novusagenda.com/agendapublic/"},
    {"name": "City of Orange City",         "county": "Volusia",       "platform": "novusagenda", "calendar_url": "https://orangecity.novusagenda.com/agendapublic/"},
    {"name": "City of Lake Helen",          "county": "Volusia",       "platform": "novusagenda", "calendar_url": "https://lakehelen.novusagenda.com/agendapublic/"},
    {"name": "City of DeBary",              "county": "Volusia",       "platform": "novusagenda", "calendar_url": "https://debary.novusagenda.com/agendapublic/"},
    # ── Brevard ───────────────────────────────────────────────────────────────
    {"name": "City of Rockledge",           "county": "Brevard",       "platform": "novusagenda", "calendar_url": "https://rockledge.novusagenda.com/agendapublic/"},
    {"name": "City of Cape Canaveral",      "county": "Brevard",       "platform": "novusagenda", "calendar_url": "https://capecanaveral.novusagenda.com/agendapublic/"},
    {"name": "City of Cocoa Beach",         "county": "Brevard",       "platform": "novusagenda", "calendar_url": "https://cocoabeach.novusagenda.com/agendapublic/"},
    {"name": "City of Satellite Beach",     "county": "Brevard",       "platform": "novusagenda", "calendar_url": "https://satellitebeach.novusagenda.com/agendapublic/"},
    {"name": "City of Indian Harbour Beach","county": "Brevard",       "platform": "novusagenda", "calendar_url": "https://indianharbourbeach.novusagenda.com/agendapublic/"},
    # ── St. Lucie ─────────────────────────────────────────────────────────────
    {"name": "City of Fort Pierce",         "county": "St. Lucie",     "platform": "novusagenda", "calendar_url": "https://fortpierce.novusagenda.com/agendapublic/"},
    # ── Martin ────────────────────────────────────────────────────────────────
    {"name": "City of Stuart",              "county": "Martin",        "platform": "novusagenda", "calendar_url": "https://stuart.novusagenda.com/agendapublic/"},
    # ── Palm Beach ────────────────────────────────────────────────────────────
    {"name": "City of Riviera Beach",       "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://rivierabeach.novusagenda.com/agendapublic/"},
    {"name": "City of Lake Worth Beach",    "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://lakeworthbeach.novusagenda.com/agendapublic/"},
    {"name": "City of Greenacres",          "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://greenacres.novusagenda.com/agendapublic/"},
    {"name": "Village of Royal Palm Beach", "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://royalpalmbeach.novusagenda.com/agendapublic/"},
    {"name": "Village of Wellington",       "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://wellington.novusagenda.com/agendapublic/"},
    {"name": "Town of Lake Park",           "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://lakepark.novusagenda.com/agendapublic/"},
    {"name": "City of Pahokee",             "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://pahokee.novusagenda.com/agendapublic/"},
    {"name": "City of Belle Glade",         "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://belleglade.novusagenda.com/agendapublic/"},
    {"name": "Town of Juno Beach",          "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://junobeach.novusagenda.com/agendapublic/"},
    {"name": "Town of Palm Beach Shores",   "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://palmbeachshores.novusagenda.com/agendapublic/"},
    {"name": "Town of Haverhill",           "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://haverhill.novusagenda.com/agendapublic/"},
    {"name": "Town of Highland Beach",      "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://highlandbeach.novusagenda.com/agendapublic/"},
    {"name": "Town of Gulf Stream",         "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://gulfstream.novusagenda.com/agendapublic/"},
    {"name": "Town of Ocean Ridge",         "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://oceanridge.novusagenda.com/agendapublic/"},
    {"name": "Town of Hypoluxo",            "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://hypoluxo.novusagenda.com/agendapublic/"},
    {"name": "Town of South Palm Beach",    "county": "Palm Beach",    "platform": "novusagenda", "calendar_url": "https://southpalmbeach.novusagenda.com/agendapublic/"},
    # ── Broward ───────────────────────────────────────────────────────────────
    {"name": "City of Oakland Park",        "county": "Broward",       "platform": "novusagenda", "calendar_url": "https://oaklandpark.novusagenda.com/agendapublic/"},
    {"name": "City of Cooper City",         "county": "Broward",       "platform": "novusagenda", "calendar_url": "https://coopercity.novusagenda.com/agendapublic/"},
    {"name": "City of West Park",           "county": "Broward",       "platform": "novusagenda", "calendar_url": "https://westpark.novusagenda.com/agendapublic/"},
    {"name": "Town of Pembroke Park",       "county": "Broward",       "platform": "novusagenda", "calendar_url": "https://pembrokepark.novusagenda.com/agendapublic/"},
    {"name": "Town of Southwest Ranches",   "county": "Broward",       "platform": "novusagenda", "calendar_url": "https://southwestranches.novusagenda.com/agendapublic/"},
    {"name": "Town of Hillsboro Beach",     "county": "Broward",       "platform": "novusagenda", "calendar_url": "https://hillsborobeach.novusagenda.com/agendapublic/"},
    # ── Miami-Dade ────────────────────────────────────────────────────────────
    {"name": "City of Miami Beach",         "county": "Miami-Dade",    "platform": "novusagenda", "calendar_url": "https://miamibeach.novusagenda.com/agendapublic/"},
    {"name": "City of Miami Springs",       "county": "Miami-Dade",    "platform": "novusagenda", "calendar_url": "https://miamisprings.novusagenda.com/agendapublic/"},
    {"name": "Village of Miami Shores",     "county": "Miami-Dade",    "platform": "novusagenda", "calendar_url": "https://miamishores.novusagenda.com/agendapublic/"},
    {"name": "Town of Cutler Bay",          "county": "Miami-Dade",    "platform": "novusagenda", "calendar_url": "https://cutlerbay.novusagenda.com/agendapublic/"},
    {"name": "Village of Palmetto Bay",     "county": "Miami-Dade",    "platform": "novusagenda", "calendar_url": "https://palmettobay.novusagenda.com/agendapublic/"},
    {"name": "Village of Key Biscayne",     "county": "Miami-Dade",    "platform": "novusagenda", "calendar_url": "https://keybiscayne.novusagenda.com/agendapublic/"},
    {"name": "City of Hialeah Gardens",     "county": "Miami-Dade",    "platform": "novusagenda", "calendar_url": "https://hialeahgardens.novusagenda.com/agendapublic/"},
    {"name": "City of North Bay Village",   "county": "Miami-Dade",    "platform": "novusagenda", "calendar_url": "https://northbayvillage.novusagenda.com/agendapublic/"},
    {"name": "Town of Medley",              "county": "Miami-Dade",    "platform": "novusagenda", "calendar_url": "https://medley.novusagenda.com/agendapublic/"},
    {"name": "Village of Biscayne Park",    "county": "Miami-Dade",    "platform": "novusagenda", "calendar_url": "https://biscaynepark.novusagenda.com/agendapublic/"},
    {"name": "City of West Miami",          "county": "Miami-Dade",    "platform": "novusagenda", "calendar_url": "https://westmiami.novusagenda.com/agendapublic/"},
    {"name": "Town of Surfside",            "county": "Miami-Dade",    "platform": "novusagenda", "calendar_url": "https://surfside.novusagenda.com/agendapublic/"},
    {"name": "Town of Bay Harbor Islands",  "county": "Miami-Dade",    "platform": "novusagenda", "calendar_url": "https://bayharborislands.novusagenda.com/agendapublic/"},
    {"name": "Village of El Portal",        "county": "Miami-Dade",    "platform": "novusagenda", "calendar_url": "https://elportal.novusagenda.com/agendapublic/"},
    {"name": "City of Virginia Gardens",    "county": "Miami-Dade",    "platform": "novusagenda", "calendar_url": "https://virginiagardens.novusagenda.com/agendapublic/"},
    # ── Sarasota ──────────────────────────────────────────────────────────────
    {"name": "City of North Port",          "county": "Sarasota",      "platform": "novusagenda", "calendar_url": "https://northport.novusagenda.com/agendapublic/"},
    # ── Lee ───────────────────────────────────────────────────────────────────
    {"name": "City of Bonita Springs",      "county": "Lee",           "platform": "novusagenda", "calendar_url": "https://bonitasprings.novusagenda.com/agendapublic/"},
    {"name": "City of Fort Myers Beach",    "county": "Lee",           "platform": "novusagenda", "calendar_url": "https://fortmyersbeach.novusagenda.com/agendapublic/"},
    {"name": "Village of Estero",           "county": "Lee",           "platform": "novusagenda", "calendar_url": "https://estero.novusagenda.com/agendapublic/"},
    # ── Manatee ───────────────────────────────────────────────────────────────
    {"name": "City of Bradenton Beach",     "county": "Manatee",       "platform": "novusagenda", "calendar_url": "https://bradentonbeach.novusagenda.com/agendapublic/"},
    {"name": "City of Holmes Beach",        "county": "Manatee",       "platform": "novusagenda", "calendar_url": "https://holmesbeach.novusagenda.com/agendapublic/"},
    # ── Charlotte ─────────────────────────────────────────────────────────────
    {"name": "City of Punta Gorda",         "county": "Charlotte",     "platform": "novusagenda", "calendar_url": "https://puntagorda.novusagenda.com/agendapublic/"},
    # ── Collier ───────────────────────────────────────────────────────────────
    {"name": "City of Everglades City",     "county": "Collier",       "platform": "novusagenda", "calendar_url": "https://evergladescity.novusagenda.com/agendapublic/"},
    # ── Flagler ───────────────────────────────────────────────────────────────
    {"name": "City of Palm Coast",          "county": "Flagler",       "platform": "novusagenda", "calendar_url": "https://palmcoast.novusagenda.com/agendapublic/"},
    {"name": "City of Flagler Beach",       "county": "Flagler",       "platform": "novusagenda", "calendar_url": "https://flaglerbeach.novusagenda.com/agendapublic/"},
    {"name": "City of Bunnell",             "county": "Flagler",       "platform": "novusagenda", "calendar_url": "https://bunnell.novusagenda.com/agendapublic/"},
    # ── Polk ──────────────────────────────────────────────────────────────────
    {"name": "City of Bartow",              "county": "Polk",          "platform": "novusagenda", "calendar_url": "https://bartow.novusagenda.com/agendapublic/"},
    {"name": "City of Auburndale",          "county": "Polk",          "platform": "novusagenda", "calendar_url": "https://auburndale.novusagenda.com/agendapublic/"},
    {"name": "City of Davenport",           "county": "Polk",          "platform": "novusagenda", "calendar_url": "https://davenport.novusagenda.com/agendapublic/"},
    {"name": "City of Fort Meade",          "county": "Polk",          "platform": "novusagenda", "calendar_url": "https://fortmeade.novusagenda.com/agendapublic/"},
    {"name": "City of Frostproof",          "county": "Polk",          "platform": "novusagenda", "calendar_url": "https://frostproof.novusagenda.com/agendapublic/"},
    {"name": "City of Lake Alfred",         "county": "Polk",          "platform": "novusagenda", "calendar_url": "https://lakealfred.novusagenda.com/agendapublic/"},
    {"name": "City of Mulberry",            "county": "Polk",          "platform": "novusagenda", "calendar_url": "https://mulberry.novusagenda.com/agendapublic/"},
    # ── Highlands ─────────────────────────────────────────────────────────────
    {"name": "City of Sebring",             "county": "Highlands",     "platform": "novusagenda", "calendar_url": "https://sebring.novusagenda.com/agendapublic/"},
    {"name": "City of Avon Park",           "county": "Highlands",     "platform": "novusagenda", "calendar_url": "https://avonpark.novusagenda.com/agendapublic/"},
    {"name": "Town of Lake Placid",         "county": "Highlands",     "platform": "novusagenda", "calendar_url": "https://lakeplacid.novusagenda.com/agendapublic/"},
    # ── Santa Rosa ────────────────────────────────────────────────────────────
    {"name": "City of Gulf Breeze",         "county": "Santa Rosa",    "platform": "novusagenda", "calendar_url": "https://gulfbreeze.novusagenda.com/agendapublic/"},
    # ── Okaloosa ──────────────────────────────────────────────────────────────
    {"name": "City of Niceville",           "county": "Okaloosa",      "platform": "novusagenda", "calendar_url": "https://niceville.novusagenda.com/agendapublic/"},
    {"name": "City of Mary Esther",         "county": "Okaloosa",      "platform": "novusagenda", "calendar_url": "https://maryesther.novusagenda.com/agendapublic/"},
    {"name": "City of Valparaiso",          "county": "Okaloosa",      "platform": "novusagenda", "calendar_url": "https://valparaiso.novusagenda.com/agendapublic/"},
    # ── Walton ────────────────────────────────────────────────────────────────
    {"name": "City of DeFuniak Springs",    "county": "Walton",        "platform": "novusagenda", "calendar_url": "https://defuniaksprings.novusagenda.com/agendapublic/"},
    {"name": "City of Freeport",            "county": "Walton",        "platform": "novusagenda", "calendar_url": "https://freeport.novusagenda.com/agendapublic/"},
    # ── Bay ───────────────────────────────────────────────────────────────────
    {"name": "City of Panama City Beach",   "county": "Bay",           "platform": "novusagenda", "calendar_url": "https://panamacitybeach.novusagenda.com/agendapublic/"},
    {"name": "City of Lynn Haven",          "county": "Bay",           "platform": "novusagenda", "calendar_url": "https://lynnhaven.novusagenda.com/agendapublic/"},
    {"name": "City of Springfield",         "county": "Bay",           "platform": "novusagenda", "calendar_url": "https://springfield.novusagenda.com/agendapublic/"},
    {"name": "City of Callaway",            "county": "Bay",           "platform": "novusagenda", "calendar_url": "https://callaway.novusagenda.com/agendapublic/"},
    {"name": "City of Parker",              "county": "Bay",           "platform": "novusagenda", "calendar_url": "https://parker.novusagenda.com/agendapublic/"},
    # ── Gulf / Franklin ───────────────────────────────────────────────────────
    {"name": "City of Port St. Joe",        "county": "Gulf",          "platform": "novusagenda", "calendar_url": "https://portstjoe.novusagenda.com/agendapublic/"},
    {"name": "City of Apalachicola",        "county": "Franklin",      "platform": "novusagenda", "calendar_url": "https://apalachicola.novusagenda.com/agendapublic/"},
    # ── Gadsden / Jackson ─────────────────────────────────────────────────────
    {"name": "City of Quincy",              "county": "Gadsden",       "platform": "novusagenda", "calendar_url": "https://quincy.novusagenda.com/agendapublic/"},
    {"name": "City of Marianna",            "county": "Jackson",       "platform": "novusagenda", "calendar_url": "https://marianna.novusagenda.com/agendapublic/"},
    # ── Columbia / Suwannee / Madison / Taylor ────────────────────────────────
    {"name": "City of Lake City",           "county": "Columbia",      "platform": "novusagenda", "calendar_url": "https://lakecityfl.novusagenda.com/agendapublic/"},
    {"name": "City of Live Oak",            "county": "Suwannee",      "platform": "novusagenda", "calendar_url": "https://liveoak.novusagenda.com/agendapublic/"},
    {"name": "City of Madison",             "county": "Madison",       "platform": "novusagenda", "calendar_url": "https://madisonfl.novusagenda.com/agendapublic/"},
    {"name": "City of Perry",               "county": "Taylor",        "platform": "novusagenda", "calendar_url": "https://perry.novusagenda.com/agendapublic/"},
    # ── Levy ──────────────────────────────────────────────────────────────────
    {"name": "City of Chiefland",           "county": "Levy",          "platform": "novusagenda", "calendar_url": "https://chiefland.novusagenda.com/agendapublic/"},
    {"name": "City of Williston",           "county": "Levy",          "platform": "novusagenda", "calendar_url": "https://williston.novusagenda.com/agendapublic/"},
    {"name": "City of Cedar Key",           "county": "Levy",          "platform": "novusagenda", "calendar_url": "https://cedarkey.novusagenda.com/agendapublic/"},
    # ── Duval ─────────────────────────────────────────────────────────────────
    {"name": "City of Jacksonville Beach",  "county": "Duval",         "platform": "novusagenda", "calendar_url": "https://jacksonvillebeach.novusagenda.com/agendapublic/"},
    {"name": "City of Neptune Beach",       "county": "Duval",         "platform": "novusagenda", "calendar_url": "https://neptunebeach.novusagenda.com/agendapublic/"},
    {"name": "City of Atlantic Beach",      "county": "Duval",         "platform": "novusagenda", "calendar_url": "https://atlanticbeach.novusagenda.com/agendapublic/"},
    # ── Nassau / Baker / St. Johns / Putnam ──────────────────────────────────
    {"name": "Town of Callahan",            "county": "Nassau",        "platform": "novusagenda", "calendar_url": "https://callahan.novusagenda.com/agendapublic/"},
    {"name": "City of Macclenny",           "county": "Baker",         "platform": "novusagenda", "calendar_url": "https://macclenny.novusagenda.com/agendapublic/"},
    {"name": "City of St. Augustine Beach", "county": "St. Johns",     "platform": "novusagenda", "calendar_url": "https://staugustinebeach.novusagenda.com/agendapublic/"},
    {"name": "City of Crescent City",       "county": "Putnam",        "platform": "novusagenda", "calendar_url": "https://crescentcity.novusagenda.com/agendapublic/"},
    # ── Alachua / Clay ────────────────────────────────────────────────────────
    {"name": "City of Newberry",            "county": "Alachua",       "platform": "novusagenda", "calendar_url": "https://newberry.novusagenda.com/agendapublic/"},
    {"name": "City of High Springs",        "county": "Alachua",       "platform": "novusagenda", "calendar_url": "https://highsprings.novusagenda.com/agendapublic/"},
    {"name": "Town of Orange Park",         "county": "Clay",          "platform": "novusagenda", "calendar_url": "https://orangepark.novusagenda.com/agendapublic/"},
    # ── Hernando / Citrus / Marion ────────────────────────────────────────────
    {"name": "City of Brooksville",         "county": "Hernando",      "platform": "novusagenda", "calendar_url": "https://brooksville.novusagenda.com/agendapublic/"},
    {"name": "City of Crystal River",       "county": "Citrus",        "platform": "novusagenda", "calendar_url": "https://crystalriver.novusagenda.com/agendapublic/"},
    {"name": "City of Dunnellon",           "county": "Marion",        "platform": "novusagenda", "calendar_url": "https://dunnellon.novusagenda.com/agendapublic/"},
    # ── Pasco ─────────────────────────────────────────────────────────────────
    {"name": "City of Dade City",           "county": "Pasco",         "platform": "novusagenda", "calendar_url": "https://dadecity.novusagenda.com/agendapublic/"},
    {"name": "City of Zephyrhills",         "county": "Pasco",         "platform": "novusagenda", "calendar_url": "https://zephyrhills.novusagenda.com/agendapublic/"},
    {"name": "City of New Port Richey",     "county": "Pasco",         "platform": "novusagenda", "calendar_url": "https://newportrichey.novusagenda.com/agendapublic/"},
    {"name": "City of Port Richey",         "county": "Pasco",         "platform": "novusagenda", "calendar_url": "https://portrichey.novusagenda.com/agendapublic/"},
    # ── Okeechobee / Hendry / DeSoto / Hardee ────────────────────────────────
    {"name": "City of Okeechobee",          "county": "Okeechobee",    "platform": "novusagenda", "calendar_url": "https://okeechobee.novusagenda.com/agendapublic/"},
    {"name": "City of LaBelle",             "county": "Hendry",        "platform": "novusagenda", "calendar_url": "https://labelle.novusagenda.com/agendapublic/"},
    {"name": "City of Arcadia",             "county": "DeSoto",        "platform": "novusagenda", "calendar_url": "https://arcadia.novusagenda.com/agendapublic/"},
    {"name": "City of Wauchula",            "county": "Hardee",        "platform": "novusagenda", "calendar_url": "https://wauchula.novusagenda.com/agendapublic/"},
    {"name": "City of Bowling Green",       "county": "Hardee",        "platform": "novusagenda", "calendar_url": "https://bowlinggreen.novusagenda.com/agendapublic/"},
    # ── Monroe ────────────────────────────────────────────────────────────────
    {"name": "City of Marathon",            "county": "Monroe",        "platform": "novusagenda", "calendar_url": "https://marathon.novusagenda.com/agendapublic/"},
    {"name": "City of Key Colony Beach",    "county": "Monroe",        "platform": "novusagenda", "calendar_url": "https://keycolonybeach.novusagenda.com/agendapublic/"},
]

# ── FL School Districts (BoardDocs) — confirmed via probe 2026-06-16 ─────────
SCHOOL_DISTRICTS = [
    {"name": "Citrus County Schools",        "county": "Citrus",      "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/citrus/Board.nsf/Public",    "entity_type": "school_district"},
    {"name": "Collier County Schools",       "county": "Collier",     "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/collier/Board.nsf/Public",   "entity_type": "school_district"},
    {"name": "DeSoto County Schools",        "county": "DeSoto",      "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/desoto/Board.nsf/Public",    "entity_type": "school_district"},
    {"name": "Escambia County Schools",      "county": "Escambia",    "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/escambia/Board.nsf/Public",  "entity_type": "school_district"},
    {"name": "Franklin County Schools",      "county": "Franklin",    "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/franklin/Board.nsf/Public",  "entity_type": "school_district"},
    {"name": "Gilchrist County Schools",     "county": "Gilchrist",   "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/gilchrist/Board.nsf/Public", "entity_type": "school_district"},
    {"name": "Hardee County Schools",        "county": "Hardee",      "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/hardee/Board.nsf/Public",    "entity_type": "school_district"},
    {"name": "Hendry County Schools",        "county": "Hendry",      "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/hendry/Board.nsf/Public",    "entity_type": "school_district"},
    {"name": "Jackson County Schools",       "county": "Jackson",     "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/jcsb/Board.nsf/Public",      "entity_type": "school_district"},
    {"name": "Lee County Schools",           "county": "Lee",         "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/lee/Board.nsf/Public",       "entity_type": "school_district"},
    {"name": "Marion County Schools",        "county": "Marion",      "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/marion/Board.nsf/Public",    "entity_type": "school_district"},
    {"name": "Martin County Schools",        "county": "Martin",      "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/martin/Board.nsf/Public",    "entity_type": "school_district"},
    {"name": "Nassau County Schools",        "county": "Nassau",      "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/nassau/Board.nsf/Public",    "entity_type": "school_district"},
    {"name": "Okaloosa County Schools",      "county": "Okaloosa",    "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/okaloosa/Board.nsf/Public",  "entity_type": "school_district"},
    {"name": "Osceola County Schools",       "county": "Osceola",     "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/osceola/Board.nsf/Public",   "entity_type": "school_district"},
    {"name": "Palm Beach County Schools",    "county": "Palm Beach",  "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/palmbeach/Board.nsf/Public", "entity_type": "school_district"},
    {"name": "Pasco County Schools",         "county": "Pasco",       "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/pasco/Board.nsf/Public",     "entity_type": "school_district"},
    {"name": "Polk County Schools",          "county": "Polk",        "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/polk/Board.nsf/Public",      "entity_type": "school_district"},
    {"name": "Putnam County Schools",        "county": "Putnam",      "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/putnam/Board.nsf/Public",    "entity_type": "school_district"},
    {"name": "St. Johns County Schools",     "county": "St. Johns",   "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/stjohns/Board.nsf/Public",   "entity_type": "school_district"},
    {"name": "St. Lucie County Schools",     "county": "St. Lucie",   "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/stlucie/Board.nsf/Public",   "entity_type": "school_district"},
    {"name": "Taylor County Schools",        "county": "Taylor",      "platform": "boarddocs", "calendar_url": "https://go.boarddocs.com/fl/taylor/Board.nsf/Public",    "entity_type": "school_district"},
]
# fmt: on


def seed() -> None:
    client = db.get_client()
    counts: dict[str, int] = {}

    all_rows = MUNICIPALITIES + SCHOOL_DISTRICTS
    for row in all_rows:
        row.setdefault("state", "FL")
        row.setdefault("active", True)
        row.setdefault("entity_type", "municipality")
        client.table("municipalities").upsert(row, on_conflict="name").execute()
        counts[row["platform"]] = counts.get(row["platform"], 0) + 1
        etype = row.get("entity_type", "municipality")
        print(f"  {row['platform']:<12}  [{etype[:6]}]  {row['name']}")

    muni_count = len(MUNICIPALITIES)
    dist_count = len(SCHOOL_DISTRICTS)
    print(f"\nDone — {muni_count} municipalities + {dist_count} school districts = {len(all_rows)} total.")
    for plat, n in sorted(counts.items()):
        print(f"  {plat}: {n}")


if __name__ == "__main__":
    seed()
