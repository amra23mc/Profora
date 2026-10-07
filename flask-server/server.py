import os
import sys

ffmpeg_bin_path = r"C:\Users\amra2\Voice Pronunciation - React\ffmpeg-9.0-essentials_build\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

from pydub import AudioSegment
from pathlib import Path

AudioSegment.converter = os.path.join(ffmpeg_bin_path, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(ffmpeg_bin_path, "ffprobe.exe")


from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np

import pyttsx3
import edge_tts
import asyncio

from transformers import AutoTokenizer, AutoModelForCausalLM

from scipy.io.wavfile import read
import matplotlib.pyplot as plt

encoder = VoiceEncoder()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

thefilepath = ""

text = "Hello World"

#Members API Route
@app.route("/text", methods = ["POST"])
def getText():
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
    model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct", device_map="auto")
    messages = [
        {"role": "user", "content": "Generate a simple coherent sentence between 5 to 7 words."},
    ]
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)

    outputs = model.generate(**inputs, max_new_tokens=40)

    global text
    text = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)

    asyncio.run(getReferenceAudio())

    return text

async def getReferenceAudio():
    mp3Path = os.path.join(app.config['UPLOAD_FOLDER'], "reference.mp3")
    wavPath = os.path.join(app.config['UPLOAD_FOLDER'], "reference.wav")

    engine = edge_tts.Communicate(text, "en-US-AvaNeural")
    await engine.save(mp3Path)

    sound = AudioSegment.from_mp3(mp3Path)
    sound = sound.set_frame_rate(16000).set_channels(1)
    sound.export(wavPath, format='wav')


@app.route("/sendAudio", methods = ["POST"])
def sendAudio():
    return send_file("uploads/reference.wav", mimetype="audio/wav")


@app.route("/resemblyzer", methods = ["POST"])
def resemblyzer():
    # engine = pyttsx3.init()

    # engine.setProperty('rate', 150)
    # engine.setProperty('volume', 1.0)
    

    if 'audioFile' not in request.files:
        return jsonify({"error": "No file payload detected in request keys"}), 400

    file = request.files['audioFile']

    if file.filename == "":
        return jsonify({"error": "Empty filename submitted"}), 400

    try:
        filename = secure_filename(file.filename)
        webm_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(webm_path)

        wav_filename = filename.rsplit('.', 1)[0] + ".wav"
        wav_path = os.path.join(app.config['UPLOAD_FOLDER'], wav_filename)

        audio = AudioSegment.from_file(webm_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_path, format = "wav")

        global thefilepath
        thefilepath = wav_path
        
        os.remove(webm_path)
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500
    

    wav1 = preprocess_wav(Path(wav_path))
    wav2 = preprocess_wav(Path("uploads/reference.wav"))

    embed1 = encoder.embed_utterance(wav1)
    embed2 = encoder.embed_utterance(wav2)

    similarity = np.dot(embed1, embed2,) / (np.linalg.norm(embed1) * np.linalg.norm(embed2))

    result = int(similarity * 100)
    
    return jsonify(result)

@app.route("/plotlib", methods = ["POST"])
def plot_lib():
    input_data = read(thefilepath)

    audio = input_data[1]

# @app.route('/')
# def home():
#     return "Welcome to the Home Page!"

if __name__ == '__main__':
    app.run(debug=True)