from mastering.main import *
import xhost
from mastering.callback import *
from mastering.setup import *
from mastering.enet import * 

pose_dict = {"pose1": [], "pose2": []}

def test():
    setup.ip_addr ='192.168.1.71'
    setup.port = 5000
    setup.joint = 2
    function.cur_joint = 1
    sensor_val = [1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    enc = [1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    #function.test_enet(setup.ip_addr, setup.port, function.cur_joint)
    print(get_data_from_res('\r\n'))
#main
test()


