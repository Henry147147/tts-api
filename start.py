from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import edge_tts
import tempfile
import base64

app = FastAPI()

# Models for input validation
class TTSRequest(BaseModel):
    text: str
    voice: str
    rate: int
    pitch: int = 0

# Endpoint to get all available voices
@app.get("/voices")
async def get_available_voices():
    try:
        voices = await edge_tts.list_voices()
        return {
            "voices": {
                f"{v['ShortName']} - {v['Locale']} ({v['Gender']})": v['ShortName']
                for v in voices
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching voices: {str(e)}")


@app.get("/languages")
async def get_available_languages():
    try:
        voices = await edge_tts.list_voices()
        langs = sorted(set([v['ShortName'].split("-")[0] for v in voices]))

        return {
            "languages": langs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching voices: {str(e)}")


# Helper function to perform TTS and return MP3 data
async def perform_tts(text, voice, rate, pitch):
    rate_str = f"{rate:+d}%"
    pitch_str = f"{pitch:+d}Hz"
    voice_short_name = voice.split(" - ")[0]
    communicate = edge_tts.Communicate(text, voice_short_name, rate=rate_str, pitch=pitch_str)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_path = tmp_file.name
        await communicate.save(tmp_path)

    # Read the MP3 data and encode it in base64
    with open(tmp_path, "rb") as mp3_file:
        mp3_data = mp3_file.read()
    return base64.b64encode(mp3_data).decode("utf-8")

# Endpoint for text-to-speech
@app.post("/text-to-speech")
async def generate_speech(request: TTSRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    if not request.voice:
        raise HTTPException(status_code=400, detail="Voice must be provided.")

    try:
        mp3_base64 = await perform_tts(request.text, request.voice, request.rate, request.pitch)
        return {
            "message": "Text-to-speech conversion successful.",
            "mp3_data": mp3_base64,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in TTS: {str(e)}")
