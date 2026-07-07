#!/usr/bin/env python3
"""
Build roundels.json for the Roundel Explorer website.

Data source: Airtable "Roundel Translation Database" (primary)
Fallback:    roundel_database_full.csv (legacy, if AIRTABLE_API_KEY not set)

Usage:
  export AIRTABLE_API_KEY=patXXXXX...
  python3 build_data.py

After updating taxonomy or other fields in Airtable, re-run this script
and the website will pick up the changes on next page load.
"""
import json, os, sys, shutil
from urllib.parse import quote, urlencode
from urllib.request import urlopen, Request

HERE = os.path.dirname(__file__)
LOWVIS_DIR = os.path.join(HERE, "images", "lowvis")


def download_attachment(url, dest_path):
    """Download an Airtable attachment to dest_path (relative site path returned).
    Airtable attachment URLs expire after a few hours, so we resolve them into
    real files at build time rather than linking them live."""
    try:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        req = Request(url, headers={"User-Agent": "roundel-build/1.0"})
        with urlopen(req, timeout=30) as resp, open(dest_path, "wb") as out:
            shutil.copyfileobj(resp, out)
        return True
    except Exception as e:
        print(f"  low-vis download failed ({e}) for {dest_path}")
        return False

# ── Airtable config ──────────────────────────────────────────────────────────
AIRTABLE_BASE_ID  = "appOTwVKnZ4BhlIBu"
AIRTABLE_TABLE_ID = "tblbkVznay3MmvWn2"
AIRTABLE_API_KEY  = os.environ.get("AIRTABLE_API_KEY", "")

# ── Geography / ISO lookups (unchanged from original) ───────────────────────
COUNTRY_COORDS = {
    "Albania": (41.1533, 20.1683), "Algeria": (28.0339, 1.6596),
    "Antigua and Barbuda": (17.0608, -61.7964), "Argentina": (-38.4161, -63.6167),
    "Australia": (-25.2744, 133.7751), "Austria": (47.5162, 14.5501),
    "Azerbaijan": (40.1431, 47.5769), "Bahamas": (25.0343, -77.3963),
    "Bahrain": (26.0275, 50.5500), "Bangladesh": (23.6850, 90.3563),
    "Belgium": (50.5039, 4.4699), "Botswana": (-22.3285, 24.6849),
    "Brazil": (-14.2350, -51.9253), "Canada": (56.1304, -106.3468),
    "CAR (Central African Republic)": (6.6111, 20.9394),
    "Burkina Faso": (12.2383, -1.5616),
    "DRC (Democratic Republic of the Congo)": (-4.0383, 21.7587),
    "Chile": (-35.6751, -71.5430), "China": (35.8617, 104.1954),
    "Colombia": (4.5709, -74.2973), "Croatia": (45.1000, 15.2000),
    "Czech Republic": (49.8175, 15.4730), "Denmark": (56.2639, 9.5018),
    "Djibouti": (11.8251, 42.5903), "Ecuador": (-1.8312, -78.1834),
    "Egypt": (26.8206, 30.8025), "El Salvador": (13.7942, -88.8965),
    "Eritrea": (15.1794, 39.7823), "Estonia": (58.5953, 25.0136),
    "France": (46.2276, 2.2137), "Gabon": (-0.8037, 11.6094),
    "Georgia": (42.3154, 43.3569), "Germany": (51.1657, 10.4515),
    "Ghana": (7.9465, -1.0232), "Greece": (39.0742, 21.8243),
    "Guinea": (9.9456, -11.3247), "Hungary": (47.1625, 19.5033),
    "India": (20.5937, 78.9629), "Indonesia": (-0.7893, 113.9213),
    "Iran": (32.4279, 53.6880), "Iraq": (33.2232, 43.6793),
    "Ireland": (53.4129, -8.2439), "Israel": (31.0461, 34.8516),
    "Italy": (41.8719, 12.5674), "Jamaica": (18.1096, -77.2975),
    "Japan": (36.2048, 138.2529), "Jordan": (30.5852, 36.2384),
    "Kazakhstan": (48.0196, 66.9237), "Kenya": (-0.0236, 37.9062),
    "Kuwait": (29.3117, 47.4818), "Kyrgyzstan": (41.2044, 74.7661),
    "Laos": (19.8563, 102.4955), "Latvia": (56.8796, 24.6032),
    "Lebanon": (33.8547, 35.8623), "Libya": (26.3351, 17.2283),
    "Lithuania": (55.1694, 23.8813), "Luxembourg": (49.8153, 6.1296),
    "Madagascar": (-18.7669, 46.8691), "Malawi": (-13.2543, 34.3015),
    "Malaysia": (4.2105, 108.9758), "Mali": (17.5707, -3.9962),
    "Malta": (35.9375, 14.3754), "Mauritania": (21.0079, -10.9408),
    "Mauritius": (-20.3484, 57.5522), "Mexico": (23.6345, -102.5528),
    "Moldova": (47.4116, 28.3699), "Montenegro": (42.7087, 19.3744),
    "Morocco": (31.7917, -7.0926), "Mozambique": (-18.6657, 35.5296),
    "Myanmar": (21.9162, 95.9560), "Nepal": (28.3949, 84.1240),
    "Netherlands": (52.1326, 5.2913), "New Zealand": (-40.9006, 174.8860),
    "Nicaragua": (12.8654, -85.2072), "Niger": (17.6078, 8.0817),
    "Nigeria": (9.0820, 8.6753), "North Korea": (40.3399, 127.5101),
    "North Macedonia": (41.6086, 21.7453), "Norway": (60.4720, 8.4689),
    "Pakistan": (30.3753, 69.3451), "Panama": (8.5380, -80.7821),
    "Papua New Guinea": (-6.3149, 143.9555), "Paraguay": (-23.4425, -58.4438),
    "Peru": (-9.1900, -75.0152), "Philippines": (12.8797, 121.7740),
    "Poland": (51.9194, 19.1451), "Portugal": (39.3999, -8.2245),
    "Qatar": (25.3548, 51.1839), "Romania": (45.9432, 24.9668),
    "Russia": (61.5240, 105.3188), "Rwanda": (-1.9403, 29.8739),
    "Saudi Arabia": (23.8859, 45.0792), "Senegal": (14.4974, -14.4524),
    "Serbia": (44.0165, 21.0059), "Seychelles": (-4.6796, 55.4920),
    "Sierra Leone": (8.4606, -11.7799), "Slovenia": (46.1512, 14.9955),
    "Somalia": (5.1521, 46.1996), "South Africa": (-30.5595, 22.9375),
    "South Korea": (35.9078, 127.7669), "South Sudan": (6.8770, 31.3070),
    "Spain": (40.4637, -3.7492), "Sri Lanka": (7.8731, 80.7718),
    "Sudan": (12.8628, 30.2176), "Suriname": (3.9193, -56.0278),
    "Sweden": (60.1282, 18.6435), "Switzerland": (46.8182, 8.2275),
    "Syria (current)": (34.8021, 38.9968), "Thailand": (15.8700, 100.9925),
    "Togo": (8.6195, 0.8248), "Trinidad and Tobago": (10.6918, -61.2225),
    "Tunisia": (33.8869, 9.5375), "Turkey": (38.9637, 35.2433),
    "Turkmenistan": (38.9697, 59.5563), "Uganda": (1.3733, 32.2903),
    "Ukraine": (48.3794, 31.1656), "United Arab Emirates": (23.4241, 53.8478),
    "United Kingdom": (55.3781, -3.4360), "USA": (37.0902, -95.7129),
    "Zambia": (-13.1339, 27.8493), "Zimbabwe": (-19.0154, 29.1549),

    # World coverage (2026-07-07)
    "Afghanistan": (33.9, 67.7),
    "Andorra": (42.5, 1.5),
    "Angola": (-11.2, 17.9),
    "Armenia": (40.1, 45.0),
    "Barbados": (13.2, -59.5),
    "Belarus": (53.7, 27.9),
    "Belize": (17.2, -88.5),
    "Benin": (9.3, 2.3),
    "Bhutan": (27.5, 90.4),
    "Bolivia": (-16.3, -63.6),
    "Bosnia and Herzegovina": (43.9, 17.7),
    "Brunei": (4.5, 114.7),
    "Bulgaria": (42.7, 25.5),
    "Burundi": (-3.4, 29.9),
    "Cambodia": (12.6, 104.9),
    "Cameroon": (7.4, 12.4),
    "Cape Verde": (16.0, -24.0),
    "Chad": (15.5, 18.7),
    "Comoros": (-11.6, 43.3),
    "Congo (Republic)": (-0.2, 15.8),
    "Costa Rica": (9.7, -83.8),
    "Cuba": (21.5, -77.8),
    "Cyprus": (35.1, 33.4),
    "Dominica": (15.4, -61.4),
    "Dominican Republic": (18.7, -70.2),
    "Equatorial Guinea": (1.6, 10.3),
    "Eswatini": (-26.5, 31.5),
    "Ethiopia": (9.1, 40.5),
    "Fiji": (-17.7, 178.1),
    "Finland": (61.9, 25.7),
    "Gambia": (13.4, -15.3),
    "Grenada": (12.1, -61.7),
    "Guatemala": (15.8, -90.2),
    "Guinea-Bissau": (11.8, -15.2),
    "Guyana": (4.9, -58.9),
    "Haiti": (18.9, -72.3),
    "Honduras": (15.2, -86.2),
    "Iceland": (64.9, -19.0),
    "Ivory Coast": (7.5, -5.5),
    "Kiribati": (-3.4, -168.7),
    "Kosovo": (42.6, 20.9),
    "Lesotho": (-29.6, 28.2),
    "Liberia": (6.4, -9.4),
    "Liechtenstein": (47.2, 9.6),
    "Maldives": (3.2, 73.2),
    "Marshall Islands": (7.1, 171.2),
    "Micronesia": (7.4, 150.6),
    "Monaco": (43.7, 7.4),
    "Mongolia": (46.9, 103.8),
    "Namibia": (-22.96, 18.5),
    "Nauru": (-0.5, 166.9),
    "Oman": (21.5, 55.9),
    "Palau": (7.5, 134.6),
    "Palestine": (31.9, 35.2),
    "Saint Kitts and Nevis": (17.4, -62.8),
    "Saint Lucia": (13.9, -61.0),
    "Saint Vincent and the Grenadines": (13.0, -61.3),
    "Samoa": (-13.8, -172.1),
    "San Marino": (43.9, 12.5),
    "Sao Tome and Principe": (0.2, 6.6),
    "Singapore": (1.35, 103.8),
    "Slovakia": (48.7, 19.7),
    "Solomon Islands": (-9.6, 160.2),
    "Taiwan": (23.7, 121.0),
    "Tajikistan": (38.9, 71.3),
    "Tanzania": (-6.4, 34.9),
    "Timor-Leste": (-8.9, 125.7),
    "Tonga": (-21.2, -175.2),
    "Tuvalu": (-7.1, 177.6),
    "Uruguay": (-32.5, -55.8),
    "Uzbekistan": (41.4, 64.6),
    "Vanuatu": (-15.4, 166.96),
    "Venezuela": (6.4, -66.6),
    "Vietnam": (14.1, 108.3),
    "Yemen": (15.6, 48.0),
}

COUNTRY_ISO = {
    "Albania": "al", "Algeria": "dz", "Antigua and Barbuda": "ag",
    "Argentina": "ar", "Australia": "au", "Austria": "at", "Azerbaijan": "az",
    "Bahamas": "bs", "Bahrain": "bh", "Bangladesh": "bd", "Belgium": "be",
    "Botswana": "bw", "Brazil": "br", "Canada": "ca",
    "CAR (Central African Republic)": "cf",
    "Burkina Faso": "bf",
    "DRC (Democratic Republic of the Congo)": "cd",
    "Chile": "cl", "China": "cn", "Colombia": "co", "Croatia": "hr",
    "Czech Republic": "cz", "Denmark": "dk", "Djibouti": "dj", "Ecuador": "ec",
    "Egypt": "eg", "El Salvador": "sv", "Eritrea": "er", "Estonia": "ee",
    "France": "fr", "Gabon": "ga", "Georgia": "ge", "Germany": "de",
    "Ghana": "gh", "Greece": "gr", "Guinea": "gn", "Hungary": "hu",
    "India": "in", "Indonesia": "id", "Iran": "ir", "Iraq": "iq",
    "Ireland": "ie", "Israel": "il", "Italy": "it", "Jamaica": "jm",
    "Japan": "jp", "Jordan": "jo", "Kazakhstan": "kz", "Kenya": "ke",
    "Kuwait": "kw", "Kyrgyzstan": "kg", "Laos": "la", "Latvia": "lv",
    "Lebanon": "lb", "Libya": "ly", "Lithuania": "lt", "Luxembourg": "lu",
    "Madagascar": "mg", "Malawi": "mw", "Malaysia": "my", "Mali": "ml",
    "Malta": "mt", "Mauritania": "mr", "Mauritius": "mu", "Mexico": "mx",
    "Moldova": "md", "Montenegro": "me", "Morocco": "ma", "Mozambique": "mz",
    "Myanmar": "mm", "Nepal": "np", "Netherlands": "nl", "New Zealand": "nz",
    "Nicaragua": "ni", "Niger": "ne", "Nigeria": "ng", "North Korea": "kp",
    "North Macedonia": "mk", "Norway": "no", "Pakistan": "pk", "Panama": "pa",
    "Papua New Guinea": "pg", "Paraguay": "py", "Peru": "pe",
    "Philippines": "ph", "Poland": "pl", "Portugal": "pt", "Qatar": "qa",
    "Romania": "ro", "Russia": "ru", "Rwanda": "rw", "Saudi Arabia": "sa",
    "Senegal": "sn", "Serbia": "rs", "Seychelles": "sc", "Sierra Leone": "sl",
    "Slovenia": "si", "Somalia": "so", "South Africa": "za",
    "South Korea": "kr", "South Sudan": "ss", "Spain": "es",
    "Sri Lanka": "lk", "Sudan": "sd", "Suriname": "sr", "Sweden": "se",
    "Switzerland": "ch", "Syria (current)": "sy", "Thailand": "th",
    "Togo": "tg", "Trinidad and Tobago": "tt", "Tunisia": "tn",
    "Turkey": "tr", "Turkmenistan": "tm", "Uganda": "ug", "Ukraine": "ua",
    "United Arab Emirates": "ae", "United Kingdom": "gb", "USA": "us",
    "Zambia": "zm", "Zimbabwe": "zw",

    # World coverage (2026-07-07)
    "Afghanistan": "af",
    "Andorra": "ad",
    "Angola": "ao",
    "Armenia": "am",
    "Barbados": "bb",
    "Belarus": "by",
    "Belize": "bz",
    "Benin": "bj",
    "Bhutan": "bt",
    "Bolivia": "bo",
    "Bosnia and Herzegovina": "ba",
    "Brunei": "bn",
    "Bulgaria": "bg",
    "Burundi": "bi",
    "Cambodia": "kh",
    "Cameroon": "cm",
    "Cape Verde": "cv",
    "Chad": "td",
    "Comoros": "km",
    "Congo (Republic)": "cg",
    "Costa Rica": "cr",
    "Cuba": "cu",
    "Cyprus": "cy",
    "Dominica": "dm",
    "Dominican Republic": "do",
    "Equatorial Guinea": "gq",
    "Eswatini": "sz",
    "Ethiopia": "et",
    "Fiji": "fj",
    "Finland": "fi",
    "Gambia": "gm",
    "Grenada": "gd",
    "Guatemala": "gt",
    "Guinea-Bissau": "gw",
    "Guyana": "gy",
    "Haiti": "ht",
    "Honduras": "hn",
    "Iceland": "is",
    "Ivory Coast": "ci",
    "Kiribati": "ki",
    "Kosovo": "xk",
    "Lesotho": "ls",
    "Liberia": "lr",
    "Liechtenstein": "li",
    "Maldives": "mv",
    "Marshall Islands": "mh",
    "Micronesia": "fm",
    "Monaco": "mc",
    "Mongolia": "mn",
    "Namibia": "na",
    "Nauru": "nr",
    "Oman": "om",
    "Palau": "pw",
    "Palestine": "ps",
    "Saint Kitts and Nevis": "kn",
    "Saint Lucia": "lc",
    "Saint Vincent and the Grenadines": "vc",
    "Samoa": "ws",
    "San Marino": "sm",
    "Sao Tome and Principe": "st",
    "Singapore": "sg",
    "Slovakia": "sk",
    "Solomon Islands": "sb",
    "Taiwan": "tw",
    "Tajikistan": "tj",
    "Tanzania": "tz",
    "Timor-Leste": "tl",
    "Tonga": "to",
    "Tuvalu": "tv",
    "Uruguay": "uy",
    "Uzbekistan": "uz",
    "Vanuatu": "vu",
    "Venezuela": "ve",
    "Vietnam": "vn",
    "Yemen": "ye",
}

IMAGE_MAP = {
    "Albania": "Roundel_of_the_Albanian_Air_Force.svg.png",
    "Algeria": "Roundel_of_Algeria.svg.png",
    "Antigua and Barbuda": "Roundel_of_Antigua_and_Barbuda.svg.png",
    "Argentina": "Roundel_of_Argentina.svg.png",
    "Australia": "Roundel_of_Australia.svg.png",
    "Austria": "Roundel_of_Austria.svg.png",
    "Azerbaijan": "Roundel_of_Azerbaijan.svg.png",
    "Bahamas": "Roundel_of_the_Bahamas.svg.png",
    "Bahrain": "Roundel_of_Bahrain.svg.png",
    "Bangladesh": "Roundel_of_Bangladesh.svg.png",
    "Belgium": "Roundel_of_Belgium.svg.png",
    "Botswana": "Roundel_of_Botswana.svg.png",
    "Brazil": "Roundel_of_Brazil.svg.png",
    "Canada": "Roundel_of_Canada.svg.png",
    "CAR (Central African Republic)": "Roundel_of_the_Central_African_Republic.svg.png",
    "Chile": "Roundel_of_Chile.svg.png",
    "China": "Roundel_of_China.svg.png",
    "Colombia": "Roundel_of_Colombia.svg.png",
    "Croatia": "Roundel_of_Croatia.svg.png",
    "Czech Republic": "Roundel_of_the_Czech_Republic.svg.png",
    "Denmark": "Roundel_of_Denmark.svg.png",
    "Djibouti": "Roundel_of_Djibouti.svg.png",
    "Ecuador": "Roundel_of_Ecuador.svg.png",
    "Egypt": "Roundel_of_Egypt.svg.png",
    "El Salvador": "Roundel_of_El_Salvador.svg.png",
    "Eritrea": "Roundel_of_Eritrea.svg.png",
    "Estonia": "Roundel_of_Estonia.svg.png",
    "France": "Roundel_of_France.svg.png",
    "Gabon": "Roundel_of_Gabon.svg.png",
    "Georgia": "Roundel_of_Georgia.svg.png",
    "Germany": "Roundel_of_Germany_–_Type_1_–_Border.svg.png",
    "Ghana": "Roundel_of_Ghana.svg.png",
    "Greece": "Roundel_of_Greece.svg.png",
    "Guinea": "Roundel_of_Guinea.svg.png",
    "Hungary": "Roundel_of_Hungary.svg.png",
    "India": "Roundel_of_India.svg.png",
    "Indonesia": "Roundel_of_Indonesia.svg.png",
    "Iran": "Roundel_of_Iran.svg.png",
    "Iraq": "Roundel_of_Iraq.svg.png",
    "Ireland": "Roundel_of_Ireland.svg.png",
    "Israel": "Roundel_of_Israel.svg.png",
    "Italy": "Roundel_of_Italy.svg.png",
    "Jamaica": "Roundel_of_Jamaica.svg.png",
    "Japan": "Roundel_of_Japan.svg.png",
    "Jordan": "Roundel_of_Jordan.svg.png",
    "Kazakhstan": "Roundel_of_Kazakhstan.svg.png",
    "Kenya": "Roundel_of_Kenya.svg.png",
    "Kuwait": "Roundel_of_Kuwait.svg.png",
    "Kyrgyzstan": "Roundel_of_Kyrgyzstan.svg.png",
    "Laos": "Roundel_of_Laos.svg.png",
    "Latvia": "Roundel_of_Latvia.svg.png",
    "Lebanon": "Roundel_of_Lebanon.svg.png",
    "Libya": "Roundel_of_Libya.svg.png",
    "Lithuania": "Roundel_of_Lithuania.svg.png",
    "Luxembourg": "Roundel_of_Luxembourg.svg.png",
    "Madagascar": "Roundel_of_Madagascar.svg.png",
    "Malawi": "Roundel_of_Malawi.svg.png",
    "Malaysia": "Roundel_of_Malaysia.svg.png",
    "Mali": "Roundel_of_Mali_–_Type_2.svg.png",
    "Malta": "Roundel_of_Malta.svg.png",
    "Mauritania": "Roundel_of_Mauritania.svg.png",
    "Mauritius": "Roundel_of_Mauritius.svg.png",
    "Mexico": "Roundel_of_Mexico.svg.png",
    "Moldova": "Roundel_of_Moldova.svg.png",
    "Montenegro": "Roundel_of_Montenegro.svg.png",
    "Morocco": "Roundel_of_Morocco.svg.png",
    "Mozambique": "Roundel_of_Mozambique.svg.png",
    "Myanmar": "Roundel_of_Myanmar.svg.png",
    "Nepal": "Roundel_of_Nepal.svg.png",
    "Netherlands": "Roundel_of_the_Netherlands.svg.png",
    "New Zealand": "Roundel_of_New_Zealand.svg.png",
    "Nicaragua": "Roundel_of_Nicaragua_(1990–1995).svg.png",
    "Niger": "Roundel_of_Niger.svg.png",
    "Nigeria": "Roundel_of_Nigeria.svg.png",
    "North Korea": "Roundel_of_North_Korea.svg.png",
    "North Macedonia": "Roundel_of_North_Macedonia.svg.png",
    "Norway": "Roundel_of_Norway.svg.png",
    "Pakistan": "Roundel_of_Pakistan.svg.png",
    "Panama": "Roundel_of_Panama.svg.png",
    "Papua New Guinea": "Roundel_of_Papua_New_Guinea.svg.png",
    "Paraguay": "Roundel_of_Paraguay.svg.png",
    "Peru": "Roundel_of_Peru.svg.png",
    "Philippines": "Roundel_of_the_Philippines.svg.png",
    "Poland": "Roundel_of_Poland.svg.png",
    "Portugal": "Roundel_of_Portugal.svg.png",
    "Qatar": "Roundel_of_Qatar.svg.png",
    "Romania": "Roundel_of_Romania.svg.png",
    "Russia": "Roundel_of_Russia.svg.png",
    "Rwanda": "Roundel_of_Rwanda.svg.png",
    "Saudi Arabia": "Roundel_of_Saudi_Arabia.svg.png",
    "Senegal": "Roundel_of_Senegal.svg.png",
    "Serbia": "Roundel_of_Serbia.svg.png",
    "Seychelles": "Roundel_of_Seychelles.svg.png",
    "Sierra Leone": "Roundel_of_Sierra_Leone.svg.png",
    "Slovenia": "Roundel_of_Slovenia.svg.png",
    "Somalia": "Roundel_of_Somalia.svg.png",
    "South Africa": "Roundel_of_South_Africa.svg.png",
    "South Korea": "Roundel_of_South_Korea.svg.png",
    "South Sudan": "Roundel_of_South_Sudan.svg.png",
    "Spain": "Roundel_of_Spain.svg.png",
    "Sri Lanka": "Roundel_of_Sri_Lanka.svg.png",
    "Sudan": "Roundel_of_Sudan.svg.png",
    "Suriname": "Roundel_of_Suriname.svg.png",
    "Sweden": "Roundel_of_Sweden.svg.png",
    "Switzerland": "Roundel_of_Switzerland.svg.png",
    "Syria (current)": "Roundel_of_Syria_(1948–1958,_1961–1963,_2025–present).svg.png",
    "Thailand": "Roundel_of_Thailand.svg.png",
    "Togo": "Roundel_of_Togo.svg.png",
    "Trinidad and Tobago": "Roundel_of_Trinidad_and_Tobago.svg.png",
    "Tunisia": "Roundel_of_Tunisia.svg.png",
    "Turkey": "Roundel_of_Turkey.svg.png",
    "Turkmenistan": "Roundel_of_Turkmenistan_(variant).svg.png",
    "Uganda": "Roundel_of_Uganda_-_Type_1.svg.png",
    "Ukraine": "Roundel_of_Ukraine.svg.png",
    "United Arab Emirates": "Roundel_of_the_United_Arab_Emirates.svg.png",
    "United Kingdom": "Roundel_of_the_United_Kingdom.svg.png",
    "USA": "Roundel_of_the_USAF.svg.png",
    "Zambia": "Roundel_of_Zambia.svg.png",
    "Zimbabwe": "Roundel_of_Zimbabwe.svg.png",
}

# ── Taxonomy mapping ──────────────────────────────────────────────────────────
# Maps Airtable singleSelect taxonomy values → (primaryMethod, subMethod)
# These are the 14 options defined in the Airtable field schema.
TAXONOMY_MAP = {
    "Radial: Standard":                                ("Radial",       "Horizontal Triband"),
    "Radial: Standard + Punch: Geometric":             ("Radial",       "Hoist Element with Rings"),
    "Radial: Standard + Punch: Symbol":                ("Radial",       "Hoist Element with Rings"),
    "Radial: Inverted":                                ("Radial",       "Horizontal Triband"),
    "Radial: Cross radial":                            ("Radial",       "Vertical or Hoist Element"),
    "Radial: Hoist element preserved + Punch: Geometric": ("Radial",   "Hoist Element with Rings"),
    "Radial: Segmented":                               ("Radial",       "Vertical or Hoist Element"),
    "Radial: Segmented + Non-Sequitur: New element":   ("Radial",       "Vertical or Hoist Element"),
    "Punch: Geometric":                                ("Punch",        "Cross or Radial Charge"),
    "Punch: Symbol":                                   ("Punch",        "Direct Extraction"),
    "Non-Sequitur: Abandonment":                       ("Non Sequitur", "Military Heraldry or Redesign"),
    "Non-Sequitur: Template inheritance":              ("Non Sequitur", "Fauna or National Symbol"),
    "Non-Sequitur: Shape collapse":                    ("Non Sequitur", "Military Heraldry or Redesign"),
    "Non-Sequitur: Forced redesign":                   ("Non Sequitur", "Military Heraldry or Redesign"),
}

def normalize_taxonomy(tax_raw):
    """Returns (primaryMethod, subMethod) from an Airtable taxonomy string."""
    result = TAXONOMY_MAP.get(tax_raw)
    if result:
        return result
    # Fallback: infer from prefix
    t = tax_raw.lower()
    if t.startswith("radial"):
        return "Radial", ""
    if t.startswith("punch"):
        return "Punch", ""
    return "Non Sequitur", ""


# ── Helpers ──────────────────────────────────────────────────────────────────
COLOR_KEYWORDS = [
    "light blue", "dark red", "dark blue", "dark green",
    "red", "white", "blue", "green", "yellow", "gold",
    "black", "orange", "purple", "maroon", "crimson",
    "carmine", "aquamarine", "saffron", "grey", "gray",
]

def extract_colors(desc):
    found = []
    d = desc.lower()
    for c in COLOR_KEYWORDS:
        if c in d and c not in found:
            found.append(c)
    return found

def has_center_symbol(taxonomy_raw, roundel_desc):
    t = taxonomy_raw.lower()
    d = roundel_desc.lower()
    symbol_words = ["star", "eagle", "cross", "lion", "chakra", "tunduk",
                    "crescent", "bird", "dragon", "sun", "cedar", "kangaroo",
                    "kiwi", "maple", "seal", "crane", "shield", "sword", "fish"]
    if "punch" in t:
        return True
    return any(w in d for w in symbol_words)

MANUAL_COLLAPSE = {
    "Romania":   ["Chad"],
    "Indonesia": ["Poland", "Monaco"],
    "Poland":    ["Indonesia", "Monaco"],
    "Iraq":      ["Egypt", "Syria (current)"],
    "Luxembourg":["Netherlands"],
    "Mali":      ["Guinea"],
}

def detect_design_collapse(notes):
    n = notes.lower()
    if "design collapse" not in n and "design failure" not in n:
        return False, []
    countries_in_db = set(COUNTRY_COORDS.keys())
    found = [c for c in countries_in_db if c.lower() in n]
    return True, found

def label_from_filename(fn):
    """'Roundel_of_Mexico_–_Low_Visibility.svg.png' → 'Low Visibility'."""
    import re as _re
    base = _re.sub(r'\.(svg|png|webp|jpg|jpeg)', '', fn or '', flags=_re.I)
    base = _re.sub(r'^Roundel_of_(the_)?', '', base, flags=_re.I)
    m = _re.search(r'[–\-—]\s*(.+)$', base)
    tail = (m.group(1) if m else base)
    tail = _re.sub(r'[_–—]+', ' ', tail)
    tail = _re.sub(r'\s+', ' ', tail).strip()
    return tail or "Variant"


def wikimedia_urls(img_filename):
    if not img_filename:
        return "", ""
    commons_name = img_filename[:-4] if img_filename.endswith('.svg.png') else img_filename
    encoded = quote(commons_name, safe="().-_–'")
    special   = f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}"
    file_page = f"https://commons.wikimedia.org/wiki/File:{encoded}"
    return special, file_page

def apply_manual_collapse(record):
    nation = record["nation"]
    if nation in MANUAL_COLLAPSE:
        record["designCollapse"] = True
        record["designCollapseWith"] = MANUAL_COLLAPSE[nation]

def build_record(nation, tax_raw, flag_desc, roundel_desc, fin_flash, notes, img_override=None, extra=None):
    coords  = COUNTRY_COORDS.get(nation, (0, 0))
    iso     = COUNTRY_ISO.get(nation, "")
    img     = img_override or IMAGE_MAP.get(nation, "")
    extra   = extra or {}
    slug    = iso or nation.lower().replace(" ", "_")

    def resolve_attachment(att, local_rel):
        """Prefer a live Wikimedia Commons URL derived from the attachment's
        filename (these attachments are Commons exports, so no bytes need to be
        bundled). Fall back to downloading the Airtable file, then to any local
        file already present."""
        fn = (att or {}).get("filename", "")
        if fn:
            special, _ = wikimedia_urls(fn if fn.endswith(".png") else fn + ".png")
            if special:
                return special
        url = (att or {}).get("url", "")
        if url and download_attachment(url, os.path.join(HERE, local_rel)):
            return local_rel
        return ""

    # Low-vis roundel
    low_vis_image = ""
    lv_atts = extra.get("Low-Vis Attach", [])
    if lv_atts:
        low_vis_image = resolve_attachment(lv_atts[0], f"images/lowvis/{slug}.png")
    if not low_vis_image:
        for ext in ("png", "svg"):
            cand = f"images/lowvis/{slug}.{ext}"
            if os.path.exists(os.path.join(HERE, cand)):
                low_vis_image = cand
                break

    # Additional roundels (historic / variants) — {src, label} each
    additional_images = []
    for i, att in enumerate(extra.get("Additional Attach", []) or []):
        src = resolve_attachment(att, f"images/additional/{slug}-{i}.png")
        if src:
            additional_images.append({"src": src, "label": label_from_filename(att.get("filename", ""))})

    primary_method, sub_method = normalize_taxonomy(tax_raw)
    # New component taxonomy (Method/Orientation/Variants) supersedes the
    # legacy Taxonomy select when present.
    method      = extra.get("Method") or primary_method
    orientation = extra.get("Radial Orientation", "")
    variants    = extra.get("Variants", []) or []
    if extra.get("Method"):
        primary_method = method
        sub_method = ", ".join(filter(None, [orientation, *variants]))
    wikimedia_img, commons_page = wikimedia_urls(img)
    is_collapse, collapse_with = detect_design_collapse(notes)

    rec = {
        "nation":          nation,
        "lat":             coords[0],
        "lng":             coords[1],
        "iso":             iso,
        "flagUrl":         f"https://flagcdn.com/w160/{iso}.png" if iso else "",
        "roundelImage":    wikimedia_img if wikimedia_img else "",  # Wikimedia Commons direct URL
        "roundelImageFile": img,
        "flagDescription":  flag_desc,
        "roundelDescription": roundel_desc,
        "finFlash":         fin_flash,
        "taxonomyRaw":      tax_raw,
        "primaryMethod":    primary_method,
        "subMethod":        sub_method,
        "notes":            notes,
        "colors":           extract_colors(roundel_desc),
        "hasCenterSymbol":  has_center_symbol(tax_raw, roundel_desc),
        "designCollapse":   is_collapse,
        "designCollapseWith": collapse_with,
        "wikimediaUrl":     wikimedia_img,
        "commonsPage":      commons_page,
        # Component taxonomy + IFIS flag facts (from Airtable 2026-07 restructure)
        "method":          method,
        "radialOrientation": orientation,
        "variants":        variants,
        "flagStatus":      extra.get("Flag Status", ""),
        "flagReverseSide": extra.get("Flag Reverse Side", ""),
        "flagFiavCode":    extra.get("Flag FIAV Code", ""),
        "yearAdopted":    extra.get("Year Adopted", ""),
        "stillInUse":     ("Yes" if extra["Still In Use"] else "No") if "Still In Use" in extra else "",
        "historicalNotes": extra.get("Historical Notes", ""),
        "finFlashImage":  "",
        "furtherReading": extra.get("Further Reading", ""),
        "lowVisImage":    low_vis_image,
        "additionalImages": additional_images,
        "hasRoundel":     bool(wikimedia_img),
    }
    apply_manual_collapse(rec)
    return rec


# ── Airtable fetch ────────────────────────────────────────────────────────────
def fetch_from_airtable():
    """Fetch all records from the Airtable Roundels table. Returns a list of row dicts."""
    if not AIRTABLE_API_KEY:
        raise RuntimeError("AIRTABLE_API_KEY not set")

    url_base = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
    headers  = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    field_names = [
        "Nation", "Taxonomy", "Flag Description",
        "Roundel Description", "Fin Flash", "Notes", "Image File",
        "Method", "Radial Orientation", "Variants",
        "Flag Status (IFIS)", "Flag Reverse Side (IFIS)", "Flag FIAV Code",
        "Year Adopted", "Still In Use", "Historical Notes", "Further Reading",
        "Low-Vis Roundel", "Additional Roundels",
    ]
    params = {"fields[]": field_names, "pageSize": "100"}

    rows = []
    offset = None
    while True:
        if offset:
            params["offset"] = offset
        query = urlencode(params, doseq=True)
        req   = Request(f"{url_base}?{query}", headers=headers)
        with urlopen(req) as resp:
            data   = json.loads(resp.read())
        for r in data.get("records", []):
            f = r.get("cellValuesByFieldId") or r.get("fields", {})

            def sel(name):
                """singleSelect → plain string ({'name': ...} or string)."""
                v = f.get(name, "")
                if isinstance(v, dict):
                    return (v.get("name") or "").strip()
                return (v or "").strip() if isinstance(v, str) else ""

            def _attachments(v):
                """Return [{filename, url}] for an attachments cell."""
                out = []
                if isinstance(v, list):
                    for a in v:
                        if isinstance(a, dict):
                            out.append({"filename": a.get("filename", ""), "url": a.get("url", "")})
                return out

            def multi(name):
                """multipleSelects → list of strings."""
                v = f.get(name) or []
                out = []
                for item in v:
                    if isinstance(item, dict):
                        item = item.get("name", "")
                    if item:
                        out.append(item)
                return out

            tax_val = sel("Taxonomy") or sel("fldgd3ftmTD4OdF0T")
            rows.append({
                "Nation":             (f.get("Nation") or f.get("fldGk9fVAlMUjmHla", "")).strip(),
                "Taxonomy":           tax_val,
                "Flag Description":   (f.get("Flag Description") or f.get("fldfDmkd1KnvCsYCW", "")).strip(),
                "Roundel Description": (f.get("Roundel Description") or f.get("fldGyWV1vvqgi6iiZ", "")).strip(),
                "Fin Flash":          (f.get("Fin Flash") or f.get("fldANG4m5LobjXkAq", "")).strip(),
                "Notes":              (f.get("Notes") or f.get("fldgVS77iMnfspaKw", "")).strip(),
                "Image File":         (f.get("Image File") or f.get("fldoiqioYNVdWWnnG", "")).strip(),
                # New taxonomy + IFIS + detail fields (2026-07 restructure)
                "Method":             sel("Method"),
                "Radial Orientation": sel("Radial Orientation"),
                "Variants":           multi("Variants"),
                "Flag Status":        sel("Flag Status (IFIS)"),
                "Flag Reverse Side":  sel("Flag Reverse Side (IFIS)"),
                "Flag FIAV Code":     (f.get("Flag FIAV Code") or "").strip(),
                "Year Adopted":       (f.get("Year Adopted") or "").strip(),
                "Still In Use":       bool(f.get("Still In Use")),
                "Historical Notes":   (f.get("Historical Notes") or "").strip(),
                "Further Reading":    (f.get("Further Reading") or "").strip(),
                "Low-Vis Attach":     _attachments(f.get("Low-Vis Roundel")),
                "Additional Attach":  _attachments(f.get("Additional Roundels")),
            })
        offset = data.get("offset")
        if not offset:
            break
    return rows


# ── CSV fallback ──────────────────────────────────────────────────────────────
def fetch_from_csv():
    import csv
    # Prefer a copy sitting inside the site folder (so the deploy is self-contained);
    # fall back to the legacy location one level up.
    local = os.path.join(HERE, "roundel_database_full.csv")
    src = local if os.path.exists(local) else os.path.join(HERE, "../roundel_database_full.csv")
    rows = []
    with open(src, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append({
                "Nation":             row["Nation"].strip(),
                "Taxonomy":           row["Taxonomy"].strip(),
                "Flag Description":   row["Flag Description"].strip(),
                "Roundel Description": row["Roundel Description"].strip(),
                "Fin Flash":          row["Fin Flash"].strip(),
                "Notes":              row["Notes"].strip(),
                "Image File":         "",
            })
    return rows


def apply_snapshot_overlay(rows):
    """When building without a live Airtable key, overlay the committed
    data/airtable_snapshot.json so the site still shows the new component
    taxonomy (method/orientation/variants + IFIS facts). Ignored the moment
    AIRTABLE_API_KEY is set — live Airtable wins."""
    path = os.path.join(HERE, "data", "airtable_snapshot.json")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        snap = json.load(f).get("records", {})
    for row in rows:
        s = snap.get(row["Nation"])
        if not s:
            continue
        row["Method"]             = s.get("method", "")
        row["Radial Orientation"] = s.get("orientation", "")
        row["Variants"]           = s.get("variants", [])
        row["Flag Status"]        = s.get("flagStatus", "")
        row["Flag Reverse Side"]  = s.get("flagReverse", "")
        row["Flag FIAV Code"]     = s.get("fiav", "")
        row["Year Adopted"]       = s.get("year", "")
        if "inUse" in s:
            row["Still In Use"]   = bool(s["inUse"])


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if AIRTABLE_API_KEY:
        print("Fetching from Airtable…")
        try:
            rows = fetch_from_airtable()
            source = "Airtable"
        except Exception as e:
            print(f"  Airtable fetch failed: {e}")
            print("  Falling back to CSV…")
            rows = fetch_from_csv()
            source = "CSV (fallback)"
    else:
        print("AIRTABLE_API_KEY not set — using CSV fallback.")
        print("To use Airtable: export AIRTABLE_API_KEY=patXXX...")
        rows = fetch_from_csv()
        apply_snapshot_overlay(rows)
        source = "CSV + snapshot overlay"

    records = []
    for row in rows:
        if not row["Nation"]:
            continue
        rec = build_record(
            nation=row["Nation"],
            tax_raw=row["Taxonomy"],
            flag_desc=row["Flag Description"],
            roundel_desc=row["Roundel Description"],
            fin_flash=row["Fin Flash"],
            notes=row["Notes"],
            img_override=row["Image File"] or None,
            extra=row,
        )
        records.append(rec)

    records.sort(key=lambda r: r["nation"])

    out = os.path.join(os.path.dirname(__file__), "data/roundels.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"Written {len(records)} records from {source} → {out}")
    for r in records:
        if not r["roundelImageFile"]:
            print(f"  NO IMAGE: {r['nation']}")
        if not r["iso"]:
            print(f"  NO ISO: {r['nation']}")
