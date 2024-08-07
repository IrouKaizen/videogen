import requests
import audioread
from PIL import Image
from transformers import pipeline, set_seed
from transformers import GPT2Tokenizer, AutoModelForCausalLM
import json
import urllib
import os
import pysrt
import whisper
from gtts import gTTS
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from icrawler.builtin import GoogleImageCrawler
from moviepy.config import change_settings
from moviepy.video.fx.all import crop
import re
import os
import pysrt
from moviepy.editor import VideoFileClip
import whisper
import datetime
import torch
import re
import logging
import threading
import configparser

"""
    1. requests :

Sert à effectuer des requêtes HTTP vers des serveurs web. Elle vous permet de récupérer des données (texte, images, etc.) à partir de sites web et d'API.
2. audioread :

Conçue pour lire des fichiers audio dans divers formats (MP3, WAV, FLAC, etc.). Elle extrait les données audio pour un traitement ultérieur.
3. PIL (Pillow Fork) :

Une bibliothèque de traitement d'image puissante. Vous pouvez l'utiliser pour charger, manipuler et enregistrer des images dans divers formats (JPEG, PNG, etc.), effectuer des transformations (redimensionnement, recadrage, etc.) et appliquer des filtres.
4. transformers :

Une bibliothèque populaire pour travailler avec des modèles de traitement du langage naturel (NLP) de pointe. Voici une description des composants spécifiques utilisés dans votre code :

Fonction pipeline : Crée des pipelines pour diverses tâches de NLP comme la génération de texte, la réponse aux questions ou la classification de texte.
set_seed : Définit une graine aléatoire pour la reproductibilité (en s'assurant que les sorties du modèle sont cohérentes pour la même entrée).
GPT2Tokenizer (facultatif) : Un tokenizer pour les modèles de langage GPT-2, utilisé pour convertir le texte en représentations numériques pour le modèle.
AutoModelForCausalLM (facultatif) : Une classe pour charger divers modèles de langage causal (modèles qui prédisent le mot suivant en fonction des précédents).
5. json :

Facilite le travail avec le format de données JSON (JavaScript Object Notation). Il vous permet d'analyser des chaînes ou des fichiers JSON en dictionnaires Python et vice versa.
6. urllib :

Offre diverses fonctionnalités liées à la programmation réseau, y compris la gestion des URL et la récupération de données.
7. os :

Fournit des fonctions pour interagir avec le système d'exploitation, telles que l'accès aux fichiers, la création de répertoires et l'exécution de commandes.
8. pysrt :

Une bibliothèque pour travailler avec les fichiers de sous-titres SubRip (SRT), un format courant pour stocker les sous-titres des vidéos. Vous pouvez l'utiliser pour lire, écrire et manipuler des sous-titres.
9. whisper :

Une bibliothèque de pointe pour la reconnaissance automatique de la parole (ASR). Elle peut transcrire des fichiers audio en texte.
10. gtts :

Bibliothèque Google Text-to-Speech (gTTS) qui vous permet de convertir du texte en parole audio dans différentes langues.
11. moviepy :

Une bibliothèque de montage vidéo puissante. Elle vous permet de créer, de manipuler et d'exporter des vidéos avec divers effets et transitions. Voici quelques composants spécifiques utilisés dans votre code :

VideoFileClip : Utilisé pour charger et modifier des fichiers vidéo existants.
CompositeVideoClip : Vous permet de combiner plusieurs clips vidéo en un seul.
TextClip : Crée des superpositions de texte sur les vidéos.
SubtitlesClip : Crée des superpositions de sous-titres sur les vidéos à l'aide de fichiers SRT.
change_settings : Modifie les paramètres de montage vidéo tels que la fréquence d'images ou le codec audio.
crop : Recadre les parties indésirables des images vidéo.
12. icrawler (non explicitement utilisé dans l'extrait de code fourni) :

Une bibliothèque de crawler d'images qui vous aide à télécharger automatiquement des images à partir d'Internet en fonction de termes de recherche ou de filtres spécifiques.
13. re (expressions régulières) :

Un module pour travailler avec les expressions régulières, des outils puissants pour la recherche de motifs et la manipulation de texte.
14. logging :

Utilisé pour créer des journaux de l'activité de votre programme, fournissant des informations précieuses sur son comportement et ses problèmes potentiels.
15. threading :

Un module pour créer des threads, ce qui permet à votre programme d'exécuter plusieurs tâches simultanément.
16. configparser :

Fournit des fonctions pour lire et écrire des fichiers de configuration au format INI (initialisation). Ces fichiers stockent les paramètres et les options de votre programme.
    """

# Load configuration from a config file
config = configparser.ConfigParser() #L'objet config créé par cette ligne sera utilisé pour stocker les données du fichier de configuration.
config.read('config.ini') #Cette ligne lit le contenu du fichier de configuration config.ini et l'enregistre dans l'objet config.

# Getting configurations from config

#ça charge des paramètres depuis un fichier de configuration et les stockent dans des variables

max_filename_length = int(config['General']['max_filename_length']) # clé du paramètre spécifique que l'on veut récupérer.
logs_dir = config['General']['logs_dir'] # récupère la valeur de la clé l'enregistre
general_log = config['General']['general_log']
google_api_key = config['API']['google_custom_search_api_key'] #recherche
search_engine_id = config['API']['search_engine_id'] #cible le moteur


# Get the search query from the user
query = input("Enter search query: ") #recherhce

# Truncate the query to the maximum filename length
filename = query[:min(len(query), max_filename_length)] #s'assure que le nom de fichier ne dépasse pas une limite de longueur maximale pour les noms de fichiers

# Replacing all non-alphanumeric characters with a hyphen using regular expression
filename = re.sub('[^0-9a-zA-Z.-]+', '-', filename) #remplace toutes les occurrences de ces caractères non alphanumériques par un
#tiret (-) dans la variable filename. Cela garantit que le nom de fichier est compatible avec la plupart des systèmes d'exploitation.

#Ce code définit la structure des répertoires pour le processus de génération vidéo.
#settingfilepaths
output_dir = "output" #les fichiers générés seront placés ici
image_dir = os.path.join(output_dir,filename) #construit le chemin d'accès au répertoire qui stockera les images utilisées dans la vidéo
audio_dir = os.path.join(output_dir,'audio')
video_dir = os.path.join(output_dir,'video')
subtitle_dir = os.path.join(output_dir,'subtitle')
# keeping the logs file seperate
llm_log = os.path.join(logs_dir,'results.txt') #fonctionnement sur n'importe quel OS

#create directories function
def create_dir(dir_path): #création du repertoire et confirmation du repertoire créé
    os.makedirs(dir_path, exist_ok= True)
    print(f'created {dir_path} directory')

create_dir(logs_dir) #appelle la fonction create_dir avec la variable logs_dir comme argument, en essayant de créer un répertoire de journaux s'il n'existe pas déjà.

# Initialize logging
#messagz de journalisation
logging.basicConfig(filename = os.path.join(logs_dir,general_log), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# logging the filename
logging.info(f'Filename: {filename}') #enregistre un message d'information dans le fichier journal.


#modifier les paramètres pour activer l'accélération matérielle FFmpeg (si possible)
def change_settings(settings):
    try:
        # Your existing settings change code...
        print("Hardware acceleration is set to: ", settings["FFMPEG_HWACCEL"])
    #Cet argument setting est un dictionnaire contenant les paramètres à modifier.

    except Exception as e:
        print("An error occurred when trying to use hardware acceleration: ", e)
        print("Falling back to running FFmpeg without hardware acceleration.") #désactiver l'accélération matérielle en raison de l'erreu

        # Modify settings to not use hardware acceleration
        settings["FFMPEG_HWACCEL"] = None #desactive
        settings["FFMPEG_VIDEO_CODEC"] = "h264" #modifie le paramètre pour s'assurer qu'un codec vidéo compatible est utilisé, tel que h264.

        # Your existing settings change code...
        print("Hardware acceleration is set to: ", settings["FFMPEG_HWACCEL"])

# Call the function with your settings
change_settings({
    "FFMPEG_HWACCEL": "auto", #active/desactive l'accélération matérielle
    "FFMPEG_VIDEOPRESET": "fast", #préréglage à utiliser pour l'encodage des vidéos. La valeur "fast" indique à change_settings de privilégier la vitesse à la qualité lors de l'encodage. 
    "FFMPEG_VIDEO_CODEC": "h264" #pour l'encodage vidéo
})



# Step 1: Search for interesting topics

# permet de rechercher un sujet sur Internet en utilisant l'API Google Custom Search.
# Elle renvoie une liste d'éléments de recherche trouvés ou une liste vide en cas d'erreur.

def search_topic(query, api_key, search_engine_id):
    try:
        url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}"
        res = requests.get(url)
        data = json.loads(res.text)
        return data.get('items', [])
    except Exception as e:
        logging.error(f'Error in search_topic: {str(e)}')
        return []

width, height = (1920, 1080)


# Step 2: Gather media

# permet de collecter des images sur Internet en utilisant un robot d'exploration d'images Google et de les enregistrer dans un répertoire spécifié.
def gather_media(query):
    try:
        create_dir(image_dir)
        google_Crawler = GoogleImageCrawler(storage ={'root_dir': image_dir})
        print(filename)
        google_Crawler.crawl(keyword=query, min_size=(width, height), max_size=None, max_num=200)
        images = os.listdir(image_dir)
        return [os.path.join(image_dir, image) for image in images]
    except Exception as e:
        logging.error(f'Error in gather_media: {str(e)}')
        return []

device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
#configure un périphérique pour les calculs. Elle utilise la librairie PyTorch et tente d'utiliser un GPU (carte graphique) si disponible (cuda:0), sinon elle utilise le CPU.

device_id = device.index #récupère l'index du périphérique stocké dans la variable device

# Define a function to generate text using the model
def generate_text(description):

    prefix ="A well-crafted and beautifully written script for a video generation program, with a focus on balance and harmony."

    # set_seed(seed)
    seed = 1

    model_name = "gpt2"
    
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    #Le tokenizer permet de convertir le texte dans un format que le modèle peut comprendre.
    try:
        generator = pipeline('text-generation',
                             max_new_tokens=1000,
                             model=model,
                             tokenizer=tokenizer,
                             prefix = prefix, #invite de départ
                             device=device_id, #GPU
                             temperature=1,
                             top_k=50,
                             top_p=1,
                             repetition_penalty=1.2,
                             length_penalty=0.5,
                             do_sample=True,
                             num_beams=4,
                             no_repeat_ngram_size=3,
                             num_return_sequences=1,
                             )

        # Generate text
        additional_sentences_ = (generator(description)[0]['generated_text'])
        additional_sentences = additional_sentences_

        # Delete the model to free GPU memory / vidage du cache pour libérer la memoire
        del generator
        del model
        torch.cuda.empty_cache()

        return additional_sentences
    except Exception as e:
        print(e)
        logging.error(f'error in generator pipeline :{str(e)}')
    
    prompt = description
    # Open the file in append mode and write the log
    #journalisation du processus de génération de texte, en enregistrant des informations clés dans un fichier
    
    with open(llm_log, "a") as f:  #le code va écrire de nouvelles informations à la fin du fichier existant, sans effacer son contenu précédent.
        # Write the timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"Timestamp: {timestamp}\n")

        # Write the seed value
        f.write(f"Seed value: {seed}\n") # configuration du modèle de langage utilisé

        # Write the model parameters
        f.write(f"Model parameters: {model.config}\n")

        # Write the input prompt
        f.write(f"Input prompt: {prompt}\n") #generation

        # Generate the text and write it to the log
        f.write(f"Generated text:\n{additional_sentences}\n\n")



# Step 3: Create audio
def create_audio(description):
    
    try:

        create_dir(audio_dir)
        # Use a pre-trained language model to generate additional sentences based on the initial description
        
        additional_sentences = generate_text(description)

        print(f"Generated audio for: {additional_sentences}")
        

        # Concatenate the original description with the additional sentences
        # text = " ".join([description] + [additional_sentences])
        text = additional_sentences
        # Generate audio file using gTTS
        tts = gTTS(text=text, lang='en')
        tts.save(os.path.join(audio_dir, filename + '.mp3'))
        return additional_sentences
    except Exception as e:
        logging.error(f'Error in create_audio: {str(e)}')
        return description


# Step 4: Create video
def create_video(images, audio_file):
    try:
        create_dir(video_dir)
        with audioread.audio_open(audio_file) as f:
            audio_duration = int(f.duration)
        image_duration = 3
        print('Total Duration: {} seconds'.format(audio_duration))

        num_loops = int(audio_duration / image_duration)
        print('number of loops:{}'.format(num_loops))

        width, height = (1920, 1080)

        clips = []
        i = 0
        while True:
            print("in while")
            for image in images:
                try:
                    clip = ImageClip(image).resize(width=width, height=height).crop(x1=0, y1=0, x2=width, y2=height).set_duration(image_duration)
                    clips.append(clip)
                    i = i + 1
                except Exception as e:
                    print(f"Error opening image: {image}. Error message: {str(e)}")
            if i >= num_loops:
                print("in if")
                break
        print("after while")
        concat_clip = concatenate_videoclips(clips, method="compose")
        audio = AudioFileClip(audio_file)
        video = concat_clip.set_audio(audio)
        video.write_videofile(os.path.join(video_dir, filename + '.mp4'), fps=24)
    except Exception as e:
        logging.error(f'Error in create_video: {str(e)}')


def generate_subtitle(audio_file):
    try:
        create_dir(subtitle_dir)
        # Load the transcription model and transcribe the audio file
        try:
            model = whisper.load_model("base", device="cuda")
            result = model.transcribe(audio_file)
        except Exception as e:
            print(e)
            model = whisper.load_model("base", device="cpu")
            result = model.transcribe(audio_file)

        # Extract the transcribed text and segments from the result
        text = result["text"]
        segments = result["segments"]

        # Generate subtitle files
        subtitles = pysrt.SubRipFile()
        for i, seg in enumerate(segments):
            start_time = int(seg["start"] * 1000)  # Convert start time to milliseconds
            end_time = int(seg["end"] * 1000)  # Convert end time to milliseconds
            subtitle = pysrt.SubRipItem(index=i, start=pysrt.SubRipTime(milliseconds=start_time),
                                        end=pysrt.SubRipTime(milliseconds=end_time), text=seg["text"])
            subtitles.append(subtitle)

        # Save the subtitle file
        subtitles.save(os.path.join(subtitle_dir, filename + '.srt'))
    except Exception as e:
        logging.error(f'Error in generate_subtitle: {str(e)}')

def add_subtitles(video_file):
    try:
        create_dir(video_dir)
        # Load the subtitles from the subtitle file
        subs = pysrt.open(os.path.join(subtitle_dir, filename + ".srt"))

        # Check if there are subtitles available
        if subs:
            # Add the subtitles to the video file
            video = VideoFileClip(video_file)
            generator = lambda text: TextClip(text, font='Arial-Bold',
                                            fontsize=32,
                                            color='white',
                                            bg_color='aqua')
            sub = SubtitlesClip(os.path.join(subtitle_dir, filename + ".srt"), generator)
            video = CompositeVideoClip([video, sub.set_pos(('center', 'bottom'))])
            video.write_videofile(os.path.join(video_dir, filename + 'with_subs.mp4'))
        else:
            print("No subtitles found")
    except Exception as e:
        logging.error(f'Error in add_subtitles: {str(e)}')


# Define main function
# 'ensemble du processus de création d'une vidéo.

def main():
    try:
        # Step 1: Search for interesting topics
        search_results = search_topic(query, google_api_key, search_engine_id)
        if search_results:
            title = search_results[0]['title']
            description = search_results[0]['snippet']
            print("\nDescription\n" + description + "\n")

            url = search_results[0]['link']

            # Step 2: Gather media
            media_links = gather_media(query)
            print(len(media_links))

            # Step 3: Create audio
            create_audio(description)

            generate_subtitle(os.path.join(audio_dir, filename + '.mp3'))

            # Step 4: Create video
            create_video(media_links, os.path.join(audio_dir, filename + '.mp3'))

            # Step 5: Add subtitles
            add_subtitles(os.path.join(video_dir, filename + '.mp4'))
    except Exception as e:
        logging.error(f'Error in main: {str(e)}')

if __name__ == '__main__':
    main()
