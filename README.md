---
title: Adaptive Learning Coach
emoji: 🎓
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: 1.35.0
app_file: streamlit_app.py
pinned: false
---

# 🎓 Adaptive Learning Coach

> AI-powered personalized learning using IRT algorithm + LangChain.

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-HuggingFace-blue?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/madhuchitikela/adaptive-learning-coach)
[![Source Code](https://img.shields.io/badge/💻%20Source%20Code-GitHub-black?style=for-the-badge&logo=github)](https://github.com/MadhuChitikela/adaptive-learning-coach)

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-0.2+-green?style=flat-square)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?style=flat-square)

## 🎯 What It Does
AI diagnoses your weak areas → generates adaptive quizzes
using IRT algorithm → builds personalized 7-day study plans.

## 📊 Features
- ✅ IRT Algorithm (same used in GRE/GMAT)
- ✅ Adaptive quizzing — difficulty adjusts per answer
- ✅ Personalized 7-day study plans
- ✅ AI Coach with memory
- ✅ Progress tracking dashboard

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq LLaMA 3.3 + Gemini Fallback |
| Framework | LangChain |
| Algorithm | Item Response Theory (IRT) |
| UI | Streamlit + Plotly |
| Database | SQLite |

## 🚀 How to Run Locally

```bash
git clone https://github.com/MadhuChitikela/adaptive-learning-coach
cd adaptive-learning-coach
pip install -r requirements.txt
```

Create `.env`:
```
GROQ_API_KEY=your_key
GEMINI_API_KEY=your_key
```

```bash
streamlit run streamlit_app.py
```
