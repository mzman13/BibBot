class StateMachine:
    def __init__(self, initialState):
        self.currentState = initialState
        # self.currentState.run()

    def process(self, message):
        self.currentState = self.currentState.next(message)
        self.currentState.run()
