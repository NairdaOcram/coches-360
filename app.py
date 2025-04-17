from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import spacy
import os
import unicodedata
import re
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(filename='logs/api.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def remove_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )


def normalize_text(text):
    text = text.lower()  # Convert to lowercase
    text = remove_accents(text)
    text = re.sub(r'[^a-záéíóúüñ0-9\s]', '', text)  # Remove special characters
    text = text.replace(" km", " kilometros")  # Expand "km" to "kilómetros"
    text = re.sub(r'(\d+)k', lambda x: str(int(x.group(1)) * 1000), text)  # Convert "100k" to "100000"
    text = re.sub(r'(\d+)\s?mil', lambda x: str(int(x.group(1)) * 1000), text)  # Convert "30 mil" or "30mil" to "30000"
    return text


# Construct absolute path to the model
model_path = os.path.join(os.path.dirname(__file__), 'model', 'output', 'model-best')

# Load SpaCy model
try:
    nlp = spacy.load(model_path)
    logging.info('SpaCy model loaded successfully')
except Exception as e:
    logging.error(f'Failed to load SpaCy model: {str(e)}')
    raise


# Database connection
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'coches360.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


@app.route('/cars', methods=['GET'])
def get_cars():
    try:
        data = request.get_json()
        if not data or 'sentence' not in data:
            logging.error('No sentence provided in request body')
            return jsonify({'error': 'Sentence is required in JSON payload'}), 400

        sentence = data['sentence']
        if not sentence:
            logging.error('Empty sentence provided in request body')
            return jsonify({'error': 'Sentence cannot be empty'}), 400

        logging.info(f'Received sentence: {sentence}')

        # Normalize and process the sentence
        normalized_sentence = normalize_text(sentence)
        doc = nlp(normalized_sentence)

        # Extract entities
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_
            })

        # Build SQL query dynamically
        query = '''
            SELECT CAR.web_id, CAR.title, CAR.price, CAR.year, CAR.km, CAR.url, BRAND.name AS brand_name
            FROM CAR
            JOIN BRAND ON CAR.brand_id = BRAND.id
            WHERE 1=1
        '''
        params = []

        # Process entities for query conditions
        brand = None
        model = None
        year = None
        mileage = None

        for entity in entities:
            if entity['label'] == 'BRAND':
                brand = entity['text']
                query += ' AND LOWER(BRAND.name) = LOWER(?)'
                params.append(brand)
            elif entity['label'] == 'MODEL':
                model = entity['text']
                query += ' AND LOWER(CAR.title) LIKE LOWER(?)'
                params.append(f'%{model}%')
            elif entity['label'] == 'YEAR':
                year = entity['text']
                query += ' AND CAR.year = ?'
                params.append(int(year))
            elif entity['label'] == 'MILEAGE':
                mileage = entity['text']
                mileage_int = int(mileage)
                query += ' AND CAR.km <= ?'
                params.append(mileage_int)

        # Execute query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        cars = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # Prepare response
        response = {
            'sentence': sentence,
            'normalized_sentence': normalized_sentence,
            'entities': entities,
            'cars': cars
        }

        if not cars:
            response['message'] = 'No cars found matching the criteria'
            logging.info(f'No cars found for sentence: {sentence}')
        else:
            logging.info(f'Found {len(cars)} cars for sentence: {sentence}')

        return jsonify(response), 200

    except Exception as e:
        logging.error(f'Error processing request: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)