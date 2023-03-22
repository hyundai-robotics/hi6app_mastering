from pickle import PROTO, encode_long
from sys import intern
from . import enet 
import xhost
import json 
from enum import Enum
from time import sleep

from .callback import *

import threading

class comm_state(Enum):
    send = 0
    recv = 1

fin_enc_offset = 0

motor_off_chk = 0 
stop_chk = 0 # stop = 1
end_chk = 0
cur_joint = 0

cur_sensor_list1 = []
min_sensor_list1 = [] 
cur_sensor_list2 = []
min_sensor_list2 = []
min_enc_list1 = []
min_enc_list2 = []
fin_enc_1 = 0
fin_enc_2 = 0

cur_pose_list = []
origin_pose_list = []
pose_dict = {"pose1": [], "pose2": []}
init_pose = ''
pose1 = ''
pose2 = ''
origin_pose = ''

enet_state = comm_state.send

delay_cnt = 0   
process_status = 'Standby'

ip_addr_param = ''
port_param = 0
con_cnt = 0
cor_final_ofs = 0

EXECUTION_STATUS = 0

CUR_STATUS = 1
INIT_STATUS = 1
MOTOR_CHK_STATUS = 2
MK_POSES_STATUS = 3

EXE_INIT_POSE_CMD_STATUS = 4
INITP_FINISH_CHK_STATUS = 5

ENET_CONNECT_STATUS = 6

EXE_P1_CMD_STATUS = 7
P1_FINISH_CHK_STATUS = 8

EXE_P2_CMD_STATUS = 9
P2_FINISH_CHK_STATUS = 10

EXE_ORIGIN_POSE_STATUS = 11
ORIGINP_FINISH_CHK_STATUS = 12 

FIND_ENC_OFS_STATUS = 13
FILE_SAVED_STATUS = 14
END_EXE_STATUS = 15
ERROR_STATUS = 16
SET_ENC_OFS_STATUS = 17

err_num = 0

def startTimer():
    #print("Timer")
    timer = threading.Timer(0.0025, startTimer)
    timer.start()

def on_period_low() -> None:
    global err_num, cur_joint, ip_addr_param, port_param, fin_enc_offset, process_status
    global EXECUTION_STATUS, CUR_STATUS, cur_sensor_list1, min_enc_list1, cur_sensor_list2, min_enc_list2
    iRet = OK
    if EXECUTION_STATUS == 1:
        if CUR_STATUS == INIT_STATUS:
            CUR_STATUS = MOTOR_CHK_STATUS

        elif CUR_STATUS == MOTOR_CHK_STATUS:
            print("---------- motor chk----------")
            iRet = get_motor_state()
            if iRet < 0: 
                err_num = iRet 
                CUR_STATUS = ERROR_STATUS
                return

            CUR_STATUS = MK_POSES_STATUS

        elif CUR_STATUS == MK_POSES_STATUS:
            print("---------- make poses ----------")
            make_pose_init_state(cur_joint)
            CUR_STATUS = EXE_INIT_POSE_CMD_STATUS

        elif CUR_STATUS == EXE_INIT_POSE_CMD_STATUS:
            print("---------- go to initial pose ----------")
            process_status = 'move to initial pose'
            iRet = post_execute_move(0,init_pose)
            if iRet < 0: 
                err_num = iRet
                CUR_STATUS = ERROR_STATUS
                return
            CUR_STATUS = INITP_FINISH_CHK_STATUS
        
        elif CUR_STATUS == INITP_FINISH_CHK_STATUS:
            iRet = finish_chk_initial_pose()
            if iRet < 0:
                err_num = iRet
                CUR_STATUS = ERROR_STATUS
                return
            elif iRet == INITP_FINISH_CHK_STATUS:
                return
            else:
                CUR_STATUS = ENET_CONNECT_STATUS

        elif CUR_STATUS == ENET_CONNECT_STATUS:
            process_status = 'tcp/ip connection..'
            iRet = connect_enet(ip_addr_param, port_param)
            if iRet < 0: 
                err_num = iRet
                CUR_STATUS = ERROR_STATUS
                return
            elif iRet == ENET_CONNECT_STATUS: 
                return
            else: 
                CUR_STATUS = EXE_P1_CMD_STATUS

        elif CUR_STATUS == EXE_P1_CMD_STATUS:
            process_status = 'move to P1'
            print("------------start exe P1 --------------")
            iRet = post_execute_move(1, pose1)
            if iRet < 0:
                err_num = iRet 
                CUR_STATUS = ERROR_STATUS
                return
            CUR_STATUS = P1_FINISH_CHK_STATUS

        elif CUR_STATUS == P1_FINISH_CHK_STATUS:
            iRet = exe_move_p1()
            if iRet < 0:
                err_num = iRet 
                CUR_STATUS = ERROR_STATUS
                return
            elif iRet == P1_FINISH_CHK_STATUS: 
                return
            else:
                CUR_STATUS = EXE_P2_CMD_STATUS

        elif CUR_STATUS == EXE_P2_CMD_STATUS:
            process_status = 'move to P2'
            print("------------start exe P2 --------------")
            iRet = post_execute_move(1, pose2)
            if iRet < 0:
                err_num = iRet 
                CUR_STATUS = ERROR_STATUS
                return
            CUR_STATUS = P2_FINISH_CHK_STATUS    

        elif CUR_STATUS == P2_FINISH_CHK_STATUS:
            iRet = exe_move_p2()
            if iRet < 0:
                err_num = iRet 
                CUR_STATUS = ERROR_STATUS
                return
            elif iRet == P2_FINISH_CHK_STATUS:
                return
            else:
                CUR_STATUS = EXE_ORIGIN_POSE_STATUS  

        elif CUR_STATUS == EXE_ORIGIN_POSE_STATUS:
            process_status = 'move to origin pose'
            print("------------origin pose--------------")
            iRet = post_execute_move(0, origin_pose)
            if iRet < 0:
                err_num = iRet 
                CUR_STATUS = ERROR_STATUS
                return
            CUR_STATUS = ORIGINP_FINISH_CHK_STATUS   

        elif CUR_STATUS == ORIGINP_FINISH_CHK_STATUS:
            iRet = goto_origin_pose(cur_joint)
            if iRet < 0:
                err_num = iRet 
                CUR_STATUS = ERROR_STATUS
                return
            elif iRet == ORIGINP_FINISH_CHK_STATUS:
                return
            else:
                CUR_STATUS = FIND_ENC_OFS_STATUS

        elif CUR_STATUS == FIND_ENC_OFS_STATUS:
            print("------------find enc ofs--------------")
            iRet = find_encoder_offset_value()
            if iRet == ERROR_TWO_VAL_CHK:
                err_num = iRet 
                CUR_STATUS = ERROR_STATUS
                return
            else: 
                fin_enc_offset = iRet
            CUR_STATUS = FILE_SAVED_STATUS

        elif CUR_STATUS == FILE_SAVED_STATUS:
            print("------------file saved--------------")
            make_file(cur_sensor_list1, min_enc_list1, cur_sensor_list2, min_enc_list2)
            CUR_STATUS = SET_ENC_OFS_STATUS

        elif CUR_STATUS == SET_ENC_OFS_STATUS:
            process_status = 'apply corrected enc offset'
            print('-----------apply encoder offset-------------')
            get_general_enc_ofse()
            CUR_STATUS = END_EXE_STATUS

        elif CUR_STATUS == END_EXE_STATUS:
            process_status = 'mastering end'
            EXECUTION_STATUS = 0
            clear_vars()
            enet.close()
            CUR_STATUS = INIT_STATUS 
        
        elif CUR_STATUS == ERROR_STATUS:
            process_status = get_error_msg(err_num)
            print("-----error status: %d-----" %err_num)
            EXECUTION_STATUS = 0
            clear_vars()
            enet.close()
            CUR_STATUS = INIT_STATUS
            return     
    else: pass
    
    return



def connect_enet(ip_addr_param:str, port_param:int)-> int:
    global con_cnt
    print("------------enent connect--------------")
    if enet.is_connected() == False:
        if enet.is_open():
            pass 
        elif enet.open(ip_addr_param, port_param) == -1:
            print('enet open error')
            return ERROR_TCP_CONNECT
        enet.connect()
        #sleep(0.1)
        con_cnt = con_cnt + 1
        if con_cnt > 4: 
            con_cnt = 0
            return ERROR_TCP_CONNECT
    else: 
        return OK

    return ENET_CONNECT_STATUS

def get_setting_data(ip_addr: str, port: int, jo_num: int) -> None:
    global cur_joint, ip_addr_param, port_param
    
    cur_joint = jo_num
    ip_addr_param = ip_addr
    port_param = port

    return


def execution(ip_addr: str, port: int, jo_num: int) -> int:
    global EXECUTION_STATUS
    global cur_joint, fin_enc_offset, process_status
    global cur_sensor_list1, cur_sensor_list2
    print("------------set param--------------")
    get_setting_data(ip_addr, port, jo_num)
    print("------------start execution--------------")
    EXECUTION_STATUS = 1

    return OK

def make_pose_init_state(jo_num) -> int:
    global cur_pose_list, origin_pose_list, init_pose, origin_pose
    cur_pose_list = get_cur_pose()

    origin_pose_list = cur_pose_list.copy()
    origin_pose_list.append('\\"encoder\\"')
    origin_pose = list_to_str(origin_pose_list)

    #초기자세 이동속도 정해야함
    target_enc = get_rtoe_conv(jo_num, -1.5, 1)
    
    cur_pose_list[jo_num] = cur_pose_list[jo_num] + target_enc
    make_target_position(jo_num)

    cur_pose_list.append('\\"encoder\\"')
    init_pose = list_to_str(cur_pose_list)

    return OK

def finish_chk_initial_pose()->int:  
    if end_chk == 0:
        if stop_chk == 1:
            chk_move_finished(cur_pose_list)
        if motor_off_chk == 1: return ERROR_MOTOR_OFF_CHK

    else:
        init_end_chk()
        sleep(0.2)
        return OK 

    return INITP_FINISH_CHK_STATUS



def exe_move_p1() -> int:
    global pose1, cur_sensor_list1, min_enc_list1, fin_enc_1, pose_dict
    global end_chk, stop_chk

    iRet = 0

    if end_chk == 0:
        if stop_chk == 1: 
            chk_move_finished(pose_dict["pose1"])
        if motor_off_chk == 1: return ERROR_MOTOR_OFF_CHK
        iRet = commu_sensor(1)
        if iRet < 0 : return iRet
    else:
        init_end_chk()
        iRet = find_min_value(cur_sensor_list1, min_enc_list1)
        if iRet < 0 : return iRet
        else: 
            fin_enc_1 = iRet
            sleep(0.2)
        return OK

    return P1_FINISH_CHK_STATUS 


def exe_move_p2() -> int:
    global pose2, cur_sensor_list2, min_enc_list2, fin_enc_2, delay_cnt
    iRet = 0

    if end_chk == 0:
        if stop_chk == 1:
            chk_move_finished(pose_dict["pose2"])
        if motor_off_chk == 1: return ERROR_MOTOR_OFF_CHK
        iRet = commu_sensor(2)
        if iRet < 0 : return iRet
    
    else: 
        init_end_chk()
        iRet = find_min_value(cur_sensor_list2, min_enc_list2)
        if iRet < 0 : return iRet
        else: 
            fin_enc_2 = iRet
            sleep(0.2)
        return OK

    return P2_FINISH_CHK_STATUS 

def chk_valid_two_values(min1: float,min2: float)-> int:
    if min1 > 0.0 and min2 > 0.0 :
        return OK
    else:
        return ERROR_TWO_VAL_CHK

def commu_sensor(play_num: int):
    global enet_state, pose1, pose2, cur_sensor_list1, min_enc_list1, cur_sensor_list2, min_enc_list2 
    iRet = OK 
    enet.req()
    if play_num == 1:
        iRet = update_data(enet.res(), cur_sensor_list1, min_enc_list1)
        if iRet == ERROR_TCP_RES_NULL or iRet == ERROR_TCP_RES_FAIL:
            return iRet 
    elif play_num == 2:
        iRet = update_data(enet.res(), cur_sensor_list2, min_enc_list2)
        if iRet == ERROR_TCP_RES_NULL or iRet == ERROR_TCP_RES_FAIL:
            return iRet 

    return iRet


def post_execute_move(flag: int, in_pose: str) -> int: 
    url = "project/context/tasks[0]/execute_move"
    exe_init_pos = ''
 
    if flag == 1:
        exe_init_pos = '{"stmt" : "move P,spd=10sec,accu=0,tool=1  ['+str(in_pose)+']"} '
    elif flag == 0:
        exe_init_pos = '{"stmt" : "move P,spd=5%,accu=0,tool=1  ['+str(in_pose)+']"} '
    elif flag == 2:
        exe_init_pos = '{"stmt" : "move P,spd=100mm/sec,accu=0,tool=1  ['+str(in_pose)+']"} '
    
    res_json = xhost.post(url, exe_init_pos)
    msg = json.loads(res_json)
    print(in_pose)
    ecode = msg['ecode']

    return ecode


def get_axis_value(jo_num: int)->dict:
    global res_enc_cur
    
    url = "project/robot/joints/monitor_axis"
    query = '{"axis_no": %d}'%(jo_num + 1)
    
    res_json = xhost.get(url, query)
    cur_axis_data = json.loads(res_json)
    
    return cur_axis_data


def get_cur_pose()-> list:
    global res_enc_pose  
    url = "project/robot/po_cur"
    res_json = xhost.get(url)
    msg = json.loads(res_json)
    
    cur_pose = msg['enc_cur']
    return cur_pose

def update_data(cur_value: int, sensor: list, enc: list) ->int:
    global cur_joint

    if cur_value == 100000000:
        return ERROR_TCP_RES_FAIL
    elif cur_value == -99999998:
        return ERROR_TCP_RES_NULL

    sensor.append(cur_value)

    axis_data = get_axis_value(cur_joint)
    cur_enc = axis_data['enc_cur']
    enc.append(cur_enc)
    
    return OK

def chk_sensor_threshold(sen_list: list) -> int:
    under_thre = 1400 
    upper_thre = 2500

    min_sen = min(sen_list)
    aver_sen = sum(sen_list) / len(sen_list)
    
    print("aver_sen: %d, aver_sen- thre : %d " %(aver_sen, abs(aver_sen-min_sen)))
    if abs(aver_sen-min_sen) < under_thre or abs(aver_sen-min_sen) > upper_thre:
        return ERROR_VAL_THRESHOLD
    

    return OK


def make_target_position(jo_num:int):
    global cur_pose_list, pose1, pose2, pose_dict
    pose1_list = cur_pose_list.copy()
    pose2_list = cur_pose_list.copy()
    
    target_enc_p1 = get_rtoe_conv(jo_num, +3.0, 1)
    
    pose1_list[jo_num] = pose1_list[jo_num] + target_enc_p1

    pose1_list.append('\\"encoder\\"')
    pose2_list.append('\\"encoder\\"')

    pose_dict["pose1"] = pose1_list
    pose_dict["pose2"] = pose2_list

    pose1 = list_to_str(pose1_list)
    pose2 = list_to_str(pose2_list)
    return 

def list_to_str(in_list:list)->str:
    out_str = ''
    out_str = ",".join([str(i) for i in in_list])

    return out_str

def find_min_value(sensor_val: list, enc: list) -> int:
    sum_min_enc = 0 
    cnt = 0
    if len(sensor_val) == 0: return ERROR_NO_SENSOR_VALS
    elif len(enc) == 0: return ERROR_NO_ENC_VALS

    min_sensor = min(sensor_val)
    print("min_sensor: %d" %min_sensor)
    iRet= chk_sensor_threshold(sensor_val)
    if iRet < 0: return iRet
    
    for i in range(len(sensor_val)):
        if sensor_val[i] == min_sensor:
            sum_min_enc += enc[i]
            cnt = cnt + 1

    aver_min_enc = sum_min_enc / cnt
    print("aver_min_enc: %d " %aver_min_enc)
    return int(aver_min_enc)


def get_rtoe_conv(jo_num:int, angle: float, incremental: int) -> int:
   
   angle_rad = angle/180*3.141592 
   url = "project/robot/joints/rtoe_conv"
   query = '{"axis_no": %d, "rad_val" : %f,"incremental": %d}'%(jo_num + 1, angle_rad, incremental)
   res_json = xhost.get(url, query)
   msg = json.loads(res_json)

   enc_val = msg['enc_val']
   
   return enc_val


def get_etor_conv(jo_num:int, enc_val: int, incremental: int) -> int:
   
   url = "project/robot/joints/etor_conv"
   query = '{"axis_no": %d, "enc_val" : %f,"incremental": %d}'%(jo_num + 1, enc_val, incremental)
   res_json = xhost.get(url, query)
   msg = json.loads(res_json)

   enc_val = msg['rad_val']
   
   return enc_val


def chk_move_finished(target_pose:list):
    global cur_joint, end_chk, delay_cnt

    axis_data = get_axis_value(cur_joint)
    cmd_enc = axis_data['enc_cmd']

    if target_pose[cur_joint] == cmd_enc:
        #delay_cnt = delay_cnt + 1
        #if delay_cnt > 500:
            print('end_chk = 1')
        #    print('activate end chk')
            end_chk = 1
        #    delay_cnt = 0

    return

def chk_move_finished_ofs(target_pose:list):
    global cur_joint, end_chk, delay_cnt

    axis_data = get_axis_value(cur_joint)
    cmd_enc = axis_data['enc_cmd']

    if target_pose[cur_joint] == cmd_enc:
        delay_cnt = delay_cnt + 1
        if delay_cnt > 500:
            print('end_chk = 1')
            print('activate end chk')
            end_chk = 1
            delay_cnt = 0

    return

def init_end_chk():
    global end_chk, stop_chk
    end_chk = 0
    stop_chk = 0
    return

def find_encoder_offset_value() -> int:
    global fin_enc_1, fin_enc_2
    iRet = chk_valid_two_values(fin_enc_1, fin_enc_2)
    if iRet < 0: return iRet

    fin_enc = int((fin_enc_1 + fin_enc_2)/2)
    print("fin_enc_1: %d fin_enc_2:%d aver_min_enc: %d" %(fin_enc_1, fin_enc_2, fin_enc))
    iRet = fin_enc - 4194304 #400000[hex]
    
    return iRet

"""
    API response :모션의 모터온 상태 체크
    (0:On, 1: Busy, 2: Off)
"""
def get_motor_state()-> int:
    iRet = OK
    url = "project/robot/motor_on_state"
    res_json = xhost.get(url)
    msg = json.loads(res_json)
    val = msg['val']
    ival = int(val)
    if ival > 0: iRet = ERROR_MOTOR_ON_CHK
    return iRet

    
def goto_origin_pose(jo_num:int)->int:
    if end_chk == 0:
        if stop_chk == 1:
            chk_move_finished(origin_pose_list)
        if motor_off_chk == 1: return ERROR_MOTOR_OFF_CHK

    else: 
        init_end_chk()    
        return OK
    return ORIGINP_FINISH_CHK_STATUS

def goto_ofs_pose(jo_num:int)->None:
    global process_status
    ofs_pose_list = get_cur_pose()
    ofs_pose_list[jo_num] = 4194304 #400000 
    
    iRet = 0

    ofs_pose_list.append('\\"encoder\\"')
    ofs_pose = list_to_str(ofs_pose_list)

    iRet = post_execute_move(2,ofs_pose)
    if iRet < 0: 
        process_status = get_error_msg(iRet)
        return
    
    while end_chk == 0:
        if stop_chk == 1:
            chk_move_finished_ofs(ofs_pose_list)
        if motor_off_chk == 1: 
            iRet = ERROR_MOTOR_OFF_CHK
            process_status = get_error_msg(iRet)
            return 

    init_end_chk()
    process_status = 'reached the offset pose'
    return

def clear_vars():
    global stop_chk, end_chk, cur_sensor_list1, min_enc_list1, cur_sensor_list2, min_enc_list2, pose1_list, pose2_list, enet_state
    global min_sensor_list1, min_sensor_list2, fin_enc_1, fin_enc_2, cur_pose_list, origin_pose_list, con_cnt
     
    stop_chk = 0 # stop = 1
    end_chk = 0
    con_cnt = 0
    cur_sensor_list1 = []
    min_sensor_list1 = [] 
    cur_sensor_list2 = []
    min_sensor_list2 = []
    min_enc_list1 = []
    min_enc_list2 = []
    fin_enc_1 = 0
    fin_enc_2 = 0
    pose1_list = ''
    pose2_list = ''
    cur_pose_list = []
    origin_pose_list = []
    enet_state = comm_state.send

    return

def make_file(list1: list, list2: list, list3: list, list4: list):
    gather_path = 'mastering_gather.txt'
    pathname = xhost.abs_path('project') + gather_path
    length_list = [len(list1),len(list3)]
    length = min(length_list)

    with open(pathname, 'w') as file: 
        print('file open')

        for i in range(0, length):
            data = "%d, %d, %d, %d" %(list1[i], list2[i], list3[i], list4[i])
            file.write(data)
            file.write('\n')
  
    file.close()
    
    return


def get_encoder_offset(jo_num: int) -> int:
	url = "project/robot/joints/j_%d/enc_ofs" %jo_num
	res_json = xhost.get(url, "")
	jo_enc_data = json.loads(res_json)
	return jo_enc_data


def get_general_enc_ofse() -> int:
	global cor_final_ofs
	cor_final_ofs = fin_enc_offset
	cor_enc = get_encoder_offset(cur_joint + 1) + cor_final_ofs
	
	print("J%d cor_final_ofs %d" %(cur_joint + 1, cor_final_ofs))
	
	url = "project/robot/joints/j_%d" %(cur_joint + 1)
	jv = '{"enc_ofs" : %d}' %cor_enc
	res_json = xhost.put(url, jv)

	url = "project/robot/joints/post_update_enc_ofs"
	res_json = xhost.post(url, "")
    
	url = "project/save_dom_to_file"
	res_json = xhost.post(url, "")

	url = "project/robot/joints/enc_ofs_exit"
	res_json = xhost.put(url, "")

	print('get_general_enc_ofse()')

	return 0


def get_error_msg(in_num: int) -> str:
    error_msg = ''
    if in_num == ERROR_MOTOR_ON_CHK:
        error_msg = 'ERROR_MOTOR_ON_CHK'
    elif in_num == ERROR_MOTOR_OFF_CHK:
        error_msg = 'ERROR_MOTOR_OFF_CHK'
    elif in_num == ERROR_VAL_THRESHOLD:
        error_msg = 'ERROR_VAL_THRESHOLD'    
    elif in_num == ERROR_TWO_VAL_CHK:
        error_msg = 'ERROR_TWO_VAL_CHK'
    elif in_num == ERROR_NO_SENSOR_VALS:
        error_msg = 'ERROR_NO_SENSOR_VALS'
    elif in_num == ERROR_NO_ENC_VALS:
        error_msg = 'ERROR_NO_ENC_VALS'
    elif in_num == ERROR_TCP_RES_FAIL:
        error_msg = 'ERROR_TCP_RES_FAIL'
    elif in_num == ERROR_TCP_RES_NULL:
        error_msg = 'ERROR_TCP_RES_NULL'
    elif in_num == ERROR_TCP_CONNECT:
        error_msg = 'ERROR_TCP_CONNECT'
    elif in_num == ERROR_PLAYBACK:
        error_msg = 'ERROR_PLAYBACK'
    else:
        error_msg = str(in_num)
    return error_msg

OK = 0
ERROR_MOTOR_ON_CHK = -1
ERROR_MOTOR_OFF_CHK = -2
ERROR_VAL_THRESHOLD = -3
ERROR_TWO_VAL_CHK = -4
ERROR_NO_SENSOR_VALS = -5
ERROR_NO_ENC_VALS = -6
ERROR_TCP_RES_FAIL = -7
ERROR_TCP_RES_NULL = -8
ERROR_TCP_CONNECT = -9
ERROR_PLAYBACK = -1442080