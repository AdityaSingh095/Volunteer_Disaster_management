import requests
import torch
import PyPDF2
import streamlit as st
from config import config, headers
import tempfile
import os

def transcribe_audio(audio_path):
    """Transcribe audio using Hugging Face Whisper model"""
    API_URL = f"https://api-inference.huggingface.co/models/{config['WHISPER_MODEL']}"
    try:
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        payload = {"options": {"task": "translate"}}
        response = requests.post(API_URL, headers=headers, data=audio_data, json=payload)
        if response.status_code == 200:
            return response.json()["text"]
        else:
            return ""
    except Exception as e:
        st.error(f"Transcription error: {e}")
        return ""

def english_speech_to_text(file_path):
    """Convert audio file to text using ASR"""
    from transformers import pipeline
    try:
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        model_asr = pipeline(
            task="automatic-speech-recognition",
            model=config["ASR_MODEL"],
            device=device
        )
        result = model_asr(
            file_path,
            generate_kwargs={"task": "translate"}  # Forces English output
        )
        return result["text"]
    except Exception as e:
        st.error(f"Speech-to-text error: {e}")
        return ""

def process_image(image_path):
    """Process image using BLIP model"""
    API_URL = f"https://api-inference.huggingface.co/models/{config['BLIP_MODEL']}"
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        response = requests.post(API_URL, headers=headers, data=image_data)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and result and 'generated_text' in result[0]:
            return result[0]['generated_text']
        else:
            return "Unexpected API response format"
    except Exception as e:
        st.error(f"Image processing error: {e}")
        return ""

def process_text(text_input):
    """Process text using CLIP model"""
    text_options = ["fire", "earthquake", "flood", "car accident", "building collapse",
                   "cyclone", "landslide", "medical emergency"]
    try:
        from transformers import CLIPProcessor, CLIPModel

        model = CLIPModel.from_pretrained(config["CLIP_MODEL"])
        processor = CLIPProcessor.from_pretrained(config["CLIP_MODEL"])

        inputs = processor(text=text_options, return_tensors="pt", padding=True)
        text_features = model.get_text_features(**inputs)
        input_text = processor(text=[text_input], return_tensors="pt", padding=True)
        input_features = model.get_text_features(**input_text)
        similarities = torch.nn.functional.cosine_similarity(input_features, text_features, dim=1)
        predicted_label = text_options[similarities.argmax().item()]
        return predicted_label, similarities.max().item()
    except Exception as e:
        st.error(f"Text processing error: {e}")
        return "unknown", 0.0

def extract_entities(text):
    """Extract entities from text using spaCy"""
    from modules.models import get_nlp

    nlp = get_nlp()
    doc = nlp(text)
    entities = {
        "location": [],
        "date": [],
        "emergency_type": [],
        "severity": [],
        "victim_condition": [],
        "damage": []
    }
    for ent in doc.ents:
        if ent.label_ == "EMERGENCY_TYPE":
            entities["emergency_type"].append(ent.text)
        elif ent.label_ == "SEVERITY":
            entities["severity"].append(ent.text)
        elif ent.label_ == "VICTIM_CONDITION":
            entities["victim_condition"].append(ent.text)
        elif ent.label_ == "DAMAGE":
            entities["damage"].append(ent.text)
        elif ent.label_ == "DATE":
            entities["date"].append(ent.text)
        elif ent.label_ in ['GPE', 'LOC']:
            entities["location"].append(ent.text)
    return entities

def generate_summary(pdf_path):
    """Generate summary from PDF using BART model"""
    from modules.models import get_tokenizer_and_summarization_model

    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

        tokenizer, model = get_tokenizer_and_summarization_model()
        inputs = tokenizer.encode('summarize: ' + text, return_tensors="pt",
                                  max_length=1024, truncation=True)
        summary_ids = model.generate(inputs, max_length=1000, min_length=50,
                                    length_penalty=2.0, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary
    except Exception as e:
        st.error(f"PDF summarization error: {e}")
        return "Error generating summary"

def get_first_aid_response(disaster_type, input_text):
    """Get first aid response using Google's Gemini model"""
    try:
        import google.generativeai as genai

        genai.configure(api_key=config["GEMINI_API_KEY"])
        model_gen = genai.GenerativeModel(config["GEMINI_MODEL"])
        prompt = f"What are the first-aid measures for a {disaster_type}? Context provided: {input_text}"
        response = model_gen.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"First aid response error: {e}")
        return "Error generating first aid response"
