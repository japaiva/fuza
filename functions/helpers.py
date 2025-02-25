from functions.database import get_all_custos
import math

def valida_campos(nome_cliente: str) -> bool:
    """Valida se um campo não está vazio."""
    return bool(nome_cliente.strip())

def formatar_demanda_placas(chapas_info): 
    paineis_texto = ( 
        f"**Painéis**:\n" 
        f"Laterais: {chapas_info['num_paineis_lateral']} de " 
        f"{chapas_info['largura_painel_lateral']*100:.2f}cm (com dobras " 
        f"{(chapas_info['largura_painel_lateral']+0.085)*100:.2f}cm), " 
        f"{chapas_info['altura_painel_lateral']:.2f}m altura; " 
        f"Fundo: {chapas_info['num_paineis_fundo']} de " 
        f"{chapas_info['largura_painel_fundo']*100:.2f}cm (com dobras " 
        f"{(chapas_info['largura_painel_fundo']+0.085)*100:.2f}cm), " 
        f"{chapas_info['altura_painel_fundo']:.2f}m altura; " 
        f"Teto: {chapas_info['num_paineis_teto']} de " 
        f"{chapas_info['largura_painel_teto']*100:.2f}cm (com dobras " 
        f"{(chapas_info['largura_painel_teto']+0.085)*100:.2f}cm), " 
        f"{chapas_info['altura_painel_teto']:.2f}m altura.\n" 
    )
    
    chapas_texto = (
        f"**Chapas Utilizadas**:\n"
        f"Laterais e Teto: {chapas_info['num_chapalt']:.0f} chapas, "
        f"sobra/chapa={chapas_info['sobra_chapalt']*100:.2f}cm,\n"
        f"Fundo: {chapas_info['num_chapaf']:.0f} chapas, "
        f"sobra/chapa={chapas_info['sobra_chapaf']*100:.2f}cm,\n"
        f"Piso: {chapas_info['num_chapa_piso']:.0f} chapas,\n"
        f"**Total Chapas (com margem): {chapas_info['num_chapatot']:.0f}**\n"
    )

    return f"{paineis_texto}\n{chapas_texto}"

def agrupar_respostas_por_pagina(respostas):
    """Agrupa as respostas de acordo com cada página, para exibir no resumo."""
    def get_unidade(campo, valor, modelo):
        unidades = {
            "Capacidade": "pessoas" if "passageiro" in modelo.lower() else "kg",
            "Pavimentos": "",
            "Altura do Poço": "m",
            "Largura do Poço": "m",
            "Comprimento do Poço": "m",
            "Altura da Cabine": "m",
            "Espessura": "mm",
            "Altura Porta": "m",
            "Largura Porta": "m",
            "Altura Porta Pavimento": "m",
            "Largura Porta Pavimento": "m"
        }
        return unidades.get(campo, "")

    paginas = {
        "Cliente": ["Solicitante", "Empresa", "Telefone", "Email"],
        "Elevador": [
            "Modelo do Elevador", "Capacidade", "Acionamento", "Tração", "Contrapeso",
            "Altura do Poço", "Largura do Poço", "Comprimento do Poço", "Pavimentos"
        ],
        "Cabine": [
            "Material", "Tipo de Inox", "Espessura", "Saída", "Altura da Cabine",
            "Piso", "Material Piso Cabine"
        ],
        "Porta Cabine": [
            "Modelo Porta", "Material Porta", "Tipo de Inox Porta",
            "Folhas Porta", "Altura Porta", "Largura Porta"
        ],
        "Porta Pavimento": [
            "Modelo Porta Pavimento", "Material Porta Pavimento",
            "Tipo de Inox Porta Pavimento", "Folhas Porta Pavimento",
            "Altura Porta Pavimento", "Largura Porta Pavimento"
        ]
    }
    modelo_elevador = respostas.get("Modelo do Elevador", "").lower()

    respostas_agrupadas = {}
    for pagina, campos in paginas.items():
        dados_pagina = {}
        for campo in campos:
            if campo in respostas:
                valor = respostas[campo]
                unidade = get_unidade(campo, valor, modelo_elevador)
                if unidade:
                    valor = f"{valor} {unidade}"
                dados_pagina[campo] = valor
        if dados_pagina:
            respostas_agrupadas[pagina] = dados_pagina
    return respostas_agrupadas
