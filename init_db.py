from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from Bio.bgzf import BgzfReader
import gzip, os, fnmatch
import config

def get_single_key(line):
	line = line.split("\t")
	if len(line) > 121:
		if line[120] == '.':return ''
		return line[120]
	return ''

def get_v_id(line):
	line = line.split("\t")
	return ":".join(line[:4])
	
def init_scan_folder(dataset):
	listOfFiles = os.listdir(config.data_dir[dataset])
	gz_pattern = "*.gz"
	data_files = []
	contigs = []
	for entry in listOfFiles:
		if fnmatch.fnmatch(entry, gz_pattern):
			contig = entry.split('.')[0]
			contigs.append(contig)
			data_files.append(config.data_dir[dataset] + entry)
	return contigs, data_files

def init_sqlite_index_tables(contigs, metadata):
	tables = {}
	for i in contigs:
		print("create table for ", i)
		tables[i] = Table(i, metadata,
			Column("vid", String(32), index=True,  primary_key=True),
			Column("rsid", String(32), index=True),
			Column("contig", String(32) ),
			Column("pt", Integer)
		)
	return tables
		
def load_datafile_index(cls, data_file, conn):
	try:
		f = BgzfReader(filename=data_file)
		print("load data index for ", data_file)
		#return
	except:
		print("load data index for ", data_file, "failed")
		return
	f.readline()
	offset = f.tell()
	index_data = {}
	vs = []
	count = 0
	for line in f:
		count += 1
		if count % 100000 == 0:
			print(count)
			conn.execute(cls.insert(), vs)
			vs = []
			#if count > 10000:break
		k1 = get_v_id(line)
		k2 = get_single_key(line)
		value = {'rsid':k2, 'vid':k1, 'contig':line.split("\t")[0], 'pt':offset}
		vs.append(value)
		offset = f.tell()
	conn.execute(cls.insert(), vs)
	#session.add_all(vs)
	#session.commit()

def db_init(anno_data = False):
	contigs, data_files = init_scan_folder("HRC")
	metadata = MetaData()
	engine = create_engine('sqlite:///anno.db')
	metadata.bind = engine
	conn = engine.connect()
	Session = sessionmaker(bind=engine)
	session = Session()
	tables = init_sqlite_index_tables(contigs, metadata)
	if anno_data:
		#create anno index tables
		try:
			for i in tables: tables[i].drop(engine)
		except:
			pass
		metadata.create_all(engine)
		#load anno index data
		for i in range(len(contigs)):
			contig, data_file = contigs[i], data_files[i]
			load_datafile_index(tables[contig], data_file, conn)
	return tables, contigs, data_files
		

if __name__ == "__main__":
	db_init(True)
