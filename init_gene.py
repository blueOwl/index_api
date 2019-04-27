from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import gzip, os, fnmatch
import config

Base = declarative_base()
class Gene(Base):
	__tablename__ = 'gene'
	unprot_name = Column(String, index=True, primary_key=True)
	contig = Column(String)
	start = Column(String)
	end = Column(String)

class GeneMapping(Base):
	__tablename__ = 'mapping'
	id = Column(Integer, primary_key=True)
	unprot_name = Column(String, index=True )
	mapping_name = Column(String, index=True)

def parse_gene_name(line):
	gn = line.split("\t")[0]
	st = gn.find("UniProtKB=")
	return gn[st + 10:]

def load_gene_data(datafile, session):
	f = open(datafile)
	data = []
	for i in f:
		gn = parse_gene_name(i)
		line = i.rstrip().split("\t")
		contig, start, end = line[1], line[2], line[3]
		data.append(Gene(unprot_name=gn, contig=contig, start=start, end=end))
	session.add_all(data)
	session.commit()

def load_mapping_data(datafile, session):
	f = open(datafile)
	data = []
	for i in f:
		line = i.rstrip().split("\t")
		unprot_name, mapping_name = line[0], line[1]
		data.append(GeneMapping(unprot_name=unprot_name, mapping_name=mapping_name))
	session.add_all(data)

if __name__ == "__main__":
	engine = create_engine('sqlite:///anno.db')
	Session = sessionmaker(bind=engine)
	session = Session()
	Base.metadata.create_all(engine, tables=[Gene.__table__, GeneMapping.__table__])
	print('load gene data')
	#load_gene_data(config.gene_data, session)
	load_mapping_data(config.mapping_data, session)
	pass
