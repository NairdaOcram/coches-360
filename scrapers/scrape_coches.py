import sqlite3
import requests
import json
import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(filename = '../logs/coches.log', level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')

COCHES_ID = os.getenv('COCHES_ID')

url_categories = "https://web.gw.coches.net/makes"
url_listing = "https://web.gw.coches.net/search/listing"

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://www.coches.net",
    "priority": "u=1, i",
    "referer": "https://www.coches.net/",
    "sec-ch-ua": '"Not(A:Brand)";v="99", "Brave";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "x-adevinta-channel": "web-desktop",
    "x-adevinta-page-url": "https://www.coches.net/search/",
    "x-adevinta-referer": "https://www.coches.net/",
    "x-adevinta-session-id": "73341d5f-4bf0-43ef-aca0-7b9f6ad75a5c",
    "x-schibsted-tenant": "coches"
}

def fetch_categories():
    logging.info('Function fetch_categories called')
    try:
        response = requests.get(url_categories, headers = headers)

        if response.status_code == 200:
            logging.info('Categories fetched successfully.')
            return response.json().get('items', [])
        else:
            logging.error(f'Failed to fetch categories. Status code: {response.status_code}')
            return None

    except Exception as e:
        logging.error(f'An error occurred while fetching categories: {str(e)}')
        return None

def insert_categories(categories):
    try:
        conn = sqlite3.connect('../database/coches360.db')
        cursor = conn.cursor()

        for category in categories:
            category_id = category.get('id', None)
            category_label = category.get('label', None)

            cursor.execute('''
                            INSERT OR IGNORE INTO category (id, name, retailer_id)
                            VALUES (?, ?, ?)
                        ''', (category_id, category_label, COCHES_ID))

        conn.commit()
        conn.close()
        logging.info('Categories saved to the database successfully.')

    except Exception as e:
        logging.error(f'An error occurred while saving categories to the database: {str(e)}')


def main():
    categories = fetch_categories()

    if categories:
        insert_categories(categories)

if __name__ == '__main__':
    main()