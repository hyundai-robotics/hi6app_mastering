""" robot application - argosx - setup

@author: 	Jane Doe, BlueOcean Robot & Automation, Ltd.
@created: 	2021-12-06
"""

import xhost
import json
#from . import enet 
from . import function

fname_setup = 'mastering.json'

def get_general_def() -> dict:
	"""
	Returns:
		default value of setting
	"""
	print('def_general_def()')

	data_def = {
		'ip_addr': '192.168.1.71',
		'port' : 5000,
		'joint': 1,
		'cor_ofs' : 0
	}
	
	return data_def


def get_general() -> dict:
	"""
	Returns:
		setting dict.
	"""
	print('get_general()')
	global cor_ofs, play_status
	
	ret = {}
	ret["ip_addr"] = ip_addr
	ret["port"] = port
	ret["joint"] = joint
	#ret["cor_ofs"] = function.cor_final_ofs
	#ret["play_status"] = play_status
	return ret

	
def put_general(body: dict) -> int:
	"""
	Args:
		body	setting dict.
	
	Returns:
		0
	"""
	global ip_addr, port, joint, cor_ofs
	print('put_general()')

	ip_addr = body["ip_addr"]
	port = body["port"]
	joint = body["joint"]
	#cor_ofs = body["cor_ofs"]
	
	save_to_setup_file(body) # save to file
	
	return 0


def load_from_setup_file() -> int:
	"""
	load setup file
	Returns:
			0		ok
			-1		error
	"""
	global ip_addr, port, joint, cor_ofs
	
	pathname = xhost.abs_path('project') + fname_setup
	try:
		with open(pathname, 'r') as file:
			data = json.load(file)
			ip_addr = data['ip_addr']
			port = data['port']
			joint = data['joint']
			#cor_ofs = data["cor_ofs"]
	except:
		print('file not found: ', pathname)
		return -1
	return 0


def save_to_setup_file(body: dict) -> int:
	"""
	save to setup file
	Returns:
			0		ok
			-1		error
	"""
	pathname = xhost.abs_path('project') + fname_setup
	try:
		with open(pathname, 'w') as file:
			json.dump(body, file, indent='\t')
	except:
		print('failed in file writing: ', pathname)
		return -1
	return 0



gen_def = get_general_def()
ip_addr : str = gen_def['ip_addr']
port : int = gen_def['port']
joint : int = gen_def['joint']
cor_ofs : int = gen_def['cor_ofs']
play_status = 'Standby'

def get_general_exe() -> int:
	global ip_addr, port, joint,play_status
	function.execution(ip_addr, port, joint-1)
	return 0


def get_general_ofs_pose() -> int:
	function.goto_ofs_pose(joint-1)
	print('get_general_ofs_pose()')
	return 0

def get_general_process_status() -> dict:	
	"""
	Returns:
		setting dict.
	"""
	#print('!!!!!!get_general_process_status()')
	#print(function.process_status)
	global play_status
	ret = {}
	ret["play_status"] = function.process_status
	ret["cor_ofs"] = function.cor_final_ofs

	return ret
