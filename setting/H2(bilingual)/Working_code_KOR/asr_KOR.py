# -*- coding:utf-8 -*-
'''
ASR (automatic speech recognition)
- Using SDK : MS Azure for python

Listen to the other player's talk and respond to it based on the keyword file
keyword files - located under the data folder (ex. data/en-US_keywords.txt)
'''

import ast, random, re
import azure.cognitiveservices.speech as speechsdk
from Working_code_KOR import config as cf_KOR
from Working_code_KOR import tts
import csv
import time
import datetime

# set API keys
speech_key, service_region = cf_KOR.speech_key, cf_KOR.service_region
speech_config = cf_KOR.speech_config
audio_config = cf_KOR.audio_config

# set logger1
logger1 = cf_KOR.logging.getLogger("__asr_KOR__")


def asr_tts_excel():
    if cf_KOR.scriptcounter == 1:
        with open(cf_KOR.script_path, encoding="utf-8-sig", newline='', mode="w") as f:
            writer = csv.writer(f)
            writer.writerow(['Speaker','Script','Start Time','Finish Time'])
            writer.writerow(cf_KOR.list_utter)
            cf_KOR.scriptcounter = cf_KOR.scriptcounter + 1
            
    elif cf_KOR.scriptcounter == 2:
        with open(cf_KOR.script_path, encoding="utf-8-sig", newline='', mode="a") as f:
            writer = csv.writer(f)
            writer.writerow(cf_KOR.list_utter)


# ASR function starts
class listen_micr:

    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        # Set up recognizer (Using MS Azure)
        # Sample codes could be checked
        # https://github.com/Azure-Samples/cognitive-services-speech-sdk/blob/master/quickstart/python/from-microphone/quickstart.py
        # https://github.com/Azure-Samples/cognitive-services-speech-sdk/blob/a5de28baa82f2633d38e2acd49a319b9df2104c3/samples/python/console/speech_sample.py#L225
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language=cf_KOR.THIS_LANGUAGE, audio_config=audio_config)

        while self._running:
            try:
                result_future = speech_recognizer.recognize_once_async()
                logger1.debug('listening ...')
                # Inform a person to know start of recognition
                print("Say Something! - KOR")

                # Recognizing speech through mike / designated speaker
                # result = speech_recognizer.recognize_once()
                result = result_future.get()
                
                # ignore punctuation marks and lower all words
                # ex) I eat foods. -> I eat foods (ignore punctuation) -> i eat foods (lower words)
                user_utt = result.text[:-1].lower()
                
                if user_utt:
                    cf_KOR.utt_start_time = round(time.time() - cf_KOR.game_start_time,5)
                    
                    # print the result to see how the recognizer recognizes
                    print("Recognized: {}".format(user_utt))

                    logger1.info('user said: ' + user_utt)
                    self.respond_to_user_utt(user_utt)

                    cf_KOR.list_utter.append("Player")
                    cf_KOR.list_utter.append(user_utt)
                    cf_KOR.list_utter.append(str(datetime.timedelta(seconds=cf_KOR.utt_start_time)).split(".")[0])
                    
                    cf_KOR.utt_finish_time = round(time.time() - cf_KOR.game_start_time,5)
                    cf_KOR.list_utter.append(str(datetime.timedelta(seconds=cf_KOR.utt_finish_time)).split(".")[0])
                    
                    asr_tts_excel()
            
                    cf_KOR.list_utter = list()

                # Force to shut down ASR only
                # pressing ctrl + z shut down ASR
                #if ('exit' in user_utt) or ('종료' in user_utt) or (keyboard.is_pressed('esc')):
                #    print("Exiting...")
                #    sys.exit()

            # If error occurs, pass and do the recognition task again
            # MS Azure recognizer errors are written below as exception
            except result.reason == speechsdk.ResultReason.NoMatch:
                logger1.info("No speech could be recognized: {}".format(result.no_match_details))
                pass
            except result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                logger1.info("Speech Recognition canceled: {}".format(cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    logger1.info("Error details: {}".format(cancellation_details.error_details))
                pass

    # Response selection based on the ASR result
    def respond_to_user_utt(self, text):
        try:
            # check all keywords to be contained in the spoken user text
            # keyword : keywords that are written at data/*_keywords.txt file
            # text : input / a sentence that is recognized and return as a result from 'def run(self)' function
            for keyword in cf_KOR.ASR_KEYS_UTTS.keys():
                # Answer would be come out only if the score of designated keyword is under 'config.py' file CHATTINESS placeholder

                # For one keywords
                # If text contains keyword
                if keyword in text :
                    # Select random answer from data/*_keywords.txt files
                    utterance = random.choice(ast.literal_eval(cf_KOR.ASR_KEYS_UTTS[keyword]))
                    # Bring the utterance to speak
                    tts.synthesize_utt(utterance)
                    # Use break for preventing multiple answers come out
                    break
                # For multiple keywords or phrase
                else:
                    # compile regular expression and keywords
                    pattern = re.compile(keyword)
                    # Compare keyword and text if the text is in keyword
                    if pattern.search(text):
                        # Select random answer from data/*_keywords.txt files
                        utterance = random.choice(ast.literal_eval(cf_KOR.ASR_KEYS_UTTS[keyword]))
                        # Bring the utterance to speak
                        tts.synthesize_utt(utterance)
                        # Use break for preventing multiple answers come out
                        break
        # If error occurs, write down the error at the logs/dm.log file
        except Exception as err:
            logger1.error("user input parsing failed " + str(err))