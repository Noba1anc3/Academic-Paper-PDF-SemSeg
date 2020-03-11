
class Region():
    def __init__(self, PageHeight, location):
        self.x0 = location[0]
        self.y0 = PageHeight - location[3]
        self.x1 = location[2]
        self.y1 = PageHeight - location[1]

