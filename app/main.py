import sqlite3

from flask import Flask
from flask import jsonify
from flask import g

app = Flask(__name__)

DATABASE = 'daylio.sqlite'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/mood/<mood>')
def get_mood(mood):
    mood_dict = []
    mood_dict.append({'data': ''})
    moods = query_db('SELECT * FROM daylio where mood = ?', [mood])
    print(moods)
    if not moods:
        return jsonify('No moods found'), 404
    else:
        for mood in moods:
            mood_dict.append({
                'mood': mood['mood'],
                'mood_rating': convert_mood(mood['mood']),
                'activities': mood['activities'],
                'note': mood['note'],
                'timestamp': mood['timestamp']
            })
        return jsonify(mood_dict)

@app.route('/mood')
def get_all():
    mood_dict = []
    for moods in query_db('SELECT * FROM daylio'):
        mood_dict.append({
            'mood' : moods['mood'],
            'mood_rating' : convert_mood(moods['mood']),
            'activities' : moods['activities'],
            'note' : moods['note'],
            'timestamp' : moods['timestamp']
        })
    return jsonify(mood_dict)


def convert_mood(mood):
    all_moods = {
        'amazing' : 4,
        'awesome' : 4,
        'good' : 3,
        'meh' : 2,
        'bad' : 1,
        'awful' : 0
    }

    return all_moods[mood]
