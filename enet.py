from . import comm
#import setup
import typing


# type
int_or_str = typing.Union[int, str]


def is_open() -> bool:
	"""
	Returns:
			True		socket is open
			False		socket is not open
	"""
	return comm.is_open()


# functions
def open(ip_addr: str, port_no: int) -> int:
	"""c
	open socket for UDP communication

	Returns:
			0		ok
			-1		error
	"""
	return comm.open(ip_addr, port_no)

def close():
	"""
	close socket
	"""
	print("enet.close()")
	comm.close()


def connect():
    """
	connect socket
	"""
    comm.connect()

def is_connected() -> bool:
	"""
	Returns:
			True		socket is conected
			False		socket is not connected
	"""
	return comm.is_connected()

def req() -> int:
	
	msg = "M0\r\n"

	return comm.send_msg(msg)


def res(timeout: int=-1, addr_on_timeout: int_or_str=-1) -> int:

	"""res() implementation for cont-mode"""
	val = 0
	msg = ""
	msg = comm.recv_msg()
	
	if msg=="res fail":
		val = ENET_ERR_RES_FAIL
	elif msg == "":
		val = ENET_ERR_RES_NONE
	else:
		iret = get_data_from_res(msg)
		val = iret
			
	return val	


	
"""
	brief	"M0,+000012390" 
"""

def get_data_from_res(msg: str) -> int:
	tmp = msg.strip('M0,+') 

	if not tmp[0].isdigit(): return -1
	
	iret= int(tmp)
	#print(iret)
	return iret


ENET_ERR_RES_FAIL = 100000000
ENET_ERR_RES_NONE = -99999998
