from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
#from Bio.bgzf import *
from init_db import *
from init_gene import *
import Bio

import gzip

engine = create_engine('sqlite:///anno.db?check_same_thread=False')
Session = sessionmaker(bind=engine)
session = Session()

tables, contigs, data_files = db_init()
def find_gene(g):
	print("search gene", g)
	res = session.query(
			GeneMapping, Gene
		).filter(
			GeneMapping.mapping_name == g
		).filter(
			GeneMapping.unprot_name == Gene.unprot_name
		).first()
	res = res[1]
	return [res.contig, res.start, res.end]
	return []
def key_get(k, filter_fun=list):
	res = ''
	for i in tables:
		table = tables[i]
		try:	
			if k[:2] == 'rs':
				res = session.query(table).filter(table.c.rsid==k).one()
			else:
				res = session.query(table).filter(table.c.vid==k).one()
			if res: break
		except:
			pass
	if not res : 
		return filter_fun('')
	offset = int(res[3])
	data_file = Bio.bgzf.BgzfReader(filename=data_files[contigs.index(i)])
	#print('s')
	#print(offset)
	#print(data_files[contigs.index(i)])
	data_file.seek(offset)
	#print('e')
	data = filter_fun(data_file.readline().rstrip().split('\t'))
	return data
	
def multi_vk_get(contig, ks, filter_fun=list):
	table = tables.get(contig)
	if table == None:return filter_fun('')
	res = []
	for v in ks :
		qr = session.query(table).filter(table.c.vid == v ).one()
		if qr: res.append(qr)
	if not res :
		return filter_fun('')
	offsets = [int(i[3]) for i in res]
	data_file = Bio.bgzf.BgzfReader(filename=data_files[contigs.index(contig)])
	data = []
	for o in offsets:
		data_file.seek(o)
		data.append(filter_fun(data_file.readline().rstrip().split('\t')))
	return data
	
def intersect_vcf(vcf, filter_fun=list):
	ks = {}
	count = 0
	for i in vcf:
		i = i.decode('utf-8')
		count += 1
		if count > 10000:
			break
		if not i: continue
		if i[0] == "#": continue
		l = i.rstrip().split('\t')
		if not l:continue
		k = ':'.join([l[0], l[1], l[3], l[4]])
		if l[0] in ks:
			ks[l[0]].append(k)
		else:
			ks[l[0]] = [k]
	res = []
	for contig in ks:
		res += multi_vk_get(contig, ks[contig], filter_fun)
	return res
	

	
if __name__ == "__main__":
	id2 = 'rs111739080'
	id1 = 'rs146658581'
	gene1 = 'A6NKL6'
	gene2 = 'Q9H324'
	print(find_gene(gene1))
	print(find_gene(gene2))
	#res = key_get(id1, list)
	#print(res)
#session.query(tables['18']).filter(tables['18'].c.rsid==id1).one()
