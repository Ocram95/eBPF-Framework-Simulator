import optparse
from scapy.utils import rdpcap
from scapy.utils import wrpcap
from scapy.all import *
from scapy.layers.inet6 import IPv6


def process_command_line(argv):
	parser = optparse.OptionParser()
	parser.add_option(
		'-r',
		'--pcap',
		help='Specify the pcap to inject.',
		action='store',
		type='string',
		dest='pcap')

	settings, args = parser.parse_args(argv)
		
	if not settings.pcap:
		raise ValueError("A pcap file must be specified.")

	return settings, args



def parse_pcap(pcap, field, period):
	bins_structure = create_bins_structure(10, 1040000)
	first_packet_time = 0
	count_pkt = 0
	initial_period = period
	#period = 30
	pkts = rdpcap(pcap)
	for x in range(len(pkts)):
		if first_packet_time == 0:
			first_packet_time = pkts[x].time
		instant_time = pkts[x].time - first_packet_time

		if field == "FL":
			value = pkts[x][IPv6].fl
		elif field == "TC":
			value = pkts[x][IPv6].tc
		elif field == "HL":
			value = pkts[x][IPv6].hlim

		if instant_time < period:
			for key in bins_structure.keys():
				if value in key:
					bins_structure[key] += 1
		else:
			print("scrivo csv " + str(period))
			print(bins_structure)
			period += initial_period
			bins_structure = create_bins_structure(10, 1040000)
			for key in bins_structure.keys():
				if value in key:
					bins_structure[key] += 1
		#print("Tempo pacchetto: " + str(pkts[x].time - first_packet_time))
		#count_pkt += 1
		#if count_pkt == 10:
		#	break
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



#d = create_bins_structure(5, 100)
d = parse_pcap("pcap_example.pcap", "FL", 0.01)
print((d))
#r = {range(0, 100): 'foo', range(100, 200): 'bar'}
#print(r)
#print({ d[key] for key in d if 4096 in key})
# value = 10




