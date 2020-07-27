import os
# import json
from json import load
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
MAX_GAMES = 50

def load_games():
    games = {}
    path = Game.filename()
    print('path is', path)

    for fn in os.listdir(path):
        print('filename is', fn)
        # TODO: check if os.path.isfile(os.path.join(path, name))
        with open(os.path.join(path, fn), "r") as file:
            game = Game.from_hash(load(file))
            games[game.game_id] = game
            print('loaded {}'.format(game.game_id))

    return games

# def game_exists(game_id):
#     filepath = Game.filename(game_id)
#     if game_id in GAMES or os.path.exists(filepath):
#         return True
#     else:
#         return False
#
# def get_game(game_id):
#     if game_id in GAMES:
#         return GAMES[game_id]
#     elif game_exists(game_id):
#         game = load_game(game_id)
#         GAMES[game_id] = game
#         return game
#     else:
#         print('no game {}'.format(game_id))
#         return None
#
# def load_game(game_id):
#     filepath = Game.filename(game_id)
#     if os.path.exists(filepath):
#         with open(filepath, "r") as file:
#             game = Game.from_hash(load(file))
#         return game

# @app.route("/delete_oldest")
# def delete_oldest():
#     games_dict = games or load_games()
#     oldest_game = min(games_dict.values(), key=lambda x: x.updated)
#     os.remove(Game.filename(oldest_game.game_id))

def game_str(show_active):
    ret = []
    for game in GAMES.values():
        if (show_active and not game.current_board.game_over) or (game.current_board.game_over and not show_active):
            ret.append(' - {}: {}'.format(game.updated, game.game_id))

    return ret

@app.route("/")
def index():
    text = [
        'Designed by Jonah Ostroff and implemented by Rachel Diamond and Josh Mundinger',
        '<b>Usage:</b>',
        ' - To start a game go to /GAMEID/new',
        ' - To see game state go to /GAMEID/show (or /GAMEID/json for raw json)',
        ' - To reset turn go to /GAMEID/reset',
        ' - To delete a game go to /GAMEID/delete',
        # ' - To delete the oldest game go to /delete_oldest'
        ' - To play send requests to /api/do_action',
        '<br /><b>Saved Games (+ last updated time): {}</b>'.format(len(GAMES)),
        '<b>active</b>',
    ] + game_str(True) + [
        '<b>ended</b>',
    ] + game_str(False)
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
        title = 'Welcome to Piously!',
        text = '</p><p>'.join(text),
    )
    return html, 200

@app.route('/about')
def about():
    return 'Designed by Jonah Ostroff and implemented by Rachel Diamond and Josh Mundinger', 200

@app.route('/<game_id>/json')
def show_json(game_id):
    if game_id in GAMES:
        game = GAMES[game_id]
        state = game.get_game_state(include_metadata=True)
        return state, 200
    else:
        return {'error': 'No game "{}"'.format(game_id)}, 500

@app.route('/<game_id>/show')
def show_board(game_id):
    # TODO: escape() game_id

    if game_id in GAMES:
        game = GAMES[game_id]
        state = game.get_game_state(include_metadata=True)
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

    GAMES[game_id] = Game(game_id)
    print('[{}] NEW_GAME'.format(game_id))
    return 'Created game {}'.format(game_id), 200

@app.route('/<game_id>/delete')
def delete_game(game_id):
    if game_id in GAMES:
        GAMES.pop(game_id)

    filepath = Game.filename(game_id)
    if os.path.exists(filepath):
        os.remove(filepath)

    return 'Ended game {}'.format(game_id), 200

    # return {'error': 'No game "{}"'.format(game_id)}, 404
    # if os.path.exists(Game.filename(game_id)):
    #     print("Removing game file")
    #     os.remove(Game.filename(game_id))
    # else:
    #     print("No game file exists")

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
            else:
                return {
                    'error': 'Game "{}" does not exist'.format(data['game_id']),
                    'game_over': True,
                }, 404

        game = GAMES[game_id]
        # if not game:
        #     # should never happen because just checked game_exists before this
        #     return {
        #         'error': 'Error loading game "{}"'.format(data['game_id']),
        #         'game_over': True,
        #     }, 500

        if data['current_action'] in ['start', 'none']:
            data['current_action'] = game.start_action

        # maybe_ending_turn = True if data['current_action'] == 'end turn' else False

        response_data = game.do_action(data)

        # if response_data['current_action'] == 'end game' and game_id in GAMES:
        #     print('[{}] END_GAME'.format(game_id))
        #     GAMES.pop(game_id)

        # elif maybe_ending_turn and response_data['current_action'] == 'none':
        #     data = {}
        #     with open(Game.filename(game_id), "r") as file:
        #         data = load(file)
        #
        #     print('reading file data')
        #     # print(data['game_id'])
        #     game = Game.from_hash(data)
        #     # print(game.game_id)
        #     GAMES[game_id] = game
        #     print('game replaced from file')

        return response_data, 200

    except Exception as error:
        exc_type, exc_value, exc_traceback = exc_info()
        return {
            'error': 'Internal Server Error',
            'backend_error': format_exception(exc_type, exc_value, exc_traceback)
        }, 500

@app.route('/<game_id>/reset')
def reset_turn(game_id):
    if game_id in GAMES:
        GAMES[game_id].do_action({
            'current_action': 'reset turn',
            'request_player': 'All',
        })
        return 'Reset turn on game {}'.format(game_id), 200
    else:
        return {'error': 'No game "{}"'.format(game_id)}, 404

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
    print('STARTING APP')
    GAMES = load_games()
    print('existing games: {}'.format(', '.join(GAMES.keys())))

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
