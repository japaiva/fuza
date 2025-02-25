import math
from functions.database import get_all_custos
from functions.helpers import formatar_demanda_placas

# dimensoes
# componentes

# largura painel
# chapas cabine

def calcular_dimensionamento_completo(respostas: dict):
    # Extrair dados das respostas
    altura = float(respostas.get("Altura da Cabine", 0))
    largura_poco = float(respostas.get("Largura do Poço", 0))
    comprimento_poco = float(respostas.get("Comprimento do Poço", 0))
    modelo_porta = respostas.get("Modelo Porta", "")
    folhas_porta = respostas.get("Folhas Porta", "")
    contrapeso = respostas.get("Contrapeso", "")
    modelo = respostas.get("Modelo do Elevador", "")
    capacidade_original = float(respostas.get("Capacidade", 0))

    # Calcular largura
    sub_largura = 0.42 if largura_poco <= 1.5 else 0.48
    largura = largura_poco - sub_largura
    if contrapeso == "Lateral":
        largura -= 0.23

    # Calcular comprimento
    comprimento = comprimento_poco - 0.10
    ajuste_porta = 0.0
    if modelo_porta == "Automática":
        if folhas_porta in ["2", "Central"]:
            ajuste_porta = 0.138
        elif folhas_porta == "3":
            ajuste_porta = 0.31
        elif folhas_porta == "4":
            ajuste_porta = 0.21
    elif modelo_porta == "Pantográfica":
        ajuste_porta = 0.13
    elif modelo_porta == "Pivotante":
        ajuste_porta = 0.04
    comprimento -= ajuste_porta
    if contrapeso == "Traseiro":
        comprimento -= 0.23

    # Arredondar dimensões
    largura = round(largura, 2)
    comprimento = round(comprimento, 2)

    # Calcular capacidade e tração
    if "Passageiro" in modelo:
        capacidade_cabine = capacidade_original * 80
    else:
        capacidade_cabine = capacidade_original
    tracao_cabine = capacidade_cabine / 2 + 500

    # Calcular chapas
    chapas_info = calcular_chapas_cabine(altura, largura, comprimento)

    # Gerar explicações
    explicacoes = f"""
    **Altura**: informada pelo usuário, valor final={altura:.2f}m;
    **Largura**: poço={largura_poco:.2f}m, subtrai={sub_largura:.2f}m{', contrapeso lateral (subtrai 0,23m)' if contrapeso == 'Lateral' else ''}, valor final={largura:.2f}m;
    **Comprimento**: poço={comprimento_poco:.2f}m, subtrai=0.10m, porta {modelo_porta}{f' {folhas_porta} folhas' if folhas_porta else ''}{', contrapeso traseiro (subtrai 0,23m)' if contrapeso == 'Traseiro' else ''}, valor final={comprimento:.2f}m;
    **Capacidade**: {'pessoas' if 'Passageiro' in modelo else 'kg'} {capacidade_original} {'* 80 kg' if 'Passageiro' in modelo else ''} = {capacidade_cabine:.2f} kg;
    **Tração**: (Capacidade Cabine / 2) + 500 = {tracao_cabine:.2f} kg.
    """

    if isinstance(chapas_info, dict):
        explicacoes += formatar_demanda_placas(chapas_info)
    else:
        explicacoes += f"\nErro no cálculo de chapas: {chapas_info}"

    # Montar o resultado
    dimensionamento = {
        "cab": {
            "altura": altura,
            "largura": largura,
            "compr": comprimento,
            "capacidade": capacidade_cabine,
            "tracao": tracao_cabine,
            "chp": {
                "corpo": chapas_info.get("num_chapatot", 0) if isinstance(chapas_info, dict) else 0,
                "piso": chapas_info.get("num_chapa_piso", 0) if isinstance(chapas_info, dict) else 0
            },
            "pnl": {
                "lateral": chapas_info.get("num_paineis_lateral", 0) if isinstance(chapas_info, dict) else 0,
                "fundo": chapas_info.get("num_paineis_fundo", 0) if isinstance(chapas_info, dict) else 0,
                "teto": chapas_info.get("num_paineis_teto", 0) if isinstance(chapas_info, dict) else 0
            }
        }
    }

    return dimensionamento, explicacoes

def calcular_componentes(dimensionamento, respostas):
    componentes = {}
    explicacoes = {}
    custos = {}
    custo_total = 0
    
    # Obter todos os custos do banco de dados
    todos_custos = {custo.codigo: custo for custo in get_all_custos()}

    # Grupo Chapa - Chapa Corpo Cabine

    material = respostas.get("Material", "")
    tipo_inox = respostas.get("Tipo de Inox", "")
    
    if material == "Inox":
        codigo_chapa = "CH01" if tipo_inox == "304" else "CH02"
    elif material == "Chapa Pintada":
        codigo_chapa = "CH06"
    elif material == "Alumínio":
        codigo_chapa = "CH07"
    else:
        codigo_chapa = None

    if codigo_chapa and codigo_chapa in todos_custos:
        componentes[codigo_chapa] = dimensionamento['cab']['chp']['corpo']
        explicacoes[codigo_chapa] = "Cálculo: Quantidade baseada no dimensionamento das chapas do corpo da cabine."

    # Parafusos
    qtd_parafusos = (13 * dimensionamento['cab']['pnl']['lateral'] + 
                     2 * dimensionamento['cab']['pnl']['fundo'] + 
                     2 * dimensionamento['cab']['pnl']['teto'])
    
    if "FE01" in todos_custos:
        componentes["FE01"] = qtd_parafusos
        explicacoes["FE01"] = f"13 por painel lateral ({dimensionamento['cab']['pnl']['lateral']}), 2 por painel de fundo ({dimensionamento['cab']['pnl']['fundo']}) e teto ({ 2 * dimensionamento['cab']['pnl']['teto']})"

    # Grupo Chapa - Chapa Piso Cabine
    
    piso_conta = respostas.get("Piso", "")
    
    if piso_conta == "Por conta da empresa":
        codigo_chapa_piso = "CH02"
        c_expl = "Cálculo: Quantidade baseada no dimensionamento das chapas do piso, mais 1 chapa extra."
    elif piso_conta == "Por conta do cliente":
        codigo_chapa_piso = "CH03"
        c_expl = "Cálculo: Quantidade baseada no dimensionamento das chapas do piso."
    else:
        codigo_chapa_piso = None

    if codigo_chapa_piso and codigo_chapa_piso in todos_custos:
        qtd_chapas_piso = dimensionamento['cab']['chp']['piso']
        componentes[codigo_chapa_piso] = componentes.get(codigo_chapa_piso, 0) + qtd_chapas_piso
        explicacoes[codigo_chapa_piso] = c_expl

        # Parafusos para o piso
        qtd_parafusos_piso = 13 * qtd_chapas_piso
        if "FE01" in todos_custos:
            componentes["FE01"] = componentes.get("FE01", 0) + qtd_parafusos_piso
            explicacoes["FE01"] += "\nCálculo para parafusos adicionais do piso: 13 por chapa de piso."

    # Grupo Chapa - Chapa Piso Cabine (Cobertura)

    tipo_piso = respostas.get("Material Piso Cabine", "")
    
    if piso_conta == "Por conta da empresa":
        if tipo_piso == "Antiderrapante 3/8":
            codigo_chapa_cobertura = "CH04"
        elif tipo_piso == "Xadrez":
            codigo_chapa_cobertura = "CH05"
        else:
            codigo_chapa_cobertura = None

        if codigo_chapa_cobertura and codigo_chapa_cobertura in todos_custos:
            qtd_chapas_cobertura = dimensionamento['cab']['chp']['piso']
            componentes[codigo_chapa_cobertura] = qtd_chapas_cobertura
            explicacoes[codigo_chapa_cobertura] = "Cálculo: Quantidade igual ao número de chapas do piso."

            # Parafusos para o piso de cobertura
            qtd_parafusos_cobertura = 13 * qtd_chapas_cobertura
            if "FE01" in todos_custos:
                componentes["FE01"] = componentes.get("FE01", 0) + qtd_parafusos_cobertura
                explicacoes["FE01"] += "\nCálculo para parafusos adicionais da cobertura do piso: 13 por chapa de cobertura."

    # Grupo CARRINHO - Chassi

    capacidade = dimensionamento['cab']['capacidade']
    largura_cabine = dimensionamento['cab']['largura']
    altura_cabine = dimensionamento['cab']['altura']

    # Travessa
    if capacidade <= 1000:
        codigo_travessa = "PE01"
    elif capacidade <= 1800:
        codigo_travessa = "PE02"
    else:
        codigo_travessa = "PE03"

    qtd_travessa = 4
    if capacidade > 2000:
        qtd_travessa += 4

    comp_travessa = largura_cabine + 0.25  # 25 cm adicional

    if codigo_travessa in todos_custos:
        componentes[codigo_travessa] = qtd_travessa
        explicacoes[codigo_travessa] = (
            f"Cálculo: Quantidade base de 4 unidades, +4 se capacidade > 2000kg. Comprimento = largura da cabine + 0,25m. "
            f"Tipo selecionado com base na capacidade do elevador."
        )

    # Longarina
    if capacidade <= 1500:
        codigo_longarina = "PE04"
    elif capacidade <= 2000:
        codigo_longarina = "PE05"
    else:
        codigo_longarina = "PE06"

    qtd_longarina = 2
    comp_longarina = altura_cabine + 0.70  # 70 cm adicional

    if codigo_longarina in todos_custos:
        componentes[codigo_longarina] = qtd_longarina
        explicacoes[codigo_longarina] = (
            f"Cálculo: 2 unidades fixas. Comprimento = altura da cabine + 0,70m. "
            f"Tipo selecionado com base na capacidade do elevador."
        )

    # Parafusos para chassi
    if "FE02" in todos_custos:
        componentes["FE02"] = 65
        explicacoes["FE02"] = "Quantidade fixa de 65 unidades para montagem do chassi."

    # Grupo CARRINHO - Plataforma

    largura_cabine = dimensionamento['cab']['largura']
    comprimento_cabine = dimensionamento['cab']['compr']

    # Perfis externos
    if capacidade <= 1000:
        codigo_perfil_externo = "PE07"
    elif capacidade <= 1800:
        codigo_perfil_externo = "PE08"
    else:
        codigo_perfil_externo = "PE09"

    qtd_perfil_externo = 4
    comp_perfil_externo_largura = largura_cabine
    comp_perfil_externo_comprimento = comprimento_cabine

    if codigo_perfil_externo in todos_custos:
        componentes[codigo_perfil_externo] = qtd_perfil_externo
        explicacoes[codigo_perfil_externo] = (
            f"Cálculo: 4 unidades fixas. 2 com comprimento igual à largura da cabine, 2 com comprimento igual ao comprimento da cabine. "
            f"Tipo selecionado com base na capacidade do elevador."
        )

    # Perfis internos
    if capacidade <= 1000:
        codigo_perfil_interno = "PE10"
    elif capacidade <= 1800:
        codigo_perfil_interno = "PE11"
    else:
        codigo_perfil_interno = "PE12"

    qtd_perfil_interno = round(largura_cabine / 0.35)  # 35 cm = 0.35 m
    comp_perfil_interno = comprimento_cabine

    if codigo_perfil_interno in todos_custos:
        componentes[codigo_perfil_interno] = qtd_perfil_interno
        explicacoes[codigo_perfil_interno] = (
            f"Cálculo: Quantidade = largura da cabine / 0,35m (arredondado). Comprimento igual ao comprimento da cabine. "
            f"Tipo selecionado com base na capacidade do elevador."
        )

    # Parafusos para plataforma
    qtd_parafusos_plataforma = 24 + (4 * qtd_perfil_interno)
    if "FE02" in todos_custos:
        componentes["FE02"] = componentes.get("FE02", 0) + qtd_parafusos_plataforma
        explicacoes["FE02"] += (
            f"\nParafusos adicionais para a plataforma: "
            f"Cálculo: 24 unidades base + (4 * número de perfis internos). Adicionados aos parafusos do chassi."
        )

    # Grupo TRAÇÃO - Motor

    acionamento = respostas.get("Acionamento", "")

    if acionamento.lower() == "hidráulico":
        if "MO01" in todos_custos:
            componentes["MO01"] = 1
            explicacoes["MO01"] = "1 unidade se o acionamento for hidráulico."

    # Grupo TRAÇÃO - Tracionamento

    tracao = respostas.get("Tração", "")
    largura_cabine = dimensionamento['cab']['largura']
    comprimento_poco = float(respostas.get("Comprimento do Poço", 0))

    # Polia (PE13)
    qtd_polias = 0
    if tracao == "2x1":
        qtd_polias = 1
        if largura_cabine > 2:
            qtd_polias = 2

    if "PE13" in todos_custos and qtd_polias > 0:
        componentes["PE13"] = qtd_polias
        explicacoes["PE13"] = "Cálculo: 1 unidade se tração 2x1, 2 unidades se tração 2x1 e largura da cabine > 2m."

    # Cabo de aço (PE14)
    comp_cabo = comprimento_poco
    if tracao == "2x1":
        comp_cabo = 2 * comprimento_poco
    comp_cabo += 5  # 5 metros adicionais

    if "PE14" in todos_custos:
        componentes["PE14"] = comp_cabo
        explicacoes["PE14"] = "Cálculo: Comprimento do poço (2x se tração 2x1) + 5m adicionais."

    # Travessa da polia (PE15)
    if qtd_polias > 1:
        comp_travessa = largura_cabine / 2
        if "PE15" in todos_custos:
            componentes["PE15"] = 1
            explicacoes["PE15"] = "1 unidade se houver 2 polias. Comprimento = largura da cabine / 2."

    # Grupo TRAÇÃO - Contrapeso

    contrapeso_posicao = respostas.get("Contrapeso", "")
    comprimento_poco = float(respostas.get("Comprimento do Poço", 0))
    largura_poco = float(respostas.get("Largura do Poço", 0))
    tracao_cabine = dimensionamento['cab']['tracao']

    contrapeso_tipo = None
    if contrapeso_posicao == "Lateral":
        if comprimento_poco < 1.90:
            contrapeso_tipo = "PE16" if tracao_cabine <= 1000 else "PE17"
        else:
            contrapeso_tipo = "PE18"
    elif contrapeso_posicao == "Traseiro":
        if largura_poco < 1.90:
            contrapeso_tipo = "PE16" if tracao_cabine <= 1000 else "PE17"
        else:
            contrapeso_tipo = "PE18"

    if contrapeso_tipo and contrapeso_tipo in todos_custos:
        componentes[contrapeso_tipo] = 1
        explicacoes[contrapeso_tipo] = "Tipo selecionado com base na posição do contrapeso, dimensões do poço e tração da cabine."

    # Pedra
    if contrapeso_tipo in ["PE16", "PE17"]:
        pedra_tipo = "PE19"
        qtd_pedras = int(tracao_cabine / 45)
    else:
        pedra_tipo = "PE20"
        qtd_pedras = int(tracao_cabine / 75)

    if pedra_tipo in todos_custos:
        componentes[pedra_tipo] = qtd_pedras
        explicacoes[pedra_tipo] = "Cálculo: Quantidade = tração da cabine / 45 (para PE16/PE17) ou tração da cabine / 75 (para PE18)."

    # Grupo TRAÇÃO - Guias
    
    altura_poco = float(respostas.get("Altura do Poço", 0))
    contrapeso = respostas.get("Contrapeso", "")
    pavimentos = int(respostas.get("Pavimentos", 0))

    # Guia do elevador (PE21)
    qtd_guia_elevador = round(altura_poco / 5 * 2)
    if "PE21" in todos_custos:
        componentes["PE21"] = qtd_guia_elevador
        explicacoes["PE21"] = "Cálculo: Quantidade = (altura do poço / 5) * 2, arredondado."

    # Suporte guia (PE22)
    qtd_suporte_guia = round(altura_poco / 5 * 2)
    if "PE22" in todos_custos:
        componentes["PE22"] = qtd_suporte_guia
        explicacoes["PE22"] = "Cálculo: Quantidade = (altura do poço / 5) * 2, arredondado."

    # Guia do contrapeso (PE23)
    if contrapeso:
        qtd_guia_contrapeso = round(altura_poco / 5 * 2)
        if "PE23" in todos_custos:
            componentes["PE23"] = qtd_guia_contrapeso
            explicacoes["PE23"] = "Cálculo: Quantidade = (altura do poço / 5) * 2, arredondado. Apenas se houver contrapeso."

    # Suporte guia do contrapeso (PE24)
    if contrapeso:
        qtd_suporte_guia_contrapeso = 4 + pavimentos * 2
        if "PE24" in todos_custos:
            componentes["PE24"] = qtd_suporte_guia_contrapeso
            explicacoes["PE24"] = "Cálculo: Quantidade = 4 + (número de pavimentos * 2). Apenas se houver contrapeso."

    
        # Grupo SISTEMAS COMPLEMENTARES - Iluminação
    comprimento_cabine = dimensionamento['cab']['compr']
    
    if "CC01" in todos_custos:
        qtd_lampadas = 2 if comprimento_cabine <= 1.80 else 4
        componentes["CC01"] = qtd_lampadas
        explicacoes["CC01"] = "Cálculo: 2 lâmpadas LED se comprimento da cabine <= 1,80m, senão 4 lâmpadas."

    # Grupo SISTEMAS COMPLEMENTARES - Ventilação
    modelo_elevador = respostas.get("Modelo do Elevador", "")
    
    if "CC02" in todos_custos:
        qtd_ventiladores = 1 if "Passageiro" in modelo_elevador else 0
        if qtd_ventiladores > 0:
            componentes["CC02"] = qtd_ventiladores
            explicacoes["CC02"] = "Cálculo: 1 ventilador se o elevador for do tipo passageiro, senão 0."
    
    componentes_formatados = {}
    for codigo, quantidade in componentes.items():
        if codigo in todos_custos:
            custo_unitario = todos_custos[codigo].valor
            custo_total_item = quantidade * custo_unitario
            custos[codigo] = custo_total_item
            custo_total += custo_total_item
            
            componentes_formatados[codigo] = {
                "descricao": todos_custos[codigo].descricao,
                "quantidade": quantidade,
                "unidade": todos_custos[codigo].unidade,
                "custo_unitario": custo_unitario,
                "custo_total": custo_total_item,
                "explicacao": explicacoes[codigo]
            }

    return componentes_formatados, custos, custo_total, todos_custos

# SUBROTINAS

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
    chapa_largura = 1.20
    chapa_comprimento = 3.00

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
    paineis_por_chapa_lt = math.floor(chapa_largura / (largura_painel_lateral + 0.085))
    paineis_por_chapa_f = math.floor(chapa_largura / (largura_painel_fundo + 0.085))

    num_chapalt = math.ceil((num_paineis_lateral + num_paineis_teto) / paineis_por_chapa_lt)
    num_chapaf = math.ceil(num_paineis_fundo / paineis_por_chapa_f)

    # Cálculo das chapas do piso
    area_piso = largura * comprimento
    area_chapa = chapa_largura * chapa_comprimento
    num_chapapiso = math.ceil(area_piso / area_chapa)

    # Cálculo da sobra da chapa do piso
    area_utilizada_piso = area_piso
    sobra_chapapiso = (num_chapapiso * area_chapa) - area_utilizada_piso

    num_chapamargem = 2
    num_chapatot = num_chapalt + num_chapaf + num_chapamargem + num_chapapiso

    # Cálculo das sobras
    sobra_chapalt = (0.40 - (largura_painel_lateral + 0.085)) * num_chapalt
    sobra_chapaf = (0.40 - (largura_painel_fundo + 0.085)) * num_chapaf


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
        "num_chapa_piso": num_chapapiso,
        "sobra_chapapiso": sobra_chapapiso,
        "num_chapatot": num_chapatot
    }