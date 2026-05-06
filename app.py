import streamlit as st
import google.generativeai as genai
import json

# ==========================================
# 1. Configuração da API
# ==========================================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Configurando o modelo para retornar JSON na primeira fase
modelo_estrutura = genai.GenerativeModel(
    model_name="gemini-3.1-flash-lite-preview",
    generation_config={"response_mime_type": "application/json"}
)

# Modelo padrão para a geração dos textos
modelo_texto = genai.GenerativeModel(model_name="gemini-3.1-flash-lite-preview")

# ==========================================
# 2. Roteiros Base (Templates)
# ==========================================
TEMPLATES = {
    "Roteiro de Aula": "Atue como um instrutor técnico especializado. Crie o roteiro de gravação detalhado para a seguinte aula: {aula}. Use o tom do projeto pedagógico: {base}. Inclua introdução, desenvolvimento e conclusão.",
    "Roteiro de Materiais": "Liste todos os equipamentos, EPIs, e ferramentas visuais necessárias para demonstrar na prática os conceitos da aula: {aula}. Norma base: {norma}.",
    "Prompts para Imagens IA": "Crie 3 prompts detalhados em inglês para gerar imagens de apoio para a aula: {aula}. As imagens devem ter estilo realista, iluminação de estúdio e focar no tema central da aula. Apenas entregue os prompts em texto."
}

# ==========================================
# 3. Interface e Lógica de Estado
# ==========================================
st.title("Gerador de Estrutura de Cursos")

# Inicializa as variáveis na sessão para não resetar a cada clique
if "estrutura_curso" not in st.session_state:
    st.session_state.estrutura_curso = None

col1, col2 = st.columns(2)
with col1:
    norma_input = st.text_area("Texto da Norma (Ex: NR-33)", height=200)
with col2:
    base_saber = st.text_area("Base do Saber / Projeto Pedagógico", height=200)

if st.button("Gerar Estrutura Inicial"):
    if norma_input and base_saber:
        prompt_json = f"""
        Baseado na norma abaixo e nas diretrizes pedagógicas, crie uma estrutura de curso dividida em módulos e aulas.
        Norma: {norma_input}
        Diretrizes: {base_saber}
        
        Retorne estritamente um JSON no seguinte formato:
        {{
            "modulos": [
                {{
                    "nome": "Módulo 1: Introdução",
                    "aulas": ["Aula 1: Conceitos", "Aula 2: Histórico"]
                }}
            ]
        }}
        """
        
        with st.spinner("Estruturando o curso..."):
            resposta = modelo_estrutura.generate_content(prompt_json)
            try:
                st.session_state.estrutura_curso = json.loads(resposta.text)
                st.success("Estrutura gerada com sucesso!")
            except Exception as e:
                st.error("Erro ao processar o JSON. Tente novamente.")

# ==========================================
# 4. Edição e Geração de Conteúdo
# ==========================================
if st.session_state.estrutura_curso:
    st.markdown("### Estrutura do Curso (Edite, Adicione ou Remova)")
    
    # Renderiza os módulos
    for idx_mod, modulo in enumerate(st.session_state.estrutura_curso["modulos"]):
        with st.expander(modulo["nome"], expanded=True):
            
            # Campo para editar o nome do módulo
            novo_nome_mod = st.text_input("Nome do Módulo", value=modulo["nome"], key=f"mod_nome_{idx_mod}")
            st.session_state.estrutura_curso["modulos"][idx_mod]["nome"] = novo_nome_mod
            
            for idx_aula, aula in enumerate(modulo["aulas"]):
                col_aula, col_acoes = st.columns([3, 1])
                
                with col_aula:
                    # Campo para editar o nome da aula
                    nova_aula = st.text_input(f"Aula {idx_aula + 1}", value=aula, key=f"aula_{idx_mod}_{idx_aula}")
                    st.session_state.estrutura_curso["modulos"][idx_mod]["aulas"][idx_aula] = nova_aula
                
                with col_acoes:
                    # Seletor de template e botão de gerar
                    tipo_geracao = st.selectbox("Gerar:", list(TEMPLATES.keys()), key=f"tipo_{idx_mod}_{idx_aula}")
                    if st.button("Gerar", key=f"btn_{idx_mod}_{idx_aula}"):
                        
                        prompt_final = TEMPLATES[tipo_geracao].format(
                            aula=nova_aula, 
                            base=base_saber, 
                            norma=norma_input
                        )
                        
                        with st.spinner(f"Gerando {tipo_geracao}..."):
                            resultado = modelo_texto.generate_content(prompt_final)
                            st.info(resultado.text)

    # Botão para salvar a estrutura final (Exportar)
    if st.button("Salvar Estrutura Completa"):
        st.json(st.session_state.estrutura_curso)
