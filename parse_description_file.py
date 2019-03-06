from retrieve import Retrieve
import config

class Annotation_tree_node:
	def __init__(self, nid=0, parent_id=0, info='', name="root"):
		self.id = nid
		self.parent_id = parent_id
		self.info = info
		self.name = name
	def get_dic(self):
		return {'id' : self.id,
			'name' : self.name,
			'detail' : self.info,
			'parent_id' : self.parent_id} 

def parse_des_file(filename):
	f = open(filename)
	item =''
	items = []
	for i in f:
		line = i.rstrip()
		if line == "":continue
		if line[0] != "\t":continue
		if line[:2] == "\t\t": 
			item += " 	" + line[2:]
			continue
		if line[0] == "\t":
			if item == "":
				item += line[1:]
			else:
				items.append(item)
				item = line[1:]
	des = {}
	for i in items:
		item = i.split(":")
		key, info = item[0], item[1]
		des[key] = info
	return des


def generate_tree_dic(headers, des):
	root = Annotation_tree_node(parent_id=None)
	tree_dic = {'root':root}
	parent_id_count = len(headers.keys())
	for i in headers:
		nid = i
		name = headers[i]
		if headers[i] in des:
			info = des[headers[i]]
		else: 
			info = ''
			continue
		if "_" in name:
			parent_name = name.split('_')[0]
			if parent_name in tree_dic:
				parent_id = tree_dic[parent_name].id
			else:
				#make parent node
				parent = Annotation_tree_node(nid=parent_id_count, name=parent_name)
				tree_dic[parent_name] = parent
				parent_id = parent_id_count
				parent_id_count += 1
			node = Annotation_tree_node(nid=nid, parent_id=parent_id, name=name, info=info)
			tree_dic[name] = node
		else:
			#single node
			node = Annotation_tree_node(nid=nid, name=name, info=info, parent_id=root.id)
			tree_dic[name] = node
	return tree_dic


def get_anno_tree_dic(dataset):
	retrieve = Retrieve(dataset)
	des = parse_des_file(config.data_dir[dataset] + retrieve.get_des_file_name())
	headers = retrieve.get_headers()
	tree_dic = generate_tree_dic(headers, des)
	return tree_dic

if __name__ == "__main__":
	tree_dic = get_anno_tree_dic("HRC")
	for k in tree_dic:
		print(tree_dic[k].get_dic())
	#for i in range(len(items)):
	#	print(i, items[i])
	#for k in sorted(des.keys()):print(k)
	#print headers
