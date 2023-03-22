
from .callback import *
from .setup import *
from .function import *

def attr_names() -> tuple:
	"""Returns the names of the attributes to be exposed."""
	return ("ip_addr", "port")


def on_app_init() -> int:
   """(callback) called just after self-diagnosis
   Returns:
      0
   """
   print('[mastering] on_app_init();')
   setup.load_from_setup_file()
   #xhost.io_assign_set_out_bit(setup.sigcode_err)
   #function.startTimer()
   return 0


