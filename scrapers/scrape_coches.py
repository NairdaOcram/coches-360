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
    "sec-fetch-model": "cors",
    "sec-fetch-site": "same-site",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "x-adevinta-channel": "web-desktop",
    "x-adevinta-page-url": "https://www.coches.net/search/",
    "x-adevinta-referer": "https://www.coches.net/",
    "x-adevinta-session-id": "73341d5f-4bf0-43ef-aca0-7b9f6ad75a5c",
    "x-schibsted-tenant": "coches",
    "content-type": "application/json",
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

            cursor.execute('SELECT id FROM BRAND WHERE name = ?', (category_label,))
            brand = cursor.fetchone()

            if brand:
                brand_id = brand[0]
            else:
                cursor.execute('''
                    INSERT INTO BRAND (name)
                    VALUES (?)
                ''', (category_label,))
                brand_id = cursor.lastrowid

            cursor.execute('''
                INSERT OR IGNORE INTO RETAILER_BRAND (retailer_id, brand_id, internal_code)
                VALUES (?, ?, ?)
            ''', (COCHES_ID, brand_id, category_id))

        conn.commit()
        conn.close()
        logging.info('Categories saved to the database successfully.')

    except Exception as e:
        logging.error(f'An error occurred while saving categories to the database: {str(e)}')

def fetch_listings():
    logging.info('Function fetch_listings called')
    try:
        conn = sqlite3.connect('../database/coches360.db')
        cursor = conn.cursor()
        cursor.execute("SELECT internal_code, brand_id FROM RETAILER_BRAND WHERE retailer_id = 1")
        categories = cursor.fetchall()
        for category_id, brand_id in categories:
            page = 1
            while True:
                data = {
                    "pagination": {"page": page, "size": 100},
                    "sort": {"order": "desc", "term": "relevance"},
                    "filters": {
                        "categories": {"category1Ids": [2500]},
                        "offerTypeIds": [0, 1, 2, 3, 4, 5],
                        "isCertified": False,
                        "onlyPeninsula": False,
                        "sellerTypeId": 0,
                        "transmissionTypeId": 0,
                        "vehicles": [{"make": "", "makeId": category_id, "model": "", "modelId": 0}]
                    }
                }
                response = requests.post(url_listing, headers=headers, json=data)
                if response.status_code == 200:
                    listings = response.json()
                    if not listings.get("items", []):
                        logging.info(f'Fetched listings for category {category_id} with a total of {page} pages')
                        break
                    for listing in listings.get("items", []):
                        image_urls = ','.join([res.get('url', '') for res in listing.get('resources', [])
                                            if res.get('type', '') == 'IMAGE'])
                        car_data = (
                            str(listing.get('id', '')),
                            listing.get('creation_date', ''),
                            listing.get('title', ''),
                            listing.get('url', ''),
                            listing.get('price', {}).get('amount', None),
                            1 if listing.get('price', {}).get('hasTaxes', False) else 0,
                            listing.get('price', {}).get('indicator', {}).get('average', None),
                            listing.get('price', {}).get('indicator', {}).get('rank', None),
                            listing.get('seller', {}).get('name', ''),
                            1 if listing.get('seller', {}).get('isProfessional', False) else 0,
                            listing.get('seller', {}).get('ratings', {}).get('scoreAverage', None),
                            listing.get('seller', {}).get('ratings', {}).get('commentsNumber', None),
                            listing.get('km', None),
                            listing.get('year', None),
                            listing.get('cubicCapacity', None),
                            listing.get('location', {}).get('regionLiteral', ''),
                            listing.get('location', {}).get('mainProvince', ''),
                            listing.get('location', {}).get('cityLiteral', ''),
                            image_urls,
                            listing.get('fuelType', ''),
                            listing.get('hp', None),
                            listing.get('warranty', {}).get('months', None),
                            listing.get('enviromentalLabel', ''),
                            COCHES_ID,
                            brand_id
                        )
                        try:
                            cursor.execute('''
                                INSERT OR IGNORE INTO CAR (
                                    web_id, creation_date, title, url, price, has_taxes,
                                    price_indicator_average, price_indicator_rank, seller_name,
                                    is_professional, seller_score_average, seller_comments_number,
                                    km, year, cubic_capacity, region, main_province, city,
                                    image_urls, fuel_type, horsepower, warranty_months,
                                    environmental_label, retailer_id, brand_id
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', car_data)
                        except sqlite3.Error as e:
                            logging.error(f'Error inserting car listing {listing.get("id", "")}: {str(e)}')
                    conn.commit()
                    page += 1
                else:
                    logging.error(f'Failed to fetch listings for category {category_id}. Status code: {response.status_code}')
                    break
        conn.close()
        logging.info('All listings saved to database successfully.')
    except Exception as e:
        logging.error(f'An error occurred while fetching listings: {str(e)}')

"""
def fetch_listings():
    logging.info('Function fetch_listings called')

    try:
        conn = sqlite3.connect('../database/coches360.db')
        cursor = conn.cursor()
        cursor.execute("SELECT internal_code FROM RETAILER_BRAND WHERE retailer_id = 1")
        category_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        for category_id in category_ids:
            page = 1
            all_listings = []

            while True:
                data = {
                    "pagination": {"page": page, "size": 100},
                    "sort": {"order": "desc", "term": "relevance"},
                    "filters": {
                        "categories": {"category1Ids": [2500]},
                        "offerTypeIds": [0, 1, 2, 3, 4, 5],
                        "isCertified": False,
                        "onlyPeninsula": False,
                        "sellerTypeId": 0,
                        "transmissionTypeId": 0,
                        "vehicles": [{"make": "", "makeId": category_id, "model": "", "modelId": 0}]
                    }
                }

                response = requests.post(url_listing, headers = headers, json = data)

                if response.status_code == 200:
                    listings = response.json()

                    if listings.get("items", []) == []:
                        logging.info(f'Fetched listings for category {category_id} with a total of {page} pages ')
                        break

                    all_listings.extend(listings.get("items", []))
                    page += 1
                else:
                    logging.error(f'Failed to fetch listings for category {category_id}. Status code: {response.status_code}')
                    break

            if all_listings:
                save_to_json(category_id, all_listings)

    except Exception as e:
        logging.error(f'An error occurred while fetching listing: {str(e)}')

def save_to_json(category_id, data):
    try:
        output_dir = '../data/listings'
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f'listings_{category_id}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f'Listings for category {category_id} saved successfully.')
    except Exception as e:
        logging.error(f'Failed to save listings for category {category_id}: {str(e)}')

"""
"""

id                                      # ID COCHE EN WEB
creation_date                           # CUANDO SE CREO EL ANUNCIO
title                                   # TITULO ANUNCIO (NOMBRE COCHE)
url                                     # coches.net + URL
price --> amount                        # PRECIO COCHE
price --> hasTaxes                      # IMPUESTO INCLUIDOS (IVA)
price --> indicator --> average         # MEDIDOR INTERNO COCHES.NET (PRECIO MEDIO RECOMENDADO)
price --> indicator --> rank            # ESCALA (1 = PRECIO ALTO, 2 = PRECIO ELEVADO, 3 = PRECIO JUSTO, 4 = BUEN PRECIO
                                        #         5 = SUPER PRECIO)
seller --> name                         # VENDEDOR DEL COCHE
seller --> isProfessional               # VENDEDOR VERIFICADO (CONCESIONARIOS NORMALMENTE)
seller --> ratings --> scoreAverage     # MEDIA CALIFACION VENDEDOR
seller --> ratings --> commentsNumber   # NUMERO TOTAL DE COMENTARIOS
km                                      # NUMERO TOTAL KM COCHE
year                                    # AÑO COCHE
cubicCapacity                           # VOLUMEN COCHE
location --> regionLiteral              # REGION VENTA COCHE
location --> mainProvince               # PROVINCIA VENTA COCHE
location --> cityLiteral                # CIUDAD VENTA COCHE

for resource in resources               # LINK IMAGENES
    resources --> type  IF == IMAGE
        resources --> type --> url      

fuelType                                # TIPO DE COMBUSTION
hp                                      # HORSE POWER
warranty --> months                     # MESES DE GARANTÍA
enviromentalLabel                       # ETIQUETA CONTAMINACION                       

"""

def main():
    categories = fetch_categories()

    if categories:
        insert_categories(categories)

    listings = fetch_listings()

if __name__ == '__main__':
    main()