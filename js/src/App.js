import React, { Component } from 'react';
import { HexGrid } from 'react-hexgrid';
import './App.css';
import light_player from './player.png';
import dark_player from './dark_player.png';

import GameLayout from './GameLayout';
import SpellList from './SpellList';

// TODO: js improvements
// critical:
//  - disable reset button during inital board setup
//  - error handling based on response code for both fetches
// nice to have:
//  - make spells prettier
//  - convert some things to drag input:
//     - rearranging auras
//     - drop spells
//     - move player???
//     - placing rooms???
//  - set the drag image
// code quality:
//  - consoldate color code (currently in css, GameLayout, and SpellList)
//  - remove console.logs
//  - clean up action_buttons_on
//     - maybe rename it buttons_enabled
//     - is it the same as action === 'none'?
//  - remove unused code (here + in GameLayout)
//     - commented out code
//     - drag+drop related things
//     - pattern / fill related things

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hexes: [],
      players: [],
      spells: [],

      current_action: null,
      current_spell: null,
      current_player: null,
      actions: null,
      game_id: 'a',
      game_over: false,
      action_buttons_on: true,

      error: null,
      info: null
    };
  }

  componentDidMount() {
    console.log('mounted!');

    // allow keybindings
    document.addEventListener("keydown", this.handleKeyDown.bind(this))

    this.fetchBoard({current_action: 'start'});
  }

  updateCurrentAction(action) {
    if (this.state.action_buttons_on || action === 'reset turn') {
      this.setState({current_action: action});
      this.fetchBoard({current_action: action});
    }
  }

  async fetchBoard(data) {
    data.game_id = this.state.game_id
    try {
      const response = await fetch('http://localhost:3000/do_action', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      const response_data = await response.json();

      console.log(response_data);
      this.setState(response_data);
    } catch (e) {
        console.log(e);
        // this.setState({...this.state, isFetching: false});
    }
  };

  handleBless() {
    this.updateCurrentAction('bless');
  }
  handleMove() {
    this.updateCurrentAction('move');
  }
  handleDrop() {
    this.updateCurrentAction('drop');
  }
  handlePickUp() {
    this.updateCurrentAction('pick up');
  }
  handleEndGame() {
    this.updateCurrentAction('maybe end game');
  }
  handleCast() {
    this.updateCurrentAction('cast spell');
  }
  handleEndTurn() {
    this.updateCurrentAction('end turn');
  }
  handleResetTurn() {
    this.updateCurrentAction('reset turn');
  }
  handleNewGame() {
    this.updateCurrentAction('start');
  }
  handleKeyDown(e) {
    // disable scrolling with arrow keys / space bar
    if([32, 37, 38, 39, 40].indexOf(e.keyCode) > -1) {
        e.preventDefault();
    }

    if (this.state.game_over === true) {
      return
    } else if (this.state.action_buttons_on || e.key === 'r') {
      if (e.key === '1') {
        this.handleBless()
      } else if (e.key === '2') {
        this.handleMove()
      } else if (e.key === '3') {
        this.handleDrop()
      } else if (e.key === '4') {
        this.handlePickUp()
      } else if (e.key === 'Q') {
        this.handleEndGame()
      } else if (e.key === 'w') {
        this.handleCast()
      } else if (e.key === 'e') {
        this.handleEndTurn()
      } else if (e.key === 'r') {
        this.handleResetTurn()
      }
    } else {
      const data = {
        choice_idx: e.key,
        current_keypress: e.key,
        current_action: this.state.current_action,
      }
      this.fetchBoard(data);
    }
  };

  // RENDER
  actionText = () => (
    this.state.actions === null ?
      '' :
      this.state.actions === 1 ?
        '· 1 action' :
        `· ${this.state.actions} actions`
  );

  render() {
    const info_text = this.state.info ? this.state.info.split("\n") : [];

    const bstate = !this.state.action_buttons_on;
    const isOver = this.state.game_over === true;

    let statusText;
    let buttons;
    if (isOver) {
      statusText = <p></p>;
      buttons =
        <div className='buttons'>
          <button onClick={this.handleNewGame.bind(this)}>Start new game</button>
        </div>;
    } else {
      statusText =
        <p>
          {this.state.current_player}'s Turn {this.actionText()}
        </p>;
      buttons =
        <div className='buttons'>
          <button disabled={bstate} onClick={this.handleBless.bind(this)}>Bless (1)</button>
          <button disabled={bstate} onClick={this.handleMove.bind(this)}>Move (2)</button>
          <button disabled={bstate} onClick={this.handleDrop.bind(this)}>Drop (3)</button>
          <button disabled={bstate} onClick={this.handlePickUp.bind(this)}>Pick up (4)</button>
          <button disabled={bstate} onClick={this.handleEndGame.bind(this)}>Quit game (shift-q)</button>
          <button disabled={bstate} onClick={this.handleCast.bind(this)}>Cast spell (w)</button>
          <button disabled={bstate} onClick={this.handleEndTurn.bind(this)}>End turn (e)</button>
          <button onClick={this.handleResetTurn.bind(this)}>Reset turn (r)</button>
        </div>
    };

    return (
      <div className="App">
        <header className="App-header">
          <img className="App-logo" alt="logo"
            src={this.state.current_player === 'Dark' ? dark_player : light_player}/>
          <h1>piously</h1>
          {statusText}
          <div className="App-intro">
            <p className='error'>{this.state.error}</p>
            {info_text.map((line, i) => <p key={i}>{line}</p>)}
          </div>
        </header>
        <div className="App-body">
          <div className="row">
            <div className='column buttons-and-board'>
              {buttons}
              <HexGrid width={800} height={500} viewBox="0 0 80 50">
                <GameLayout
                  onAction={this.fetchBoard.bind(this)}
                  hexes={this.state.hexes}
                  current_action={this.state.current_action}
                />
              </HexGrid>
            </div>
            <div className="column spells">
              <SpellList
                onAction={this.fetchBoard.bind(this)}
                spells={this.state.spells}
                current_action={this.state.current_action}
              />
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default App;
