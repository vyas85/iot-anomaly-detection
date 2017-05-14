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

    # Resets the voltage based on parameters with randomization and resets device to first in line
    def initialize(self):
        self.voltage = random.normalvariate(self.base_voltage, self.base_variation) + self.bonus
        self.device = 0

    # Iterates to next device in line
    # Calculates new voltage based upon current voltage and drop with randomization
    def next_meter(self):
        if self.device == self.num_devs - 1:
            self.initialize()
        else:
            self.device += 1
            self.next_voltage()
        return self.get_values()

    # Returns voltage from next device, with small chance for erroneous data
    def next_voltage(self):
        if self.voltage >= self.voltage * 3:  # adjust to normal voltage after anomaly
            self.voltage = self.base_voltage - (self.base_drop * self.device)
        self.voltage -= random.normalvariate(self.base_drop, self.base_drop / 2.)
        if random.uniform(0, 1) <= 0.1:  # 1% chance of erroneous data
            self.voltage += self.voltage * 4

    # Returns line number, device number, voltage at device and device ID
    def get_values(self):
        return self.line, self.device, self.voltage, self.ids[self.device]

    # Adjusts bonus to starting voltage
    def adjust_bonus(self, modifier):
        self.bonus += modifier

    # Modifies bonus to bring back average levels
    def correct_bonus(self):
        modifier = (self.base_voltage - (self.base_drop * self.device) - self.voltage) / 2
        self.adjust_bonus(modifier)
        return modifier
