import os
import uuid
from init_db import *
contigs, data_files = init_scan_folder("HRC")

def tabix_compare(contig, filename):
	data_file = data_files[contigs.index(contig)]
	cmd = "tabix {data_file} -R {region_file}".format(data_file=data_file, region_file=filename)
	#print(cmd)
	try:
		return os.popen(cmd) 
	except:
		return []

def split_based_on_contig(f):
	contigs = {}
	for i in f:
		line = i.rstrip().split('\t')
		contig, pos = line[0], line[1]
		if contig in contigs:
			contigs[contig].append(contig + "\t" + pos)
		else:
			contigs[contig] = [contig + "\t" + pos]
	cs, fs = [], []
	for c in contigs:
		file_path = config.TMPDIR['HRC'] + str(uuid.uuid4())
		open(file_path, 'w').write('\n'.join(contigs[c]))
		cs.append(c)
		fs.append(file_path)
	return cs, fs

def batch_retrieve(f, filter_func=list):
	cs, fs = split_based_on_contig(f)
	res = []
	for c, f in zip(cs, fs):
		print(c,f)
		res += tabix_compare(c, f)
	res = [filter_func(i.split("\r")) for i in res]
	file_path = config.TMPDIR['HRC'] + str(uuid.uuid4())
	open(file_path,"w").write(''.join(['\t'.join(i) for i in res]))
	return file_path
if __name__ == "__main__":
	n = batch_retrieve(open("data/query_input"))
	print(n)
