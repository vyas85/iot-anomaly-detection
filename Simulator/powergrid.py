# Simulates power grid with multiple FeederLines

from __future__ import print_function
from feederline import FeederLine
import random


class PowerGrid:
    def __init__(self, num_lines, voltage, drop, devices):
        self.thresholds = [voltage - drop * (devices + 1), voltage + drop * 2]
        self.base_voltage = voltage
        self.drop_base = drop
        self.num_devices = devices
        self.lines = []
        self.index = 0
        for i in range(0, num_lines):
            self.add_line()

    # Removes FeederLine number line_num
    def remove_line(self, line_num):
        self.lines.pop(line_num)

    # Adds FeederLine to PowerGrid with randomized drop value based upon base drop
    def add_line(self):
        drop = random.normalvariate(self.drop_base, self.drop_base / 4.)
        self.lines.append(FeederLine(line=len(self.lines), voltage=self.base_voltage,
                                     drop=drop, num_devs=self.num_devices))

    # Returns current line based on index
    @property
    def get_line(self):
        return self.index % len(self.lines)

    # Simulates PowerGrid in action by cycling through lines and
    def update(self):
        result = self.lines[self.get_line].next_meter()
        self.index += 1
        output = result + self.result_status(result)
        return output

    # Function to handle results, check for anomalies and normal activity outside of thresholds
    def result_status(self, results):
        voltage = results[2]
        modifier = 0
        if voltage > self.thresholds[1] * 2:  # Anomaly requires reporting but no action
            status = 'Anomaly'
        elif voltage > self.thresholds[1]:  # High voltage requires adjustment to line voltage modifier
            status = 'High'
            modifier = voltage - self.thresholds[1]
            #print("Modifying Line")
            #self.modify_line(self.lines[self.get_line], modifier)
        elif voltage < self.thresholds[0]:  # Low voltage requires adjustment to line voltage modifier
            status = 'Low'
            modifier = self.thresholds[1] - voltage
            #print("Modifying Line")
            #self.modify_line(self.lines[self.get_line], modifier)
        else:
            status = 'Normal'
        return status, modifier

    # Adjusts voltage for a particular FeederLine
    def modify_line(self, line, modifier):
        self.lines[line].adjust_bonus(modifier)
