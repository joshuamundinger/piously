import os
import json
from traceback import format_exception
from sys import exc_info
from flask import Flask, url_for, render_template, request, make_response, jsonify
from markupsafe import escape
from copy import deepcopy

from backend.game import Game
from backend.errors import InvalidMove

# run with: python -m heroku.app

app = Flask(__name__)
GAMES = {}
ENDGAME_STATES = {} # store the end state of the most recently ended game
MAX_GAMES = 10


@app.route("/")
def index():
    text = [
        'Designed by Jonah Ostroff and implemented by Rachel Diamond and Josh Mundinger',
        '<b>Active games: </b>' + ', '.join(GAMES.keys()),
        '<b>Most recently ended: </b>' + ', '.join(ENDGAME_STATES.keys()),
        '<b>Usage:</b>',
        ' - To see game state go to /GAMEID',
        ' - To end a game go to /GAMEID/end',
        ' - To start a game go to /GAMEID/new',
        ' - To play send requests to /do_action',
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
    return html

@app.route('/about')
def about():
    return 'Designed by Jonah Ostroff and implemented by Rachel Diamond and Josh Mundinger'

@app.route('/<game_id>')
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
        return html
    else:
        return 'ERROR: No game "{}"'.format(game_id)

@app.route('/<game_id>/new')
def new_game(game_id):
    if game_id in GAMES:
        return 'ERROR: Game "{}" already exists'.format(game_id)

    if len(GAMES) >= MAX_GAMES:
        # TODO: handle this
        return {
            'error': 'Too many games: Please wait for another game to complete',
            'game_over': True,
        }

    GAMES[game_id] = Game("Dark")
    return ''

@app.route('/<game_id>/end')
def end_game(game_id):
    if game_id in GAMES:
        GAMES.pop(game_id)
        return 'Ended game {}'.format(game_id)
    return 'ERROR: No game "{}"'.format(game_id)

@app.route('/do_action', methods=['POST', 'OPTIONS'])
def do_action():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()

    try:
        data = request.json
        game_id = data['game_id']
        if not game_id in GAMES:
            if data['current_action'] == 'start':
                # start a new game
                error = new_game(game_id)
                if error:
                    return error
            elif game_id in ENDGAME_STATES:
                return jsonify(ENDGAME_STATES[game_id])
            else:
                return {
                    'error': 'Game "{}" does not exist'.format(data['game_id']),
                    'game_over': True,
                }

        game = GAMES[game_id]
        if data['current_action'] in ['start', 'none']:
            data['current_action'] = game.start_action

        response_data = game.do_action(data)

        if response_data['current_action'] == 'end game':
            print('app deleting game + saving ENDGAME')
            ENDGAME_STATES.clear() # only store the 1 most recently ended game
            ENDGAME_STATES[game_id] = response_data
            GAMES.pop(game_id)
    except Exception as error:
        exc_type, exc_value, exc_traceback = exc_info()
        response_data = {
            'error': 'Internal Server Error',
            'backend_error': format_exception(exc_type, exc_value, exc_traceback)
        }

    response = jsonify(response_data)
    # response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

# # TODO:
# https://flask.palletsprojects.com/en/1.1.x/patterns/apierrors/
# @app.errorhandler(InvalidMove)
# def handle_invalid_move(error):
#     response = jsonify(error.to_dict())
#     response.status_code = error.status_code
#     return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
