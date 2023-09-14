# -*- coding:utf-8 -*-
import time
import warnings
import pandas as pd
import numpy as np
import tensorflow as tf
import pyautogui
import csv
import towhee
from pickle import load
import datatable as dt
from pathlib import Path
import datetime


from Working_code import config as cf
from deepface.basemodels import SFace
from deepface.commons import functions


# ignore the warnings
warnings.filterwarnings(action='ignore')
tf.autograph.experimental.do_not_convert(func=None)


logger = cf.logging.getLogger("__turn_taking__")


def planning_excel():
    if cf.planning_counter == 1:
        with open(cf.planning_path, encoding="utf-8-sig", newline='', mode="w") as f:
            writer = csv.writer(f)
            writer.writerow(['Acc','Pred time','Game time', 'Pred Cat'])
            writer.writerow(cf.prediction_result_data)
        cf.planning_counter = cf.planning_counter + 1
        
    elif cf.planning_counter == 2:
        with open(cf.planning_path, encoding="utf-8-sig", newline='', mode="a") as f:
            writer = csv.writer(f)
            writer.writerow(cf.prediction_result_data)



def planning(row):    
    # append multimodal data every seconds
    turn_start = time.time()

    # game data
    cf.game_list.append(row)
    
    
    # vision data
    capture_img = np.array(pyautogui.screenshot(region=(cf.fixed_x, cf.fixed_y, cf.fixed_w, cf.fixed_h)))[:, :, ::-1]
    try:
        temp_vision = np.array(represent(capture_img, model=vision_model))
        if len(temp_vision) >= 2:
            loc_list = [temp_vision[i]['facial_area'].get('y') for i in range(len(temp_vision)) ]
            temp_vision = np.array(temp_vision[np.argmin(loc_list)]['embedding']).astype(np.float32)
        # Only Avatar detected
        else:
            temp_vision = np.array(temp_vision[0]['embedding']).astype(np.float32)
            logger.info("Face detection failed: Only Avatar detected")
    # No face detected
    except:
        temp_vision = np.zeros(128)
        print("Face detection failed: None of both detected")
        logger.info("Face detection failed: None of both detected")
    cf.vision_list.append(np.array(temp_vision).astype(np.float32))
    
    
    # audio data
    audio_start = time.time()
    audio_csv = dt.fread('audio.txt', fill=True, skip_blank_lines=True, sep=';', verbose=False).to_pandas()
    audio_runtime = round(time.time()-audio_start, 4)
    if np.array(audio_csv.iloc[-96:-51,2:67].mean()).shape == (65,):
        cf.audio_list.append(np.array(audio_csv.iloc[-96:-51,2:67].mean()).astype(np.float32))
        cf.audio_list.append(np.array(audio_csv.iloc[-46:-1,2:67].mean()).astype(np.float32))
    Path('audio.txt').touch()
    
    
    # text data
    cf.text_list.append(cf.text)
    cf.text = ''
    
    
    logger.info("Extracting raw data done")
    
    
    # if the length of audio list is over 10(= 1sec) then execute below
    if len(cf.audio_list) >= 10:
        
        # Text
        utterance = ''.join(cf.text_list[-5:])
        if utterance == '     ':
            text = np.zeros((1,35,768))
        else:
            text = bert_op(utterance)

            if len(text) == 0:
                text = np.zeros((35,768))
            elif len(text) > 35:
                text = text[:35,:]
            else:
                text = np.append(text,np.zeros([35-len(text), 768]),axis=0)
            text = np.reshape(text,(1,35,768)).astype(np.float32)
        
        
        # Vision
        vision = np.array(cf.vision_list[-5:]).reshape((1,5,128)).astype(np.float32)
        
        
        # Audio
        audio = np.array(cf.audio_list[-10:]).reshape((1,10,65)).astype(np.float32)
        
        
        # Game
        game = pd.DataFrame(cf.game_list[-5:], columns=cf.columns)
        game = data_cleaning(game)
        game = game[cf.planning_columns]
        game = np.array(game).reshape((1,5,40)).astype(np.float32)
        
        
        # Scaler
        audio = audio_scaler.fit_transform(audio.reshape(-1, audio.shape[-1])).reshape(audio.shape)
        game = game_scaler.fit_transform(game.reshape(-1, game.shape[-1])).reshape(game.shape)
        
        
        # Prediction   
        interpreter.set_tensor(input_details[0]['index'], vision)
        interpreter.set_tensor(input_details[1]['index'], audio)
        interpreter.set_tensor(input_details[2]['index'], text)
        interpreter.set_tensor(input_details[3]['index'], game)
        interpreter.invoke()
        turn_pred_result = round(float(interpreter.get_tensor(output_details[0]['index'])[0][0]), 4)
        
        
        if turn_pred_result >= cf.threshold:
            cf.turn_check = 0
        else:
            cf.turn_check = 1
            cf.turn_result_to_tts =  turn_pred_result
        
        
        if len(cf.audio_list) >= 300:
            del cf.vision_list[:-295]
            del cf.text_list[:-295]
            del cf.audio_list[:-290]
            del cf.game_list[:-295]
            del vision
            del text
            del audio
            del game
            del temp_vision
            del audio_csv
        
        
        turn_runtime = round(time.time() - turn_start, 4)
        logger.info(f"total duration: {turn_runtime}, pred_result: {turn_pred_result}, audio_runtime: {audio_runtime}")
        
        
        cf.prediction_result_data.append(turn_pred_result)
        cf.prediction_result_data.append(turn_runtime)
        cf.prediction_result_data.append(str(datetime.timedelta(seconds=round(time.time() - cf.game_start_time,5))).split(".")[0])
        cf.prediction_result_data.append(cf.turn_check)
        planning_excel()
        cf.prediction_result_data.clear()
        
        

def data_cleaning(dataframe_list):    
    
    for i in range(len(dataframe_list)):
        
        # Food_AVATAR - replace 'nil' & type conversion
        if dataframe_list.loc[i, 'Food_value(hunger)_AVATAR'] == 'nil':
            dataframe_list.loc[i, 'Food_value(hunger)_AVATAR'] = 0
        else:
            dataframe_list.loc[i, 'Food_value(hunger)_AVATAR'] = float(dataframe_list.loc[i, 'Food_value(hunger)_AVATAR'])
        
        
        # Food_PLAYER - replace 'nil' & type conversion
        if dataframe_list.loc[i, 'Food_value(hunger)_PLAYER'] == 'nil':
            dataframe_list.loc[i, 'Food_value(hunger)_PLAYER'] = 0
        else:
            dataframe_list.loc[i, 'Food_value(hunger)_PLAYER'] = float(dataframe_list.loc[i, 'Food_value(hunger)_PLAYER'])
        
        
        # AVATAR_Xloc - replace 'nil' & type conversion
        if dataframe_list.loc[i, 'AVATAR_Xloc'] == 'nil':
            dataframe_list.loc[i, 'AVATAR_Xloc'] = 0
        else:
            dataframe_list.loc[i, 'AVATAR_Xloc'] = float(dataframe_list.loc[i, 'AVATAR_Xloc'])
        
        
        # AVATAR_Zloc - replace 'nil' & type conversion
        if dataframe_list.loc[i, 'AVATAR_Zloc'] == 'nil':
            dataframe_list.loc[i, 'AVATAR_Zloc'] = 0
        else:
            dataframe_list.loc[i, 'AVATAR_Zloc'] = float(dataframe_list.loc[i, 'AVATAR_Zloc'])
        
        
        # PLAYER_Xloc - replace 'nil' & type conversion
        if dataframe_list.loc[i, 'PLAYER_Xloc'] == 'nil':
            dataframe_list.loc[i, 'PLAYER_Xloc'] = 0
        else:
            dataframe_list.loc[i, 'PLAYER_Xloc'] = float(dataframe_list.loc[i, 'PLAYER_Xloc'])
        
        
        # PLAYER_Zloc - replace 'nil' & type conversion
        if dataframe_list.loc[i, 'PLAYER_Zloc'] == 'nil':
            dataframe_list.loc[i, 'PLAYER_Zloc'] = 0
        else:
            dataframe_list.loc[i, 'PLAYER_Zloc'] = float(dataframe_list.loc[i, 'PLAYER_Zloc'])
        
        
        # Hunger_PLAYER - replace 'nil' 
        if dataframe_list.loc[i, 'Hunger_PLAYER'] == 'no player joined':
            dataframe_list.loc[i, 'Hunger_PLAYER'] = 0        
        
        
        # Phase -day:0, dusk:1, night:2
        if dataframe_list.loc[i, 'Phase'] == 'day':
            dataframe_list.loc[i, 'Phase'] = 0
        elif dataframe_list.loc[i, 'Phase'] == 'dusk':
            dataframe_list.loc[i, 'Phase'] = 1
        else:
            dataframe_list.loc[i, 'Phase'] = 2


        # Curr_Active_Item
        if dataframe_list.loc[i, 'Curr_Active_Item_AVATAR'] == 'nil':
            dataframe_list.loc[i, 'Curr_Active_Item_AVATAR'] = 0
        else:
            dataframe_list.loc[i, 'Curr_Active_Item_AVATAR'] = 1


        # Curr_Equip_Hands
        if dataframe_list.loc[i, 'Curr_Equip_Hands_AVATAR'] == 'nil':
            dataframe_list.loc[i, 'Curr_Equip_Hands_AVATAR'] = 0
        else:
            if dataframe_list.loc[i, 'Curr_Equip_Hands_AVATAR'].rsplit('-')[1].lstrip() == 'axe(LIMBO)':
                dataframe_list.loc[i, 'Curr_Equip_Hands_AVATAR'] = 1
            elif dataframe_list.loc[i, 'Curr_Equip_Hands_AVATAR'].rsplit('-')[1].lstrip() == 'pickaxe(LIMBO)':
                dataframe_list.loc[i, 'Curr_Equip_Hands_AVATAR'] = 2
            else:
                dataframe_list.loc[i, 'Curr_Equip_Hands_AVATAR'] = 3
                
                
        # Attack_Target
        if dataframe_list.loc[i, 'Attack_Target_AVATAR'] == 'nil':
            dataframe_list.loc[i, 'Attack_Target_AVATAR'] = 0
        else:
            dataframe_list.loc[i, 'Attack_Target_AVATAR'] = 1
            
            
        # Defense_Target
        if dataframe_list.loc[i, 'Defense_Target_AVATAR'] == 'nil':
            dataframe_list.loc[i, 'Defense_Target_AVATAR'] = 0
        else:
            dataframe_list.loc[i, 'Defense_Target_AVATAR'] = 1
            
            
        # Recent_attacked
        if dataframe_list.loc[i, 'Recent_attacked_AVATAR'] == 'nil':
            dataframe_list.loc[i, 'Recent_attacked_AVATAR'] = 0
        else:
            dataframe_list.loc[i, 'Recent_attacked_AVATAR'] = 1
            
        
        # Food -'No Food!':0, 'Less Food!':1, 'Fine!':2
        if dataframe_list.loc[i, 'Food_value(hunger)_AVATAR'] == 0:
            dataframe_list.loc[i, 'Food_value(hunger)_AVATAR'] = 0
        elif dataframe_list.loc[i, 'Food_value(hunger)_AVATAR'] < 50:
            dataframe_list.loc[i, 'Food_value(hunger)_AVATAR'] = 1
        else:
            dataframe_list.loc[i, 'Food_value(hunger)_AVATAR'] = 2
            

        # Is_Light -'No lights!':0, 'Lights nearby':1, 'Campfire nearby':2
        if dataframe_list.loc[i, 'Is_Light_AVATAR'] == 'nil':
            dataframe_list.loc[i, 'Is_Light_AVATAR'] = 0
        elif dataframe_list.loc[i, 'Is_Light_AVATAR'] == True:
            dataframe_list.loc[i, 'Is_Light_AVATAR'] = 1
        elif dataframe_list.loc[i, 'Is_Fireplace_AVATAR'] == True:
            dataframe_list.loc[i, 'Is_Light_AVATAR'] = 2
        else:
            dataframe_list.loc[i, 'Is_Light_AVATAR'] = 2

        
        # Curr_Active_Item
        if dataframe_list.loc[i, 'Curr_Active_Item_PLAYER'] == 'nil':
            dataframe_list.loc[i, 'Curr_Active_Item_PLAYER'] = 0
        else:
            dataframe_list.loc[i, 'Curr_Active_Item_PLAYER'] = 1


        # Curr_Equip_Hands
        if dataframe_list.loc[i, 'Curr_Equip_Hands_PLAYER'] == 'nil':
            dataframe_list.loc[i, 'Curr_Equip_Hands_PLAYER'] = 0
        else:
            if dataframe_list.loc[i, 'Curr_Equip_Hands_PLAYER'].rsplit('-')[1].lstrip() == 'axe(LIMBO)':
                dataframe_list.loc[i, 'Curr_Equip_Hands_PLAYER'] = 1
            elif dataframe_list.loc[i, 'Curr_Equip_Hands_PLAYER'].rsplit('-')[1].lstrip() == 'pickaxe(LIMBO)':
                dataframe_list.loc[i, 'Curr_Equip_Hands_PLAYER'] = 2
            else:
                dataframe_list.loc[i, 'Curr_Equip_Hands_PLAYER'] = 3
                
                
        # Attack_Target
        if dataframe_list.loc[i, 'Attack_Target_PLAYER'] == 'nil':
            dataframe_list.loc[i, 'Attack_Target_PLAYER'] = 0
        else:
            dataframe_list.loc[i, 'Attack_Target_PLAYER'] = 1
            
            
        # Defense_Target
        if dataframe_list.loc[i, 'Defense_Target_PLAYER'] == 'nil':
            dataframe_list.loc[i, 'Defense_Target_PLAYER'] = 0
        else:
            dataframe_list.loc[i, 'Defense_Target_PLAYER'] = 1
            
            
        # Recent_attacked
        if dataframe_list.loc[i, 'Recent_attacked_PLAYER'] == 'nil':
            dataframe_list.loc[i, 'Recent_attacked_PLAYER'] = 0
        else:
            dataframe_list.loc[i, 'Recent_attacked_PLAYER'] = 1
            
        
        # Food -'No Food!':0, 'Less Food!':1, 'Fine!':2
        if dataframe_list.loc[i, 'Food_value(hunger)_PLAYER'] == 0:
            dataframe_list.loc[i, 'Food_value(hunger)_PLAYER'] = 0
        elif dataframe_list.loc[i, 'Food_value(hunger)_PLAYER'] < 50 :
            dataframe_list.loc[i, 'Food_value(hunger)_PLAYER'] = 1
        else:
            dataframe_list.loc[i, 'Food_value(hunger)_PLAYER'] = 2
            

        # Is_Light -'No lights!':0, 'Lights nearby':1, 'Campfire nearby':2
        if dataframe_list.loc[i, 'Is_Light_PLAYER'] == 'nil':
            dataframe_list.loc[i, 'Is_Light_PLAYER'] = 0
        elif dataframe_list.loc[i, 'Is_Light_PLAYER'] == True:
            dataframe_list.loc[i, 'Is_Light_PLAYER'] = 1
        elif dataframe_list.loc[i, 'Is_Fireplace_PLAYER'] == True:
            dataframe_list.loc[i, 'Is_Light_PLAYER'] = 2
        else:
            dataframe_list.loc[i, 'Is_Light_PLAYER'] = 2
    
    dataframe_list = dataframe_list.replace('nil',0)
    
    return dataframe_list
    


def build_model(model_name):

    # singleton design pattern
    global model_obj

    models = {
        "SFace": SFace.load_model,
    }

    if not "model_obj" in globals():
        model_obj = {}

    if not model_name in model_obj:
        model = models.get(model_name)
        if model:
            model = model()
            model_obj[model_name] = model
        else:
            raise ValueError(f"Invalid model_name passed - {model_name}")

    return model_obj[model_name]



def represent(
    img_path,
    model,
    enforce_detection=True,
    detector_backend="opencv",
    align=True,
    normalization="base"):
    
    resp_objs = []

    model = model

    # ---------------------------------
    # we have run pre-process in verification. so, this can be skipped if it is coming from verify.
    if detector_backend != "skip":
        target_size = functions.find_target_size(model_name="SFace")

        img_objs = functions.extract_faces(
            img=img_path,
            target_size=target_size,
            detector_backend=detector_backend,
            grayscale=False,
            enforce_detection=enforce_detection,
            align=align,
        )
    else:  # skip
        if isinstance(img_path, str):
            img = functions.load_image(img_path)
        elif type(img_path).__module__ == np.__name__:
            img = img_path.copy()
        else:
            raise ValueError(f"unexpected type for img_path - {type(img_path)}")

        img_region = [0, 0, img.shape[1], img.shape[0]]
        img_objs = [(img, img_region, 0)]
    # ---------------------------------

    for img, region, _ in img_objs:
        # custom normalization
        img = functions.normalize_input(img=img, normalization=normalization)

        # represent
        if "keras" in str(type(model)):
            # new tf versions show progress bar and it is annoying
            embedding = model.predict(img, verbose=0)[0].tolist()
        else:
            # SFace and Dlib are not keras models and no verbose arguments
            embedding = model.predict(img)[0].tolist()

        resp_obj = {}
        resp_obj["embedding"] = embedding
        resp_obj["facial_area"] = region
        resp_objs.append(resp_obj)

    return resp_objs



bert_op = towhee.ops.text_embedding.transformers(model_name='distilbert-base-multilingual-cased').get_op()
audio_scaler = load(open('./Working_code/saved_model/scaler/audio_scaler.pkl', 'rb'))
game_scaler = load(open('./Working_code/saved_model/scaler/game_scaler.pkl', 'rb'))
vision_model = build_model("SFace")


interpreter = tf.lite.Interpreter(model_path = "Working_code/saved_model/tflite_model/our_model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
input_shape_vision = input_details[0]['shape']
input_shape_audio = input_details[1]['shape']
input_shape_text = input_details[2]['shape']
input_shape_game = input_details[3]['shape']