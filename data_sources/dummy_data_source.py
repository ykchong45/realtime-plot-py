import math

class DummyDataSource:
    def __init__(self):
        self.x = 0

    def get_data(self):
        self.x += 1
        y = math.sin(self.x * 2 * math.pi / 1000)
        return self.x, y