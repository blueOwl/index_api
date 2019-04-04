from Bio.bgzf import *

f = BgzfReader("data/18.annotated.snp.withPanther.gz")
for i in range(300000):
	r = f.readline()
offset = f.tell()
l = f.readline()
f = BgzfReader("data/18.annotated.snp.withPanther.gz")
print('s', offset)
f.seek(offset)
print('s')
f.readline()
