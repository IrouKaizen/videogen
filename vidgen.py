import os

def create_dir(dir_path):
    os.makedirs(dir_path, exist_ok=True)
    print(f'Created {dir_path} directory')

from icrawler.builtin import GoogleImageCrawler

def gather_media(query):
    try:
        create_dir(image_dir)
        google_Crawler = GoogleImageCrawler(storage={'root_dir': image_dir})
        google_Crawler.crawl(keyword=query, min_size=(width, height), max_size=None, max_num=200)
        images = os.listdir(image_dir)
        print(f"Collected {len(images)} images.")
        return [os.path.join(image_dir, image) for image in images]
    except Exception as e:
        logging.error(f'Error in gather_media: {str(e)}')
        print(f'Error in gather_media: {str(e)}')
        return []

def generate_text(description):
    additional_sentences = f"Generated text based on the description: {description}"
    print(f"Generated text: {additional_sentences}")
    return additional_sentences

from gtts import gTTS

def create_audio(description):
    try:
        create_dir(audio_dir)
        additional_sentences = generate_text(description)
        text = additional_sentences
        tts = gTTS(text=text, lang='en')
        audio_file_path = os.path.join(audio_dir, filename + '.mp3')
        tts.save(audio_file_path)
        print(f"Generated audio file at: {audio_file_path}")
        return additional_sentences
    except Exception as e:
        logging.error(f'Error in create_audio: {str(e)}')
        print(f'Error in create_audio: {str(e)}')
        return description

from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import audioread

def create_video(images, audio_file):
    try:
        create_dir(video_dir)
        with audioread.audio_open(audio_file) as f:
            audio_duration = int(f.duration)
        image_duration = 3
        print('Total Duration: {} seconds'.format(audio_duration))

        num_loops = int(audio_duration / image_duration)
        print('Number of loops: {}'.format(num_loops))

        width, height = (1920, 1080)

        clips = []
        i = 0
        while i < num_loops:
            print("Creating video clips")
            for image in images:
                try:
                    clip = ImageClip(image).set_duration(image_duration)
                    clips.append(clip)
                    print(f"Added clip: {image}")
                    i += 1
                    if i >= num_loops:
                        break
                except Exception as e:
                    print(f"Error opening image: {image}. Error message: {str(e)}")
            if i >= num_loops:
                break
        print("Combining video clips")
        concat_clip = concatenate_videoclips(clips, method="compose")
        audio = AudioFileClip(audio_file)
        video = concat_clip.set_audio(audio)
        print("Writing video file")
        video_file_path = os.path.join(video_dir, filename + '.mp4')
        video.write_videofile(video_file_path, fps=24)
        print(f"Video saved at {video_file_path}")
    except Exception as e:
        logging.error(f'Error in create_video: {str(e)}')
        print(f"Error in create_video: {str(e)}")

import os
import logging

# Configurer le logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Définir les variables globales
image_dir = 'images'
audio_dir = 'audio'
video_dir = 'videos'
filename = 'output_video'
width, height = (1920, 1080)

# Fonction de création de répertoire
def create_dir(dir_path):
    os.makedirs(dir_path, exist_ok=True)
    print(f'Created {dir_path} directory')

# Fonction de collecte de médias
def gather_media(query):
    try:
        create_dir(image_dir)
        google_Crawler = GoogleImageCrawler(storage={'root_dir': image_dir})
        google_Crawler.crawl(keyword=query, min_size=(width, height), max_size=None, max_num=200)
        images = os.listdir(image_dir)
        print(f"Collected {len(images)} images.")
        return [os.path.join(image_dir, image) for image in images]
    except Exception as e:
        logging.error(f'Error in gather_media: {str(e)}')
        print(f'Error in gather_media: {str(e)}')
        return []

# Fonction de génération de texte
def generate_text(description):
    additional_sentences = f"Generated text based on the description: {description}"
    print(f"Generated text: {additional_sentences}")
    return additional_sentences

# Fonction de création d'audio
from gtts import gTTS

def create_audio(description):
    try:
        create_dir(audio_dir)
        additional_sentences = generate_text(description)
        text = additional_sentences
        tts = gTTS(text=text, lang='en')
        audio_file_path = os.path.join(audio_dir, filename + '.mp3')
        tts.save(audio_file_path)
        print(f"Generated audio file at: {audio_file_path}")
        return additional_sentences
    except Exception as e:
        logging.error(f'Error in create_audio: {str(e)}')
        print(f'Error in create_audio: {str(e)}')
        return description

# Fonction de création de vidéo
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import audioread

def create_video(images, audio_file):
    try:
        create_dir(video_dir)
        with audioread.audio_open(audio_file) as f:
            audio_duration = int(f.duration)
        image_duration = 3
        print('Total Duration: {} seconds'.format(audio_duration))

        num_loops = int(audio_duration / image_duration)
        print('Number of loops: {}'.format(num_loops))

        width, height = (1920, 1080)

        clips = []
        i = 0
        while i < num_loops:
            print("Creating video clips")
            for image in images:
                try:
                    clip = ImageClip(image).set_duration(image_duration)
                    clips.append(clip)
                    print(f"Added clip: {image}")
                    i += 1
                    if i >= num_loops:
                        break
                except Exception as e:
                    print(f"Error opening image: {image}. Error message: {str(e)}")
            if i >= num_loops:
                break
        print("Combining video clips")
        concat_clip = concatenate_videoclips(clips, method="compose")
        audio = AudioFileClip(audio_file)
        video = concat_clip.set_audio(audio)
        print("Writing video file")
        video_file_path = os.path.join(video_dir, filename + '.mp4')
        video.write_videofile(video_file_path, fps=24)
        print(f"Video saved at {video_file_path}")
    except Exception as e:
        logging.error(f'Error in create_video: {str(e)}')
        print(f"Error in create_video: {str(e)}")

# Exemple d'utilisation des fonctions
description = "Beautiful landscapes of Togo"
images = gather_media(description)
audio_text = create_audio(description)
audio_file = os.path.join(audio_dir, filename + '.mp3')
create_video(images, audio_file)

import os
import logging
from icrawler.builtin import GoogleImageCrawler
from gtts import gTTS
from moviepy.editor import ImageSequenceClip, AudioFileClip

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up directories
if not os.path.exists('images'):
    os.makedirs('images')
    logging.info('Created images directory')

if not os.path.exists('audio'):
    os.makedirs('audio')
    logging.info('Created audio directory')

# Set up Google image crawler
google_crawler = GoogleImageCrawler(storage={'root_dir': 'images'})
logging.info('Starting image crawl')
google_crawler.crawl(keyword='Beautiful landscapes of Togo', max_num=10, file_idx_offset=0)

# Check for downloaded images
if not os.listdir('images'):
    logging.error('No images downloaded. Exiting...')
    exit(1)

# Generate text and convert to speech
text = "Generated text based on the description: Beautiful landscapes of Togo"
logging.debug(f'Generated text: {text}')
tts = gTTS(text)
audio_path = 'audio/narration.mp3'
tts.save(audio_path)
logging.info(f'Audio saved at {audio_path}')

# Create video from images
image_files = [os.path.join('images', img) for img in os.listdir('images')]
logging.debug(f'Image files: {image_files}')
clip = ImageSequenceClip(image_files, fps=1)

# Add audio to video
audio = AudioFileClip(audio_path)
video = clip.set_audio(audio)
video_path = 'output_video.mp4'
video.write_videofile(video_path, codec='libx264', audio_codec='aac')
logging.info(f'Video created at {video_path}')

