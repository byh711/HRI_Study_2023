# -*- coding:utf-8 -*-
'''
This code file checks columns of the 'test.csv' file and drags needed information.
(header columns and data separately)
Then, it sends the appropriate information to the 'parse_tree.py' file.
'''
import time
import traceback

from Working_code_ENG import config as cf_ENG
from Working_code_ENG import parse_tree as pt_ENG


# set logger
logger2 = cf_ENG.logging.getLogger("__state_checker__")

# Read the current CSV file line ('test.csv') continuously
def get_line_from_csv(csvfile):
    # Read current line continuously
    csvfile.seek(0,2)   

    # Read the csv file current line
    while True:
        line = csvfile.readline()      

        time_interval = time.time() - cf_ENG.start  # 180 360 540 ...
        interval = round(time_interval,1)

        if interval >= cf_ENG.initial:
            cf_ENG.synthesize_utt_check2 += 1
            cf_ENG.initial += 180
            print(f"ENG: {interval},{cf_ENG.initial}")
            if cf_ENG.synthesize_utt_check2 % 2 == 0:
                cf_ENG.synthesize_utt_check3 = 0
            else:
                cf_ENG.synthesize_utt_check3 = 1
        
        # If it is not line, then pause for a while
        if not line:
            time.sleep(0.1)   
            continue

        yield line

# Appending data to the lists and sending it to the 'parse_tree.py file'
def update_data_from_csv(csvfile, initial_state):
    lines = get_line_from_csv(csvfile)

    # Split the line by ',' as the format is CSV
    for line in lines:
        row = line.split(',')

        # Put this because file reading returns number 1(\n)/28(avatar data)/1/28 continuously...
        if row[0] == '\n':
            continue

        try:
            # if the line is not the header line and if it is completely written
            if row[0] != 'OS_timestamp' and (len(row)-1) == no_columns_csv:
                # ToDo : replace indices by generic variable, e.g. from the headers
                # Avatar data
                # row[0] 'OS_timestamp', row[1] 'Game_Runtime'
                cf_ENG.data['Phase'] = row[2]
                cf_ENG.data['Hunger_AVATAR'] = row[4]
                cf_ENG.data['Health_AVATAR'] = row[5]
                cf_ENG.data['Sanity_AVATAR'] = row[6]
                cf_ENG.data['Curr_Active_Item_AVATAR'] = row[12]
                cf_ENG.data['Curr_Equip_Hands_AVATAR'] = row[13]
                cf_ENG.data['Attack_Target_AVATAR'] = row[14]
                cf_ENG.data['Defense_Target_AVATAR'] = row[15]
                cf_ENG.data['Food_AVATAR'] = row[17]
                cf_ENG.data['Tool_AVATAR'] = row[19]
                cf_ENG.data['Lights_AVATAR'] = row[21]
                cf_ENG.data['Is_Light_AVATAR'] = row[23]
                cf_ENG.data['Is_Monster_AVATAR'] = row[24]
                # Player data
                cf_ENG.data['Player_Xloc'] = row[31]

                # append data to current_state
                current_state = cf_ENG.data

                logger2.info("Update state and hand over to decision tree.")

                # Send the current state data to 'parse_tree'.py file
                pt_ENG.parse_decision_tree(current_state, initial_state)

                logger2.info("Planning part starts")
                
                #planning.planning(row)
                

                # ToDo : replace indices by generic variable, e.g. from the headers

            # If the case is not like above, the pass
            else:
                pass

        # error occurs, then write errors at the log file
        except Exception as e:
            logger2.error('error reading current line as data : %s', e )
            logger2.error('the line is: ' + line)
            logger2.error(traceback.format_exc())

# Set up initial state, read each line in real time and pass to above update_data_from_csv() function
def state_changed_withoutHandler():
    '''
    check csv file for game updates and process it to new representation (if necessary)
    then execute the decision tree for the virtual avatar
    creating empty initial_state
    '''
    # Set up empty initial state
    # Avatar data
    cf_ENG.initial_state['Phase'] = ''
    cf_ENG.initial_state['Huger_AVATAR'] = ''
    cf_ENG.initial_state['Health_AVATAR'] = ''
    cf_ENG.initial_state['Sanity_AVATAR'] = ''
    cf_ENG.initial_state['Curr_Active_Item_AVATAR'] = ''
    cf_ENG.initial_state['Curr_Equip_Hands_AVATAR'] = ''
    cf_ENG.initial_state['Attack_Target_AVATAR'] = ''
    cf_ENG.initial_state['Defense_Target_AVATAR'] = ''
    cf_ENG.initial_state['Food_AVATAR'] = ''
    cf_ENG.initial_state['Tool_AVATAR'] = ''
    cf_ENG.initial_state['Lights_AVATAR'] = ''
    cf_ENG.initial_state['Is_Light_AVATAR'] = ''
    cf_ENG.initial_state['Is_Monster_AVATAR'] = ''
    # Player data
    cf_ENG.initial_state['Player_Xloc'] = ''

    logger2.info('opening the csv file and regularly check for added lines')

    try:
        with open(cf_ENG.INTERFACE_FILEFOLDER, 'r', encoding='utf-8', newline='') as csvfile:
            # get the number of columns to check later, if each newline is completely written
            csvheader = csvfile.readline().strip().split(',')

            # Set 'no_columns_csv' as global because it would be used at above 'update_data_from_csv' function
            global no_columns_csv

            # Counting All columns
            no_columns_csv = len(csvheader)-1

            logger2.debug(' printing all header names: ')

            # Write down column information to log file
            for i in range(no_columns_csv):
                logger2.debug('%s : %s', i, csvheader[i])

            # start reading all new lines
            update_data_from_csv(csvfile, cf_ENG.initial_state)

    # Write down error to log file if error occurs
    except Exception as e:
        logger2.error(' error during opening csv file: %s', e)