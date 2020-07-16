import React, { Component } from 'react';
import './SpellList.css';

import purify from './images/purify.png';
import priestess from './images/priestess.png';
import imprint from './images/imprint.png';
import imposter from './images/imposter.png';
import opportunist from './images/opportunist.png';
import overwork from './images/overwork.png';
import usurper from './images/usurper.png';
import upset from './images/upset.png';
import stonemason from './images/stonemason.png';
import shovel from './images/shovel.png';
import locksmith from './images/locksmith.png';
import leap from './images/leap.png';
import yeoman from './images/yeoman.png';
import yoke from './images/yoke.png';
import none from './images/none.png';

class SpellDetail extends React.Component {
  render() {
    let info = null;
    switch (this.props.spell) {
      case 'Priestess':
        info = <><img className="spell-img" alt="priestess" src={priestess} />
        <p><em>priestess</em> · Grow linked region by one aura.</p></>;
        break;
      case 'Purify':
        info = <><img className="spell-img" alt="purify" src={purify} />
        <p><em>purify</em> · Bless underneath one adjacent object.</p></>;
        break;
      case 'Imposter':
        info = <><img className="spell-img" alt="imposter" src={imposter} />
        <p><em>imposter</em> · Copy all auras from the Imposter's room to
        another linked room. This includes copying auraless state.</p></>;
        break;
      case 'Imprint':
        info = <><img className="spell-img" alt="imprint" src={imprint} />
        <p><em>imprint</em> · Copy auras under and around your opponent to the
        hexes under and around yourself, in the corresponding orientations.
        This does not copy auraless state.</p></>;
        break;
      case 'Opportunist':
        info = <><img className="spell-img" alt="opportunist" src={opportunist} />
        <p><em>opportunist</em> · Cast spell from one linked room a
        second time this turn.</p></>;
        break;
      case 'Overwork':
        info = <><img className="spell-img" alt="overwork" src={overwork} />
        <p><em>overwork</em> · Gain one action for each adjacent object.</p></>;
        break;
      case 'Usurper':
        info = <><img className="spell-img" alt="usurper" src={usurper} />
        <p><em>usurper</em> · Turn two of your linked auras into your opponent's auras.
        If you do, grow linked region by two auras (one at a time).</p></>;
        break;
      case 'Upset':
        info = <><img className="spell-img" alt="upset" src={upset} />
        <p><em>upset</em> · Rearrange auras under and around yourself.</p></>;
        break;
      case 'Stonemason':
        info = <><img className="spell-img" alt="stonemason" src={stonemason} />
        <p><em>stonemason</em> · Move one linked room anywhere (connectivity
        rules apply).</p></>;
        break;
      case 'Shovel':
        info = <><img className="spell-img" alt="shovel" src={shovel} />
        <p><em>shovel</em> · Place the shovel room on the board adjacent to
        yourself. Or, if you're on it, move it anywhere.</p></>;
        break;
      case 'Locksmith':
        info = <><img className="spell-img" alt="locksmith" src={locksmith} />
        <p><em>locksmith</em> · Move one linked object anywhere.</p></>;
        break;
      case 'Leap':
        info = <><img className="spell-img" alt="leap" src={leap} />
        <p><em>leap</em> · Swap places with an object in your row. You may Leap
        over objects, but not gaps in the temple.</p></>;
        break;
      case 'Yeoman':
        info = <><img className="spell-img" alt="yeoman" src={yeoman} />
        <p><em>yeoman</em> · Rearrange objects within all linked rooms.
        Each object must stay in its room.</p></>;
        break;
      case 'Yoke':
        info = <><img className="spell-img" alt="yoke" src={yoke} />
        <p><em>yoke</em> · Move yourself and any other object one hex in
        the same direction.</p></>;
        break;
      default:
        info = <><img className="spell-img" alt="none" src={none} />
        <span className='text-center'>
        Hover over a spell to see its description.</span></>;
    }
    return <div className="spell-detail">{info}</div>;
  }
}

class SpellList extends Component {
  constructor(props) {
    super(props);
    this.state = {current_spell: null, hover_spell: null};
  }

  onClick(event) {
    const index = parseInt(event.currentTarget.getAttribute('idx'));
    // const tidx = parseInt(event.currentTarget.getAttribute('tabIndex'));
    const name = event.currentTarget.getAttribute('name');
    const art_unplaced = event.currentTarget.getAttribute('art_unplaced');
    const classes = event.currentTarget.className.split(' ');
    // console.log(`clicked ${name} (i=${index}) (${classes}) art(${art_unplaced}) tidx(${tidx})`)
    this.setState({ current_spell: name });

    if (classes[0] === 'active') {
      let data = {
        current_action: 'cast spell',
        click_spell: name,
        click_spell_idx: index,
      };

      if (this.props.current_action === 'none' && art_unplaced === 'true') {
        data.current_action = 'drop';
      } else if (this.props.current_action === 'cast spell') {
        // do nothing
      } else if (this.props.current_action === 'none') {
        // do nothing
      } else {
        return;
      };

      this.props.onAction(data);
    };
  }

  onMouseEnter(event, source) {
    const name = event.currentTarget.getAttribute('name');
    this.setState({ hover_spell: name });
  }

  onMouseLeave(event, source) {
    this.setState({ hover_spell: null });
  }

  handleKeyDown(e) {
    if (e.key === 'Enter') {
        this.onClick(e);
    }
  };

  spellHashToRow(spell) {
    return (
      <tr
        key={spell.idx}
        className={`${spell.active} ${spell.art_color} ${spell.current_player}`}
        name={spell.name}
        art_unplaced={spell.art_unplaced}
        idx={spell.idx}
        onClick={this.onClick.bind(this)}
        onMouseEnter={(e, h) => this.onMouseEnter(e, h)}
        onMouseLeave={(e, h) => this.onMouseLeave(e, h)}
        onKeyDown={this.handleKeyDown.bind(this)}
        tabIndex={spell.tidx}
      >
        <td>{spell.name}</td>
        <td>{spell.tapped}</td>
        <td>{spell.art_status}</td>
        <td>{spell.faction}</td>
      </tr>
    )
  }

  render() {
    let spells = this.props.spells.map((s, i) => ({
      name: s.name.trim(),
      description: s.description,
      active: s.active ? 'active' : 'disabled',
      current_player: s.faction === this.props.current_player ? 'activePlayer' : '',
      idx: i,
      tidx: s.active ? '0' : '-1',
      tapped: s.tapped ? 'X' : '',
      art_status: s.has_artwork ? (s.unplaced_artwork ? 'unplaced' : 'placed') : '-',
      art_unplaced: s.unplaced_artwork ? 'true' : 'false',
      art_color: s.name[0],
      faction: s.faction,
    }));

    return (
      <>
      <table className="spellTable" rules="groups">
      <thead>
        <tr>
          <th>Spell</th>
          <th>Cast</th>
          <th>Artwork</th>
          <th>Faction</th>
        </tr>
      </thead>
      <tbody>
        {spells.filter(s => s.faction === 'Dark').map(s => this.spellHashToRow(s))}
      </tbody>
      <tbody>
        {spells.filter(s => s.faction === null).map(s => this.spellHashToRow(s))}
      </tbody>
      <tbody>
        {spells.filter(s => s.faction === 'Light').map(s => this.spellHashToRow(s))}
      </tbody>
    </table>
    <SpellDetail spell={this.state.hover_spell}/>
    </>
    );
  }
}

export default SpellList;
