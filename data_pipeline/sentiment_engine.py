import streamlit as st
from transformers import pipeline

@st.cache_resource
def get_model():
    return pipeline("sentiment-analysis", model="ProsusAI/finbert", trust_remote_code=True)

def analyze_headlines(headlines):
    if not headlines: return 0.0
    model = get_model()
    results = model(headlines)
    scores = []
    for res in results:
        score = res['score'] if res['label'] == 'positive' else (-res['score'] if res['label'] == 'negative' else 0)
        scores.append(score)
    return sum(scores) / len(scores)