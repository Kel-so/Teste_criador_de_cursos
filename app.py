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

Use formatação rica (negrito, tópicos) e emojis. Seu retorno DEVE conter OBRIGATORIAMENTE os seguintes blocos:

- 🎯 Título Impactante (Curioso e direto)
- 💬 Frase de Abertura (Para gerar conexão)
- 🎥 Bloco de Vídeo: 
   ATENÇÃO: Este é o roteiro exato da fala do professor (estilo teleprompter). 
   TOM DE VOZ: Conversacional, humano, empático e direto. Sem academicismo engessado. 
   ESTRUTURA DA FALA: Use parágrafos curtos (1 a 3 frases no máximo por parágrafo) para dar ritmo de respiração. Comece sempre conectando o tema com uma situação real ou dor do aluno no dia a dia. Depois, traga a fundamentação técnica da norma de forma mastigada e fluida. Termine mostrando o impacto prático disso e fazendo um gancho para a próxima aula. Inspire-se em scripts de vídeos dinâmicos de alta qualidade.
- 📝 Bloco de Texto Guiado (Resumo em tópicos curtos e pontos-chave com até 3 linhas por bloco)
- 🛠️ Bloco de Aplicação (Passo a passo prático para o dia a dia, como aplicar)
- 🤔 Bloco de Reflexão (Pergunta reflexiva estratégica para o aluno)
- ❓ Quiz (1 ou 2 questões com 4 alternativas focadas na prática)
- 🎯 Resultado da Aula (Lista do que o aluno atingiu ao final desta aula)

Contexto Técnico da Norma: {norma}
Diretrizes do Projeto Pedagógico: {pedagogico}
Base de Produção: {base_producao}""",

    "Roteiro de Materiais": "Liste todos os equipamentos, EPIs, e ferramentas visuais necessárias para demonstrar na prática os conceitos da aula: {aula}. Baseie-se na norma: {norma}.",
    
    "Prompts IA (Imagens)": "Crie 3 prompts detalhados em inglês para gerar imagens de apoio visual para a aula: {aula}. As imagens devem ter estilo realista, iluminação de estúdio, proporção 16:9 e focar no tema central da aula. Apenas entregue os prompts em texto puro."
}

# ==========================================
# 3. Interface Visual e Estados
# ==========================================
st.set_page_config(page_title="Studio Saber - IA", layout="wide", page_icon="⚙️")
st.title("⚙️ Gerador de Estrutura e Roteiros")

if "estrutura_curso" not in st.session_state:
    st.session_state.estrutura_curso = None
if "roteiros_gerados" not in st.session_state:
    st.session_state.roteiros_gerados = {}

with st.sidebar:
    st.header("📂 Arquivos de Base")
    file_norma = st.file_uploader("1. Norma (Ex: NR-33)", type=["pdf", "docx", "txt"])
    file_pedagogico = st.file_uploader("2. Projeto Pedagógico", type=["pdf", "docx", "txt"])
    file_base_producao = st.file_uploader("3. Base de Produção", type=["pdf", "docx", "txt"])

norma_texto = extrair_texto(file_norma)
pedagogico_texto = extrair_texto(file_pedagogico)
base_producao_texto = extrair_texto(file_base_producao)

aba_estrutura, aba_roteiros = st.tabs(["🏗️ 1. Estruturar Curso", "📝 2. Produção de Roteiros"])

# ==========================================
# ABA 1: Geração da Estrutura Inicial
# ==========================================
with aba_estrutura:
    st.markdown("Faça o upload dos 3 arquivos na barra lateral para gerar a base do curso.")
    
    arquivos_ok = norma_texto and pedagogico_texto and base_producao_texto
    
    if not arquivos_ok:
        st.info("💡 Aguardando upload de todos os arquivos base na lateral para liberar a geração.")
    
    if st.button("🚀 Gerar Estrutura do Curso", disabled=not arquivos_ok):
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
                st.success("✅ Estrutura gerada! Vá para a aba 'Produção de Roteiros'.")
            except Exception as e:
                st.error("Erro ao processar a estrutura. Verifique os arquivos e tente novamente.")

# ==========================================
# ABA 2: Edição e Geração de Conteúdo
# ==========================================
with aba_roteiros:
    if st.session_state.estrutura_curso:
        st.markdown("### 🗂️ Estrutura do Curso")
        st.caption("Edite os nomes, escolha o template e gere o conteúdo. Os botões de leitura e download aparecerão automaticamente à direita.")
        
        for idx_mod, modulo in enumerate(st.session_state.estrutura_curso["modulos"]):
            with st.expander(modulo["nome"], expanded=True):
                
                novo_nome_mod = st.text_input("Nome do Módulo", value=modulo["nome"], key=f"mod_{idx_mod}")
                st.session_state.estrutura_curso["modulos"][idx_mod]["nome"] = novo_nome_mod
                
                st.divider() # Linha sutil separando o título do módulo da lista de aulas
                
                for idx_aula, aula in enumerate(modulo["aulas"]):
                    chave_roteiro = f"{idx_mod}_{idx_aula}"
                    texto_gerado = st.session_state.roteiros_gerados.get(chave_roteiro)
                    
                    # Colunas alinhadas ao centro para manter a estética impecável
                    col_aula, col_tipo, col_btn, col_ler, col_baixar = st.columns([5, 3, 2, 1, 1], vertical_alignment="center")
                    
                    with col_aula:
                        nova_aula = st.text_input("Aula", value=aula, key=f"aula_{chave_roteiro}", label_visibility="collapsed")
                        st.session_state.estrutura_curso["modulos"][idx_mod]["aulas"][idx_aula] = nova_aula
                    
                    with col_tipo:
                        tipo_geracao = st.selectbox("Template", list(TEMPLATES.keys()), key=f"tipo_{chave_roteiro}", label_visibility="collapsed")
                    
                    with col_btn:
                        gerar_clicado = st.button("✨ Gerar IA", key=f"btn_{chave_roteiro}", use_container_width=True)
                    
                    with col_ler:
                        if texto_gerado:
                            with st.popover("👁️", use_container_width=True):
                                st.markdown(texto_gerado)
                    
                    with col_baixar:
                        if texto_gerado:
                            docx_file = gerar_docx(texto_gerado)
                            st.download_button(
                                label="📥",
                                data=docx_file,
                                file_name=f"Roteiro_{nova_aula[:15].strip()}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"down_{chave_roteiro}",
                                use_container_width=True
                            )
                            
                    # Lógica de geração fica separada para não travar o layout
                    if gerar_clicado:
                        prompt_final = TEMPLATES[tipo_geracao].format(
                            aula=nova_aula, 
                            pedagogico=pedagogico_texto, 
                            norma=norma_texto,
                            base_producao=base_producao_texto
                        )
                        with st.spinner(f"Escrevendo {tipo_geracao}..."):
                            resultado = modelo_texto.generate_content(prompt_final)
                            st.session_state.roteiros_gerados[chave_roteiro] = resultado.text
                            st.rerun() 
                            
    else:
        st.info("A estrutura do curso aparecerá aqui após ser gerada na aba anterior.")
