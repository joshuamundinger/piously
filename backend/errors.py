"""
Game specific error types
"""

class InvalidMove(Exception, object):
    """Raised when an invalid move is attempted"""

    def __init__(self, error_message):
        self.full_error = 'INVALID MOVE: {}'.format(error_message)

    def __str__(self):
        return self.full_error
