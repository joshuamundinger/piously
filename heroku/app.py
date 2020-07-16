import os
import json
from traceback import format_exception
from sys import exc_info
from flask import Flask, url_for, render_template, request, make_response, jsonify, abort
from markupsafe import escape
from copy import deepcopy
from collections import OrderedDict

from backend.game import Game
from backend.errors import InvalidMove

# run with: python -m heroku.app

app = Flask(__name__)
GAMES = {}
ENDGAME_STATES = OrderedDict() # store the end state of the most recently ended games
MAX_GAMES = 20

@app.route("/")
def index():
    text = [
        'Designed by Jonah Ostroff and implemented by Rachel Diamond and Josh Mundinger',
        '<b>Active games: </b>' + ', '.join(GAMES.keys()),
        '<b>Most recently ended: </b>' + ', '.join(ENDGAME_STATES.keys()),
        '<b>Usage:</b>',
        ' - To see game state go to /GAMEID/show',
        ' - To end a game go to /GAMEID/end',
        ' - To start a game go to /GAMEID/new',
        ' - To play send requests to /api/do_action',
    ]
    html = """
    <html>
        <head>
            <h3>{title}</h3>
        </head>
        <body>
            <p>{text}</p>
        </body>
    </html>
    """.format(
        title = 'Hello from piously!',
        text = '</p><p>'.join(text),
    )
    return html, 200

@app.route('/about')
def about():
    return 'Designed by Jonah Ostroff and implemented by Rachel Diamond and Josh Mundinger', 200

@app.route('/<game_id>/show')
def show_board(game_id):
    # TODO: escape() game_id

    if game_id in GAMES:
        game = GAMES[game_id]
        state = game.get_game_state()
        state_text = ['<p><b>{}: </b>{}</p>'.format(k, v) for k, v in state.items()]

        html = """
        <html>
            <head>
                <h3>{title}</h3>
            </head>
            <body>
                {text}
            </body>
        </html>
        """.format(
            title = 'Game "{}"'.format(game_id),
            text = ''.join(state_text),
        )
        return html, 200
    else:
        return {'error': 'No game "{}"'.format(game_id)}, 500

@app.route('/<game_id>/new')
def new_game(game_id):
    if game_id in GAMES:
        return {'error': 'Game "{}" already exists'.format(game_id)}, 500

    if len(GAMES) >= MAX_GAMES:
        return {
            'error': 'Too many games: Please wait for another game to complete',
            'game_over': True,
        }, 500

    GAMES[game_id] = Game("Dark")
    return 'Created game {}'.format(game_id), 200

@app.route('/<game_id>/end')
def end_game(game_id):
    if game_id in GAMES:
        GAMES.pop(game_id)
        return 'Ended game {}'.format(game_id), 200
    return {'error': 'No game "{}"'.format(game_id)}, 404


def get_response(request):
    try:
        data = request.json
        game_id = data['game_id']
        if not game_id in GAMES:
            if data['current_action'] == 'start':
                # start a new game
                error, status = new_game(game_id)
                if status != 200:
                    return error, status
            elif game_id in ENDGAME_STATES:
                return ENDGAME_STATES[game_id], 200
            else:
                return {
                    'error': 'Game "{}" does not exist'.format(data['game_id']),
                    'game_over': True,
                }, 404

        game = GAMES[game_id]
        if data['current_action'] in ['start', 'none']:
            data['current_action'] = game.start_action

        response_data = game.do_action(data)

        if response_data['current_action'] == 'end game':
            print('app deleting game + saving ENDGAME')
            if game_id in ENDGAME_STATES:
                ENDGAME_STATES.move_to_end(game_id) # make this key newest
                print('overwriting {}'.format(game_id))
            elif len(ENDGAME_STATES) == MAX_GAMES:
                k, v = ENDGAME_STATES.popitem(last=False) # remove oldest
                print('deleting oldest ({}) and saving {}'.format(k, game_id))
            else:
                print('adding new endgame entry {}'.format(game_id))

            ENDGAME_STATES[game_id] = response_data
            GAMES.pop(game_id)

        return response_data, 200

    except Exception as error:
        exc_type, exc_value, exc_traceback = exc_info()
        return {
            'error': 'Internal Server Error',
            'backend_error': format_exception(exc_type, exc_value, exc_traceback)
        }, 500

@app.route('/api/do_action', methods=['POST', 'OPTIONS'])
def do_action():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()

    response_data, status = get_response(request)
    response = jsonify(response_data)
    response.headers.add("Access-Control-Allow-Origin", "*")

    return response, status

def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
