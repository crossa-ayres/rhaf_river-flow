import os
import requests
import pandas as pd
import streamlit as st
import json, urllib.parse, urllib.request




#: One page of the USGS daily endpoint. The service caps this, and a long
#: record runs well past it -- a gage operating since 1950 has ~27,000 daily
#: values -- so the `next` link has to be followed or the data is silently
#: truncated rather than refused.
USGS_PAGE_LIMIT = 10000

USGS_DAILY_URL = "https://api.waterdata.usgs.gov/ogcapi/v0/collections/daily/items"


def as_rfc3339_date(value, suffix="-01-01"):
    """A year or a date, returned as a full date.

    The sidebar collects a *year* ("2020"), but the API's `datetime` parameter
    is RFC 3339 and rejects a bare year with HTTP 400 -- which is opaque,
    because the year is obviously valid to anyone reading the form.
    """
    text = str(value).strip()
    if not text:
        raise ValueError("begin_year is empty; expected a year like 2020")
    return text if len(text) > 4 else f"{text}{suffix}"


def download_usgs_data(site="06721000", begin_year="2011"):
    """Daily mean discharge for one gage, written to CSV. Returns its path.

    Reads the modernised Water Data API. The legacy WaterServices endpoints are
    being decommissioned in Winter 2027, and this one returns GeoJSON rather
    than the old tab-delimited RDB -- so the rows are flattened here into the
    columns `load_flow_data` expects, rather than leaving that function to
    parse a format that no longer arrives.
    """
    yesterday = pd.Timestamp.now() - pd.Timedelta(days=1)
    query = urllib.parse.urlencode({
        "monitoring_location_id": f"USGS-{site}",
        "parameter_code": "00060",              # discharge, cubic feet/second
        "statistic_id": "00003",                # daily mean
        "datetime": f"{as_rfc3339_date(begin_year)}/{yesterday:%Y-%m-%d}",
        "limit": USGS_PAGE_LIMIT,
        "f": "json",
    })

    rows = []
    url = f"{USGS_DAILY_URL}?{query}"
    while url:
        with urllib.request.urlopen(url, timeout=60) as resp:
            payload = json.load(resp)
        for feature in payload.get("features", []):
            props = feature.get("properties", {})
            rows.append({
                "agency_cd": "USGS",
                "site_no": site,
                "date": props.get("time"),
                # Sent as a string to preserve precision; load_flow_data coerces.
                "avg_flow": props.get("value"),
                "qc": props.get("approval_status", ""),
            })
        url = next((link["href"] for link in payload.get("links", [])
                    if link.get("rel") == "next"), None)

    if not rows:
        raise ValueError(
            f"USGS returned no daily discharge for site {site} from "
            f"{begin_year} onward. Check the gage number, and that it records "
            "parameter 00060 (discharge) over that period."
        )

    os.makedirs("data/temp", exist_ok=True)
    file_path = os.path.join("data/temp", "flow_data.csv")
    pd.DataFrame(rows).to_csv(file_path, index=False)

    info_path = download_site_coords(site)
    return file_path, info_path

def extract_site_info(info_path):
    """
    Extracts site information from the info file.
    
    Args:
        info_path (str): The path to the info file.
        
    Returns:
        dict: A dictionary containing site information.
    """
    with open(info_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    features = payload.get("features") or []
    if not features:
        raise ValueError(f"{info_path} holds no monitoring location.")

    # GeoJSON order is [longitude, latitude], and both are already signed
    # decimal degrees. The previous version parsed DMS out of a web page and
    # then negated the longitude by hand, which quietly assumed every gage was
    # in the western hemisphere.
    coords = (features[0].get("geometry") or {}).get("coordinates")
    if not coords or len(coords) < 2:
        raise ValueError(
            f"{info_path} has no coordinates for this site. Some monitoring "
            "locations are published without a mapped position."
        )
    longitude, latitude = float(coords[0]), float(coords[1])
    return pd.DataFrame({"latitude": [latitude], "longitude": [longitude]})

USGS_LOCATIONS_URL = (
    "https://api.waterdata.usgs.gov/ogcapi/v0/collections/"
    "monitoring-locations/items"
)


def download_site_coords(site_id):
    """Fetch one gage's location as GeoJSON and cache it. Returns the path.

    This used to scrape the NWIS inventory *web page* and pull degrees, minutes
    and seconds out of the HTML by splitting on spaces. That page is being
    retired with the rest of NWISWeb, and once its markup shifted the parser
    started reading a tag -- hence `could not convert string to float:
    'html><html'`. Scraping a rendered page for numbers was always going to end
    that way.

    The API returns a GeoJSON Point in decimal degrees, already signed, so there
    is no DMS arithmetic and no hemisphere assumption to get wrong.
    """
    query = urllib.parse.urlencode({
        "monitoring_location_number": site_id,
        "agency_code": "USGS",
        "f": "json",
    })
    os.makedirs("data/temp", exist_ok=True)
    info_path = os.path.join("data/temp", "info_data.json")
    with urllib.request.urlopen(f"{USGS_LOCATIONS_URL}?{query}", timeout=60) as resp:
        payload = json.load(resp)

    if not payload.get("features"):
        raise ValueError(
            f"USGS has no monitoring location numbered {site_id}. Check the "
            "gage number -- it should be 8 digits or more, e.g. 06721000."
        )
    with open(info_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)
    return info_path

