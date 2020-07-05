import os
import json
from flask import Flask, url_for, render_template, request
from markupsafe import escape

from backend.game import Game
from backend.errors import InvalidMove

# run with: python -m heroku.app

app = Flask(__name__)
GAMES = {}
MAX_GAMES = 2

def get_game(id):
    if id in GAMES:
        return GAMES[id]

@app.route("/")
def index():
    print(url_for('play_game')) # , username='John Doe'))
    # return "Hello from piously!\nTo play visit /play"
    return render_template("index.html", name="Ela")

@app.route("/play")
def play_game():
    return "active games: {}".format(', '.join(GAMES.keys()))

@app.route('/about')
def about():
    return 'The about page'

@app.route('/play/<game_id>')
def show_board(game_id):
    # TODO: escape() game_id

    if game_id in GAMES:
        return str(GAMES[game_id])
    else:
        if len(GAMES) >= MAX_GAMES:
            return 'Too many games: Please wait for another game to complete'

        new_board = Game("Dark")

        # TODO: don't hard code placing the players
        light_player = new_board.current_board.players['Light']
        dark_player = new_board.current_board.players['Dark']
        hex1 = new_board.current_board.rooms[0].hexes[0]
        hex2 = new_board.current_board.rooms[0].hexes[1]
        new_board.current_board.move_object(light_player, to_hex=hex1)
        new_board.current_board.move_object(dark_player, to_hex=hex2)
        new_board.sync_boards()

        GAMES[game_id] = new_board
        print('Created new game! {}'.format(new_board))
        return str(new_board)

@app.route('/hexes/<game_id>')
def get_hexes(game_id):
    # TODO: escape() game_id

    if game_id in GAMES:
        game = GAMES[game_id]
        hexes = game.current_board.return_hex_data()
        print('hexes:', hexes)
        return json.dumps(hexes)
    else:
        print("ERROR: invalid game_id {}".format(game_id))
        return json.dumps([])

@app.route('/play/<game_id>/end')
def end_game(game_id):
    if game_id in GAMES:
        GAMES.pop(game_id)
        return 'Ended game {}'.format(game_id)
    return 'No game {}'.format(game_id)

@app.route('/do_action', methods=['POST'])
def do_action():
    data = request.json
    game = get_game(data['game_id'])

    if game:
        if data['current_action'] == 'end game':
            new_state = game.do_action(data)
            print('ending game')
            GAMES.pop(data['game_id'])
            # new_state = {'game_over': True}
        else:
            new_state = game.do_action(data)
    else:
        new_state = {}
        # TODO: error
    return new_state

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
