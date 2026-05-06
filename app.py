import streamlit as st
import google.generativeai as genai
import json
from PyPDF2 import PdfReader
from docx import Document
import io

# ==========================================
# 1. Configuração e Funções de Suporte
# ==========================================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
modelo_estrutura = genai.GenerativeModel("gemini-3.1-flash-lite-preview", generation_config={"response_mime_type": "application/json"})
modelo_texto = genai.GenerativeModel("gemini-3.1-flash-lite-preview")

def extrair_texto(arquivo):
    if arquivo.type == "application/pdf":
        leitor = PdfReader(arquivo)
        texto = ""
        for pagina in leitor.pages:
            texto += pagina.extract_text()
        return texto
    elif arquivo.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(io.BytesIO(arquivo.read()))
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return arquivo.read().decode("utf-8")

# ==========================================
# 2. Interface (Uploaders)
# ==========================================
st.set_page_config(page_title="Gerador de Cursos IA", layout="wide")
st.title("🚀 Sistema de Produção de Cursos Automatizado")

with st.sidebar:
    st.header("Arquivos Base")
    file_norma = st.file_uploader("Upload da Norma (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    file_pedagogico = st.file_uploader("Upload do Projeto Pedagógico", type=["pdf", "docx", "txt"])
    
    st.divider()
    templates_base = {
        "Roteiro de Aula": "Crie um roteiro de aula para: {aula}...",
        "Roteiro de Materiais": "Liste materiais para a aula: {aula}...",
        "Prompts de Imagem": "Gere prompts de IA para a aula: {aula}..."
    }

# Lógica de processamento dos arquivos
norma_texto = extrair_texto(file_norma) if file_norma else ""
pedagogico_texto = extrair_texto(file_pedagogico) if file_pedagogico else ""

# O restante da lógica de geração de estrutura permanece, 
# mas agora usando 'norma_texto' e 'pedagogico_texto'.
if st.button("Gerar Estrutura do Curso") and norma_texto and pedagogico_texto:
    # (Inserir aqui a chamada ao Gemini mostrada anteriormente)
    st.success("Arquivos processados e estrutura pronta para geração!")
