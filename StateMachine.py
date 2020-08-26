class StateMachine:
    def __init__(self, initialState):
        self.currentState = initialState
        # self.currentState.run()

    def process(self, event):
        self.currentState = self.currentState.next(event)
        self.currentState.run()
