import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
page_size = 100	
res_max = 1000 * 1000

data_dir = {"HRC":dir_path + '/data/'}

TMPDIR = {"HRC": dir_path + '/tmp/'}
DOWNLOAD_DIR = ['tmp','data']
HOST = 'http://127.0.0.1:5000'
