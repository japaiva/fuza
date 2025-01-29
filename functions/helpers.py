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
    altura = float(respostas.get("Altura da Cabine", 0))
    largura_poco = float(respostas.get("Largura do Poço", 0))
    comprimento_poco = float(respostas.get("Comprimento do Poço", 0))
    modelo_porta = respostas.get("Modelo Porta", "")
    folhas_porta = respostas.get("Folhas Porta", "")
    contrapeso = respostas.get("Contrapeso", "")

    if largura_poco <= 1.5:
        largura = largura_poco - 0.42
    else:
        largura = largura_poco - 0.48

    comprimento = comprimento_poco - 0.10
    # Ajustes baseados no tipo de porta
    ajuste_porta = 0.0
    if modelo_porta == "Automática":
       if folhas_porta in ["2", "Central"]:
            ajuste_porta = 0.138
       elif folhas_porta == "3":
            ajuste_porta = 0.31
       elif modelo_porta == "4":
            ajuste_porta = 0.21
    elif modelo_porta == "Pantográfica":
        ajuste_porta = 0.13
    elif modelo_porta == "Pivotante":
        ajuste_porta = 0.04

    comprimento -= ajuste_porta

    if contrapeso == "Lateral":
        largura -= 0.23
    elif contrapeso == "Traseiro":
        comprimento -= 0.23

    return altura, round(largura, 2), round(comprimento, 2)

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
    num_chapamargem = 2
    num_chapatot = num_chapalt+num_chapaf+num_chapamargem

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
        "sobra_chapaf": sobra_chapaf,
        "num_chapatot": num_chapatot
    }

def dem_placas(chapas_info):
    demonstrativo = """
    Painéis:
    - Laterais: {num_paineis_lateral} painéis de {largura_painel_lateral:.2f}cm L ({largura_painel_lateral_com_dobras:.2f}cm considerando dobras) e {altura_painel_lateral:.2f}m A
    - Fundo: {num_paineis_fundo} painéis de {largura_painel_fundo:.2f}cm L ({largura_painel_fundo_com_dobras:.2f}cm considerando dobras) e {altura_painel_fundo:.2f}m A
    - Teto: {num_paineis_teto} painéis de {largura_painel_teto:.2f}cm L ({largura_painel_teto_com_dobras:.2f}cm considerando dobras) e {altura_painel_teto:.2f}m A
    """

    demonstrativo += """
    Chapas Utilizadas:   
    - Laterais e Teto: {num_chapalt:.0f} chapas, sobra por chapa: {sobra_chapalt:.2f}cm
    - Fundo: {num_chapaf:.0f} chapas, sobra por chapa: {sobra_chapaf:.2f}cm
    - Total Chapas: {num_chapatot:.0f} chapas, considerando margem
    """

    demonstrativo += """   
    Observações:   
    - O cálculo considera a otimização do uso das chapas, minimizando sobras.
    - Dobras acrescentam 8,5 cm em cada painel.
    - Consideradas 2 chapas adicionais como margem de segurança.
    - As dimensões das Chapas de Aço Brutas consideradas são 1,20m x 3,00m.
    """
    
    return demonstrativo.format(
        num_paineis_lateral=chapas_info['num_paineis_lateral'],
        largura_painel_lateral=chapas_info['largura_painel_lateral']*100,
        largura_painel_lateral_com_dobras=(chapas_info['largura_painel_lateral']+0.085)*100,
        altura_painel_lateral=chapas_info['altura_painel_lateral'],
        num_paineis_fundo=chapas_info['num_paineis_fundo'],
        largura_painel_fundo=chapas_info['largura_painel_fundo']*100,
        largura_painel_fundo_com_dobras=(chapas_info['largura_painel_fundo']+0.085)*100,
        altura_painel_fundo=chapas_info['altura_painel_fundo'],
        num_paineis_teto=chapas_info['num_paineis_teto'],
        largura_painel_teto=chapas_info['largura_painel_teto']*100,
        largura_painel_teto_com_dobras=(chapas_info['largura_painel_teto']+0.085)*100,
        altura_painel_teto=chapas_info['altura_painel_teto'],
        num_chapalt=chapas_info['num_chapalt'],
        sobra_chapalt=chapas_info['sobra_chapalt']*100,
        num_chapaf=chapas_info['num_chapaf'],
        sobra_chapaf=chapas_info['sobra_chapaf']*100,
        num_chapatot=chapas_info['num_chapatot']
    )

def calcular_dimensoes_e_explicacao(respostas: dict):
    altura = float(respostas.get("Altura da Cabine", 0))
    largura_poco = float(respostas.get("Largura do Poço", 0))
    comprimento_poco = float(respostas.get("Comprimento do Poço", 0))
    modelo_porta = respostas.get("Modelo Porta", "")
    folhas_porta = respostas.get("Folhas Porta", "")
    contrapeso = respostas.get("Contrapeso", "")

    # Inicializa as variáveis para o cálculo
    largura = largura_poco
    comprimento = comprimento_poco

    # Explicação do cálculo
    explicacao_calc = """
    **CRITÉRIOS**
    """
    explicacao_calc += """
    **Altura**: 
    - Informada na seção da cabine
    """
    explicacao_calc += """
    **Largura**:
    - Inicia com largura do poço
    - Até 1,5m de poço: subtrai 42cm no total
    - Acima de 1,5m: subtrai 48cm no total
    - Contrapeso lateral: -23cm
    """
    explicacao_calc += """
    **Comprimento**:
    - Inicia com comprimento do poço - 10cm
    - Ajustes baseados no tipo de porta:
        - Automática 2 folhas/Central: -13,8cm
        - Automática 3 folhas: -30cm
        - Automática 4 folhas: -21cm
        - Pantográfica: -13cm
        - Pivotante: -4cm
    - Contrapeso traseiro: -23cm

    **DEMONSTRATIVO**
    """

    explicacao_altura = f"""
    **Altura**: 
    - Informada pelo usuário
    """
    explicacao_altura += f"""
    - Resultado: {altura:.2f}m
    """

    explicacao_largura = f"""
    **Largura**:
    - Largura do poço: {largura_poco:.2f}m
    {"- Até 1,5m de poço: subtrai 0,42m" if largura_poco <= 1.5 else "- Acima de 1,5m de poço: subtrai 0,48m"}
    """
    if largura_poco <= 1.5:
        largura -= 0.42
    else:
        largura -= 0.48

    if contrapeso == "Lateral":
        largura -= 0.23
        explicacao_largura += f"""
    - Contrapeso lateral: subtrai 0,23m
        """
               
    explicacao_largura += f"""
    - Resultado: {largura:.2f}m
    """

    # Explicação do comprimento
    explicacao_comprimento = f"""
    **Comprimento**:
    - Comprimento do poço: {comprimento_poco:.2f}m
    - Subtração padrão: 0,10m
    """
    comprimento -= 0.10

    # Ajustes baseados no tipo de porta
    ajuste_porta = 0.0
    if modelo_porta == "Automática":
       if folhas_porta in ["2", "Central"]:
            ajuste_porta = 0.138
       elif folhas_porta == "3":
            ajuste_porta = 0.31
       elif modelo_porta == "4":
            ajuste_porta = 0.21
    elif modelo_porta == "Pantográfica":
        ajuste_porta = 0.13
    elif modelo_porta == "Pivotante":
        ajuste_porta = 0.04

    if ajuste_porta > 0:
        comprimento -= ajuste_porta
        if modelo_porta == "Automática":
            explicacao_comprimento += f"""
    - Porta Automática, folhas {folhas_porta}: subtrai {ajuste_porta:.3f}m
        """
        else:
            explicacao_comprimento += f"""
    - Porta {modelo_porta}: subtrai {ajuste_porta:.3f}m
        """

    # Ajuste para contrapeso traseiro
    if contrapeso == "Traseiro":
        comprimento -= 0.23
        explicacao_comprimento += f"""
    - Contrapeso traseiro: subtrai 0,23m
        """
    explicacao_comprimento += f"""
    - Resultado: {comprimento:.2f}m
    """

    # Junta todas as explicações
    explicacao_completa = f"""
    {explicacao_calc}
    {explicacao_altura}
    {explicacao_largura}
    {explicacao_comprimento}
    """

    return altura, round(largura, 2), round(comprimento, 2), explicacao_completa