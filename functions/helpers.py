# functions/helpers.py
import math

def valida_campos(nome_cliente: str) -> bool:
    """Valida se um campo não está vazio."""
    return bool(nome_cliente.strip())

def calcula_custo_elevador(capacidade: float, pavimentos: int) -> float:
    """
    Calcula de forma fictícia um custo de elevador 
    baseado na capacidade e na quantidade de pavimentos.
    """
    custo_basico = 10000
    custo_por_pavimento = 2000
    custo_por_kg = 50
    return custo_basico + (pavimentos * custo_por_pavimento) + (capacidade * custo_por_kg)

def calcular_dimensoes_cabine(respostas: dict):
    """
    Retorna uma tupla (altura, largura, comprimento) 
    com base nas respostas e nas regras de cálculo definidas.
    """
    altura = float(respostas.get("Altura da Cabine", 0))
    largura_poco = float(respostas.get("Largura do Poço", 0))
    comprimento_poco = float(respostas.get("Comprimento do Poço", 0))
    modelo_porta = respostas.get("Modelo Porta", "")
    contrapeso = respostas.get("Contrapeso", "")

    if largura_poco <= 1.5:
        largura = largura_poco - 0.42
    else:
        largura = largura_poco - 0.48
    comprimento = comprimento_poco - 0.14

    if modelo_porta in ["Automática 2 folhas", "Central"]:
        comprimento -= 0.138
    elif modelo_porta == "Automática 3 folhas":
        comprimento -= 0.31
    elif modelo_porta == "Automática 4 folhas":
        comprimento -= 0.21
    elif modelo_porta == "Pantográfica":
        comprimento -= 0.13
    elif modelo_porta == "Pivotante":
        comprimento -= 0.04

    if contrapeso == "Lateral":
        largura -= 0.23
    elif contrapeso == "Traseiro":
        comprimento -= 0.23

    return altura, round(largura, 2), round(comprimento, 2)

def explicacao_calculo() -> str:
    """Retorna texto de explicação das regras de cálculo."""
    return """
    1. **Altura**: Informada na seção da cabine.
    2. **Largura**:
       - Até 1,5m de poço: subtrai 42cm no total.
       - Acima de 1,5m: subtrai 48cm no total.
       - Contrapeso lateral: -23cm adicional.
    3. **Comprimento**:
       - Inicia com: comprimento do poço - 14cm
       - Ajustes baseados no tipo de porta:
         - Automática 2 folhas/Central: -13,8cm
         - Automática 3 folhas: -30cm
         - Automática 4 folhas: -21cm
         - Pantográfica: -13cm
         - Pivotante: -4cm
       - Contrapeso traseiro: -23cm adicional
    """

def calcular_largura_painel(dimensao):
    """Calcula a largura ideal do painel, entre 25 e 33 cm, não excedendo 40 cm com as dobras."""
    for divisoes in range(10, 1, -1):  # Começamos com 10 divisões e vamos até 2
        largura_base = dimensao / divisoes
        if .25 <= largura_base <= .33 and largura_base + .085 <= .40:
            return largura_base, divisoes
    return None, None  # Retorna None se nenhuma divisão for adequada

def calcular_chapas_cabine(altura, largura, comprimento):
    """Calcula o número de chapas e painéis necessários para a cabine do elevador."""
    # Dimensões da Chapa de Aço Bruta
    chapa_largura = 1.20*100
    chapa_comprimento = 3.00*100

    # Cálculo para as paredes laterais
    largura_painel_lateral, num_paineis_lateral = calcular_largura_painel(comprimento)
    if largura_painel_lateral is None:
        return "Erro: Não foi possível calcular uma largura de painel adequada para as laterais."
    
    # Cálculo para a parede do fundo
    largura_painel_fundo, num_paineis_fundo = calcular_largura_painel(largura)
    if largura_painel_fundo is None:
        return "Erro: Não foi possível calcular uma largura de painel adequada para o fundo."

    # Ajustes para o número total de painéis
    num_paineis_lateral *= 2  # Duas laterais
    num_paineis_teto = num_paineis_lateral // 2

    # Cálculo do número de Chapas de Aço Brutas (CAB) necessárias
    paineis_por_chapa_lt = math.floor(chapa_largura / (largura_painel_lateral*100 + 8.5))
    paineis_por_chapa_f = math.floor(chapa_largura / (largura_painel_fundo*100 + 8.5))

    num_chapalt = (num_paineis_lateral+num_paineis_teto)/ paineis_por_chapa_lt
    num_chapaf = (num_paineis_fundo)/ paineis_por_chapa_f

    # Cálculo das sobras
    sobra_chapalt = (.40 - (largura_painel_lateral + .085)) * num_chapalt
    sobra_chapaf = (.40 - (largura_painel_fundo + .085)) * num_chapaf

    return {
        "num_paineis_lateral": num_paineis_lateral,
        "largura_painel_lateral": largura_painel_lateral,
        "altura_painel_lateral": altura,
        "num_paineis_fundo": num_paineis_fundo,
        "largura_painel_fundo": largura_painel_fundo,
        "altura_painel_fundo": altura,
        "num_paineis_teto": num_paineis_teto,
        "largura_painel_teto": largura_painel_lateral,
        "altura_painel_teto": largura,
        "num_chapalt": num_chapalt,
        "sobra_chapalt": sobra_chapalt,
        "num_chapaf": num_chapaf,
        "sobra_chapaf": sobra_chapaf
    }