import sqlite3
import os

from dotenv import load_dotenv

load_dotenv()

conn = sqlite3.connect('coches360.db')
cursor = conn.cursor()

COCHES_ID = os.getenv('COCHES_ID')
COCHES_NAME = os.getenv('COCHES_NAME')

def insert_retailers():
    cursor.execute("INSERT INTO RETAILER (id, name) VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET name = excluded.name",
                   (COCHES_ID, COCHES_NAME))


def main():
    insert_retailers()

    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()