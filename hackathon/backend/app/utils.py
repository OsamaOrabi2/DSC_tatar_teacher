import os
import shutil
from django.conf import settings
import requests
import base64

import numpy as np
import noisereduce as nr
from pydub import AudioSegment
from pydub.playback import play
import matplotlib.pyplot as plt

"""
def get_tts_audio(text, speaker='almaz'):
    # API endpoint
    api_url = 'https://tat-tts.api.translate.tatar/listening/'

    # Parameters
    params = {
        'speaker': speaker,
        'text': text
    }

    try:
        save_directory = os.path.join(settings.MEDIA_ROOT, 'uploaded_audio')
        # Perform the GET request with parameters
        response = requests.get(api_url, params=params, headers={'accept': 'application/json'})

        # Check if request was successful
        if response.status_code == 200:
            # Parse JSON response
            json_response = response.json()

            # Extract WAV data and sample rate from JSON
            wav_base64 = json_response['wav_base64']
            sample_rate = json_response['sample_rate']

            # Decode base64 to binary
            audio_data = base64.b64decode(wav_base64)

            # Write the binary audio data to a WAV file
            output_file = os.path.join(save_directory, 'spoken_phrase.wav')
            #output_file = f'{speaker}_{text[:10]}.wav'  # Limiting text length for filename
            with open(output_file, 'wb') as f:
                f.write(audio_data)

            print(f'WAV file saved: {output_file}')
            #return output_file
        else:
            print(f'Failed to get response. Status code: {response.status_code}')
            #return None
    except requests.RequestException as e:
        print(f'Request failed: {e}')
        #return None
"""

def get_tts_audio(speaker, text):
    print("the text: ",text)
    """
    text to speech
    """
    # API endpoint
    api_url = 'https://tat-tts.api.translate.tatar/listening/'

    # Parameters
    params = {
        'speaker': speaker,
        'text': text
    }

    try:
        # Perform the GET request with parameters
        response = requests.get(api_url, params=params, headers={'accept': 'application/json'})

        # Check if request was successful
        if response.status_code == 200:
            # Parse JSON response
            json_response = response.json()

            # Extract WAV data and sample rate from JSON
            wav_base64 = json_response['wav_base64']
            sample_rate = json_response['sample_rate']

            # Decode base64 to binary
            audio_data = base64.b64decode(wav_base64)

            save_directory = os.path.join(settings.MEDIA_ROOT, 'uploaded_audio')
            output_file = os.path.join(save_directory, 'spoken_phrase.wav')
            with open(output_file, 'wb') as f:
                f.write(audio_data)
            print(f'WAV file saved: {output_file}')
            return output_file
        else:
            print(f'Failed to get response. Status code: {response.status_code}')
            return None
    except requests.RequestException as e:
        print(f'Request failed: {e}')
        return None

def transcribe_audio(file_path):
    """
    speech to text
    """
    # API endpoint
    api_url = 'https://tat-asr.api.translate.tatar/listening/'

    # Extract the file name from the complete file path
    file_name = os.path.basename(file_path)

    # Open the audio file in binary mode
    with open(file_path, 'rb') as audio_file:
        files = {
            'file': (file_name, audio_file, 'audio/wav')
        }

        try:
            # Perform the POST request with the audio file
            response = requests.post(api_url, headers={'accept': 'application/json'}, files=files)

            # Check if request was successful
            if response.status_code == 200:
                # Parse JSON response
                json_response = response.json()

                # Extract the transcribed text
                transcribed_text = json_response.get('text', '')
                return transcribed_text
            else:
                print(f'Failed to get response. Status code: {response.status_code}')
                return None
        except requests.RequestException as e:
            print(f'Request failed: {e}')
            return None

def process_text_to_audio(input_text, speaker):
    # Step 1: Split the input text into a list of words
    words = input_text.split()

    # Step 2: Get TTS audio for each word and save them
    audio_files = []
    for index, word in enumerate(words, start=1):
        audio_file = get_tts_audio(speaker, word)
        if audio_file:
            # Rename the file to word1.wav, word2.wav, etc.
            new_file_name = f'word{index}.wav'
            if os.path.exists(new_file_name):
                os.remove(new_file_name)
            os.rename(audio_file, new_file_name)
            audio_files.append(new_file_name)
        else:
            print(f"Failed to get TTS for word: {word}")

    # Step 3: Calculate the duration of each audio file
    durations = []
    for audio_file in audio_files:
        audio = AudioSegment.from_wav(audio_file)
        durations.append(len(audio))

    # Step 4: Combine all the individual audio files into one single audio file
    combined = AudioSegment.empty()
    for audio_file in audio_files:
        audio = AudioSegment.from_wav(audio_file)
        combined += audio

    combined_output_file = 'combined_output.wav'
    combined.export(combined_output_file, format='wav')

    print(f'Combined audio file saved as: {combined_output_file}')
    return combined_output_file, durations


def get_audio_duration(input_audio_file):
    audio = AudioSegment.from_file(input_audio_file, format="wav")
    duration_ms = len(audio)
    return duration_ms

from pydub.exceptions import CouldntDecodeError

def duplicate_audio_segment(input_audio_file, start_ms, end_ms):
    try:
        # Load the input audio file
        audio = AudioSegment.from_file(input_audio_file, format="wav")

        # Ensure the start and end points are within the bounds of the audio
        start_ms = max(0, start_ms)
        end_ms = min(end_ms, len(audio))

        # Calculate the duration to be duplicated (30 milliseconds)
        duration_ms = 20

        # Initialize an empty list to store duplicated segments
        duplicated_segments = []

        # Iterate over the specified range and duplicate each 30 milliseconds segment
        for i in range(start_ms, end_ms, duration_ms):
            segment = audio[i:min(i + duration_ms, end_ms)]
            for j in range(3):

                 duplicated_segments.append(segment)
            

        # Concatenate duplicated segments into a single AudioSegment
        duplicated_audio = sum(duplicated_segments)

        # Extract the original audio segments before and after the specified range
        original_before = audio[:start_ms]
        original_after = audio[end_ms:]

        # Concatenate the original segments and the duplicated audio
        final_audio = original_before + duplicated_audio + original_after

        return final_audio

    except CouldntDecodeError as e:
        print("Could not decode the audio file. Please check the file format and content.")
        print(e)
        return None

def slow_sesntence_on_case(case_num_array,input_audio_files_array):
    print(input_audio_files_array)
    final=[]
    for case_num,word in zip(case_num_array,input_audio_files_array):
        duration=get_audio_duration(word)
        if case_num==0:
           final.append(AudioSegment.from_file(word, format="wav"))

        if case_num==1:
             final.append(duplicate_audio_segment(word, 0, duration//2))
        if case_num==2:
             final.append(duplicate_audio_segment(word,duration//2, duration))
        if case_num==3:
             final.append(duplicate_audio_segment(word,0, duration))
        
    return sum(final)

def string_compare(str1, str2):
    print(f"Comparing {str1} and {str2}")
    str1 = str1.lower()
    str2 = str2.lower()
    while len(str1) > len(str2):
      str2+='-'
    return [int(c[0] == c[1]) for c in list(zip(str1, str2))]


def compare(w1, w2):
    if(len(w1) != len(w2)):
        return 3
    cnt = 0

    for i in range(len(w1)):
        if(w1[i] != w2[i]):
            cnt+=1

    if(cnt == 0):
        return 0
    elif(cnt >= 2):
        return 3

    for i in range(len(w1)):
        if(w1[i] != w2[i]):
            place = (i+1) / len(w1)
            if(place <= 0.4):
                return 1
            elif(place > 0.4 and place < 0.6):
                return 3
            elif(place >= 0.6):
                return 2


def check_two_texts(s1, s2):
    words1 = s1.split()
    words2 = s2.split()
    res = []
    for i in range(len(words1)):
        ans = compare(words1[i], words2[i])
        res.append(ans)

    print(res)
    return res

import os
from pydub import AudioSegment

def main_workflow(original_text, user_audio_path, speaker='almaz'):
    # Step 1: Convert original text to audio and get durations
    combined_audio, durations = process_text_to_audio(original_text, speaker)
    # Step 2: Create an array of paths for each word's audio
    words = original_text.split()
    word_audio_paths = [f'word{i+1}.wav' for i in range(len(words))]


    # Step 3: Convert user audio to text using transcribe_audio
    print(user_audio_path)
    user_transcribed_text = transcribe_audio(user_audio_path)
    print(f"Doing somthg {user_transcribed_text}")
    if not user_transcribed_text:
        print("Transcription of user audio failed.")
        return "False"

    print("Comparing...")
    # Step 4: Compare the original text with the user transcribed text
    comparison_results = check_two_texts(original_text, user_transcribed_text)

    print("Done Comparing...")
    # Step 5: Generate a new audio with slowed segments based on comparison results
    slowed_audio = slow_sesntence_on_case(comparison_results, word_audio_paths)

    if slowed_audio:
        output_file = "final_slowed_audio.wav"
        slowed_audio.export(os.path.join(settings.MEDIA_ROOT ,output_file), format="wav")
        print(f'Final slowed audio file saved as: {output_file}')
    else:
        print("Failed to create slowed audio.")
    print("Main workflow reached end!")
    if all(result == 0 for result in comparison_results):
        print("returns True")
        return user_transcribed_text
    print("returns False")
    return user_transcribed_text


def process_letter_audio(file_path, original_letter):
    """
    takes path to audio file, and original_letter

    transcribe_audio: takes an audio file and gives text
    """
    print("Processing Letter")
    print(file_path)
    print(original_letter)
    text = transcribe_audio(file_path)
    print("transcribed text:", text)
    if list(text)[0] == original_letter.lower():
        return True
    return False

def process_audio_image(file_path, original_word):
    text = transcribe_audio(file_path)
    print("transcribed text from image:", text)
    if text == original_word:
        return True
    return False


def process_audio_phrase(file_path, phrase):
    try:
        print("Starting main workflow with phrase:", phrase, "and file path:", file_path)
        answer = main_workflow(phrase, file_path)
        return answer
    except Exception as e:
        print("Error in process_audio_phrase:", e)
        raise  # Re-raise the exception to be handled by the caller
