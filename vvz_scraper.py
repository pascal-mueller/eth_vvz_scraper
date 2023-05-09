import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import re
import time

base_url = "https://www.vorlesungen.ethz.ch"


def get_url(seite):
    return f"{base_url}/Vorlesungsverzeichnis/sucheLehrangebot.view?lerneinheitscode=&deptId=&famname=&unterbereichAbschnittId=&seite={seite}&lerneinheitstitel=&rufname=&kpRange=0,999&lehrsprache=&bereichAbschnittId=&semkez=2023S&studiengangAbschnittId=&studiengangTyp=&ansicht=1&lang=de&katalogdaten=&wahlinfo="


def get_max_page():
    # Get how many pages there are
    url_de = get_url(1)

    search_results = requests.get(url_de)

    html = search_results.text

    soup = BeautifulSoup(html, "html.parser")

    last_page_link = base_url + soup.select(".lastPage")[0].parent.get("href")

    parsed_url = urlparse(last_page_link)
    max_page = parse_qs(parsed_url.query)["seite"][0]

    return int(max_page)


seite_max = get_max_page()

for seite in range(1, seite_max + 1):
    start_time = time.time()

    selector = "tr > td:nth-child(2) > b > a"

    url_de = get_url(seite)

    search_results = requests.get(url_de)

    html = search_results.text

    soup = BeautifulSoup(html, "html.parser")

    lecture_links = soup.select(selector)

    for i, lecture_link in enumerate(lecture_links):
        print(f"Seite: {seite}/{seite_max} > {i}/{len(lecture_links)} Lectures")
        # Get German page of lecture
        lecture_link_de = base_url + lecture_link.get("href")

        parsed_url = urlparse(lecture_link_de)
        lecture_id = parse_qs(parsed_url.query)["lerneinheitId"][0]

        html_de = requests.get(lecture_link_de).text

        with open(f"lectures/{lecture_id}_de.html", "w") as f:
            f.write(html_de)

        # Get English page of lecture
        parsed_url = urlparse(lecture_link_de)
        lecture_id = parse_qs(parsed_url.query)["lerneinheitId"][0]
        lecture_link_en = lecture_link_de.replace("lang=de", "lang=en")

        html_en = requests.get(lecture_link_en).text

        with open(f"lectures/{lecture_id}_en.html", "w") as f:
            f.write(html_en)

    end_time = time.time()
    print(
        f"\n\n APPROX: DURATION: {((seite_max - seite) * (end_time - start_time)) / 60}min"
    )
