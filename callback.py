from . import setup
from . import function


def on_motor_on() -> int:
   """(callback) on motor-on
   Returns: 0
   """
   function.motor_off_chk = 0
   print('on_motor_on')
   return 0
 
 
def on_motor_off() -> int:
   """(callback) on motor-off
   Returns: 0
   """
   function.motor_off_chk = 1
   print('on_motor_off')
   return 0

 
def on_stop(lTask:int) -> None:
   """(callback) on motor-on
   Returns: 0
   """
   function.stop_chk = 1
   
   print('on_stop: %d' %function.stop_chk)

   return


