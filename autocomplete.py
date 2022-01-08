from flask import Flask, render_template
from flask import request, jsonify, make_response
import pandas as pd
from src.data_gen import suggest
from src.data_gen import song_from_id
from src.data_gen import genre_from_id
from src.recommender import getRecs
import json

app= Flask(__name__)

@app.route('/', methods = ["POST"])
def autocomplete():
    song = request.get_json()
    suggestions = suggest(json.dumps(song))
    suggestions = suggestions.to_dict()
    suggestions = make_response(jsonify(suggestions))
    return suggestions

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/generator') 
def search():
    song_id = request.args.get("ids")
    song = song_from_id(song_id)
    genre = genre_from_id(song_id)
    recs =getRecs(genre, song)
    recs = recs.to_dict()
    return render_template('recommendations.html', recs=recs)
    

