from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from Bio.bgzf import *
from init_db import *
from init_gene import *

import gzip

engine = create_engine('sqlite:///anno.db?check_same_thread=False')
Session = sessionmaker(bind=engine)
session = Session()

tables, contigs, data_files = db_init()
def find_gene(g):
	try:
		res = session.query(
				GeneMapping, Gene
			).filter(
				GeneMapping.mapping_name == g
			).filter(
				GeneMapping.unprot_name == Gene.unprot_name
			).one()
		res = res[1]
		return [res.contig, res.start, res.end]
	except:
		return []
def key_get(k, filter_fun):
	res = ''
	for i in tables:
		table = tables[i]
		try:	
			if k[:2] == 'rs':
				res = session.query(table).filter(table.c.rsid==k).one()
			else:
				res = session.query(table).filter(table.c.vid==k).one()
			break
		except:
			pass
	if not res : 
		pass
		#return filter_fun('')
	offset = int(res[3])
	data_file = BgzfReader(filename=data_files[contigs.index(i)])
	#print('s')
	data_file.seek(offset)
	#print('e')
	data = filter_fun(data_file.readline().rstrip().split('\t'))
	return data
if __name__ == "__main__":
	id2 = 'rs111739080'
	id1 = 'rs146658581'
	gene1 = 'XP_001621175'
	gene2 = 'NP_006834'
	#print(find_gene(gene1))
	#print(find_gene(gene2))
	res = key_get(id1, list)
	print(res)
#session.query(tables['18']).filter(tables['18'].c.rsid==id1).one()
