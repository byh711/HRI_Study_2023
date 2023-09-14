# -*- coding:utf-8 -*-
'''
All kind of settings (MS Azure API keys, setting the log file, taking *.txt files)
Setting global variables, read data files (*_utterances.txt, *_keywords.txt, settings.txt)
'''
################### load packages
# generaL behavior
import os, json
import pandas as pd
from collections import defaultdict
import time

# for logging:
import warnings, logging


#for TTS
import azure.cognitiveservices.speech as speechsdk
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
################### load packages end


################### set API keys
# MS Auzre / used at 'tts.py' and 'asr.py' files
speech_key, service_region = "YOUR_SPEECH_KEY", "YOUR_SERVICE_REGION"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
audio_config = speechsdk.audio.AudioConfig(device_name="YOUR_DEVICE_NAME")   
################### set API keys ends


################### set logging
# Ignoring the warnings
warnings.filterwarnings(action='ignore')

# Making the 'logs' folder if the folder does not exist
if not os.path.exists("./logs/"):
    os.mkdir("./logs/")
    
if not os.path.exists("./Data_result/"):
    os.mkdir("./Data_result/")

if not os.path.exists("./Data_result/Script/"):
    os.mkdir("./Data_result/Script/")
    
if not os.path.exists("./Data_result/Planning/"):
    os.mkdir("./Data_result/Planning/")  
    
if not os.path.exists("./Data_result/Turn_Pass/"):
    os.mkdir("./Data_result/Turn_Pass/")

# Set up log file written format ex) 01:39:09
logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(name)s: %(message)s",
    level=logging.DEBUG,
    filename='./logs/dm.log',
    # encoding='utf-8',
    datefmt="%H:%M:%S",
    #stream=sys.stderr,
)

logging.getLogger("chardet.charsetprober").disabled = True
################### set logging end

################### set global variables and constants

################### PLACEHOLDERS (All used at 'parse_tree.py' file)
### Set up repetition delay count
REP_DELAY_AMT = 3 # prevent too much talk
LOCAL_REP_DELAY_AMT = REP_DELAY_AMT
### repetition delay count ends

### Other placeholders
HUNGRY = 50
STARVING = 30
INJURED = 50
DYING = 30
SANITY_LOW = 50
SANITY_DANGER = 30
CHATTINESS = 3.0 # talkative or not
### Other placeholders end
################## PLACEHOLDERS END

################## Define dictionaries, lists (used at 'state_changed.py file or 'parse_tree.py' file)
### For repetition delay
# Set up state_list that are used at the 'state_changed.py' file
state_list = ['Phase', 'Hunger_AVATAR', 'Health_AVATAR', 'Sanity_AVATAR', 'Curr_Active_Item_AVATAR',
              'Curr_Equip_Hands_AVATAR', 'Attack_Target_AVATAR',  'Defense_Target_AVATAR', 'Food_AVATAR',
              'Tool_AVATAR', 'Lights_AVATAR', 'Is_Light_AVATAR', 'Is_Monster_AVATAR']

# Concatenate above 'state_list' and 'REP_DELAY_AMT' as a dictionary
rep_delay_states = dict.fromkeys(state_list, REP_DELAY_AMT)
### repetition delay ends


### turn-taking start
prediction_result_data = list()

columns = ['OS_timestamp', 'Game_Runtime', 'Phase', 'AVATAR_ID', 'AVATAR_Xloc',
           'AVATAR_Yloc', 'AVATAR_Zloc', 'Curr_Inv_Cnt_AVATAR',
           'Curr_Active_Item_AVATAR', 'Curr_Equip_Hands_AVATAR', 'Health_AVATAR',
           'Hunger_AVATAR', 'Sanity_AVATAR', 'Attack_Target_AVATAR',
           'Defense_Target_AVATAR', 'Recent_attacked_AVATAR',
           'Food_value(hunger)_AVATAR', 'Twigs_AVATAR', 'Flint_AVATAR',
           'Rock_AVATAR', 'Grass_AVATAR', 'Log_AVATAR',
           'Tool_resource(twig:flint)_AVATAR',
           'Fireplace_resource(logs:rock:grass:flint)_AVATAR',
           'Is_Fireplace_AVATAR', 'Is_Light_AVATAR', 'Is_Monster(num)_AVATAR',
           'Action_AVATAR', 'Target_AVATAR', 'Invobject_AVATAR',
           'IsRunning_AVATAR', 'Rotation_AVATAR', 'Dist_from_Basecamp_AVATAR',
           'PLAYER_ID', 'PLAYER_Xloc', 'PLAYER_Yloc', 'PLAYER_Zloc',
           'Curr_Inv_Cnt_PLAYER', 'Curr_Active_Item_PLAYER',
           'Curr_Equip_Hands_PLAYER', 'Health_PLAYER', 'Hunger_PLAYER',
           'Sanity_PLAYER', 'Attack_Target_PLAYER', 'Defense_Target_PLAYER',
           'Recent_attacked_PLAYER', 'Food_value(hunger)_PLAYER', 'Twigs_PLAYER',
           'Flint_PLAYER', 'Rock_PLAYER', 'Grass_PLAYER', 'Log_PLAYER',
           'Tool_resource(twig:flint)_PLAYER',
           'Fireplace_resource(logs:rock:grass:flint)_PLAYER',
           'Is_Fireplace_PLAYER', 'Is_Light_PLAYER', 'Is_Monster(num)_PLAYER',
           'Action_PLAYER', 'Target_PLAYER', 'Invobject_PLAYER',
           'IsRunning_PLAYER', 'Rotation_PLAYER', 'Dist_from_Basecamp_PLAYER',
           'Distance']

planning_columns = ['Phase', 'Hunger_AVATAR', 'Health_AVATAR', 'Sanity_AVATAR',
                    'AVATAR_Xloc', 'AVATAR_Zloc', 'Curr_Inv_Cnt_AVATAR', 'Curr_Active_Item_AVATAR',
                    'Curr_Equip_Hands_AVATAR', 'Attack_Target_AVATAR', 'Defense_Target_AVATAR',
                    'Recent_attacked_AVATAR', 'Food_value(hunger)_AVATAR', 'Is_Light_AVATAR', 'Is_Monster(num)_AVATAR',
                    'Twigs_AVATAR', 'Flint_AVATAR', 'Log_AVATAR', 'Rock_AVATAR', 'Grass_AVATAR',
                    'Hunger_PLAYER', 'Health_PLAYER', 'Sanity_PLAYER',
                    'PLAYER_Xloc', 'PLAYER_Zloc', 'Curr_Inv_Cnt_PLAYER', 'Curr_Active_Item_PLAYER',
                    'Curr_Equip_Hands_PLAYER', 'Attack_Target_PLAYER', 'Defense_Target_PLAYER',
                    'Recent_attacked_PLAYER', 'Food_value(hunger)_PLAYER',
                    'Is_Light_PLAYER', 'Is_Monster(num)_PLAYER',
                    'Twigs_PLAYER', 'Flint_PLAYER', 'Log_PLAYER', 'Rock_PLAYER', 'Grass_PLAYER', 'Distance']

data = dict()
initial_state = dict()
status = defaultdict(list)
################## Define dictionaries, lists end

planning_counter = 1
script_counter = 1
utt_start_time = 0
utt_finish_time = 0
list_utter = list()
synthesize_utt_check = 0

script_path = './Data_result/Script/Script' +"("+time.strftime('%y-%m-%d %H-%M', time.localtime(time.time()))+")"+'.csv'
planning_path = './Data_result/Planning/Planning_Result' +"("+time.strftime('%y-%m-%d %H-%M', time.localtime(time.time()))+")"+'.csv'
turn_pass_path = './Data_result/Turn_Pass/Turn_Pass_Result' +"("+time.strftime('%y-%m-%d %H-%M', time.localtime(time.time()))+")"+'.csv'

game_list = []
vision_list = []
audio_list = []
text_list = []
text = ''
threshold = 0.4
turn_check = 0
turn_counter = 1
turn_result_to_tts = 0
list_turn_pass = list()
fixed_x = 1200
fixed_y = 50
fixed_w = 800
fixed_h = 1000
################## turn-taking ends


# read settings from 'settings.txt' file
language =  input("type 'eng' or 'kor': ")
game_start_time = time.time()

if language == 'ENG' or language == 'eng' or language == 'Eng':
    THIS_LANGUAGE = 'en-US'
    print("ENG start!")
else:
    THIS_LANGUAGE = 'ko-KR'
    print("KOR start!")

with open('settings.txt', 'r', encoding='utf-8') as settingsfile:
    exec(settingsfile.read())

# read list of utterances from the 'data/*_utterances.txt' file
with open('data/' + THIS_LANGUAGE + '_utterances.txt', 'r', encoding='utf-8') as utterancefile:
    utt_data = utterancefile.read()
    RESPONSE_UTTS = json.loads(utt_data, strict=False)

# read list of keywords from the 'data/*_keywords.txt' file
with open('data/' + THIS_LANGUAGE + '_keywords.txt', 'r', encoding='utf-8') as keywordfile:
    asrkeys_data = keywordfile.read()
    ASR_KEYS_UTTS = json.loads(asrkeys_data, strict=False)
    
# read list of planning utterances from the 'data/*_planning_utterances.txt' file
with open('data/' + THIS_LANGUAGE + '_planning_utterances.txt', 'r', encoding='utf-8') as planningfile:
    asrkeys_data = planningfile.read()
    PLANNING_UTTS = json.loads(asrkeys_data, strict=False)
    
# change '(something)' to KOR
# https://m.blog.naver.com/PostView.naver?isHttpsRedirect=true&blogId=spceoa&logNo=221204271885
with open('data/ko-KR_conversion.txt', 'r', encoding='utf-8') as convfile:
    asrkeys_data = convfile.read()
    CONV_UTTS = json.loads(asrkeys_data, strict=False)

# read list of utterances priority median value from the 'data/*_priority_utterances.xlsx' file as dictionary type
# Read the Excel file under data folder. Currently, use 'category' and 'median' columns for Self-generated utterances
priority_utterance = pd.read_excel('data/' + THIS_LANGUAGE + '_priority_utterances.xlsx', usecols = ['category', 'median'])
# Making 'category' and 'median' dataframe type to list type
category_list = priority_utterance['category'].values.tolist()
median_list = priority_utterance['median'].values.tolist()
# Concatenate both to dictionary
priority_utterance_score = dict(zip(category_list,median_list))

# read list of keyword priority median value from the 'data/*_priority_keywords.xlsx' file as dictionary type
# Read the Excel file under data folder. Currently, use the 'median' column for keywords
priority_keyword = pd.read_excel('data/' + THIS_LANGUAGE + '_priority_keywords.xlsx', usecols = ['median'])
# Making 'median' dataframe type to list type
value_list = priority_keyword.values.tolist()
# Making 'median' list-list type to list (ex. [[3.0]] -> [3.0])
value_list = sum(value_list, [])
# Concatenate 'keywords' and 'median' to dictionary
priority_keyword_score = dict(zip(ASR_KEYS_UTTS.keys(),value_list))

INTERFACE_FILEFOLDER = INTERFACE_FOLDER + INTERFACE_FILE
################ set global variables and constants end