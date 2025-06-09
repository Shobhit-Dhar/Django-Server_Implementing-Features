from django.shortcuts import render
import tempfile
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

# Import our AI services
from .services.transcription import transcribe_and_diarize
from .services.title_generator import generate_titles


class AudioTranscriptionView(APIView):

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        audio_file = request.FILES.get('audio_file')
        if not audio_file:
            return Response(
                {"error": "No audio file provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        temp_file_path = None
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as temp_f:
                for chunk in audio_file.chunks():
                    temp_f.write(chunk)
                temp_file_path = temp_f.name

            # Process the file using our transcription service
            transcription_result = transcribe_and_diarize(temp_file_path)
            return Response(transcription_result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"An error occurred during processing: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            # Clean up the temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)


class TitleSuggestionView(APIView):


    def post(self, request, *args, **kwargs):
        content = request.data.get('content')
        if not content or len(content.strip()) < 100:
            return Response(
                {"error": "Content is missing or too short. Please provide at least 100 characters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get suggestions from our title generation service
            suggestions = generate_titles(content)
            return Response({"suggestions": suggestions}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Failed to generate titles: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
