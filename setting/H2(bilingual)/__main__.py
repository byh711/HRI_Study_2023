# -*- coding:utf-8 -*-
'''
this file provides speech capabilities to a character playing "Don't starve together"
this is the startup file
It runs ASR -> State_Changed(Taking data from the game data file) in order
'''

################ load packages
# generaL behavior
import threading
import time

# import subdirectories
'''from Working_code_ENG import config as cf
from Working_code_ENG import state_changed as sc
from Working_code_ENG import asr'''

from Working_code_KOR import config as cf_KOR
from Working_code_KOR import state_changed as sc_KOR
from Working_code_KOR import asr_KOR
from Working_code_ENG import config as cf_ENG
from Working_code_ENG import state_changed as sc_ENG
from Working_code_ENG import asr_ENG


# For ENG+KOR

################ load packages end
real_start = time.time()
# set logger
logger1 = cf_KOR.logging.getLogger("__dm_KOR__")
logger2 = cf_ENG.logging.getLogger("__dm_ENG__")
"""start the speech agent (Both ASR and speaking utterances)"""

def KOR():
    
    cf_KOR.start = real_start
    cf_KOR.game_start_time = time.time()
    
    cf_KOR.script_path = './Script_KOR/Script' + "(" + time.strftime('%y-%m-%d %H-%M',time.localtime(time.time())) + ")" + '_KOR.csv'
    cf_KOR.planning_path = './Planning_KOR/Planning_Result' + "(" + time.strftime('%y-%m-%d %H-%M', time.localtime(time.time())) + ")" + '_KOR.csv'
    asr= asr_KOR.listen_micr()
    asr_KOR_thread = threading.Thread(target=asr.run)

    logger1.info('starting the ASR - KOR')

    asr_KOR_thread.start()

    logger1.info('starting dm program')

    sc_KOR.state_changed_withoutHandler()

    asr.terminate()

    logger1.info('stopping asr')

    asr_KOR_thread.join()

    # final_message = asyncio.run(main())
    logger1.info('stopping dm program, DONE')

def ENG():
    
    cf_ENG.start = real_start
    cf_ENG.game_start_time = time.time()
    
    cf_ENG.script_path = './Script_ENG/Script' + "(" + time.strftime('%y-%m-%d %H-%M',time.localtime(time.time())) + ")" + '_ENG.csv'
    cf_ENG.planning_path = './Planning_ENG/Planning_Result' + "(" + time.strftime('%y-%m-%d %H-%M', time.localtime(time.time())) + ")" + '_ENG.csv'

    asr = asr_ENG.listen_micr()
    asr_ENG_thread = threading.Thread(target=asr.run)

    logger2.info('starting the ASR - ENG')

    asr_ENG_thread.start()

    logger2.info('starting dm program')

    sc_ENG.state_changed_withoutHandler()

    asr.terminate()

    logger2.info('stopping asr')

    asr_ENG_thread.join()

    # final_message = asyncio.run(main())
    logger2.info('stopping dm program, DONE')

if __name__ == "__main__":
    thread1 = threading.Thread(target=KOR)
    thread2 = threading.Thread(target=ENG)

    thread1.start()
    thread2.start()   