# -*- coding:utf-8 -*-
'''
Synthesize utterances using Microsoft Azure TTS SDK mainly from 'parse_tree.py' file and 'asr.py' file.
'''
import azure.cognitiveservices.speech as speechsdk
import time
import datetime
import re
import csv

from Working_code import asr
from Working_code import config as cf

# set API keys
speech_key, service_region = cf.speech_key, cf.service_region
speech_config = cf.speech_config

# set logger
logger = cf.logging.getLogger("__tts__")


def turn_pass_excel():
    if cf.turn_counter == 1:
        with open(cf.turn_pass_path, encoding="utf-8-sig", newline='', mode="w") as f:
            writer = csv.writer(f)
            writer.writerow(['Speaker','Acc','Script','Time', 'Self_ASR'])
            writer.writerow(cf.list_turn_pass)
            cf.turn_counter = cf.turn_counter + 1
            
    elif cf.turn_counter == 2:
        with open(cf.turn_pass_path, encoding="utf-8-sig", newline='', mode="a") as f:
            writer = csv.writer(f)
            writer.writerow(cf.list_turn_pass)


# MS Azure Text to Speech(TTS) SDK synthesize the sentence
def synthesize_utt(utterance, self_asr_check):
    # get a text and synthesize it
    
    if cf.synthesize_utt_check == 0 and utterance != None and cf.turn_check == 0:
        cf.synthesize_utt_check = 1
        cf.utt_start_time = round(time.time() - cf.game_start_time,5)
        logger.info(f"New utterance is: {utterance}")
        
        # MS Azure TTS / Synthesize text and make it to speak
        # Sample codes could be checked right below link
        # https://github.com/Azure-Samples/cognitive-services-speech-sdk/blob/master/quickstart/python/text-to-speech/quickstart.py
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        
        
        # print result which utterance is selected
        print()
        print('**********' * 5)
        print('Avatar: ', utterance)
        print('**********' * 5)
        print()
        
        cf.list_utter.append("Avatar")
        cf.list_utter.append(utterance)
        
        
        cf.list_utter.append(str(datetime.timedelta(seconds=cf.utt_start_time)).split(".")[0])
        cf.utt_finish_time = round(time.time() - cf.game_start_time,5)
        cf.list_utter.append(str(datetime.timedelta(seconds=cf.utt_finish_time)).split(".")[0])
        
        if self_asr_check == 'self':
            cf.list_utter.append('self')
        else:
            cf.list_utter.append('asr')
        
        asr.asr_tts_excel()
        cf.list_utter = list()
        
        result = speech_synthesizer.speak_text_async(utterance).get()
        
        if cf.THIS_LANGUAGE == 'en-US':
            utterance = re.sub(r'[^a-zA-Z ]', '', utterance).lower()
        else:
            utterance = re.sub(r'[^ ㄱ-ㅣ가-힣+]', '', utterance)

        cf.text += utterance + ' '

        # If error occurs, print it and pass to work next utterance with no problem
        # Below is an error that is occurring for MS Azure
        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logger.info("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logger.info("Error details: {}".format(cancellation_details.error_details))
        
        # ToDo: put synthesizer and player in separate threads and queue
        time.sleep(0.2)
        cf.synthesize_utt_check = 0
                
    elif cf.synthesize_utt_check == 0 and utterance != None and cf.turn_check == 1:
        cf.list_turn_pass.append("Avatar")
        cf.list_turn_pass.append(cf.turn_result_to_tts)
        cf.list_turn_pass.append(utterance)
        
        turn_pass_time = round(time.time() - cf.game_start_time,5)
        cf.list_turn_pass.append(str(datetime.timedelta(seconds=turn_pass_time)).split(".")[0])
        
        if self_asr_check == 'self':
            cf.list_turn_pass.append('self')
        else:
            cf.list_turn_pass.append('asr')
        
        turn_pass_excel()
        cf.list_turn_pass = list()