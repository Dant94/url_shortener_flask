from flask import Flask, request, redirect, jsonify, abort
from sqlite3 import OperationalError
import string
import sqlite3
import random
import base64
from urllib.parse import urlparse  # Python 3

str_encode = str.encode

try:
    from string import ascii_lowercase
    from string import ascii_uppercase
except ImportError:
    from string import lowercase as ascii_lowercase
    from string import uppercase as ascii_uppercase

# Assuming urls.db is in your app root folder
app = Flask(__name__)
host = 'http://localhost:5000/'


def table_check():
    create_table = """
        CREATE TABLE WEB_URL(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        URL TEXT NOT NULL,
        HASH_URL TEXT NOT NULL
        );
        """
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
        except OperationalError:
            pass


def check_if_url_in_db(url):
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        res = cursor.execute('SELECT HASH_URL FROM WEB_URL WHERE URL=?', [base64.urlsafe_b64encode(url)])
        try:
            hash_url = res.fetchone()[0]
            if hash_url is not None:
                short_url = host + hash_url
        except Exception as e:
            print(e)
    conn.close()
    return short_url


def insert_into_db(url):
    with sqlite3.connect('urls.db') as conn:
        hashed_url = str(base64.urlsafe_b64encode(url)).replace("=", "").replace("\'", "")[-6:] + str(
            random.randint(1, 10))
        cursor = conn.cursor()
        res = cursor.execute(
            'INSERT INTO WEB_URL (HASH_URL, URL) VALUES (?, ?)',
            [hashed_url, base64.urlsafe_b64encode(url)]
        )
    conn.close()
    short_url = host + hashed_url
    return short_url


@app.route('/', methods=['POST', 'GET'])
def post_short_url():
    if not request.args.get('url'):
        abort(400)
    original_url = str_encode(request.args.get('url'))
    if urlparse(original_url).scheme == '':
        url = 'http://' + original_url
    else:
        url = original_url
        try:
            return jsonify({'short_url': check_if_url_in_db(url)})
        except:
            return jsonify({'short_url': insert_into_db(url)})


@app.route('/<short_url>')
def get_full_url(short_url):
    url = host  # fallback if no URL is found
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        res = cursor.execute('SELECT URL FROM WEB_URL WHERE HASH_URL=?', [short_url])
        try:
            short = res.fetchone()
            if short is not None:
                url = base64.urlsafe_b64decode(short[0])
        except Exception as e:
            print(e)
    return redirect(url)


if __name__ == '__main__':
    # This code checks whether database table is created or not
    table_check()
    app.run(debug=True)
