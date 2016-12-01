# SmartMeter class representation
from __future__ import print_function
import random
import uuid


class FeederLine:
    def __init__(self, line, voltage, drop, num_devs):
        self.base_voltage = voltage
        self.base_variation = 0.5
        self.base_drop = drop
        self.num_devs = num_devs
        self.bonus = 0
        self.device = 0
        self.line = line
        self.voltage = 0
        self.ids = []
        for i in range(0, self.num_devs):
            self.ids.append(str(uuid.uuid4()))
        self.initialize()

    def initialize(self):
        self.voltage = random.normalvariate(self.base_voltage, self.base_variation) + self.bonus
        self.device = 0
        # Reset bonus to 0?

    def next_meter(self):
        if self.device == self.num_devs - 1:
            self.initialize()
        else:
            self.device += 1
            self.voltage -= random.normalvariate(self.base_drop, self.base_drop / 4.)
        return self.get_values()

    def get_values(self):
        return self.ids[self.device], self.voltage, self.device, self.line

    def adjust_bonus(self, modifier):
        self.bonus += modifier
