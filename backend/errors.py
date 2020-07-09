"""
Game specific error types
"""

class InvalidMove(Exception):
    """Raised when an invalid move is attempted"""

    def __init__(self, error_message):
        self.full_error = error_message

    def __str__(self):
        return self.full_error
