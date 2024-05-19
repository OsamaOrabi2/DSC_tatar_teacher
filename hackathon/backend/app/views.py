# backend/audio_processing/views.py

from django.http import JsonResponse
from django.views import View
from django.core.files.storage import default_storage
from .utils import process_letter_audio, process_audio_image
import os
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
from .utils import get_tts_audio, process_audio_phrase, string_compare

@csrf_exempt
def tts(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        text = data.get('text')
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)
        
        audio_path = get_tts_audio(speaker='almaz',text=text)
        return JsonResponse({'audio_path': audio_path})
"""
from .utils import filter_noise

def filter_noise_view(request):
    if request.method == 'POST':
        # Assuming the audio file path is sent as a POST request
        audio_file_path = request.POST.get('path')
        
        if audio_file_path:
            # Call the filter_noise function
            improved_audio_path, ratio = filter_noise(audio_file_path)
            
            # Return the response
            return JsonResponse({'improved_audio_path': improved_audio_path, 'ratio': ratio})
        else:
            return JsonResponse({'error': 'Audio file path is required.'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
"""
class FileUploadView(View):
    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return JsonResponse({'result': False, 'message': 'No file uploaded.'}, status=400)
        
        uploaded_file = request.FILES['file']
        file_name = default_storage.save(uploaded_file.name, uploaded_file)
        file_path = default_storage.path(file_name)

        try:
            # Process the audio file
            is_correct = process_audio(file_path)
            result = {'result': is_correct}
        except Exception as e:
            result = {'result': False, 'message': str(e)}
            return JsonResponse(result, status=500)
        finally:
            # Clean up the uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return JsonResponse(result, status=201)


class LetterFileUploadView(View):
    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return JsonResponse({'result': False, 'message': 'No file uploaded.'}, status=400)

        uploaded_file = request.FILES['file']
        letter = request.POST.get('letter', '')

        # Define the save directory and ensure it exists
        save_directory = os.path.join(settings.MEDIA_ROOT, 'uploaded_audio')

        # Save the uploaded file to the directory
        file_path = os.path.join(save_directory, uploaded_file.name)
        try:
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            print(f"File saved successfully at: {file_path}")
        except Exception as e:
            print(f"Error saving file: {e}")
            return JsonResponse({'result': False, 'message': 'File saving failed.'}, status=500)

        try:
            # Process the audio file
            is_correct = process_letter_audio(file_path, letter)
            result = {'result': is_correct}
        except Exception as e:
            result = {'result': False, 'message': str(e)}
            return JsonResponse(result, status=500)
        finally:
            #pass
            #Clean up the uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return JsonResponse(result, status=201)

class WordFileUploadView(View):
    def post(self, request, *args, **kwargs):
        # Check if the image file exists in the request.FILES
        if 'file' not in request.FILES:
            return JsonResponse({'result': False, 'message': 'No word uploaded.'}, status=400)

        # Get the uploaded image file
        uploaded_word = request.FILES['file']
        word = request.POST.get('word', '')

        print(uploaded_word.name)
        # Define the save directory and ensure it exists
        save_directory = os.path.join(settings.MEDIA_ROOT, 'uploaded_audio')

        # Save the uploaded image to the directory
        file_path = os.path.join(save_directory, uploaded_word.name)
        try:
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_word.chunks():
                    destination.write(chunk)
            print(f"Image word saved successfully at: {file_path}")
        except Exception as e:
            print(f"Error saving image: {e}")
            return JsonResponse({'result': False, 'message': 'Image saving failed.'}, status=500)

        try:
            # Process the image
            # Add your image processing logic here
            is_correct = process_audio_image(file_path, word)
            result = {'result': is_correct}
        except Exception as e:
            result = {'result': False, 'message': str(e)}
            return JsonResponse(result, status=500)
        finally:
            # Clean up the uploaded image file
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return JsonResponse(result, status=201)
"""        
class ImageFileUploadView(View):
    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return JsonResponse({'result': False, 'message': 'No file uploaded.'}, status=400)
        
        uploaded_file = request.FILES['file']
        file_name = default_storage.save(uploaded_file.name, uploaded_file)
        file_path = default_storage.path(file_name)
        word = request.POST['word']
        try:
            # Process the audio file
            is_correct = process_audio_image(file_path, word)
            result = {'result': is_correct}
        except Exception as e:
            result = {'result': False, 'message': str(e)}
            return JsonResponse(result, status=500)
        finally:
            # Clean up the uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return JsonResponse(result, status=201)
"""
"""
class PhraseFileUploadView(View):
    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return JsonResponse({'result': False, 'message': 'No file uploaded.'}, status=400)

        uploaded_file = request.FILES['file']
        phrase = request.POST.get('phrase', '')

        # Define the save directory and ensure it exists
        save_directory = os.path.join(settings.MEDIA_ROOT, 'uploaded_audio')
        os.makedirs(save_directory, exist_ok=True)

        # Save the uploaded file to the directory
        file_path = os.path.join(save_directory, uploaded_file.name)
        try:
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            print(f"File saved successfully at: {file_path}")
        except Exception as e:
            print(f"Error saving file: {e}")
            return JsonResponse({'result': False, 'message': 'File saving failed.'}, status=500)

        try:
            print("Processing...")
            is_correct = process_audio_phrase(file_path, phrase)
            print("Result from processing:", is_correct)
            result = {'result': is_correct}
        except Exception as e:
            print("Error during processing:", e)
            result = {'result': False, 'message': str(e)}
            return JsonResponse(result, status=500)
        finally:
            pass
            # Clean up the uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return JsonResponse(result, status=201)
"""
class PhraseFileUploadView(View):
    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return JsonResponse({'result': False, 'message': 'No file uploaded.'}, status=400)

        uploaded_file = request.FILES['file']
        phrase = request.POST.get('phrase', '')

        # Define the save directory and ensure it exists
        save_directory = os.path.join(settings.MEDIA_ROOT, 'uploaded_audio')
        os.makedirs(save_directory, exist_ok=True)

        # Save the uploaded file to the directory
        file_path = os.path.join(save_directory, uploaded_file.name)
        try:
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            print(f"File saved successfully at: {file_path}")
        except Exception as e:
            print(f"Error saving file: {e}")
            return JsonResponse({'result': False, 'message': 'File saving failed.'}, status=500)

        try:
            print("Processing...")
            # Process the audio file to get the transcribed phrase
            transcribed_phrase = process_audio_phrase(file_path, phrase)
            print("Transcribed phrase:", transcribed_phrase)
            
            # Compare the transcribed phrase with the provided phrase
            evaluation = string_compare(transcribed_phrase, phrase)
            is_correct = all(evaluation)
            print("Evaluation:", evaluation)
            result = {'result': is_correct, 'evaluation': evaluation}
        except Exception as e:
            print("Error during processing:", e)
            result = {'result': False, 'message': str(e)}
            return JsonResponse(result, status=500)
        finally:
            # Clean up the uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return JsonResponse(result, status=201)