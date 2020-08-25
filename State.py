class State:
    def __init__(self):
        self.transitions = None

    def run(self):
        assert 0, "run not implemented"

    def next(self, input):
        if input in self.transitions:
            return self.transitions[input]
        else:
            raise Exception("Input not supported for current state")
