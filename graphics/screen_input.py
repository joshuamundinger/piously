"""
User input helper functions. Currently they all rely on keypresses, but eventaully they will be based on clicks on the UI.
Some of them are just to make testing easier
"""
from backend.location import location_to_axial

def get_keypress(screen):
    screen.key = None
    while True:
        screen.loop_once()
        if screen.key == None:
            continue
        else:
          keypress = screen.key
          return keypress

def get_click(screen):
    screen.click_hex = None
    while True:
        screen.loop_once()
        if screen.click_hex == None:
            continue
        else:
          axial_pos = screen.click_hex
          return axial_pos

'''
Params: none
Returns: string representation of the move to make
'''
def choose_move(screen):
    screen.info.text = 'Select option (click button or use keybinding)'
    return get_keypress(screen)

'''
Params: list of objects
Returns: chosen object
'''
def choose_from_list(screen, ls, prompt_text='Choose one:'):
    if len(ls) == 0:
        return None
    elif len(ls) == 1:
        return ls[0]

    prompt = prompt_text
    for idx, obj in enumerate(ls, start=1):
        prompt += ' ({}) {}'.format(idx, obj)

    screen.info.text = prompt
    screen.toggle_action_buttons()
    while True:
        choice = get_keypress(screen)
        try:
            ret = ls[int(choice) - 1]
            screen.toggle_action_buttons()
            screen.info.error = None
            return ret
        except (ValueError, IndexError):
            screen.info.error = 'Please enter a number 1-{}'.format(len(ls))

"""
Choose a location based on clicking a hex

Params:
 - screen: a PiouslyApp() UI object
 - axial_pos: a list of tuples (x-coord, y-coord)
 - prompt_text: a string to display to give the user extra info

Returns: index of the chosen location
"""
def choose_location(screen, axial_pos, prompt_text="Click a location"):
    if len(axial_pos) == 0:
        return None
    elif len(axial_pos) == 1:
        return 0

    # set prompt
    screen.info.text = prompt_text
    screen.toggle_action_buttons()
    while True:
        pos = get_click(screen)
        if pos in axial_pos:
            ret = axial_pos.index(pos)
            screen.info.error = None
            screen.toggle_action_buttons()
            return ret
        else:
            screen.info.error = 'Please click one of {}'.format(axial_pos)

"""
Choose a location from a list of hexes based on clicking a hex

Params:
 - hex_list: a list of hexes from which to choose
 - return_index: boolean which determines if returns an index

Returns: chosen hex, or index of chosen hex if return_index is True
"""
def choose_hexes(screen, hex_list, prompt_text="Choose a hex:", return_index = False):
    # get a list of axial coordinates for the hexes
    axial_coordinates = [location_to_axial(x.location) for x in hex_list]
    chosen_index = choose_location(screen, axial_coordinates, prompt_text)
    if return_index:
        return chosen_index
    elif chosen_index != None:
        return hex_list[chosen_index]
