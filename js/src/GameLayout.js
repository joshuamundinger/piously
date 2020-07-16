import React, { Component } from 'react';
import { Layout, Hexagon, Text } from 'react-hexgrid';
import './GameLayout.css';

class GameLayout extends Component {
  constructor(props) {
    super(props);
    this.state = {current_hex: null};
  }

  onClick(event, source) {
    const hex = source.state.hex
    // console.log(`click ${hex.q} ${hex.r} ${hex.s}`)
    const data = {
      current_action: this.props.current_action,
      click_x: hex.r,
      click_y: hex.q,
    }
    switch(this.props.current_action) {
      case 'move':
      case 'drop':
      case 'pick up':
      case 'cast spell':
      case 'place players':
        this.props.onAction(data)
        break;
      default:
        // do nothing
    }
  }

  onMouseEnter(event, source) {
    const hex = source.state.hex
    this.setState({ current_hex: hex });
  }

  onMouseLeave(event, source) {
    this.setState({ current_hex: null });
  }

  // map from the provided props (x, y, object_type, etc) to the props
  // needed for rendering (q, r, s, object graphics, etc)
  processHexData() {
    const { hexes, hex_size } = this.props;
    const player_pts = ".5 0, 0 .75, .65 1, 1 .7, .5 0, .65 1";
    const formattedHexData = hexes.map(h => {
      // aura graphic
      const aura = (h.aura_color ? <circle className={`aura ${h.aura_color}`} r={hex_size*.7}/> : null);

      // object graphic
      let object = null;
      if (h.obj_type === 'player') {
        object = <>
          <defs>
            <radialGradient id="Light_player_grad" cx="50%" cy="50%" r="50%" fx="50%" fy="0%">
              <stop offset="30%" style={{'stopOpacity':0}} />
              <stop offset="100%" style={{'stopColor':'black', 'stopOpacity':0.3}} />
            </radialGradient>
            <radialGradient id="Dark_player_grad" cx="50%" cy="50%" r="50%" fx="50%" fy="0%">
              <stop offset="30%" style={{'stopColor':'white', 'stopOpacity':0.3}} />
              <stop offset="100%" style={{'stopOpacity':0}} />
            </radialGradient>
          </defs>
          <polygon
            className={`player ${h.obj_color}`}
            points={player_pts}
            style={{'strokeWidth':hex_size*0.01}}
            transform={`scale(${hex_size}) translate(-.5 -.6)`}
          />
          <polygon
            className="player-grad"
            points={player_pts}
            style={{fill:`url(#${h.obj_color}_player_grad)`, 'strokeWidth':0}}
            transform={`scale(${hex_size}) translate(-.5 -.6)`}
          />
        </>
      } else if (h.obj_type === 'artwork') {
        object = <>
          <defs>
            <radialGradient id="art_grad" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
              <stop offset="0%" style={{'stopOpacity':0}} />
              <stop offset="100%" style={{'stopColor':'black', 'stopOpacity':0.3}} />
            </radialGradient>
          </defs>
          <circle
            className={`artwork ${h.obj_color.charAt(0)}`}
            r={hex_size*.4}
          />
          <circle
            className="artwork-grad"
            r={hex_size*.4}
            fill="url(#art_grad)"
          />
          <Text>{h.obj_color.charAt(0)}</Text>
        </>
      }

      return {
        q: h.y,
        r: h.x,
        s: -h.x-h.y,
        text: h.room,
        active: h.active ? 'active' : 'disabled',
        hex_color: h.room_color,
        aura: aura,
        object: object,
      }
    });

    return formattedHexData;
  }

  render() {
    const { hexes, hex_size, center_x, center_y } = this.props;

    const cur_hex = this.state.current_hex;
    let hover_hex = null;
    if (cur_hex) {
      hover_hex = hexes.find(h => cur_hex.r === h.x && cur_hex.q === h.y)
    }
    let hover_label = '';
    if (hover_hex) {
      hover_label = `(${hover_hex.x}, ${hover_hex.y}): ${hover_hex.room} room`;
      if (hover_hex.aura_color) {
        hover_label = hover_label.concat(`, ${hover_hex.aura_color} aura`);
      }
      if (hover_hex.obj_type === 'player') {
        hover_label = hover_label.concat(`, ${hover_hex.obj_color} player`);
      } else if (hover_hex.obj_type === 'artwork') {
        hover_label = hover_label.concat(`, ${hover_hex.obj_color} artwork`);
      }
    }

    return (
      <>
        <Layout className="game" spacing={1.02} size={{x: hex_size, y: hex_size}} origin={{x: -center_x, y: -center_y}}>
          {
            this.processHexData().map((hex, i) => (
              <Hexagon
                key={i}
                q={hex.q}
                r={hex.r}
                s={hex.s}
                className={`${hex.hex_color} hex${hex.active}`}
                data={hex}
                onClick={(e, h) => this.onClick(e, h)}
                onMouseEnter={(e, h) => this.onMouseEnter(e, h)}
                onMouseLeave={(e, h) => this.onMouseLeave(e, h)}
                tabindex={hex.tidx}
              >
                <Text>{hex.hex_color}</Text>
                {hex.aura}
                {hex.object}
              </Hexagon>
            ))
          }
        </Layout>
        <text className="hoverText background">{hover_label}</text>
        <text className="hoverText">{hover_label}</text>
      </>
    );
  }
}

export default GameLayout;
