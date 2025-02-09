import sqlite3
import os

from dotenv import load_dotenv

load_dotenv()

conn = sqlite3.connect('coches360.db')
cursor = conn.cursor()

COCHES_ID = os.getenv('COCHES_ID')

def insert_retailers():
    cursor.execute("INSERT INTO retailer (id, name) VALUES (?, ?)",
                   (COCHES_ID, 'coches.net'))


def main():
    insert_retailers()

    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()