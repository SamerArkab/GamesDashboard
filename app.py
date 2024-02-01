from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

with sqlite3.connect('database.db') as connection:
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            type TEXT CHECK(type IN ('normal', 'admin')) DEFAULT 'normal'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            poster_url TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS review (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            game_id INTEGER,
            review TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (game_id) REFERENCES games (id)
        )
    ''')
    connection.commit()


def is_username_unique(username):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM users WHERE username=?', (username,))
        existing_user = cursor.fetchone()
        return existing_user is None


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not is_username_unique(username):
            return render_template('signup.html', error='Username already in-use.')

        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            connection.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT id, username, type FROM users WHERE username=? AND password=?', (username, password))
            user_info = cursor.fetchone()

        if user_info:
            session['user_id'] = user_info[0]
            session['username'] = user_info[1]
            session['user_type'] = user_info[2]
            return redirect(url_for('homepage'))

        else:
            flash("Invalid login information!")
            return render_template('login.html')

    return render_template('login.html')


@app.route('/')
def homepage():
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT id, title, poster_url FROM games')
        posters = cursor.fetchall()

        owner = 'owner'
        if is_username_unique(owner):
            password = 'owner12'
            cursor.execute("INSERT INTO users (username, password, type) VALUES (?, ?, ?)",
                       (owner, password, 'admin'))
            connection.commit()

    user_status = 'guest'
    username = None
    is_admin = False

    if 'user_id' in session:
        user_status = 'logged'
        username = session['username']
        is_admin = session.get('user_type') == 'admin'

    return render_template('homepage.html', posters=posters, user_status=user_status, username=username, is_admin=is_admin)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('homepage'))


@app.route('/add_poster', methods=['GET', 'POST'])
def add_poster():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('homepage'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        poster_url = request.form['poster_url']

        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO games (title, description, poster_url) VALUES (?, ?, ?)",
                           (title, description, poster_url))
            connection.commit()

        return redirect(url_for('homepage'))

    return render_template('add_poster.html')


@app.route('/description_reviews/<int:game_id>')
def description_reviews(game_id):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM games WHERE id=?', (game_id,))
        game = cursor.fetchone()

        cursor.execute('''
            SELECT review.review, users.username
            FROM review
            JOIN users ON review.user_id = users.id
            WHERE review.game_id=?
            ORDER BY review.id DESC
        ''', (game_id,))
        reviews = [{'text': review[0], 'username': review[1]} for review in cursor.fetchall()]

    user_status = 'guest'
    username = None

    if 'user_id' in session:
        user_status = 'logged'
        username = session['username']

    return render_template('description_reviews.html', game=game, reviews=reviews, user_status=user_status, username=username)


@app.route('/add_review/<int:game_id>', methods=['POST'])
def add_review(game_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    review_text = request.form.get('review_text', '')

    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO review (user_id, game_id, review) VALUES (?, ?, ?)',
                       (user_id, game_id, review_text))
        connection.commit()

    return redirect(url_for('description_reviews', game_id=game_id))


if __name__ == '__main__':
    app.run(debug=True)