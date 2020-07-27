import React, { Component } from 'react';
import light_player from './images/light_player.png';
import board_img from './images/example_board.png';

class Rules extends Component {
  render () {
    return (
      <>
      <p><em>rules of piously</em> ··· Your goal is to link all seven
      rooms with your auras. On your turn you may take up to three
      actions and cast each of your spells at most once, in any order.

      You start with no spells, but at the end of each turn you can claim
      an unclaimed spell from your current room.
      </p>

      <p><b>Rooms</b></p>
      <ul>
        <li>There are seven main rooms, each of which has four hexes.
        Hexes within a room are all the same color. </li>
        <li>There is a special one-hex room called the Shovel, which can be
        added to and moved around the board once a player gets the Shovel spell. </li>
      </ul>

      <p><b>Auras</b></p>
      <ul>
        <li>Adjacent auras form a linked region, and linking all seven rooms is
        how you win. They are shown as light (white) and dark (black) circles.</li>
        <li>You can add an aura to a hex using a Bless action or by casting a spell.
        Each hex can have at most one aura. Auras are not objects.</li>
      </ul>

      <p><b>Actions</b></p>
      <ul>
        <li>[ Move ] ··· Move your player object to an adjacent unoccupied hex.</li>
        <li>[ Bless ] ··· Place an aura on your current hex. If your opponent's
        aura is already there, this requires two actions.</li>
        <li>[ Drop ] ··· Place an artwork object that you own on an adjacent unoccupied hex.</li>
        <li>[ Pick up ] ··· Remove an adjacent artwork object that you own.</li>
      </ul>

      <p><b>Spells</b></p>
      <ul>
        <li>There are fourteen spells: one artwork and one bewitchment for
        each of the seven rooms.</li>
        <ul>
          <li>Artworks are often more powerful, but in order to be used, the
          artwork object must be on the player's aura. Artworks affect the region
          connected by auras to the artwork object.</li>
          <li> Bewitchments are simple spells that affect your player object
          or its surroundings. They do not have associated artwork objects.</li>
        </ul>
        <li>At the end of your turn, if you don’t have a spell from
        your current room, you may claim one of them, which will give your
        opponent the other spell.</li>
      </ul>

      <p><b>Objects</b></p>
      <ul>
        <li>
          There are nine objects: one artwork object for each of the seven
          artwork spells and two player objects.
          Two objects may never share the same hex. Many of the spells allow
          you to act on objects and move them around the board.
        </li>
      </ul></>
    )
  }
}

class RulesModal extends Component {
  render () {
    return (
      <div className="modal modal-background" onClick={this.props.onClick}>
        <div className="modal modal-content">
          <button className="modal modal-close-btn" onClick={this.props.onDisable}>x</button>
          <div className="text-left">
            <Rules />
          </div>
        </div>
      </div>
    )
  }
}

class Intro extends Component {
  constructor(props) {
    super(props);
    this.state = {game_id: null, error: null};
  }

  handleInputChange(event) {
    const target = event.target;
    const name = target.name;

    if (name === 'game_id') {
      const value = target.value;
      if (value.match(/^[0-9a-zA-Z]{1,16}$/)) {
        this.setState({
          game_id: value,
          error: '',
        });
      } else if (!value.match(/^[0-9a-zA-Z]*$/)) {
        this.setState({
          game_id: value,
          error: 'Error: Game ID can only include letters and numbers'
        });
      } else if (value === '') {
        this.setState({
          game_id: value,
          error: 'Error: Game ID is required'
        });
      } else {
        this.setState({
          game_id: value,
          error: 'Error: Game ID must be 1-16 characters and can only include letters and numbers'
        });
      }
    } else {
      // one of the faction checkboxes
      const value = target.checked;
      this.setState({
        [name]: value
      });
    }
  }

  handleClick(e) {
    if (!this.state || !this.state.game_id) {
      this.setState({
        error: 'Error: Game ID is required'
      });
      e.preventDefault();
      return;
    } else if (!this.state.game_id.match(/^[0-9a-zA-Z]{1,16}$/)) {
      this.setState({
        error: 'Error: Game ID must be 1-16 characters and can only include letters and numbers'
      });
      e.preventDefault();
      return;
    }

    this.props.onStart(
      null,
      this.state.Light,
      this.state.Dark,
      this.state.game_id,
    );
  };

  render() {
    const text = <>
      <p><span style={{fontVariant:'small-caps', fontSize:'14px'}}>
        designed by jonah ostroff ···
        implemented by rachel diamond and josh mundinger
      </span></p>
      <div className="text-left">
        <p>
          <em>introduction</em> ··· You are the high priests of Light and Darkness,
          and your patron deities have been at war for ages. The fate of their
          struggle rests with the seven goddesses. You’ve come to the Temple of
          the Seven to seek their gifts and exert your influence, but beware:
          the Seven do not take sides prematurely. Whenever you are gifted with
          a spell, your opponent will recieve a spell as well. Wield the spells
          you recieve carefully to gain control of the temple.

          If you form a connected region of auras that includes all seven rooms
          of the temple, you triumph!
        </p>

        <button className="rules-modal" onClick={this.props.onModalEnable}>
          <em>see full rules</em>
        </button>

        <img className="Board-img" alt="board" src={board_img}/>
        <p><em>
          how to use this website
        </em></p>
        <ul>
          <li><b>Choose your faction:</b> Dark will arrange the rooms of the temple and Light will
          decide who goes first. Check off the corresponding boxes -- select both boxes only
          if people of opposite factions will be using the same computer.</li>
          <li><b>Choose a game ID:</b> Any number of computers can connect to
          the same game by entering the same game ID.</li>
        </ul>

        <form>
          <label htmlFor="dark_checkbox">Dark:</label>
          <input type="checkbox" id="dark_checkbox" name="Dark" value="true"
            onChange={this.handleInputChange.bind(this)}/>
          <br />

          <label htmlFor="light_checkbox">Light:</label>
          <input type="checkbox" id="light_checkbox" name="Light" value="true"
            onChange={this.handleInputChange.bind(this)}/>
          <br />

          <label htmlFor="game_id">Game ID: </label>
          <input
            type="text"
            id="game_id"
            name="game_id"
            maxLength="16"
            autoComplete="off"
            required="required"
            size="16"
            onChange={this.handleInputChange.bind(this)}
          /><label> (up to 16 alphanumeric characters)</label>
          <div className="error"><p>{this.state.error}</p></div>

          <button onClick={this.handleClick.bind(this)}>Start Game</button>
        </form>
        <RulesModal
          onClick={this.props.onModalClick}
          onDisable={this.props.onModalDisable}
        />
      </div>
    </>

    return (
      <div className="App">
        <header className="App-header">
          <div className="App-preintro">
            <img className="App-logo" alt="logo" src={light_player}/>
            <h1>piously</h1>
          </div>
          <div className="App-intro">
            {text}
          </div>
        </header>
      </div>
    );
  }
}

export { Intro, RulesModal };
