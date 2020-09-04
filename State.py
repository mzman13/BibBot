class State:
    def __init__(self):
        self.transitions = None
        self.lastState = False

    def run(self, event):
        assert 0, "run not implemented"

    def next(self, event):
        if event in self.transitions:
            return self.transitions[event]
        else:
            raise Exception("Input not supported for current state")
