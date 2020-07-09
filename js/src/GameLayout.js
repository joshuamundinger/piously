import React, { Component } from 'react';
import { Layout, Hexagon, Text, HexUtils } from 'react-hexgrid';
import './GameLayout.css';

import drag_img from './blank_hex.png';

class GameLayout extends Component {
  constructor(props) {
    super(props);
    this.state = {current_hex: null};
  }

  // // onDrop you can read information of the hexagon that initiated the drag
  // onDrop(event, source, targetProps) {
  //   // log drop location
  //   const hex = source.state.hex
  //   console.log(`L drop ${hex.q} ${hex.r} ${hex.s}`)
  //
  //   // const { hexagons } = this.state;
  //   // const hexas = hexagons.map(hex => {
  //   //   // When hexagon is dropped on this hexagon, copy it's image and text
  //   //   if (HexUtils.equals(source.state.hex, hex)) {
  //   //     hex.image = targetProps.data.image;
  //   //     hex.text = targetProps.data.text;
  //   //   }
  //   //   return hex;
  //   // });
  //   // this.setState({ hexagons: hexas });
  // }

  onClick(event, source) {
    const hex = source.state.hex
    console.log(`click ${hex.q} ${hex.r} ${hex.s}`)

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
    // console.log(hex);
    // console.log(`enter ${hex.q} ${hex.r} ${hex.s}`)
    this.setState({ current_hex: hex });
  }

  onMouseLeave(event, source) {
    // const hex = source.state.hex
    // console.log(`leave ${hex.q} ${hex.r} ${hex.s}`)
    this.setState({ current_hex: null });
  }

  // onDragStart(event, source) {
  //   var img = new Image();
  //   img.src = drag_img;
  //   // note: need to make setDragImage the right size or remove it
  //   // event.dataTransfer.setDragImage(img, img.width/2, img.height/2)
  //
  //   const hex = source.state.hex
  //   console.log(`L drag start ${hex.q} ${hex.r} ${hex.s}`)
  //   // If this tile is empty, let's disallow drag
  //   if (!source.props.data.text) {
  //     event.preventDefault();
  //   }
  // }
  //
  // // Decide here if you want to allow drop to this node
  // onDragOver(event, source) {
  //   // Find blocked hexagons by their 'blocked' attribute
  //   // const blockedHexas = this.state.hexagons.filter(h => h.blocked);
  //   // // Find if this hexagon is listed in blocked ones
  //   // const blocked = blockedHexas.find(blockedHex => {
  //   //   return HexUtils.equals(source.state.hex, blockedHex);
  //   // });
  //   //
  //   // const { text } = source.props.data;
  //   // // Allow drop, if not blocked and there's no content already
  //   // if (!blocked && !text) {
  //   //   // Call preventDefault if you want to allow drop
  //   //   event.preventDefault();
  //   // }
  // }
  //
  // // onDragEnd you can do some logic, e.g. to clean up hexagon if drop was success
  // onDragEnd(event, source, success) {
  //   const hex = source.state.hex
  //   console.log(`L drag end ${hex.q} ${hex.r} ${hex.s}`)
  //   if (!success) {
  //     return;
  //   }
  //   // Drop the whole hex from array, currently somethings wrong with the patterns
  //   // const { hexagons } = this.state;
  //   // // When hexagon is successfully dropped, empty it's text and image
  //   // const hexas = hexagons.map(hex => {
  //   //   if (HexUtils.equals(source.state.hex, hex)) {
  //   //     hex.text = null;
  //   //     hex.image = null;
  //   //   }
  //   //   return hex;
  //   // });
  //   // this.setState({ hexagons: hexas });
  // }

  color_str(name) {
    switch(name) {
      case 'Dark':
        return '#333'
      case 'Light':
        return '#eee'
      case 'Pink':
        return '#faa7f3'
      case 'Indigo':
          return '#8372ab'
      case 'Orange':
          return '#ffad3b'
      case 'Umber':
          return '#997443'
      case 'Sapphire':
          return '#56c6cc'
      case 'Lime':
          return '#62c248'
      case 'Yellow':
          return '#e8dd61'
      case null:
        return null
      default:
        return 'red'
    }
  }

  render() {
    const hexagons = this.props.hexes.map(h => ({
      q: h.y,
      r: h.x,
      s: -h.x-h.y,
      text: h.room,
      hex_color: h.room,
      obj_color: this.color_str(h.obj_color),
      aura_color: this.color_str(h.aura_color),
      obj_darkness: (h.obj_color === 'Dark' ? 'dark' : 'light'),
      aura_darkness: (h.aura_color === 'Dark' ? 'dark' : 'light'),
    }));

    const cur_hex = this.state.current_hex;
    let hover_hex = null;
    if (cur_hex) {
      hover_hex = this.props.hexes.find(h => cur_hex.r === h.x && cur_hex.q === h.y)
    }

    // Calculations to center .game in upper left corner of parent (.grid).
    // In congunction with the CSS rule "transform: translate(50%, 50%)" this
    // aligns center of .game with the center of .grid
    const S = 1.5; // half side length of hex
    const H = S*Math.sqrt(3); // half height of hex

    // filter out temp so that board doesn't shift when adding temp hexes
    const filteredHexes = this.props.hexes.filter(h => h.room !== 'Temp');

    // horizontal offset of each hex relative to the (0, 0) hex depends only
    // on the q (y) coordinate
    const h_vals = filteredHexes.map(h => 3*S*h.y);
    const h_max = Math.max(...h_vals);
    const h_min = Math.min(...h_vals);
    const h_mid = (h_max + h_min) / 2;

    // vertical offset of each hex relative to the (0, 0) hex depends on both
    // the q (y) and r (x) coordinates
    const v_vals = filteredHexes.map(h => H*h.y + 2*H*h.x);
    const v_max = Math.max(...v_vals);
    const v_min = Math.min(...v_vals);
    const v_mid = (v_max + v_min) / 2;

    return (
      <>
        <text className="hoverText">
          {hover_hex ? `${hover_hex.room} (${hover_hex.x}, ${hover_hex.y})` : ''}
        </text>
        <Layout className="game" size={{ x: 2*S, y: 2*S }} origin={{ x: -h_mid, y: -v_mid}}>
          {
            hexagons.map((hex, i) => (
              <Hexagon
                key={i}
                q={hex.q}
                r={hex.r}
                s={hex.s}
                className={`${hex.hex_color} len${this.props.hexes.length}`}
                data={hex}
                onDragStart={(e, h) => this.onDragStart(e, h)}
                onClick={(e, h) => this.onClick(e, h)}
                onMouseEnter={(e, h) => this.onMouseEnter(e, h)}
                onMouseLeave={(e, h) => this.onMouseLeave(e, h)}
                onDragEnd={(e, h, s) => this.onDragEnd(e, h, s)}
                onDrop={(e, h, t) => this.onDrop(e, h, t) }
                onDragOver={(e, h) => this.onDragOver(e, h) }
              >
                <Text>{hex.text || HexUtils.getID(hex)}</Text>
                <defs>
                  <radialGradient id="obj_grad" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
                    <stop offset="30%" style={{'stopOpacity':0}} />
                    <stop offset="100%" style={{'stopColor':'black', 'stopOpacity':0.3}} />
                  </radialGradient>
                </defs>
                {hex.aura_color ? <circle className={hex.aura_darkness} r="1.9" fill={hex.aura_color} /> : null}
                {hex.obj_color ? <circle className={hex.obj_darkness} r="1.2" fill={hex.obj_color} /> : null}
                {hex.obj_color ? <circle className={hex.obj_darkness} r="1.2" fill="url(#obj_grad)" /> : null}
              </Hexagon>
            ))
          }
        </Layout>
      </>
    );
  }
}

export default GameLayout;
