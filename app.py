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

modelo_estrutura = genai.GenerativeModel(
    "gemini-3.1-flash-lite-preview", 
    generation_config={"response_mime_type": "application/json"}
)
modelo_texto = genai.GenerativeModel("gemini-3.1-flash-lite-preview")

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

def gerar_docx(texto):
    """Cria um arquivo DOCX em memória para o botão de download"""
    doc = Document()
    for linha in texto.split('\n'):
        doc.add_paragraph(linha)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# ==========================================
# 2. Roteiros Base (Templates)
# ==========================================
TEMPLATES = {
    "Roteiro de Aula": """Atue como um instrutor técnico especializado e conteudista sênior da Saber Gestão. 
Crie o roteiro de gravação DETALHADO para a aula: {aula}.

REGRA ABSOLUTA: Você DEVE estruturar o roteiro rigorosamente conforme o 'Modelo de Aula - Estrutura Detalhada' presente na Base de Produção fornecida.

Use formatação rica (negrito, tópicos) e emojis. Seu retorno DEVE conter OBRIGATORIAMENTE os seguintes blocos descritos na Base:
- 🎯 Título Impactante (Curioso e direto)
- 💬 Frase de Abertura (Para gerar conexão)
- 🎥 Bloco de Vídeo (O roteiro do que o instrutor vai explicar na câmera, com contexto real)
- 📝 Bloco de Texto Guiado (Resumo em tópicos curtos e pontos-chave)
- 🛠️ Bloco de Aplicação (Passo a passo prático para o dia a dia)
- 🤔 Bloco de Reflexão (Pergunta para o aluno)
- ❓ Quiz (1 ou 2 questões com 4 alternativas focadas na prática)

Contexto Técnico da Norma: {norma}
Diretrizes do Projeto Pedagógico: {pedagogico}
Base de Produção: {base_producao}""",

    "Roteiro de Materiais": "Liste todos os equipamentos, EPIs, e ferramentas visuais necessárias para demonstrar na prática os conceitos da aula: {aula}. Baseie-se na norma: {norma}.",
    
    "Prompts para Imagens IA": "Crie 3 prompts detalhados em inglês para gerar imagens de apoio visual para a aula: {aula}. As imagens devem ter estilo realista, iluminação de estúdio, proporção 16:9 e focar no tema central da aula. Apenas entregue os prompts em texto puro."
}

# ==========================================
# 3. Interface Visual e Estados
# ==========================================
st.set_page_config(page_title="Sistema de Produção de Cursos", layout="wide")
st.title("⚙️ Gerador de Estrutura e Roteiros")

if "estrutura_curso" not in st.session_state:
    st.session_state.estrutura_curso = None
if "roteiros_gerados" not in st.session_state:
    st.session_state.roteiros_gerados = {}

with st.sidebar:
    st.header("Arquivos de Base")
    file_norma = st.file_uploader("1. Norma (Ex: NR-33)", type=["pdf", "docx", "txt"])
    file_pedagogico = st.file_uploader("2. Projeto Pedagógico", type=["pdf", "docx", "txt"])
    file_base_producao = st.file_uploader("3. Base de Produção", type=["pdf", "docx", "txt"])

norma_texto = extrair_texto(file_norma)
pedagogico_texto = extrair_texto(file_pedagogico)
base_producao_texto = extrair_texto(file_base_producao)

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
        Sua tarefa principal é EXTRAIR a estrutura do curso fornecida no Projeto Pedagógico e formatá-la em JSON.
        NÃO crie módulos novos. NÃO divida módulos existentes.
        
        DOCUMENTO 1 - Norma Técnica:
        {norma_texto}
        
        DOCUMENTO 2 - Projeto Pedagógico (A FONTE DA VERDADE):
        {pedagogico_texto}
        
        DOCUMENTO 3 - Base de Produção:
        {base_producao_texto}
        
        Regras Absolutas:
        1. O curso deve ter EXATAMENTE a mesma quantidade de módulos descrita no Projeto Pedagógico.
        2. Copie os nomes dos módulos e as respectivas aulas exatamente como estão no Projeto Pedagógico.
        3. Aplique as regras da Base de Produção apenas para nomenclatura.
        
        Retorne estritamente um JSON no seguinte formato:
        {{
            "modulos": [
                {{
                    "nome": "Módulo 1 - Nome",
                    "aulas": ["Aula 1.1 - Nome", "Aula 1.2 - Nome"]
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
                    chave_roteiro = f"{idx_mod}_{idx_aula}"
                    
                    col_aula, col_tipo, col_btn = st.columns([3, 1, 1])
                    
                    with col_aula:
                        nova_aula = st.text_input(f"Aula {idx_aula + 1}", value=aula, key=f"aula_{chave_roteiro}", label_visibility="collapsed")
                        st.session_state.estrutura_curso["modulos"][idx_mod]["aulas"][idx_aula] = nova_aula
                    
                    with col_tipo:
                        tipo_geracao = st.selectbox("Template", list(TEMPLATES.keys()), key=f"tipo_{chave_roteiro}", label_visibility="collapsed")
                    
                    with col_btn:
                        gerar_clicado = st.button("Gerar IA", key=f"btn_{chave_roteiro}", use_container_width=True)
                        
                    # Lógica de geração do Roteiro
                    if gerar_clicado:
                        prompt_final = TEMPLATES[tipo_geracao].format(
                            aula=nova_aula, 
                            pedagogico=pedagogico_texto, 
                            norma=norma_texto,
                            base_producao=base_producao_texto
                        )
                        with st.spinner(f"Processando {tipo_geracao}..."):
                            resultado = modelo_texto.generate_content(prompt_final)
                            # Salva o texto gerado na memória do Streamlit
                            st.session_state.roteiros_gerados[chave_roteiro] = resultado.text
                            st.rerun() # Atualiza a tela para exibir os botões de ler/baixar
                    
                    # Exibe os botões de Ler e Baixar apenas se o roteiro já foi gerado
                    if chave_roteiro in st.session_state.roteiros_gerados:
                        texto_gerado = st.session_state.roteiros_gerados[chave_roteiro]
                        
                        col_espaco, col_ler, col_baixar = st.columns([3, 1, 1])
                        with col_ler:
                            with st.popover("Ler Roteiro", use_container_width=True):
                                st.markdown(texto_gerado)
                        with col_baixar:
                            docx_file = gerar_docx(texto_gerado)
                            st.download_button(
                                label="Baixar DOCX",
                                data=docx_file,
                                file_name=f"Roteiro_{nova_aula[:15].strip()}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"down_{chave_roteiro}",
                                use_container_width=True
                            )
    else:
        st.info("A estrutura do curso aparecerá aqui após ser gerada na aba anterior.")
