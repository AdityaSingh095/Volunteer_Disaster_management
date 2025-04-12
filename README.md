# Volunteer and Victim Management & Communication System

This project is a **Disaster Management System** designed to streamline coordination between victims, volunteers, and emergency services during natural or man-made disasters. The system uses **AI-powered communication tools**, **geospatial data**, and **automated workflows** to manage crisis response effectively.

---

## 🗂️ Repository Structure

disaster_management/ ├── app.py # Main application entry point ├── config.py # Configuration settings ├── requirements.txt # Dependencies ├── static/ # Static files like CSS, JS ├── modules/ │ ├── init.py │ ├── auth.py # Authentication related functions │ ├── database.py # Database operations │ ├── geospatial.py # Map and location functions │ ├── models.py # Model loading and AI functions │ ├── processing.py # Processing functions (text, audio, image) │ └── utils.py # Utility functions ├── views/ │ ├── init.py │ ├── user.py # User workflow │ ├── volunteer.py # Volunteer workflow │ └── dashboard.py # Dashboard views

python
Copy
Edit

---

## ⚙️ Configuration (`config.py`)

Create a `config.py` file in the root directory with the following content:

```python
# Configuration
config = {
    # API keys
    "TWILIO_ACCOUNT_SID": "your_twilio_sid",
    "TWILIO_AUTH_TOKEN": "your_twilio_token",
    "TWILIO_PHONE_NUMBER": "+1xxxxxxxxxx",
    "HF_API_TOKEN": "your_huggingface_token",
    "GEMINI_API_KEY": "your_gemini_key",
    "OPENCAGE_API_KEY": "your_opencage_key",

    # Database
    "DB_PATH": "disaster_management.db",

    # Model parameters
    "ASR_MODEL": "openai/whisper-small",
    "SUMMARIZATION_MODEL": "facebook/bart-large-cnn",
    "SPACY_MODEL": "en_core_web_lg",
    "CLIP_MODEL": "openai/clip-vit-base-patch32",
    "WHISPER_MODEL": "openai/whisper-large-v3",
    "BLIP_MODEL": "Salesforce/blip-image-captioning-large",
    "GEMINI_MODEL": "models/gemini-1.5-pro"
}

# Headers for API requests
headers = {"Authorization": f"Bearer {config['HF_API_TOKEN']}"}
Note: Replace sensitive API keys with your actual keys. Use environment variables or .env for security in production.

💡 Features
📍 Real-time location tracking with OpenCage Geocoder

🤖 AI-based summarization, audio processing, and image captioning

📞 Twilio integration for SMS-based communication

📋 Volunteer and victim dashboard

🧠 Powered by Hugging Face, OpenAI Whisper, Gemini API, and more

🚀 Getting Started
Clone the repository

bash
Copy
Edit
git clone https://github.com/yourusername/disaster_management.git
cd disaster_management
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Add your config Create a config.py using the template above and replace with your credentials.

Run the application

bash
Copy
Edit
python app.py
📦 Dependencies
Main libraries and tools used:

Flask

Hugging Face Transformers

OpenAI Whisper

Twilio

geopy

spaCy

OpenCage API

Google Gemini API

See requirements.txt for the complete list.
