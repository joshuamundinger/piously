"""
User input helper functions for js frontend.
"""
from backend.location import location_to_axial
from backend.errors import InvalidMove

def get_keypress(screen):
    if 'current_keypress' in screen.data:
        key = screen.data['current_keypress']
        screen.data.pop('current_keypress')

        # not calling complete_choice() since don't need to track these
        screen.action_buttons_on = True
        screen.info.error = None
        return key
    else:
        screen.action_buttons_on = False

'''
Params: list of objects
Returns: chosen object
'''
def choose_from_list(screen, ls, prompt_text='Choose one:', error_text='No valid choices', all_spells=None):
    print('choose from list {}'.format(ls))
    if len(ls) == 0:
        raise InvalidMove(error_text)
    elif len(ls) == 1:
        return complete_choice(screen, ls[0])

    if 'choice_idx' in screen.data:
        print('using choice_idx')
        choice = screen.data['choice_idx']
        screen.data.pop('choice_idx')
        try:
            ret = ls[int(choice) - 1]
            return complete_choice(screen, ret)
        except (ValueError, IndexError):
            screen.info.error = 'Please enter a number 1-{}'.format(len(ls))
            return None
    elif 'click_spell_idx' in screen.data and all_spells:
        # This is a bit hacky, but will work for now
        # This depends on the order of board.spells matching the order on the frontend
        print('using click_spell_idx')
        spell = all_spells[screen.data['click_spell_idx']]
        screen.data.pop('click_spell_idx')
        if spell not in ls:
            screen.info.error = 'Cannot cast {}'.format(spell)
            return None

        return complete_choice(screen, spell)
    else:
        print('setting prompt')
        prompt = prompt_text
        for idx, obj in enumerate(ls, start=1):
            prompt += ' ({}) {}'.format(idx, obj)

        screen.info.text = prompt
        screen.action_buttons_on = False

"""
Choose a location based on clicking a hex

Params:
 - screen: a PygameScreen() UI object
 - axial_pos: a list of tuples (x-coord, y-coord)
 - prompt_text: a string to display to give the user extra info

Returns: index of the chosen location
"""
def location_helper(screen, axial_pos, prompt_text="Click a location", error_text="No valid locations"):
    # not calling complete_choice() since caller will do that

    if len(axial_pos) == 0:
        raise InvalidMove(error_text)
    elif len(axial_pos) == 1:
        return 0
    # user already clicked a hex
    elif 'click_x' in screen.data and 'click_y' in screen.data:
        selected_coords = screen.data['click_x'], screen.data['click_y']
        screen.data.pop('click_x')
        screen.data.pop('click_y')
        if selected_coords in axial_pos:
            return axial_pos.index(selected_coords)
        else:
            screen.info.error = 'Cannot choose {}. Please click one of {}'.format(
                selected_coords,
                ', '.join(str(pos) for pos in axial_pos),
            )
            return None
    # user has not yet clicked a hex
    else:
        screen.info.text = prompt_text
        screen.action_buttons_on = False
        return None # just being explicit

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
    chosen_index = location_helper(screen, axial_coordinates, prompt_text, error_text)

    if return_index:
        return complete_choice(screen, chosen_index)
    elif chosen_index != None:
        return complete_choice(screen, hex_list[chosen_index])
    else:
        return None # just being explicit

"""
Helper to make all the needed changes once a choice has been made
"""
def complete_choice(screen, choice):
    screen.action_buttons_on = True
    screen.choices.append(choice)
    screen.info.error = None
    print('appended + returning {}. Choices: {}'.format(choice, screen.choices))
    return choice
