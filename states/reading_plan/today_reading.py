from State import State


class TodayReading(State):
    def __init__(self):
        self.lastState = True

    def run(self, event):
        plannerContext = event[1]
        plannerContext.updateToday()
        if plannerContext.nextChp:
            response = plannerContext.getTodayReading()
            if plannerContext.nextBook == 'done':
                plannerContext.sendMessage(response)
                celebrate = u'\U0001F389'
                smile = u'\U0001F601'
                highfive = u'\U0001F64C'
                clap = u'\U0001F44F'
                response = f"Congratulations!!! {celebrate}{celebrate}{celebrate}\nToday's the last day of your reading plan!{smile}{smile}{smile}\nGreat job on making it this far!{highfive}{highfive}{clap}"
        else:
            response = "No reading plan found!\nPlease start a new reading plan!"
        plannerContext.sendMessage(response)

    def next(self, event):
        return None
