import math
import matplotlib.pyplot as plt
import pandas as pd
import sys
import optparse
import csv


def process_command_line(argv):
	parser = optparse.OptionParser()
	parser.add_option(
		'-r',
		'--csv',
		help='Specify the csv to read.',
		action='store',
		type='string',
		dest='csv')

	settings, args = parser.parse_args(argv)
		
	if not settings.csv:
		raise ValueError("The csv file must be specified.")

	return settings, args


def tmp_plot(number_of_bins_different_from_zero):
	fig, ax = plt.subplots()
	ax.plot(number_of_bins_different_from_zero["timestamp"], number_of_bins_different_from_zero["!=0"], label='your label')
	ax.set_ylabel('no. of bins != 0')
	ax.set_xlabel('time [s]')
	ax.legend()
	plt.grid()
	plt.show()

def plot_nprobe(file):
	time_nprobe = []
	active_flows = []
	dumped_flows_inst = []
	new_flows = []
	active_flows_period = []
	with open(file) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				line_count += 1
			else:
				time_nprobe.append(int(row[0])/1000)
				active_flows.append(int(row[1]))
	return time_nprobe, active_flows


settings, args = process_command_line(sys.argv)
read_data = pd.read_csv(settings.csv, header=None)
#pop method remove and return a column
time_col = read_data.pop(read_data.columns[0])
number_of_bins_different_from_zero = read_data.astype(bool).sum(axis=1).to_frame(name="!=0")
number_of_bins_different_from_zero.insert(loc=0, column='timestamp', value=time_col)
time_nprobe, active_flows = plot_nprobe("caida2_2Mbps_15min_l=130k.csv")
fig, ax = plt.subplots()
ax.plot(number_of_bins_different_from_zero["timestamp"], number_of_bins_different_from_zero["!=0"], label='your label')
ax.step(time_nprobe, active_flows, label="F")
ax.set_ylabel('no. of bins != 0')
ax.set_xlabel('time [s]')
ax.legend()
plt.grid()
plt.show()



