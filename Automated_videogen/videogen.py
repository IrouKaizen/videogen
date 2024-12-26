import requests
import audioread
from PIL import Image
from transformers import pipeline, set_seed
from transformers import GPT2Tokenizer, AutoModelForCausalLM
import json
import os
import pysrt
import whisper
from gtts import gTTS
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from icrawler.builtin import GoogleImageCrawler
import re
import logging
import torch
import configparser
import datetime


# Load configuration from a config file
config = configparser.ConfigParser()
config.read('config.ini')

# Getting configurations from config
max_filename_length = int(config['General']['max_filename_length'])
logs_dir = config['General']['logs_dir']
general_log = config['General']['general_log']
google_api_key = config['API']['google_custom_search_api_key']
search_engine_id = config['API']['search_engine_id']

# Create directories for output
output_dir = "output"
image_dir = os.path.join(output_dir, 'images')
audio_dir = os.path.join(output_dir, 'audio')
video_dir = os.path.join(output_dir, 'video')
subtitle_dir = os.path.join(output_dir, 'subtitle')

# Create directories function
def create_dir(dir_path):
    os.makedirs(dir_path, exist_ok=True)
    print(f'Created {dir_path} directory')

create_dir(logs_dir)

# Initialize logging
logging.basicConfig(filename=os.path.join(logs_dir, general_log), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Log filename
filename = "default_filename"  # Replace this as needed
logging.info(f'Filename: {filename}')

# Configure settings for FFmpeg
def change_settings(settings):
    try:
        print("Hardware acceleration is set to:", settings.get("FFMPEG_HWACCEL", "None"))
    except Exception as e:
        logging.error(f'Error in change_settings: {str(e)}')

# Change FFmpeg settings for hardware acceleration
change_settings({
    "FFMPEG_HWACCEL": "auto",
    "FFMPEG_VIDEOPRESET": "fast",
    "FFMPEG_VIDEO_CODEC": "h264"
})

# Search for a topic using Google Custom Search API
def search_topic(query, api_key, search_engine_id):
    try:
        url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}"
        res = requests.get(url)
        data = json.loads(res.text)
        return data.get('items', [])
    except Exception as e:
        logging.error(f'Error in search_topic: {str(e)}')
        return []

# Gather media using Google Image Crawler
def gather_media(query):
    try:
        create_dir(image_dir)
        google_Crawler = GoogleImageCrawler(storage={'root_dir': image_dir})
        google_Crawler.crawl(keyword=query, min_size=(1920, 1080), max_num=200)
        images = os.listdir(image_dir)
        return [os.path.join(image_dir, image) for image in images]
    except Exception as e:
        logging.error(f'Error in gather_media: {str(e)}')
        return []

# Device configuration for PyTorch
device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
device_id = device.index

# Generate text using GPT-2
def generate_text(description):
    model_name = "gpt2"
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    
    try:
        generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=device_id)
        additional_sentences = generator(description, max_length=1000, num_return_sequences=1)[0]['generated_text']
        del generator
        del model
        torch.cuda.empty_cache()
        return additional_sentences
    except Exception as e:
        logging.error(f'Error in generate_text: {str(e)}')
        return description

# Create audio using gTTS
def create_audio(description):
    try:
        additional_sentences = generate_text(description)
        tts = gTTS(text=additional_sentences, lang='en')
        audio_path = os.path.join(audio_dir, filename + '.mp3')
        tts.save(audio_path)
        return additional_sentences
    except Exception as e:
        logging.error(f'Error in create_audio: {str(e)}')
        return description

# Create video from images and audio
def create_video(images, audio_file):
    try:
        create_dir(video_dir)
        with audioread.audio_open(audio_file) as f:
            audio_duration = int(f.duration)

        image_duration = 3
        num_loops = int(audio_duration / image_duration)
        clips = []

        for image in images:
            try:
                clip = ImageClip(image).set_duration(image_duration)
                clips.append(clip)
                if len(clips) >= num_loops:
                    break
            except Exception as e:
                logging.error(f'Error opening image: {image}. Error message: {str(e)}')

        concat_clip = concatenate_videoclips(clips, method="compose")
        audio = AudioFileClip(audio_file)
        video = concat_clip.set_audio(audio)
        video_path = os.path.join(video_dir, filename + '.mp4')
        video.write_videofile(video_path, fps=24)
        logging.info(f'Video saved at {video_path}')
    except Exception as e:
        logging.error(f'Error in create_video: {str(e)}')

# Generate subtitles using Whisper
def generate_subtitle(audio_file):
    try:
        create_dir(subtitle_dir)
        model = whisper.load_model("base", device="cuda")
        result = model.transcribe(audio_file)
        subtitle_path = os.path.join(subtitle_dir, filename + '.srt')
        subs = pysrt.SubRipFile()
        for idx, segment in enumerate(result['segments']):
            start_time = datetime.timedelta(seconds=segment['start'])
            end_time = datetime.timedelta(seconds=segment['end'])
            text = segment['text']
            subs.append(pysrt.SubRipItem(index=idx+1, start=start_time, end=end_time, text=text))
        subs.save(subtitle_path)
        logging.info(f'Subtitles saved at {subtitle_path}')
    except Exception as e:
        logging.error(f'Error in generate_subtitle: {str(e)}')

# Main execution flow
def main(query):
    images = gather_media(query)
    description = "This is a sample description for video generation."  # Replace with actual content
    create_audio(description)
    audio_file = os.path.join(audio_dir, filename + '.mp3')
    create_video(images, audio_file)
    generate_subtitle(audio_file)

# Run the main function
if __name__ == "__main__":
    search_query = input("Enter search query: ")
    main(search_query)
