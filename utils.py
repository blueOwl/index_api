from uuid import uuid4
import config
def index_get_func(idx):
	valid_idx = []
	def fil(row):
		if len(row) == 0:return []
		nonlocal valid_idx
		if not valid_idx: 
			max_idx = len(row)
			valid_idx = config.DEFAULT_IDXS + \
				    sorted([i for i in idx if i < max_idx if not i in config.DEFAULT_IDXS])
			#print(valid_idx)
		return [row[i] for i in valid_idx]
	return fil

class PageHolder:
	def __init__(self, max_r = 100):
		self.max_r = max_r
		self.id_list = []
		self.d = {}
	def put(self, data):
		data_id = str(uuid4())
		if self.get_length() == self.max_r:
			old_data_id = self.id_list.pop(0)
			del self.d[old_data_id]
		self.id_list.append(data_id)
		self.d[data_id] = data
		return data_id
	def get(self, data_id):
		if not data_id in self.d:
			return 0
		return self.d[data_id]
	def get_length(self):
		return len(self.id_list)

if __name__ == "__main__":
	ph = PageHolder(2)
	id1 = ph.put(1)
	ph.put(1)
	id2 = ph.put(1)
	print(ph.get(id1))
	print(ph.get(id2))
	print("idx", index_get_func([1,2])([4,5,6]))
