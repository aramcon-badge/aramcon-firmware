# Run this code through shell in interactive mode in order to find the quietest
# Frequency available in the area, use an RF-choked USB cable in order to 
# avoid measuring the noise of the laptop power supply.
from arambadge import badge
from si4703 import SI4703
import board
from digitalio import DigitalInOut
from time import sleep
fm = SI4703(badge.i2c, DigitalInOut(board.D2), channel=106.8)
fm.reset()
fm.volume=0
sleep(0.2)
freq_to_rssi = {}

# This loop might take about 1.5 minutes to finish
# The theoretical optimum is 64 seconds, but actually
# it takes about a minute and a half, because setting 
# the channel takes time.
for i in map(lambda x: x/10.0, range(760, 1080, 1)):
	fm.channel=i
	# Let the noise stabilize after changing the RX frequency
	sleep(0.2)
	freq_to_rssi[i] = fm.read_registers()['STATUSRSSI'] & 0xff




for i in sorted(freq_to_rssi, key=freq_to_rssi.get):
	print('%5.1f\t%d' % (i, freq_to_rssi[i]))




quietest_freq_1 = min(freq_to_rssi, key=freq_to_rssi.get)
del freq_to_rssi[quietest_freq_1]
quietest_freq_2 = min(freq_to_rssi, key=freq_to_rssi.get)
print("Quietest frequency 1:", quietest_freq_1)
print("Quietest frequency 2:", quietest_freq_2)

