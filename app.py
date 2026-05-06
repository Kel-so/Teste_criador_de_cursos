import streamlit as st
import google.generativeai as genai
import json
from PyPDF2 import PdfReader
from docx import Document
import io

# ==========================================
# 1. Configuração da API e Funções
# ==========================================
# Pega a chave dos secrets do Streamlit
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Modelos atualizados para o Flash Lite
modelo_estrutura = genai.GenerativeModel(
    "gemini-3.1-flash-lite-preview", 
    generation_config={"response_mime_type": "application/json"}
)
modelo_texto = genai.GenerativeModel("gemini-3.1-flash-lite-preview")

# Função para extrair texto de diferentes arquivos
def extrair_texto(arquivo):
    if arquivo is None:
        return ""
    
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
# 2. Roteiros Base (Templates)
# ==========================================
TEMPLATES = {
    "Roteiro de Aula": "Atue como um instrutor técnico especializado. Crie o roteiro de gravação detalhado para a seguinte aula: {aula}. Siga estritamente as regras de produção: {base_producao}. Tom do projeto pedagógico: {pedagogico}. Inclua introdução, desenvolvimento e conclusão.",
    "Roteiro de Materiais": "Liste todos os equipamentos, EPIs, e ferramentas visuais necessárias para demonstrar na prática os conceitos da aula: {aula}. Norma base: {norma}.",
    "Prompts para Imagens IA": "Crie 3 prompts detalhados em inglês para gerar imagens de apoio para a aula: {aula}. As imagens devem ter estilo realista, iluminação de estúdio e focar no tema central da aula. Apenas entregue os prompts em texto."
}

# ==========================================
# 3. Interface Visual
# ==========================================
st.set_page_config(page_title="Sistema de Produção de Cursos", layout="wide")
st.title("⚙️ Gerador de Estrutura e Roteiros")

# Controle de estado para manter a estrutura na tela
if "estrutura_curso" not in st.session_state:
    st.session_state.estrutura_curso = None

# Sidebar para Upload de todos os arquivos base
with st.sidebar:
    st.header("Arquivos de Base")
    file_norma = st.file_uploader("1. Norma (Ex: NR-33)", type=["pdf", "docx", "txt"])
    file_pedagogico = st.file_uploader("2. Projeto Pedagógico", type=["pdf", "docx", "txt"])
    file_base_producao = st.file_uploader("3. Base de Produção", type=["pdf", "docx", "txt"], help="Regras de composição e comportamento do curso")

# Extração dos textos
norma_texto = extrair_texto(file_norma)
pedagogico_texto = extrair_texto(file_pedagogico)
base_producao_texto = extrair_texto(file_base_producao)

# Abas principais
aba_estrutura, aba_roteiros = st.tabs(["1. Estruturar Curso", "2. Produção de Roteiros"])

# ==========================================
# ABA 1: Geração da Estrutura Inicial
# ==========================================
with aba_estrutura:
    st.markdown("Faça o upload dos 3 arquivos na barra lateral para gerar a base do curso.")
    
    arquivos_ok = norma_texto and pedagogico_texto and base_producao_texto
    
    if not arquivos_ok:
        st.warning("Aguardando upload de todos os arquivos base na lateral...")
    
    if st.button("Gerar Estrutura do Curso", disabled=not arquivos_ok):
        prompt_json = f"""
        Baseado nos documentos abaixo, crie uma estrutura de curso dividida em módulos e aulas.
        
        DOCUMENTO 1 - Norma Técnica:
        {norma_texto}
        
        DOCUMENTO 2 - Projeto Pedagógico:
        {pedagogico_texto}
        
        DOCUMENTO 3 - Base de Produção (Regras e Formatos):
        {base_producao_texto}
        
        A estrutura deve respeitar absolutamente as regras definidas na Base de Produção.
        Retorne estritamente um JSON no seguinte formato:
        {{
            "modulos": [
                {{
                    "nome": "Nome do Módulo",
                    "aulas": ["Nome da Aula 1", "Nome da Aula 2"]
                }}
            ]
        }}
        """
        
        with st.spinner("Analisando documentos e montando estrutura..."):
            try:
                resposta = modelo_estrutura.generate_content(prompt_json)
                st.session_state.estrutura_curso = json.loads(resposta.text)
                st.success("Estrutura gerada! Vá para a aba 'Produção de Roteiros'.")
            except Exception as e:
                st.error("Erro ao processar a estrutura. Verifique os arquivos e tente novamente.")

# ==========================================
# ABA 2: Edição e Geração de Conteúdo
# ==========================================
with aba_roteiros:
    if st.session_state.estrutura_curso:
        st.markdown("### Estrutura (Edite, Adicione ou Remova Aulas)")
        
        for idx_mod, modulo in enumerate(st.session_state.estrutura_curso["modulos"]):
            with st.expander(modulo["nome"], expanded=True):
                
                novo_nome_mod = st.text_input("Nome do Módulo", value=modulo["nome"], key=f"mod_{idx_mod}")
                st.session_state.estrutura_curso["modulos"][idx_mod]["nome"] = novo_nome_mod
                
                for idx_aula, aula in enumerate(modulo["aulas"]):
                    col_aula, col_tipo, col_btn = st.columns([3, 1, 1])
                    
                    with col_aula:
                        nova_aula = st.text_input(f"Aula {idx_aula + 1}", value=aula, key=f"aula_{idx_mod}_{idx_aula}", label_visibility="collapsed")
                        st.session_state.estrutura_curso["modulos"][idx_mod]["aulas"][idx_aula] = nova_aula
                    
                    with col_tipo:
                        tipo_geracao = st.selectbox("Template", list(TEMPLATES.keys()), key=f"tipo_{idx_mod}_{idx_aula}", label_visibility="collapsed")
                    
                    with col_btn:
                        if st.button("Gerar", key=f"btn_{idx_mod}_{idx_aula}", use_container_width=True):
                            
                            prompt_final = TEMPLATES[tipo_geracao].format(
                                aula=nova_aula, 
                                pedagogico=pedagogico_texto, 
                                norma=norma_texto,
                                base_producao=base_producao_texto
                            )
                            
                            with st.spinner(f"Processando {tipo_geracao}..."):
                                resultado = modelo_texto.generate_content(prompt_final)
                                st.info(resultado.text)

        st.divider()
        if st.button("Salvar Estrutura Final em JSON"):
            st.json(st.session_state.estrutura_curso)
    else:
        st.info("A estrutura do curso aparecerá aqui após ser gerada na aba anterior.")
