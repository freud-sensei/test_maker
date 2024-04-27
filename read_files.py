# -*- coding: utf-8 -*-

import streamlit as st
from PyPDF2 import PdfReader
from docx import Document

@st.cache_data
def read_pdf(file):
    text = ""
    reader = PdfReader(file)
    pages = reader.pages
    for page in pages:
        sub = page.extract_text()
        text += sub         
    return text

@st.cache_data
def read_docx(file):
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def save_txt(sts):
    result = f"Model: {sts['model']}, User: {sts['code']}\n\n"
    for idx in range(len(sts["questionnaire"])):
        try:
            question = sts["questionnaire"][idx]
            result += f"question {idx + 1}: {question['question']}\n"
            for idx, s in enumerate(question["selection"]):
                result += f"{idx + 1}. {s}\n"
            result += f"selected: {sts[f'chosen_{idx}']}\n"
            result += f"answer: {question['correct']}\n"
            result += f"explanation: {question['explanation']}\n"
            result += "\n"
        except:
            pass
    result += "===== Input Text ====="
    result += "\n"
    result += f"{sts['input_text']}"
    return result