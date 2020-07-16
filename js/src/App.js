import React, { Component } from 'react';
import { HexGrid } from 'react-hexgrid';
import { Intro, RulesModal } from './Intro.js';
import './App.css';
import light_player from './images/light_player.png';
import dark_player from './images/dark_player.png';

import GameLayout from './GameLayout';
import SpellList from './SpellList';

// js TODOs:
// before next deploy
//  - update host
// bugs:
//  - cannot use enter to select button while setting up board
// nice to have:
//  - font size based on hex size
//  - room being moved renders on top
//  - make modal always narrower than app
//  - run backend on same heroku app
//  - allow tab + enter to select hexagons
//     - probably requires forking react-hexgrid
//     // document.querySelectorAll('svg .game .hexactive').forEach(x => x.tabIndex = 0);
//     // document.querySelectorAll('svg .game .hexdisabled').forEach(x => x.tabIndex = -1);
//  - convert some things to drag input:
//     - rearranging auras
//     - drop spells
//     - move player?
//     - placing rooms?
//  - set the drag image
//  - sounds when moves are done
// code quality:
//  - stop sending both click_spell and click_spell_idx
//  - make handlers into arrow fcts and remove bind calls
//  - be consistent about fct names - camel vs underscore, on vs handle
//  - consolidate spell descriptions between here and the backend
//  - replace setInterval with a web socket
//  - remove console.logs

// const HOST = 'https://piously-backend.herokuapp.com/';
const HOST = 'http://localhost:3000';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      // settings
      half_hex_size: 1.8, // half side length of hex
      auto_refresh_ms: 1000, // 1 sec
      max_auto_refresh: 60 * 10, // 10 min

      // set internally
      game_id: null,
      enabled: {null: true}, // player(s) that are enabled

      // received from backend
      game_over: false,
      hexes: [],
      spells: [],
      actions_remaining: null,
      current_action: null,
      current_player: null,
      reset_on: false,
      error: null,
      info: null,
    };
  }

  componentDidMount() {
    this.setState(JSON.parse(sessionStorage.getItem('state')));

    // listen for keybindings
    document.addEventListener("keydown", this.handleKeyDown.bind(this));

    // set up auto-refresh to regularly check for updates
    this.tick_cnt = 0;
    this.update_interval = setInterval(this.tick.bind(this), this.state.auto_refresh_ms);
  }

  componentWillUnmount() {
    clearInterval(this.update_interval);
  }

  tick() {
    if (this.tick_cnt === this.state.max_auto_refresh){
      console.log(`${this.tick_cnt} ticks, clearing interval, not fetching`);
      clearInterval(this.update_interval);
      this.update_interval = null;
      this.forceUpdate() // needed so that the wait text updates
      return;
    } else if (this.state.game_over) {
      console.log(`game over, ${this.tick_cnt} ticks, clearing interval, not fetching`);
      clearInterval(this.update_interval);
      this.update_interval = null;
      return;
    }

    this.tick_cnt++;

    // only need to check for updates when game_id is set
    // and it is not your turn
    if (this.state.game_id && !this.play_enabled()) {
      // console.log(`<tick> (${this.tick_cnt})`);
      this.fetchBoard({current_action: 'none'}, false);
    }
  }

  // function to send changes to current_action and get data from the backend
  async fetchBoard(data, user_initiated=true) {
    if (user_initiated) {
      this.tick_cnt = 0;
    }

    if (user_initiated && !this.play_enabled()) {
      console.log(`not fetching because ${this.state.current_player} is not enabled`)
      return;
    } else if (!this.state.game_id) {
      console.log(`not fetching because game_id is not set`)
      return;
    }

    // console.log('fetching')
    data.game_id = this.state.game_id
    try {
      const response = await fetch(`${HOST}/api/do_action`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      const response_data = await response.json();
      this.setState(response_data);

      if (response_data.backend_error) {
        console.log('backend error, clearing interval');
        console.log(response_data.backend_error);
        clearInterval(this.update_interval);
        this.update_interval = null;
      } else if (response.status !== 200){
        console.log('non-200 status, clearing interval', response.status);
        clearInterval(this.update_interval);
        this.update_interval = null;
      }

    } catch (e) {
      console.log('in fetch catch, clearing interval');
      this.setState({error: 'Internal Server Error :('})
      clearInterval(this.update_interval);
      this.update_interval = null;
    }
  };

  actions_on() {
    return this.state.current_action === 'none';
  }

  updateCurrentAction(action) {
    if (this.actions_on() || (this.state.reset_on && action === 'reset turn')) {
      this.setState({current_action: action});
      this.fetchBoard({current_action: action});
    }
  }

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
  handleCast() {
    this.updateCurrentAction('cast spell');
  }
  handleEndTurn() {
    this.updateCurrentAction('end turn');
  }
  handleResetTurn() {
    this.updateCurrentAction('reset turn');
  }
  handleEndGame() {
    this.fetchBoard({current_action: 'maybe end game'});
  }
  handleStartGame(
    event=null,
    light_enabled=this.state.enabled.Light,
    dark_enabled=this.state.enabled.Dark,
    game_id=this.state.game_id,
  ) {
    const state = {
      enabled: {
        'Light': light_enabled,
        'Dark': dark_enabled,
      },
      game_id: game_id,
    }
    sessionStorage.setItem('state', JSON.stringify(state));

    this.setState(
      state,
      () => {this.fetchBoard({current_action: 'start'}, false);} // false here to override enabled players
    );
  }
  handleNewGame() {
    sessionStorage.clear();
    window.location.href = '/';
  }
  handleKeyDown(e) {
    // console.log(`keypress (${e.key})`)
    // disable scrolling with arrow keys + space bar
    if (this.state.game_id && [32, 37, 38, 39, 40].indexOf(e.keyCode) > -1) {
        e.preventDefault();
    }

    if (this.state.game_over === true) {
      return;
    }

    // restart autorefresh if it is off
    if (!this.update_interval) {
      this.tick_cnt = 0;
      this.update_interval = setInterval(this.tick.bind(this), this.state.auto_refresh_ms);
    }

    if (e.key === '[') {
        // zoom out board (hexes get smaller)
        this.setState({half_hex_size: Math.max(0.5, this.state.half_hex_size - 0.1)});
    } else if (e.key === ']') {
        // zoom in board (hexes get bigger)
        this.setState({half_hex_size: Math.min(5, this.state.half_hex_size + 0.1)});
    } else if (this.actions_on() || (this.state.reset_on && e.key === 'r')) {
      if (e.key === '1') {
        this.handleBless()
      } else if (e.key === '2') {
        this.handleMove()
      } else if (e.key === '3') {
        this.handleDrop()
      } else if (e.key === '4') {
        this.handlePickUp()
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

  // calculate board boundaries from hexes
  grid_max_min() {
    // don't include temp hexes in grid size
    const filteredHexes = this.state.hexes.filter(h => h.room !== 'Temp');

    // horizontal offset of each hex relative to the (0, 0) hex depends only
    // on the q (y) coordinate
    const h_vals = filteredHexes.map(h => 3 * this.state.half_hex_size * h.y);
    const h_max = Math.max(...h_vals);
    const h_min = Math.min(...h_vals);

    // vertical offset of each hex relative to the (0, 0) hex depends on both
    // the q (y) and r (x) coordinates
    const H = this.state.half_hex_size * Math.sqrt(3); // half height of hex
    const v_vals = filteredHexes.map(h => (H * h.y) + (2 * H * h.x));
    const v_max = Math.max(...v_vals);
    const v_min = Math.min(...v_vals);

    return {
      v_min: v_min,
      v_max: v_max,
      h_min: h_min,
      h_max: h_max,
    }
  }

  // helpers to detemine with player(s) are enabled
  play_enabled() {
    return this.state.enabled[this.state.current_player];
  }
  view_only() {
    return !this.state.enabled.Dark && !this.state.enabled.Light;
  }
  both_enabled() {
    return this.state.enabled.Dark && this.state.enabled.Light;
  }

  // show img for enabled player if there is just one, otherwise track current player
  player_img() {
    const images = {
      Light: light_player,
      Dark: dark_player,
      null: light_player,
    }
    if (this.play_enabled() || this.view_only()) {
      return images[this.state.current_player]
    } else if (this.state.enabled.Dark) {
      return images['Dark'];
    } else {
      return images['Light'];
    }
  }

  handleModalClick(event) {
    var background = document.querySelector(".modal-background");
    if (event.target === background) {
      this.modal_off();
    }
  }
  modal_on() {
    let modal = document.querySelector(".modal-background");
    modal.style.display = "block";
  }
  modal_off() {
    let modal = document.querySelector(".modal-background");
    modal.style.display = "none";
  }

  get_wait_text() {
    if (this.state.game_over || this.view_only()) {
      return '';
    } else if (this.state.current_player) {
      if (this.play_enabled()){
        return '';
      } else if (this.update_interval) {
        return 'It is not your turn, please wait. Board will auto-refresh.';
      } else {
        return 'It is not your turn, please wait. Auto-refresh is off - press any key to restart auto-refresh.';
      }
    } else {
      return 'Loading, please wait';
    };
  };

  get_buttons() {
    const bstate = !this.actions_on();
    const rstate = !this.state.reset_on;
    if (this.state.game_id && !this.state.current_player) {
      return (
        <div className='buttons'>
          <button onClick={this.handleStartGame.bind(this)}>Start game</button>
        </div>
      );
    } else if (this.state.game_over) {
      return (
        <div className='buttons'>
          <button onClick={this.handleNewGame.bind(this)}>New game</button>
        </div>
      );
    } else {
      return (
        <><div className='buttons1'>
          <div className='button-label'>Action options</div>
          <button disabled={bstate} onClick={this.handleBless.bind(this)}>Bless (1)</button>
          <button disabled={bstate} onClick={this.handleMove.bind(this)}>Move (2)</button>
          <button disabled={bstate} onClick={this.handleDrop.bind(this)}>Drop (3)</button>
          <button disabled={bstate} onClick={this.handlePickUp.bind(this)}>Pick up (4)</button>
        </div>
        <div className='buttons2'>
          <div className='button-label'>Other options</div>
          <button disabled={bstate} onClick={this.handleCast.bind(this)}>Cast spell (w)</button>
          <button disabled={bstate} onClick={this.handleEndTurn.bind(this)}>End turn (e)</button>
          <button disabled={rstate} onClick={this.handleResetTurn.bind(this)}>Reset turn (r)</button>
        </div></>
      );
    };
  };

  render_game() {
    // Calculate board size
    const { v_min, v_max, h_min, h_max } = this.grid_max_min();
    const width = '100%';
    const height = '100%';
    const center_x = (h_max + h_min)/2;
    const center_y = (v_max + v_min)/2;
    const view_box='0 0 80 50';

    // Fill in text
    let instructions_text = this.state.info ? this.state.info.split("\n") : [];
    if (instructions_text.length > 0) { // bold first line of instructions
      instructions_text[0] = <b>{instructions_text[0]}</b>
    }
    const action_text =
      this.state.actions_remaining === null ?
        '' :
        this.state.actions_remaining === 1 ?
          '· 1 action' :
          `· ${this.state.actions_remaining} actions`;
    const status_text = (this.state.game_over || !this.state.current_player) ? null :
        <p>{this.state.current_player}'s Turn {action_text}</p>;

    let enabled_players = '';
    if (this.state.enabled.Dark && this.state.enabled.Light) {
      enabled_players = 'Playing as Dark and Light';
    } else if (this.state.enabled.Dark) {
      enabled_players = 'Playing as Dark';
    } else if (this.state.enabled.Light) {
      enabled_players = 'Playing as Light';
    } else {
      enabled_players = 'View only';
    }
    const game_and_player_text = this.state.game_id ?
      <p>Game [ <span className='mono'>{this.state.game_id}</span> ] · {enabled_players}</p> : null;

    return (
      <div className="App">
        <header className="App-header">
          <div className="App-preintro flex">
            <div className="header-left nav-btns">
              <button className="nav-btn modal" onClick={this.modal_on.bind(this)}>
                <p><em>review rules</em></p>
              </button>
              <button className="nav-btn back" onClick={this.handleNewGame.bind(this)} data-tooltip="(does not end game)">
                <p><em>back to form</em></p>
              </button>
              <button
                className="nav-btn end"
                disabled={!this.actions_on() || this.state.game_over}
                onClick={this.handleEndGame.bind(this)}
                data-tooltip="(ends game)"
              >
                <p><em>forefit game</em></p>
              </button>
            </div>
            <div className="header-center title">
              <div className="name-and-logo">
                <img className="App-logo" alt="logo" src={this.player_img()}/>
                <h1>piously</h1>
              </div>
              {status_text}
            </div>
            <div className="header-right game_and_player_text">{game_and_player_text}</div>
          </div>
          <div className="App-intro small-padding">
            <p className='error'>{this.get_wait_text()}</p>
            <p className='error'>{this.state.error}</p>
            {instructions_text.map((line, i) => <p key={i}>{line}</p>)}
          </div>
        </header>
        <div className="App-body">
          <div className="row">
            <div className='column buttons-and-board'>
              {this.get_buttons()}
              <div className='board'>
                <HexGrid width={width} height={height} viewBox={view_box}>
                  <GameLayout
                    onAction={this.fetchBoard.bind(this)}
                    current_action={this.state.current_action}
                    hexes={this.state.hexes}
                    hex_size={this.state.half_hex_size*2}
                    center_x={center_x}
                    center_y={center_y}
                  />
                </HexGrid>
              </div>
            </div>
            <div className="column spells">
              <SpellList
                onAction={this.fetchBoard.bind(this)}
                spells={this.state.spells}
                current_action={this.state.current_action}
                current_player={this.state.current_player}
              />
            </div>
          </div>
        </div>
        <RulesModal
          onClick={this.handleModalClick.bind(this)}
          onDisable={this.modal_off.bind(this)}
        />
      </div>
    );
  }

  render() {
    if (this.state.game_id){
      return this.render_game()
    }
    return <Intro
      current_player={this.state.current_player}
      onStart={this.handleStartGame.bind(this)}
      onModalClick={this.handleModalClick.bind(this)}
      onModalDisable={this.modal_off.bind(this)}
      onModalEnable={this.modal_on.bind(this)}
    />
  }
}

export default App;
