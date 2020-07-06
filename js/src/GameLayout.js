import React, { Component } from 'react';
import { Layout, Hexagon, Text, HexUtils } from 'react-hexgrid';
import './GameLayout.css';

import drag_img from './blank_hex.png';

class GameLayout extends Component {
  constructor(props) {
    super(props);
    // const { hexes } = props;
    //
    // console.log('creating hexagons');
    // console.log(`${hexes[0]}`);
    // const hexagons = hexes.map(h => {return new Hex(h.x, h.y, -h.x-h.y)});
    // hexes.map(h => (new Hex(h.x, h.y, -h.x-h.y)))
    // GridGenerator.hexagon(1);
    // Add custom prop to couple of hexagons to indicate them being blocked
    // hexagons[0].blocked = true;
    // hexagons[1].blocked = true;
    this.state = {current_hex: null};
  }

  // onDrop you can read information of the hexagon that initiated the drag
  onDrop(event, source, targetProps) {
    // log drop location
    const hex = source.state.hex
    console.log(`L drop ${hex.q} ${hex.r} ${hex.s}`)

    // const { hexagons } = this.state;
    // const hexas = hexagons.map(hex => {
    //   // When hexagon is dropped on this hexagon, copy it's image and text
    //   if (HexUtils.equals(source.state.hex, hex)) {
    //     hex.image = targetProps.data.image;
    //     hex.text = targetProps.data.text;
    //   }
    //   return hex;
    // });
    // this.setState({ hexagons: hexas });
  }

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

  // TODO: make setDragImage the right size or remove it
  onDragStart(event, source) {
    var img = new Image();
    img.src = drag_img;
    event.dataTransfer.setDragImage(img, img.width/2, img.height/2)

    const hex = source.state.hex
    console.log(`L drag start ${hex.q} ${hex.r} ${hex.s}`)
    // If this tile is empty, let's disallow drag
    if (!source.props.data.text) {
      event.preventDefault();
    }
  }

  // Decide here if you want to allow drop to this node
  onDragOver(event, source) {
    // Find blocked hexagons by their 'blocked' attribute
    // const blockedHexas = this.state.hexagons.filter(h => h.blocked);
    // // Find if this hexagon is listed in blocked ones
    // const blocked = blockedHexas.find(blockedHex => {
    //   return HexUtils.equals(source.state.hex, blockedHex);
    // });
    //
    // const { text } = source.props.data;
    // // Allow drop, if not blocked and there's no content already
    // if (!blocked && !text) {
    //   // Call preventDefault if you want to allow drop
    //   event.preventDefault();
    // }
  }

  // onDragEnd you can do some logic, e.g. to clean up hexagon if drop was success
  onDragEnd(event, source, success) {
    const hex = source.state.hex
    console.log(`L drag end ${hex.q} ${hex.r} ${hex.s}`)
    if (!success) {
      return;
    }
    // TODO Drop the whole hex from array, currently somethings wrong with the patterns

    // const { hexagons } = this.state;
    // // When hexagon is successfully dropped, empty it's text and image
    // const hexas = hexagons.map(hex => {
    //   if (HexUtils.equals(source.state.hex, hex)) {
    //     hex.text = null;
    //     hex.image = null;
    //   }
    //   return hex;
    // });
    // this.setState({ hexagons: hexas });
  }

  color_str(name) {
    switch(name) {
      case 'Dark':
        return '#333'
      case 'Light':
        return '#eee'
      case 'Pink':
        return '#faa7f3'
      case 'Indigo':
          return '#6e5c99'
      case 'Orange':
          return '#ffad3b'
      case 'Umber':
          return '#70522b'
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

  // TODO: sort out using color
  render() {
    const hexagons = this.props.hexes.map(h => ({
      q: h.y,
      r: h.x,
      s: -h.x-h.y,
      text: h.room,
      hex_color: h.room,
      obj_color: this.color_str(h.obj_color),
      aura_color: this.color_str(h.aura_color),
    }));

    const cur_hex = this.state.current_hex;
    let hover_hex = null;
    if (cur_hex) {
      hover_hex = this.props.hexes.find(h => cur_hex.r === h.x && cur_hex.q === h.y)
    }

    // TODO: outline white player in black
    // TODO: position hover text better
    // TODO: auras <circle cx="0" cy="0" r="4" fill={'#333'} />
    // TODO: can remove more becasue of removing:
    //   { hex.image && <Pattern id={HexUtils.getID(hex)} link={hex.image} /> }
    // more Layout params: flat={true} spacing={1}
    // origin() => (
    //   this.props.hexes.map
    // );
    return (
      <Layout className="game" size={{ x: 6, y: 6 }} origin={{ x: 0, y: 0 }}>

        {
          hexagons.map((hex, i) => (
            <Hexagon
              key={i}
              q={hex.q}
              r={hex.r}
              s={hex.s}
              className={hex.hex_color}
              fill={(hex.image) ? HexUtils.getID(hex) : null}
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
              {hex.aura_color ? <circle r="4" fill={hex.aura_color} /> : null}
              {hex.obj_color ? <circle r="2.5" fill={hex.obj_color} /> : null}
            </Hexagon>
          ))
        }
        <text x="-40" y="0">
          {hover_hex ? `hoverhex: ${hover_hex.room} (${hover_hex.x}, ${hover_hex.y})` : ''}
        </text>
      </Layout>
    );
  }
}

export default GameLayout;
