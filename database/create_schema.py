import sqlite3

conn = sqlite3.connect('coches360.db')
cursor = conn.cursor()

def create_retailer_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS retailer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    ''')

def create_categories_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS category (
        id INTEGER NOT NULL,
        name TEXT NOT NULL,
        retailer_id INTEGER,
        PRIMARY KEY (id, retailer_id),
        FOREIGN KEY (retailer_id) REFERENCES retailer(id)
    )
    ''')


def main():
    create_retailer_table()
    create_categories_table()

    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
