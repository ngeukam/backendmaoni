import io
from google.cloud import speech
from transformers import pipeline

def speech_to_text(audio_file_path, language_code="fr-FR"):
    """
    Convertit un fichier audio en texte à l'aide de Google Cloud Speech-to-Text.
    Prend en charge plusieurs langues.
    """
    client = speech.SpeechClient()

    with io.open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # Changez selon votre format
        language_code=language_code,  # Ex : "en-US", "fr-FR", "es-ES"
    )

    response = client.recognize(config=config, audio=audio)

    transcript = " ".join(result.alternatives[0].transcript for result in response.results)
    return transcript



def analyze_sentiment(text, model_name="nlptown/bert-base-multilingual-uncased-sentiment"):
    """
    Analyse multilingue de sentiment en utilisant Hugging Face Transformers.
    """
    sentiment_pipeline = pipeline("sentiment-analysis", model=model_name)
    result = sentiment_pipeline(text)
    return result[0]  # Retourne le premier résultat
