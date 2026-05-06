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
