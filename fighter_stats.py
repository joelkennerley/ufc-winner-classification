from bs4 import BeautifulSoup
import requests
import pandas as pd
from fake_useragent import UserAgent
import random
import time
from concurrent.futures import ThreadPoolExecutor
import string
ua = UserAgent()

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

def main():
    for i in range(20):
        print(get_fighter_profile('http://ufcstats.com/fighter-details/8d11d9c13e2ccdf7'))

if __name__ == "__main__":
    main()
