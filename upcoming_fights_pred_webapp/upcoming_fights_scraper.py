# This .py file was generated through the use of Claude

"""
UFC Stats – Upcoming Event Fight Card Scraper
=============================================
Scrapes http://ufcstats.com/statistics/events/upcoming to find the closest
upcoming UFC event, then returns a DataFrame of every bout on that card.

DataFrame columns:
    fighter1_name  : str   – name of the first fighter
    fighter1_id    : str   – fighter1's ufcstats ID
    fighter2_name  : str   – name of the second fighter
    fighter2_id    : str   – fighter2's ufcstats ID
    weight_class   : str   – weight class for the bout
    date           : str   – scheduled fight date (e.g. "March 28, 2026")
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd


BASE_URL = "http://ufcstats.com"
UPCOMING_URL = f"{BASE_URL}/statistics/events/upcoming"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _get_soup(url: str, timeout: int = 15) -> BeautifulSoup:
    """Fetch a URL and return a BeautifulSoup object."""
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def _get_closest_event() -> tuple[str, str]:
    """
    Parse the upcoming events list and return (event_url, event_date)
    for the soonest scheduled event.
    """
    soup = _get_soup(UPCOMING_URL)

    rows = soup.select("tr.b-statistics__table-row")

    for row in rows:
        link_tag = row.select_one("td.b-statistics__table-col i.b-statistics__table-content a")
        if not link_tag:
            continue

        event_url = link_tag["href"].strip()

        date_span = row.select_one(
            "td.b-statistics__table-col i.b-statistics__table-content span.b-statistics__date"
        )
        if date_span:
            event_date = date_span.get_text(strip=True)
        else:
            i_tag = row.select_one("i.b-statistics__table-content")
            raw = i_tag.get_text(" ", strip=True) if i_tag else ""
            lines = [t.strip() for t in raw.splitlines() if t.strip()]
            event_date = lines[-1] if lines else ""

        return event_url, event_date

    raise ValueError(
        "No upcoming events found on ufcstats.com – "
        "the page structure may have changed."
    )


def _scrape_fight_card(event_url: str, event_date: str) -> pd.DataFrame:
    """
    Given the URL of an event detail page, scrape all bouts and return
    a DataFrame with fighter names, IDs, weight class, and the event date.

    Table columns on ufcstats event page:
        0: W/L  1: Fighter  2: Kd  3: Str  4: Td  5: Sub  6: Weight class  7: Method  8: Round  9: Time
    """
    soup = _get_soup(event_url)

    weight_class_keywords = [
        "weight", "Weight", "Flyweight", "Bantamweight", "Featherweight",
        "Lightweight", "Welterweight", "Middleweight", "Heavyweight", "Strawweight"
    ]

    records = []
    for row in soup.find_all("tr"):
        fighter_links = [
            a for a in row.find_all("a")
            if "/fighter-details/" in a.get("href", "")
        ]
        if len(fighter_links) < 2:
            continue

        # Weight class is the 7th <td> (index 6):
        # W/L | Fighter | Kd | Str | Td | Sub | Weight class | ...
        weight_class = ""
        tds = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(tds) > 6:
            weight_class = tds[6]
        else:
            # Fallback: scan all tds for a weight class keyword
            for td_text in tds:
                if any(k in td_text for k in weight_class_keywords):
                    weight_class = td_text
                    break

        records.append(
            {
                "fighter1": fighter_links[0].get_text(strip=True),
                "fighter1_id": fighter_links[0]["href"].strip().split("/")[-1],
                "fighter2": fighter_links[1].get_text(strip=True),
                "fighter2_id": fighter_links[1]["href"].strip().split("/")[-1],
                "bout": weight_class,
                "date": event_date,
            }
        )

    if not records:
        raise ValueError(
            f"No fight rows found at {event_url}. "
            "The page structure may have changed."
        )

    return pd.DataFrame(records)


def scrape_upcoming_card() -> pd.DataFrame:
    """
    Top-level function.

    Fetches the closest upcoming UFC event from ufcstats.com and returns
    a pandas DataFrame where every row represents one scheduled bout.

    Returns
    -------
    pd.DataFrame with columns:
        fighter1_name, fighter1_id, fighter2_name, fighter2_id, weight_class, date
    """
    print("Fetching upcoming events list...")
    event_url, event_date = _get_closest_event()
    print(f"  -> Closest event URL : {event_url}")
    print(f"  -> Event date        : {event_date}")

    print("Scraping fight card...")
    df = _scrape_fight_card(event_url, event_date)
    print(f"  -> {len(df)} bouts found.\n")
    df.to_csv('raw_upcoming_fights.csv', index=False)
    return df


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    df = scrape_upcoming_card()
    pd.set_option("display.max_colwidth", 60)
    pd.set_option("display.max_rows", None)
    df.to_csv('raw_upcoming_fights.csv', index=False)
