"""
User input helper functions for js frontend.
"""
from backend.location import location_to_axial
from backend.errors import InvalidMove

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

# '''
# Params: none
# Returns: string representation of the move to make
# '''
# def choose_move(screen):
#     screen.info.text = 'Select option (click button or use keybinding)'
#     return get_keypress(screen)

'''
Params: list of objects
Returns: chosen object
'''
def choose_from_list(screen, ls, prompt_text='Choose one:', error_text='No valid choices', all_spells=None):
    # if data:
    #     if len(eligible_spells) == 0:
    #         raise InvalidMove('{} does not have untapped spells'.format(faction))
    #     elif 'click_spell_idx' in data:
    #         # This depends on the order of board.spells matching the order on the frontend
    #         spell = self.current_board.spells[data['click_spell_idx']]
    #         if spell not in eligible_spells:
    #             raise InvalidMove('Cannot cast {}'.format(spell))
    #     else:
    #         self.screen.info.text = 'Click on a spell to cast'
    print('choose from list {}'.format(ls))
    if len(ls) == 0:
        raise InvalidMove(error_text)
    elif len(ls) == 1:
        screen.action_buttons_on = True
        return ls[0]

    if 'choice_idx' in screen.data:
        print('using choice_idx')
        choice = screen.data['choice_idx']
        try:
            ret = ls[int(choice) - 1]
            screen.action_buttons_on = True
            screen.info.error = None
            print('returning {}'.format(ret))
            return ret
        except (ValueError, IndexError):
            raise InvalidMove('Please enter a number 1-{}'.format(len(ls)))
    elif 'click_spell_idx' in screen.data and all_spells:
        # This depends on the order of board.spells matching the order on the frontend
        print('using click_spell_idx')
        spell = all_spells[data['click_spell_idx']]
        if spell not in ls:
            raise InvalidMove('Cannot cast {}'.format(spell))
    else:
        print('setting prompt')
        prompt = prompt_text
        for idx, obj in enumerate(ls, start=1):
            prompt += ' ({}) {}'.format(idx, obj)

        screen.info.text = prompt
        screen.action_buttons_on = False # TODO make this disable buttons

"""
Choose a location based on clicking a hex

Params:
 - screen: a PiouslyApp() UI object
 - axial_pos: a list of tuples (x-coord, y-coord)
 - prompt_text: a string to display to give the user extra info

Returns: index of the chosen location
"""
def choose_location(screen, axial_pos, prompt_text="Click a location", error_text="No valid locations"):
    if len(axial_pos) == 0:
        raise InvalidMove(error_text)
    elif len(axial_pos) == 1:
        screen.action_buttons_on = True
        return 0

    if 'click_x' in screen.data and 'click_y' in screen.data:
        selected_coords = screen.data['click_x'], screen.data['click_y']
        if selected_coords in axial_pos:
            screen.action_buttons_on = True
            return axial_pos.index(selected_coords)
        else:
            raise InvalidMove('Cannot move to {}. Please click one of {}'.format(
                selected_coords,
                ', '.join(str(pos) for pos in axial_pos),
            ))
    else:
        # set prompt
        screen.info.text = prompt_text
        screen.action_buttons_on = False

"""
Choose a location from a list of hexes based on clicking a hex

Params:
 - hex_list: a list of hexes from which to choose
 - return_index: boolean which determines if returns an index

Returns: chosen hex, or index of chosen hex if return_index is True
"""
def choose_hexes(screen, hex_list, prompt_text="Choose a hex:", error_text="No valid hexes", return_index = False):
    # get a list of axial coordinates for the hexes
    axial_coordinates = [location_to_axial(x.location) for x in hex_list]
    chosen_index = choose_location(screen, axial_coordinates, prompt_text, error_text)
    if return_index:
        return chosen_index
    elif chosen_index != None:
        return hex_list[chosen_index]
