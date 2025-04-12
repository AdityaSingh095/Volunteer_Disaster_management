import streamlit as st
from functools import lru_cache
import spacy
from config import config

# Global variables for models and processors
models = {
    "tokenizer": None,
    "summarization": None,
    "nlp": None,
    "entity_ruler": None,
    "clip_model": None,
    "clip_processor": None
}

@lru_cache(maxsize=1)
def get_nlp():
    """Lazy load spaCy NLP model"""
    if models["nlp"] is None:
        st.info("Loading language model... This may take a moment.")
        models["nlp"] = spacy.load(config["SPACY_MODEL"])

        # Add entity ruler if not already present
        if "entity_ruler" not in [pipe for pipe, _ in models["nlp"].pipeline]:
            ruler = models["nlp"].add_pipe("entity_ruler", before="ner")
            patterns = [
                {"label": "EMERGENCY_TYPE", "pattern": [{"lower": "earthquake"}]},
                {"label": "EMERGENCY_TYPE", "pattern": [{"lower": "fire"}]},
                {"label": "EMERGENCY_TYPE", "pattern": [{"lower": "flood"}]},
                {"label": "EMERGENCY_TYPE", "pattern": [{"lower": "hurricane"}]},
                {"label": "EMERGENCY_TYPE", "pattern": [{"lower": "tornado"}]},
                {"label": "EMERGENCY_TYPE", "pattern": [{"lower": "tsunami"}]},
                {"label": "EMERGENCY_TYPE", "pattern": [{"lower": "landslide"}]},
                {"label": "SEVERITY", "pattern": [{"lower": "critical"}]},
                {"label": "SEVERITY", "pattern": [{"lower": "severe"}]},
                {"label": "SEVERITY", "pattern": [{"lower": "urgent"}]},
                {"label": "SEVERITY", "pattern": [{"lower": "major"}]},
                {"label": "SEVERITY", "pattern": [{"lower": "minor"}]},
                {"label": "VICTIM_CONDITION", "pattern": [{"lower": "injured"}]},
                {"label": "VICTIM_CONDITION", "pattern": [{"lower": "unconscious"}]},
                {"label": "VICTIM_CONDITION", "pattern": [{"lower": "stuck"}]},
                {"label": "VICTIM_CONDITION", "pattern": [{"lower": "trapped"}]},
                {"label": "VICTIM_CONDITION", "pattern": [{"lower": "missing"}]},
                {"label": "DAMAGE", "pattern": [{"lower": "collapsed"}]},
                {"label": "DAMAGE", "pattern": [{"lower": "destroyed"}]},
                {"label": "DAMAGE", "pattern": [{"lower": "damaged"}]},
                {"label": "DAMAGE", "pattern": [{"lower": "flooded"}]},
                {"label": "DAMAGE", "pattern": [{"lower": "burned"}]}
            ]
            ruler.add_patterns(patterns)
            models["entity_ruler"] = ruler
    return models["nlp"]

@lru_cache(maxsize=1)
def get_tokenizer_and_summarization_model():
    """Lazy load summarization model and tokenizer"""
    if models["tokenizer"] is None or models["summarization"] is None:
        st.info("Loading summarization model... This may take a moment.")
        from transformers import BartTokenizer, BartForConditionalGeneration
        models["tokenizer"] = BartTokenizer.from_pretrained(config["SUMMARIZATION_MODEL"])
        models["summarization"] = BartForConditionalGeneration.from_pretrained(config["SUMMARIZATION_MODEL"])
    return models["tokenizer"], models["summarization"]

@lru_cache(maxsize=1)
def get_clip_model_and_processor():
    """Lazy load CLIP model and processor"""
    if models["clip_model"] is None or models["clip_processor"] is None:
        st.info("Loading CLIP model... This may take a moment.")
        from transformers import CLIPProcessor, CLIPModel
        models["clip_model"] = CLIPModel.from_pretrained(config["CLIP_MODEL"])
        models["clip_processor"] = CLIPProcessor.from_pretrained(config["CLIP_MODEL"])
    return models["clip_model"], models["clip_processor"]
