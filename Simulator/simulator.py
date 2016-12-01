# Simulator for SmartMeter data
# Creates data for several FeederLines of smartmeters

from __future__ import print_function
from feederline import FeederLine

start_voltage = 26
num_lines = 10
drop_base = 1
num_devices = 5

lines = []

test = FeederLine(0, 26, 1, 5)

# Create FeederLines
for i in range(0, num_lines):
    lines.append(FeederLine(line=i, voltage=start_voltage, drop=drop_base, num_devs=num_devices))

# Run application for X amount of iterations
X = 100
for k in range(0, X):
    print(lines[(k % num_lines)].next_meter())
