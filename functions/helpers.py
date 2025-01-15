def valida_campos(nome_cliente: str, nome_empresa: str) -> bool:
    """Exemplo de função para validar se campos não estão vazios."""
    return bool(nome_cliente.strip() and nome_empresa.strip())

def calcula_custo_elevador(capacidade: float, pavimentos: int) -> float:
    """Exemplo de função para calcular custo de elevador (fictício)."""
    custo_basico = 10000
    custo_por_pavimento = 2000
    custo_por_kg = 50
    return custo_basico + (pavimentos * custo_por_pavimento) + (capacidade * custo_por_kg)

def calcular_dimensoes_cabine(respostas):
    altura = float(respostas.get("Altura da Cabine", 0))
    largura_poco = float(respostas.get("Largura do Poço", 0))
    comprimento_poco = float(respostas.get("Comprimento do Poço", 0))
    modelo_porta = respostas.get("Modelo Porta", "")
    contrapeso = respostas.get("Contrapeso", "")

    # Cálculo da largura
    if largura_poco <= 1.5:
        largura = largura_poco - 0.42  # 21 cm de cada lado
    else:
        largura = largura_poco - 0.48  # 24 cm de cada lado

    # Cálculo do comprimento
    comprimento = comprimento_poco - 0.11  # 11 cm do comprimento do poço

    # Ajustes baseados no modelo da porta
    if modelo_porta in ["Automática 2 folhas", "Central"]:
        comprimento -= 0.21
    elif modelo_porta == "Automática 3 folhas":
        comprimento -= 0.31
    elif modelo_porta == "Pantográfica":
        comprimento -= 0.13
    elif modelo_porta == "Pivotante":
        comprimento -= 0.04

    # Ajustes baseados no contrapeso
    if contrapeso == "Lateral":
        largura -= 0.23
    elif contrapeso == "Traseiro":
        comprimento -= 0.23

    return altura, round(largura, 2), round(comprimento, 2)

def explicacao_calculo():
    return """

    1. **Altura**: 
    - Informada na seção da cabine.

    2. **Largura**:
    - Se a largura do poço <= 1,5m: Largura do poço - 42cm (21cm de cada lado)
    - Se a largura do poço > 1,5m: Largura do poço - 48cm (24cm de cada lado)
    - Se contrapeso lateral: Reduz mais 23cm

    3. **Comprimento**:
    - Inicia com: Comprimento do poço - 11cm
    - Ajustes adicionais baseados no tipo de porta
     (Porta automática 2 folhas ou central: -21cm,
     Porta automática 3 folhas: -31cm,
     Porta pantográfica: -13cm,
     Porta pivotante: -4cm)
    - Se contrapeso traseiro: Reduz mais 23cm
    """

