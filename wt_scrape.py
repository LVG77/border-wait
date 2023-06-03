import re
import urllib.parse
import urllib.request
import json

url = "https://www.quebec511.info/en/Carte/Element.ashx"
action = "PosteFrontalier"


def make_get_request(url: str, **kwargs):
    params = urllib.parse.urlencode(kwargs)
    url = f"{url}?{params}"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())

    return data


def get_info_html(url: str, **kwargs):
    params = urllib.parse.urlencode(kwargs)
    url = f"{url}?{params}"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")

    return html


import re


def parse_time_expression(expression):
    time_in_minutes = 0
    # Extract the numerical value and the unit from the expression using regex
    match = re.search(r"(\d+(?:\.\d+)?)\s*(\b\w+\b)", expression)
    if match:
        value = float(match.group(1))
        unit = match.group(2).lower()
        # Convert the unit to minutes
        if unit == "minute" or unit == "minutes":
            time_in_minutes = value
        elif unit == "hour" or unit == "hours":
            time_in_minutes = value * 60
        elif unit == "day" or unit == "days":
            time_in_minutes = value * 60 * 24
        elif unit == "week" or unit == "weeks":
            time_in_minutes = value * 60 * 24 * 7
        elif unit == "month" or unit == "months":
            time_in_minutes = value * 60 * 24 * 30
        elif unit == "year" or unit == "years":
            time_in_minutes = value * 60 * 24 * 365
    return int(time_in_minutes)


def extract_waittime(html):
    re_start = re.compile("tdAttenteVoyageurAmericain")
    to_can = re_start.split(html)[1].split("</td>")[0].strip('"')
    to_can_int = parse_time_expression(to_can)
    re_start = re.compile("tdAttenteVoyageurCanadien")
    to_us = re_start.split(html)[1].split("</td>")[0].strip('"')
    to_us_int = parse_time_expression(to_us)
    return {
        "Travellers to CAN": to_can,
        "Travellers to US": to_us,
        "Waittime to CAN": to_can_int,
        "Waittime to US": to_us_int,
    }


def add_waittime(data: list):
    url_info = (
        "https://www.quebec511.info/en/Carte/Fenetres/FenetrePosteFrontalier.aspx"
    )
    result = []
    for d in data:
        id = d["id"]
        info_html = get_info_html(url=url_info, id=id)
        wt_dict = extract_waittime(info_html)
        result.append(d | wt_dict)
    return result


if __name__ == "__main__":
    data = make_get_request(
        url=url,
        action=action,
        lang="en",
        zoom=8,
        xMin=-78.25,
        yMin=42.19,
        xMax=-68.11,
        yMax=49.41,
    )
    data = add_waittime(data)
    with open("wt_data.json", "w") as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))
