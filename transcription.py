
import whisperx
from whisperx.diarize import DiarizationPipeline
import torch
import gc


# Determine device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = 16
COMPUTE_TYPE = "float16" if torch.cuda.is_available() else "int8"


model = whisperx.load_model("large-v2", DEVICE, compute_type=COMPUTE_TYPE)


def transcribe_and_diarize(audio_file_path: str):
    try:
        audio = whisperx.load_audio(audio_file_path)

        result = model.transcribe(audio, batch_size=BATCH_SIZE)


        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=DEVICE)
        result = whisperx.align(result["segments"], model_a, metadata, audio, DEVICE, return_char_alignments=False)


        diarize_model = DiarizationPipeline(use_auth_token=True, device=DEVICE)
        diarize_segments = diarize_model(audio)

        result = whisperx.assign_word_speakers(diarize_segments, result)

        # Clean up memory
        del model_a
        gc.collect()
        torch.cuda.empty_cache()

        # Formatting
        formatted_segments = []
        for segment in result["segments"]:
            formatted_segments.append({
                "start": segment.get("start"),
                "end": segment.get("end"),
                "text": segment.get("text").strip(),
                "speaker": segment.get("speaker", "UNKNOWN")
            })

        return formatted_segments

    except Exception as e:
        print(f"Error during transcription/diarization: {e}")
        raise e
