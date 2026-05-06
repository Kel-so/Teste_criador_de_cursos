prompt_json = f"""
        Sua tarefa principal é EXTRAIR a estrutura do curso fornecida no Projeto Pedagógico e formatá-la em JSON.
        NÃO crie módulos novos. NÃO divida módulos existentes.
        
        DOCUMENTO 1 - Norma Técnica (Apenas para contexto):
        {norma_texto}
        
        DOCUMENTO 2 - Projeto Pedagógico (A FONTE DA VERDADE):
        {pedagogico_texto}
        
        DOCUMENTO 3 - Base de Produção:
        {base_producao_texto}
        
        Regras Absolutas:
        1. O curso deve ter EXATAMENTE a mesma quantidade de módulos descrita no Projeto Pedagógico (DOCUMENTO 2).
        2. Copie os nomes dos módulos e as respectivas aulas exatamente como estão listados no Projeto Pedagógico.
        3. Aplique as regras da Base de Produção (DOCUMENTO 3) apenas para garantir a nomenclatura interna dos blocos, mas a divisão de módulos e aulas pertence ao Projeto Pedagógico.
        
        Retorne estritamente um JSON no seguinte formato:
        {{
            "modulos": [
                {{
                    "nome": "Módulo 1 - Nome do Módulo",
                    "aulas": ["Aula 1.1 - Nome da Aula", "Aula 1.2 - Nome da Aula"]
                }}
            ]
        }}
        """
