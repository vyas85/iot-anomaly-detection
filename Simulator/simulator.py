# Simulator for SmartMeter data
# Creates data for several FeederLines of SmartMeters

from __future__ import print_function
from powergrid import PowerGrid

start_voltage = 26
num_lines = 10
drop_base = 1
num_devices = 10

grid = PowerGrid(num_lines=num_lines, voltage=start_voltage, drop=drop_base, devices=num_devices)

for i in range(0, 2000):
    print(grid.update())
