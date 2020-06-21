"""
User input helper functions. Currently they all rely on keypresses, but eventaully they will be based on clicks on the UI.
Some of them are just to make testing easier
"""

def get_keypress(screen):
    screen.key = None
    while True:
        screen.loop_once()
        if screen.key == None:
            continue
        else:
          keypress = screen.key
          screen.key = None
          return keypress

def get_click(screen):
    screen.click_hex = None
    while True:
        screen.loop_once()
        if screen.click_hex == None:
            continue
        else:
          axial_pos = screen.click_hex
          screen.click_hex = None
          return axial_pos

def choose_move(screen):
    '''
    Params: none
    Returns: string representation of the move to make
    '''
    while True:
        print('> Would you like to (1) move (2) bless (3) drop (4) pick up (5) cast spell (6) end turn (7) restart turn or (8) end game? ')
        move_type = get_keypress(screen)

        if move_type == '1':
            return 'move'
        elif move_type == '2':
            return 'bless'
        elif move_type == '3':
            return 'drop'
        elif move_type == '4':
            return 'pick up'
        elif move_type == '5':
            return 'cast spell'
        elif move_type == '6':
            return 'end turn'
        elif move_type == '7':
            return 'reset turn'
        elif move_type == '8':
            return 'end'
        else:
            print('Please enter a number 1-8')

'''
Params: list of objects
Returns: chosen object
'''
def choose_from_list(screen, ls, prompt_text=None):
    if len(ls) == 0:
        return None
    elif len(ls) == 1:
        return ls[0]
    if prompt_text:
        # print optional prompt
        print(prompt_text)
    while True:
        for idx, obj in enumerate(ls):
            print(' ({}) {}'.format(idx + 1, obj))
        print('> Which do you want? ')
        choice = get_keypress(screen)
        try:
            return ls[int(choice) - 1]
        except (ValueError, IndexError):
            print('Please a number 1-{}'.format(len(ls) + 1))

"""
Choose a location based on clicking a hex

Params:
 - screen: a PiouslyApp() UI object
 - axial_pos: a list of tuples (x-coord, y-coord)
 - prompt_text: a string to print to give the user extra info

Returns: index of the chosen location
"""
def choose_location(screen, axial_pos, prompt_text="Click a location"):
    if len(axial_pos) == 0:
        return None
    elif len(axial_pos) == 1:
        return 0
    if prompt_text:
        # print optional prompt
        print(prompt_text)

    while True:
        pos = get_click(screen)
        if pos in axial_pos:
            return  axial_pos.index(pos)
        else:
            print('Please click one of {}'.format(axial_pos))
