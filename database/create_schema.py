import sqlite3

conn = sqlite3.connect('coches360.db')
cursor = conn.cursor()

def create_retailer_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS RETAILER (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    ''')

def create_brand_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS BRAND (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    ''')

def create_retailer_brand_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS RETAILER_BRAND (
        retailer_id INTEGER,
        brand_id INTEGER,
        internal_code INTEGER NOT NULL,
        PRIMARY KEY (retailer_id, brand_id),
        FOREIGN KEY (retailer_id) REFERENCES RETAILER(id),
        FOREIGN KEY (brand_id) REFERENCES BRAND(id)
    )
    ''')

def create_products_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CAR (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        web_id TEXT UNIQUE,                     -- ID from API
        creation_date TEXT,                     -- Creation date of listing
        title TEXT NOT NULL,                    -- Car title/name
        url TEXT,                               -- Listing URL
        price REAL NOT NULL,                    -- Car price
        has_taxes INTEGER,                      -- Boolean for taxes included (0/1)
        price_indicator_average REAL,           -- Average recommended price
        price_indicator_rank INTEGER,           -- Price rank (1-5)
        seller_name TEXT,                       -- Seller name
        is_professional INTEGER,                -- Boolean for professional seller (0/1)
        seller_score_average REAL,              -- Seller rating average
        seller_comments_number INTEGER,         -- Number of seller comments
        km INTEGER,                             -- Car mileage
        year INTEGER,                           -- Car year
        cubic_capacity INTEGER,                 -- Engine volume
        region TEXT,                            -- Region of sale
        main_province TEXT,                     -- Province of sale
        city TEXT,                              -- City of sale
        image_urls TEXT,                        -- Comma-separated image URLs
        fuel_type TEXT,                         -- Fuel type
        horsepower INTEGER,                     -- Horsepower
        warranty_months INTEGER,                -- Warranty duration
        environmental_label TEXT,               -- Environmental label
        retailer_id INTEGER,                    -- Foreign key to RETAILER
        brand_id INTEGER,                       -- Foreign key to BRAND
        FOREIGN KEY (retailer_id) REFERENCES RETAILER(id),
        FOREIGN KEY (brand_id) REFERENCES BRAND(id)
    )
    ''')

def main():
    create_retailer_table()
    create_brand_table()
    create_retailer_brand_table()
    create_products_table()

    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()