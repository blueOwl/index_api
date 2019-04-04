from functools import reduce
import gzip
import config
import os
import fnmatch
try:
   import cPickle as pickle
except:
   import pickle

def make_combine_key(line):
	try:
		line = line.split("\t")
		return ':'.join(line[:4])
	except:
		return ''

def get_single_key(line):
	line = line.split("\t")
	if len(line) > 121:
		if line[120] == '.':return ''
		return line[120]
	return ''

def make_hidx(data_file):
	hash_idx_file = data_file + '.hidx.pkl'
	f = gzip.open(data_file)
	f.readline()
	offset = f.tell()
	index_data = {}
	for line in f:
		line = line.decode("utf-8")
		k1 = make_combine_key(line)
		if k1:
			if index_data.get(k1):
				index_data[k1].append(offset)
			else:
				index_data[k1] = [offset]
		k2 = get_single_key(line)
		if k2:
			if index_data.get(k2):
				index_data[k2].append(offset)
			else:
				index_data[k2] = [offset]
		offset = f.tell()
	hash_idx_file = open(hash_idx_file, "wb")
	pickle.dump(index_data, hash_idx_file)
			
def hash_key_get(data_file, index_dic, key, filter_fun=str):
	offset = index_dic.get(key, None)
	if offset == None:
		return filter_fun('')
	res = []
	for i in offset:
		data_file.seek(i)
		res.append(filter_fun(data_file.readline().decode("utf-8").rstrip()))
	return res

def init_hash_idx(dataset):
	listOfFiles = os.listdir(config.data_dir[dataset])
	gz_pattern = "*.gz"
	data_files = {}
	idxs = {}
	for entry in listOfFiles:
		if fnmatch.fnmatch(entry, gz_pattern):
			contig = entry.split('.')[0]
			data_files[contig] = entry
			hash_idx = config.data_dir[dataset] + entry + '.hidx.pkl'
			try:
				print("read h_idx for " + entry)
				idxs[entry] = pickle.load(open(hash_idx, 'rb'))
			except:
				print("make h_idx for " + entry)
				make_hidx(config.data_dir[dataset] + entry)
				idxs[entry] = pickle.load(open(hash_idx, 'rb'))
	return idxs, data_files

class H_idx:
	def __init__(self, dataset):
		self.dataset = dataset
		self.idxs, self.data_files_names = init_hash_idx(dataset)
		self.data_dir = config.data_dir[dataset]
		self.data_files = {contig:gzip.open(self.data_dir + self.data_files_names[contig], 'rb') for contig in self.data_files_names} 
	@staticmethod
	def tab_split(l):
		if not l:return []
		return l.split("\t")
	def k_get(self, key):
		reses = []
		for contig in self.data_files:
			file_name = self.data_files_names[contig]
			data_file = self.data_files[contig]
			idx = self.idxs[file_name]
			reses.append(hash_key_get(data_file, idx, key, self.tab_split))
		return reduce(lambda a,b:a+b, reses)	
#test part
if __name__ == "__main__":
	'''
	dataset = 'HRC'
	idxs, data_files = init_hash_idx(dataset)
	idx_file = idxs["19.annotated.snp.withPanther.gz"]
	data_file = gzip.open('data/19.annotated.snp.withPanther.gz','rb')
	key = '19:90678:G:A'
	print(key)
	print(hash_key_get(data_file, idx_file, key))
	key = 'rs11084984'
	print(key)
	print(hash_key_get(data_file, idx_file, key))
	'''
	idx = H_idx("HRC")
	print('finished init')
	key = '19:90678:G:A'
	print(idx.k_get(key))
	key = 'rs11084984'
	print(idx.k_get(key))
