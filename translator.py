import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from playsound import playsound
import os
import time

# Maps spoken language names to language codes
language_map = {
    'english': 'en',
    'hindi': 'hi',
    'bengali': 'bn',
    'marathi': 'mr',
    'punjabi': 'pa',
    'gujarati': 'gu',
    'tamil': 'ta',
    'telugu': 'te',
    'kannada': 'kn',
    'french': 'fr',
    'german': 'de',
    'spanish': 'es',
    'arabic': 'ar',
    'russian': 'ru',
    'urdu': 'ur',
    'japanese': 'ja',
    'korean': 'ko',
    'chinese': 'zh-cn'
}

# Recognize voice input
def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Boliye kuch bhi...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"🗣️ Aapne kaha: {text}")
        return text
    except:
        print("❌ Voice input not detected properly.")
        return None

# Text-to-Speech with gTTS
def speak(text, lang_code):
    tts = gTTS(text=text, lang=lang_code)
    filename = "voice.mp3"
    tts.save(filename)
    playsound(filename)  # Windows
    time.sleep(4)
    os.remove(filename) 

def translate_text(text, target_lang_code):
    if not text:
        return "⚠️ No text provided for translation.",None
    
    try:
        translator = Translator()
        detected = translator.detect(text)
        translated = translator.translate(text, src=detected.lang, dest=target_lang_code).text
        return translated, detected.lang
    except Exception as e:
        return f"❌ Translation failed: {e}", None
    


# MAIN
if __name__ == "__main__":
    spoken_text = take_command()
    if spoken_text:
        translator = Translator()

        # Auto detect language
        detected = translator.detect(spoken_text)
        source_lang = detected.lang
        print(f"🌐 Detected Source Language: {source_lang}")

        # Ask user for target language
        print("\n🔤 Kis language me translate karna hai? (e.g., English, Hindi, Bengali...)")
        target_input = input("🎯 Enter Target Language: ").lower().strip()

        if target_input in language_map:
           target_lang_code = language_map[target_input]

           # Translate
           translated = translator.translate(spoken_text, src=source_lang, dest=target_lang_code).text
           print(f"\n✅ Translation in {target_input}: {translated}")

           # Speak
           speak(translated, target_lang_code)

        else:
           print("⚠️ Sorry, language not supported.")
