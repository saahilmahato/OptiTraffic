class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.vehicles = []

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def update(self, dt):
        new_list = []
        for v in self.vehicles:
            v.update(dt)
            x, y = v.pos
            if 0 <= x <= self.width and 0 <= y <= self.height:
                new_list.append(v)
        self.vehicles = new_list
