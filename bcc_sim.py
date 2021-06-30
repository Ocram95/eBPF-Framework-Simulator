import optparse
from scapy.utils import rdpcap
from scapy.utils import wrpcap
from scapy.all import *
from scapy.layers.inet6 import IPv6
import csv

FIELD_LENGTH = {
	"FL": 20,
	"TC": 8,
	"HL": 8
}

POSSIBLE_BINS = {
	"FL": range(1, pow(2,20)),
	"TC": range(1, pow(2,8)),
	"HL": range(1, pow(2,8))
}

def process_command_line(argv):
	parser = optparse.OptionParser()

	parser.add_option('-r', '--pcap', help='Specify the pcap to read.', action='store', type='string', dest='pcap')

	parser.add_option('-b', '--bins', help='Specify the number of bins to use.', action='store', type='int', dest='bins')

	parser.add_option('-f', '--field', help='Specify the field to inspect.', action='store', type='string', dest='field')

	parser.add_option('-i', '--sampling_interval', help='Specify the sampling interval.', default=1, action='store', type='int', dest='sampling_interval')

	parser.add_option('-t', '--T_window', help='Specify the time window.', default=-1, action='store', type='int', dest='T_window')

	parser.add_option('-w', '--W_window', help='Specify the sampling window.', default=-1, action='store', type='int', dest='W_window')

	parser.add_option('-o', '--output_file', help='Specify the output file.', action='store', type='string', dest='output_file')

	settings, args = parser.parse_args(argv)
		
	if settings.bins not in POSSIBLE_BINS[settings.field]:
		raise ValueError("error")	
	return settings, args

def parse_pcap(bins_structure, pcap, field, sampling_interval, T_window, W_window, output_file):
	first_packet_time = 0
	count_pkt = 0
	pkts = rdpcap(pcap)
	elapsed_time = 0
	current_time = 0
	window_time = 0
	number_of_samples = 0
	first_row = True
	for x in range(len(pkts)):
		initial_time = time.perf_counter()
		if first_packet_time == 0:
			first_packet_time = pkts[x].time
		instant_time = pkts[x].time - first_packet_time

		if field == "FL":
			value = pkts[x][IPv6].fl
		elif field == "TC":
			value = pkts[x][IPv6].tc
		elif field == "HL":
			value = pkts[x][IPv6].hlim

		#Write first line of zeros	
		if first_row:
			write_csv(output_file, bins_structure, current_time)
			first_row = False

		for key in bins_structure.keys():
			if value in key:
				bins_structure[key] += 1
				number_of_samples += 1

		#TODO: Remove. It is necessary for short pcap files
		time.sleep(0.5)

		final_time = time.perf_counter()
		elapsed_time += final_time - initial_time
		window_time += elapsed_time

		if elapsed_time >= sampling_interval:
			#print(str(elapsed_time) + " scrivo riga csv")
			current_time += elapsed_time
			write_csv(output_file, bins_structure, current_time)
			elapsed_time = 0

		if T_window != -1:
			if window_time >= T_window:
				print("resetto mappa")
				for key in bins_structure.keys():
					bins_structure[key] = 0
				window_time = 0
				first_row = True
		if W_window != -1:
			if number_of_samples >= W_window:
				print("resetto mappa")
				for key in bins_structure.keys():
					bins_structure[key] = 0
				number_of_samples = 0
				first_row = True

	return bins_structure


def create_bins_structure(number_of_bins, dim_field):
	dictionary = {}
	prev = 0
	bin_size = int(dim_field/number_of_bins)
	succ = int(dim_field/number_of_bins)
	for x in range(number_of_bins):
		dictionary[range(prev, succ)] = 0
		prev = succ
		succ += bin_size
	#print(dictionary)
	return dictionary

def write_csv(csv_file_name, bins_structure, current_time):
	with open(csv_file_name, mode='a') as file:
		writer = csv.writer(file)
		bins_values = list(bins_structure.values())
		bins_values.insert(0, current_time)
		print(bins_values)
		writer.writerow(bins_values)



settings, args = process_command_line(sys.argv)
bins_structure = create_bins_structure(settings.bins, pow(2, FIELD_LENGTH[settings.field]))
#print(bins_structure)
parse_pcap(bins_structure, settings.pcap, settings.field, settings.sampling_interval, settings.T_window, settings.W_window, settings.output_file)




