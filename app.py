from flask import Flask, request, render_template, redirect
from math import floor
from sqlite3 import OperationalError
import string
import sqlite3
import random

from urllib.parse import urlparse  # Python 3
str_encode = str.encode

try:
    from string import ascii_lowercase
    from string import ascii_uppercase
except ImportError:
    from string import lowercase as ascii_lowercase
    from string import uppercase as ascii_uppercase

import base64

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


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = str_encode(request.form.get('url'))
        if urlparse(original_url).scheme == '':
            url = 'http://' + original_url
        else:
            url = original_url
        with sqlite3.connect('urls.db') as conn:
            hashed_url = str(base64.urlsafe_b64encode(url)).replace("=", "").replace("\'", "")[-6:] + str(random.randint(1, 10))
            cursor = conn.cursor()
            res = cursor.execute(
                'INSERT INTO WEB_URL (HASH_URL, URL) VALUES (?, ?)',
                [hashed_url, base64.urlsafe_b64encode(url)]
            )
        return render_template('home.html', short_url=host + hashed_url)
    return render_template('home.html')


@app.route('/<short_url>')
def redirect_short_url(short_url):
    print(short_url)
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
