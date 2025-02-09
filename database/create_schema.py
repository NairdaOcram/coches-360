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
        name TEXT NOT NULL,
        sku TEXT NOT NULL,
        price REAL NOT NULL,
        retailer_id INTEGER,
        brand_id INTEGER,

        FOREIGN KEY (retailer_id) REFERENCES RETAILER(id),
        FOREIGN KEY (brand_id) REFERENCES BRAND(id)
    )
    ''')


def main():
    # Create the tables
    create_retailer_table()
    create_brand_table()
    create_retailer_brand_table()
    create_products_table()

    # Commit and close the connection
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
