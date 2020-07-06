import React, { Component } from 'react';
// import { Layout, Hexagon, Text, HexUtils } from 'react-hexgrid';
import './GameLayout.css';

// import drag_img from './blank_hex.png';

class SpellList extends Component {
  constructor(props) {
    super(props);
    this.state = {current_spell: null};
  }

  onClick(event) {
    console.log(`spell before click was ${this.state.current_spell}`)
    const spell_index = parseInt(event.currentTarget.getAttribute('idx'));
    const spell_name = event.currentTarget.getAttribute('name');
    console.log(`clicked ${spell_name} (i=${spell_index})`)
    this.setState({ current_spell: spell_name });
    if (this.props.current_action === 'cast spell') {
      const data = {
        current_action: 'cast spell',
        click_spell: spell_name,
        click_spell_idx: spell_index,
      }
      this.props.onAction(data)
    };
  }

  onMouseEnter(event, source) {
    const hex = source.state.hex
    // console.log(`enter ${hex.q} ${hex.r} ${hex.s}`)
    this.setState({ current_hex: hex });
  }

  onMouseLeave(event, source) {
    // const hex = source.state.hex
    // console.log(`leave ${hex.q} ${hex.r} ${hex.s}`)
    this.setState({ current_hex: null });
  }

  color_str(name) {
    switch(name) {
      case 'Dark':
        return '#333'
      case 'Light':
        return '#eee'
      case 'P':
        return '#faa7f3'
      default:
        return 'red'
    }
  }

  // <div className={`spell ${spell.art_color}`}>
  //   <h3>{spell.name}</h3>
  //   <p>{spell.description}</p>
  //   <p>Tapped: {spell.tapped}</p>
  //   <p>Unplaced artwork: {spell.unplaced_art}</p>
  //   <p>Faction: {spell.faction}</p>
  // </div>

  // TODO: sort out using color, consolidate with GameLayout
  render() {
    const spells = this.props.spells.map(s => ({
      name: s.name,
      description: s.description,
      tapped: s.tapped.toString(),
      unplaced_art: s.artwork.toString(),
      faction: s.faction,
      faction_color: this.color_str(s.faction),
      art_color: s.name[0],
    }));

    return (
      <table class="spellTable">
      <caption>Spells</caption>
      <thead>
        <tr>
          <th>name</th>
          <th>description</th>
          <th>tapped</th>
          <th>unplaced artwork</th>
          <th>faction</th>
        </tr>
      </thead>
      <tbody>
        {spells.map((spell, i) => (
          <tr key={i} name={spell.name} idx={i} onClick={this.onClick.bind(this)}>
            <td>{spell.name}</td>
            <td>{spell.description}</td>
            <td>{spell.tapped}</td>
            <td>{spell.unplaced_art}</td>
            <td>{spell.faction}</td>
          </tr>
        ))}
      </tbody>
    </table>
    );
  }
}

export default SpellList;
