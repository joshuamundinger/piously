import React, { Component } from 'react';
import './GameLayout.css';

class SpellList extends Component {
  constructor(props) {
    super(props);
    this.state = {current_spell: null};
  }

  onClick(event) {
    // console.log(`spell before click was ${this.state.current_spell}`)
    const index = parseInt(event.currentTarget.getAttribute('idx'));
    const name = event.currentTarget.getAttribute('name');
    const unplaced_art = event.currentTarget.getAttribute('unplaced_art');
    const state = event.currentTarget.className;
    console.log(`clicked ${name} (i=${index}) ${state}`)
    this.setState({ current_spell: name });

    if (state === 'active') {
      let data = {
        current_action: 'cast spell',
        click_spell: name,
        click_spell_idx: index,
      };

      if (this.props.current_action === 'none' && unplaced_art) {
        data.current_action = 'drop';
      } else if (this.props.current_action === 'cast spell') {
        // do nothing
      } else if (this.props.current_action === 'none') {
        // do nothing
      } else {
        return;
      };

      console.log(data)
      this.props.onAction(data);
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

  render() {
    const spells = this.props.spells.map(s => ({
      name: s.name,
      description: s.description,
      active: s.active ? 'active' : 'disabled',
      tapped: s.tapped ? 'X' : '',
      unplaced_art: s.artwork ? 'X' : '',
      faction: s.faction,
      art_color: s.name[0],
    }));

    return (
      <table className="spellTable">
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
          <tr
            key={i}
            className={spell.active}
            name={spell.name}
            unplaced_art={spell.unplaced_art}
            idx={i}
            onClick={this.onClick.bind(this)
          }>
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
