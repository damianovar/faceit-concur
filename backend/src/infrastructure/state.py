# state.py


class SingletonMeta(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]


class State(metaclass=SingletonMeta):
    """
    Keeps track of logging in and last used values
    """
    def __init__(self, user=None):
        self.user = user
        self.kc_list = None
        self.kc_matrix = None
        self.connection = None
        self.course = None
        self.questions = None
