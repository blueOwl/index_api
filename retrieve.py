import config
import os, fnmatch
import pysam
import gzip
import uuid
import math
from utils import index_get_func

def rebuildIndex(path, datafile):
	status_code = os.system("cd {path} && tabix -S 1  -s 1 -b 2 -e 2 {datafile}".format(path=path, datafile=datafile))
	if status_code != 0:
		raise 
def get_header(path, header_dic, chrm_name):
	f = gzip.open(path, 'rt')
	header = f.readline().rstrip().split('\t')
	header_dic[chrm_name] = header
	
def init_dataset(dataset):
	#init 
	#find all files
	listOfFiles = os.listdir(config.data_dir[dataset])
	gz_pattern = "*.gz"
	des_pattern = "*.annotated.snp.description.txt"
	data_files = []
	des_files = []
	chroms_names = []
	for entry in listOfFiles:  
		if fnmatch.fnmatch(entry, gz_pattern):
			try:
				prefix = entry.split('.')[0]
				prefix = prefix.replace('chr','')
				chrm_name = prefix
			except:
				print("{} has an invalid name and won't be used".format(entry))
			finally:
				data_files.append(entry)
				chroms_names.append(chrm_name)
		if fnmatch.fnmatch(entry, des_pattern):
			des_files.append(entry)
	#load data files and headers
	#load pysam links
	sam_dic = {}
	used_data_files = []
	used_chroms_names = []
	used_header = {}
	for idx, name in enumerate(data_files):
		try:
			get_header(config.data_dir[dataset] + name, used_header, chroms_names[idx])
			sam_dic[chroms_names[idx]] = pysam.TabixFile(config.data_dir[dataset] + name)
			used_data_files.append(name)
			used_chroms_names.append(chroms_names[idx])
		except:
			try:
				rebuildIndex(config.data_dir[dataset], name)
				print('build index for file {}'.format(name))
				get_header(config.data_dir[dataset] + name, used_header, chroms_names[idx])
				sam_dic[chroms_names[idx]] = pysam.TabixFile(config.data_dir[dataset] + name)
				used_data_files.append(name)
				used_chroms_names.append(chroms_names[idx])
			except:
				print("no index for {} and it will not be used".format(name))
	retrieve = {"des_files": des_files, "tabix_links":sam_dic, "used_data_files":used_data_files, "used_chroms_names":used_chroms_names, "used_header":used_header}
	return retrieve
	
def empty_generator(**kwargs): return []

class QueryResult:
	def __init__(self, generator, generator_kargs={}, page_size = config.page_size, col_converter=list):
		self.headers = []
		self.col_converter = col_converter
		self.generator = generator
		self.gen_kargs = generator_kargs
		self.page_size = page_size
		self.info = {}

		self.exceed = False	
		self.records_num = self.get_total_records_num()
		self.total_page = math.ceil(self.records_num / self.page_size)
		
		self.rebuild()
		try:
			self.cur_page = next(self.pages)
			#print("c_page", self.cur_page)
		except:
			self.cur_page = []

	def get_gen(self): 
		return self.generator(**self.gen_kargs)
	
	def rebuild(self):
		self.gen = self.get_gen()
		self.pages = self.get_pages_iter()
		self.page_num = 1


	def get_page(self, page_num):
		if page_num < 0 or page_num > self.total_page:return []
		if page_num == self.page_num:
			return self.get_cur_page()
		elif page_num > self.page_num:
			past_num = self.page_num * self.page_size
		else:
			self.rebuild()
			past_num = 0
		need_past = (page_num - 1) * self.page_size
		count = 0
		if (need_past - past_num) > 0:
			for i in self.gen:
				count += 1
				if count == (need_past - past_num): break
		self.page_num = page_num
		certain_page = next(self.pages)
		self.get_cur_page()
		#update cur_page and page_num + 1
		return certain_page

	def get_total_records_num(self):
		r_nums = 1
		gen = self.get_gen()
		for i in gen: 
			r_nums += 1
			if r_nums > config.res_max:
				break
				self.exceed = True
		return r_nums
	
	def get_pages_iter(self):
		#pagination part
		'''use iterator for pagination, next page in self.cur_page, get current page by get_cur_page'''
		page = []
		for item in self.gen:
			page.append(self.col_converter(item))
			if len(page) == self.page_size:
				yield page
				page= []
		if len(page) != 0:yield page
	def get_cur_page(self):
		cur_page = self.cur_page
		try:
			self.cur_page = next(self.pages)
		except:
			self.cur_page = None
		if cur_page : self.page_num += 1
		return cur_page
	def has_next(self):
		if self.cur_page:return True
		return False
	def get_page_info(self):
		return {"page_num":self.page_num - 1,
		 "total_page":self.total_page,
		 "page_size":self.page_size}

	def write_to_file(self, res_dir = ''):
		# 1.rebuld generator
		# 2.write to file
		# 3.rebuild and back to same page
		# 4.return filenames
		filename = str(uuid.uuid4())
		f = open(res_dir + filename, 'w')
		cur_page_num = self.page_num
		self.rebuild()
		if self.headers: f.write("#" + "\t".join(self.headers.values()) + "\n")
		for item in self.gen:
			line = '\t'.join(self.col_converter(item))
			f.write(line + '\n')
		self.rebuild()
		self.get_page(cur_page_num - 1)
		return filename
#query part
class Retrieve:
	def __init__(self, dataset):
		self.dataset = dataset
		self.r = init_dataset(dataset)
		self.col_filter = list

	def region_query(self, chrom, start, end, col_filter=list):
		if not chrom in self.r['used_chroms_names']:return QueryResult(empty_generator)
		self.col_filter = col_filter
		try:
			start, end = int(start), int(end)
		except:
			[]
		q = QueryResult(self.r['tabix_links'][chrom].fetch, {'reference':chrom, 'start':start, 'end':end, 'multiple_iterators':True, 'parser':pysam.asTuple()}, col_converter=col_filter)
		q.headers = self.get_headers()
		q.info['dataset'] = self.dataset
		return q

	def query_to_file(self, chrom, start, end, col_filter=list):
		if not chrom in self.r['used_chroms_names']:return ''
		cids = col_filter(range(len(self.r['used_header'][chrom])))
		header = [self.r['used_header'][chrom][i] for i in cids]
		filename = config.TMPDIR[self.dataset] + str(uuid.uuid4())
		f = open(filename, 'w')
		f.write("#" + "\t".join(header) + "\n")
		for line in self.r['tabix_links'][chrom].fetch(chrom, start, end, parser=pysam.asTuple()) :
			f.write('\t'.join([line[i] for i in cids]) + '\n')
		return filename

	def get_headers(self, chrom = ''):
		if not chrom: chrom = self.r['used_chroms_names'][0]
		if not chrom in self.r['used_chroms_names']:
			return {}
		return {i:self.r['used_header'][chrom][i] for i in self.col_filter(range(len(self.r['used_header'][chrom])))}

	def get_des_file_name(self):
		return self.r["des_files"][0]

	def get_data_file_names(self):
		return self.r["used_data_files"]

	def variant_query(self, chrom, start, end):
		pass

if __name__ == "__main__":
	retrieve = Retrieve('HRC')
	print(retrieve)
	page = retrieve.region_query('18',10,100000)
	page = retrieve.region_query('18',10,100000, col_filter=index_get_func([1,2,3]))
	print(page.get_cur_page())
	#print(retrieve.get_headers('18'))
	#print(retrieve.get_data_file_names())
	#filename = retrieve.query_to_file('18',10,100000)
	#print(filename)
	#filename = retrieve.query_to_file('18',10,100000, [0,1,2,3,4,5])
	#print(filename)
	def mg():
		for i in range(10):yield [i] + list(range(8))
	q = QueryResult(mg,{}, col_converter=index_get_func([1,2,3]), page_size=3)
	print(q.total_page)
	print("page 1", q.get_cur_page())
	print("page 1", q.get_page(1))
	print("page 3", q.get_page(3))
	print("page 1", q.get_page(1))
	print("page 4", q.get_page(4))
	
