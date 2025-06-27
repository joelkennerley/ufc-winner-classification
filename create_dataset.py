from bs4 import BeautifulSoup
import requests
import pandas as pd
from fake_useragent import UserAgent
import random
import time
from concurrent.futures import ThreadPoolExecutor

ua = UserAgent()

ufc_stats = "http://ufcstats.com/statistics/events/completed?page=all"

# ============== Helper functions ================================

def get_headers():
    return {"User-Agent": ua.random}

# Delay between requests
def sleep_polite():
    time.sleep(random.uniform(1, 2))

def flatten(list_of_lists):
    flattened_list = []
    for nested in list_of_lists:
        flattened_list.extend(nested)
    return flattened_list

def create_summary_df(data):
    # cols = ['fight_id', 'fighter1', 'fighter2', 'result', 'bout', 'method', 'round', 'time', 'format', 'ref']
    fight_summary_df = pd.DataFrame(data)
    return fight_summary_df

# ==============================================================

# ============= Retrieving links for extraction ================

# scraping ufcstats.com to give links to every documented fight card
def card_finder(url):
    result = requests.get(url)
    soup = BeautifulSoup(result.content, 'html.parser')
    s = soup.find('tbody')
    cards = s.find_all('a')
    card_links = []
    for card in cards:
        card_links.append(card['href'])
    return card_links

# retrieving each fight link in each card
def get_fight_links(link):
    sleep_polite()
    card = requests.get(link, headers=get_headers())
    card_soup = BeautifulSoup(card.content, 'html.parser')
    fight_element = card_soup.find('tbody', class_='b-fight-details__table-body')
    fight_rows = fight_element.find_all('tr')
    return [fights['data-link'] for fights in fight_rows]

# ================================================================

# ============ Extracting fight stats and summaries ==============


def get_summary(fight_urls):
    fight_id, url = fight_urls
    sleep_polite()
    fight = requests.get(url, headers=get_headers())
    fight_soup = BeautifulSoup(fight.content, 'html.parser')

    fighter1, fighter2 = fight_soup.find_all('a', class_='b-link b-fight-details__person-link')
    fighter1_link = fighter1['href']
    fighter2_link = fighter2['href']
    fighter1, fighter2 = fighter1.get_text(strip=True), fighter2.get_text(strip=True)
    bout_type = fight_soup.find('i', class_='b-fight-details__fight-title').get_text(strip=True)
    fight_details = fight_soup.find('p', class_='b-fight-details__text')

    # retrieving outcome of fight
    fighters = fight_soup.find_all('div', class_='b-fight-details__person')
    result = 'N/A'
    for fighter in fighters:
        outcome = fighter.find('i', class_='b-fight-details__person-status').get_text(strip=True)
        if outcome == 'W':
            result = fighter.find('a', class_='b-link b-fight-details__person-link').get_text(strip=True)
            break
        elif outcome == 'NC':
            result = 'NC'
            break
        elif outcome == 'D':
            result = 'Draw'
            break

    method_tag = fight_soup.find('i', class_='b-fight-details__text-item_first')
    method = method_tag.find_next('i', style='font-style: normal').get_text(strip=True)

    ref = fight_details.find('span').get_text(strip=True)

    values = [fight_id, fighter1, fighter2, result, bout_type, method]

    # retrieves round, time, and format
    for tag in fight_details.find_all('i'):
        # Get the next sibling text after each i tag
        next_text = tag.next_sibling
        if next_text:
            cleaned = next_text.strip()
            if cleaned:
                values.append(cleaned)
    values.append(ref)

    values.extend(get_fighter_profile(fighter1_link))
    values.extend(get_fighter_profile(fighter2_link))
    return values


def get_fighter_profile(fighter_url):
    """
    :param fighter_url: url of fighter
    :return: list of the fighters attributes and stats
    """
    sleep_polite()
    stat_list = []
    response = requests.get(fighter_url, headers=get_headers())
    soup = BeautifulSoup(response.content, 'html.parser')
    name = soup.find('span', class_='b-content__title-highlight').get_text(strip=True)
    stat_list.append(name)
    record = get_record(soup)
    stat_list.extend(record)
    fighter_stats = get_fighter_stats(soup)
    stat_list.extend(fighter_stats)
    stat_list.pop(-5) # deleting because theres an extra li element in every stats table
    return stat_list

def get_fighter_stats(soup):
    """
    :param soup: soup of the fighters url
    :return: list of the fighters stats, eg. 'SLpM', 'str acc', 'SApM'
    """
    stat_list = []
    div_element = soup.find('div', class_='b-fight-details b-fight-details_margin-top')
    li_elements = div_element.find_all('li', class_='b-list__box-list-item b-list__box-list-item_type_block')
    for li in li_elements:
        full_text = li.get_text(strip=True)
        value = full_text.split(":", 1)[-1].strip()  # Split at the first colon and take the part after it
        stat_list.append(value)
    return stat_list

def get_record(soup):
    """
    separates record into wins, losses, draws, and ncs
    :param soup: soup of the fighter url
    :return: list of their records wins losses draws and no contests
    """
    record_element = soup.find('span', class_='b-content__title-record').get_text(strip=True)
    # record element looks smth like: record: 11-1-1 (1 NC)
    # record list: ['record:', '11-1-1', '(1', 'NC)']
    record_list = record_element.split()
    wins, losses, draws = record_list[1].split('-')
    if len(record_list)>2: # fighter has nc on record
        nc = record_list[2][1] # removes '(' before number
    else: # fighter does not have nc on record
        nc = 0
    return [wins, losses, draws, nc]

# ================================================================

# ==================== main ======================================

def main():
    start = time.time()
    # Get card links
    fight_cards = card_finder(ufc_stats)[1:2]

    # Fetch fight links concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        fight_links = list(executor.map(get_fight_links, fight_cards))

    # Flatten the list of lists of fight links
    flat_fight_links = flatten(fight_links)

    # Retrieve stats concurrently
    # with ThreadPoolExecutor(max_workers=10) as executor:
    #     fight_summaries = list(executor.map(get_summary, enumerate(flat_fight_links)))

    fight_summaries = []
    for fight in enumerate(flat_fight_links):
        fight_summaries.append(get_summary(fight))

    summary_df = create_summary_df(fight_summaries)
    summary_df.to_csv('fight_summaries2.csv', index=False)

    end = time.time()
    print(f'Time taken: {end - start:.2f} seconds')

if __name__ == "__main__":
    main()
