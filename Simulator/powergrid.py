# Simulates power grid with multiple FeederLines

from __future__ import print_function
from feederline import FeederLine


class PowerGrid:
    def __init__(self, num_lines, voltage, drop, devices):
        self.base_voltage = voltage
        self.drop_base = drop
        self.num_devices = devices
        self.lines = []
        for i in range(0, num_lines):
            self.add_line()

    # Removes FeederLine number line_num
    def remove_line(self, line_num):
        self.lines.pop(line_num)

    # Adds FeederLine to PowerGrid
    def add_line(self):
        self.lines.append(FeederLine(line=len(self.lines), voltage=self.base_voltage, drop=self.drop_base,
                                     num_devs=self.num_devices))

    # Simulates PowerGrid in action by cycling through lines and
    def simulate(self):
        i = 0
        # Can modify to run indefinitely by changing to i > -1
        while i < 200:
            print(self.lines[(i % len(self.lines))].next_meter())
            i += 1
