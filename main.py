import os
from transcriber import extract_audio, transcribe_audio
from summarizer import summarize_text
from utils import chunked_summarize

def video_to_summary(
        video_path: str, 
        model_size: str = "base", 
        summarizer_model_name: str = "facebook/bart-large-cnn",
        use_chunking: bool = False
) -> str:
    
    # 1. Extract audio from video
    audio_path = "temp_audio.wav"
    extract_audio(video_path, audio_path)

    # 2. Transcribe audio to text
    transcript = transcribe_audio(audio_path, model_size=model_size)

    # 3. Summarize the transcript
    if use_chunking:
        # Summarize in multiple chunks and then do a final summary
        final_summary = chunked_summarize(
            text=transcript,
            summarize_func=lambda txt: summarize_text(
                txt, model_name=summarizer_model_name
            ),
            max_chunk_size=2000
        )
    else:
        # Summarize the entire transcript at once
        final_summary = summarize_text(
            transcript, 
            model_name=summarizer_model_name
        )

    # Audio file is not deleted
    return final_summary