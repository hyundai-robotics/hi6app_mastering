""" ArgosX Vision System interface - comm.

@author: 	Jane Doe, BlueOcean Robot & Automation, Ltd.
@created: 	2021-12-10
"""

from typing import Optional
import socket
import xhost

# global variables
raddr : tuple
sock : Optional[socket.socket] = None
buf_size = 0x8000		# 32kb ; permitted packet length
connected_state = False

def is_open() -> bool:
	"""
	Returns:
			True		socket is open
			False		socket is not open
	"""
	return (sock is not None)


def open(ip_addr: str, port: int) -> int:
	"""
	open socket for UDP communication
	Args:
		ip_addr		ip adddress of remote. e.g. "192.168.1.172"
		port			port# of remote. e.g. "192.168.1.172"

	Returns:
			0		ok
			-1		error
	"""
	global raddr, sock
	if sock is not None: return -1
	try:
		raddr = (ip_addr, port)
		sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
		#sock.setblocking(False)
		sock.settimeout(5)
	except socket.error as e:
		print("socket creation or binding error :", e)
		return -1
	#logd('comm.open: ' + str(raddr))
	return 0


def close() -> None:
	global sock, connected_state
	if sock is None: return
	#logd('comm.close')
	sock.close()
	sock = None
	connected_state = False

def connect():
	global sock, raddr, connected_state
	connected_state = True
	if sock is None: 
		connected_state = False 
		return 

	try:
		sock.connect(raddr)
	except BlockingIOError:
		connected_state = False
		return
	except socket.error as e:
		connected_state = False
		return 
		
	return 


def is_connected() -> bool:
	"""
	Returns:
			True		socket is connected
			False		socket is not connected
	"""
	return connected_state


def send_msg(msg: str) -> int:
	"""
	send msg to sock, raddr
	Args:
		msg

	Returns:
			>=0	the number of bytes sent
			-1		no socket. init() should be called.
	"""
	if sock is None: return -1

	try:
		#logd('request : ' + msg)
		bts = bytearray(str.encode(msg))
		return sock.sendto(bts, raddr)
	except:
		print('except send_msg()')
		return 0


def recv_msg():
	"""
	wait msg from sock
	Returns:
		received string
	"""
	if sock is None: return ""

	try:
		data, ip_port = sock.recvfrom(buf_size)
		bts = bytearray(data)
		msg = bts.decode()
		#logd('response: ' + msg)
		return msg
	except BlockingIOError:
		#print('BlockingIOError')
		return ""
	except Exception as e:
		print('exception from recv_msg(): ' + str(e))
		return ""


def logd(text: str):
	print(text)
	xhost.printh(text)

