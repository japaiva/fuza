from functions.database import get_all_custos
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
    # Painéis
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

    # Chapas
    chapas_texto = (
        f"**Chapas Utilizadas**:\n"
        f"Laterais e Teto: {chapas_info['num_chapalt']:.0f} chapas, \n"
        f"sobra/chapa={chapas_info['sobra_chapalt']*100:.2f}cm, \n"
        f"Fundo: {chapas_info['num_chapaf']:.0f} chapas, "
        f"sobra/chapa={chapas_info['sobra_chapaf']*100:.2f}cm. \n"
        f"**Total Chapas (com margem): {chapas_info['num_chapatot']:.0f}**\n"
    )

    return f"{paineis_texto}\n{chapas_texto}"

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
        f"Laterais e Teto: {chapas_info['num_chapalt']:.0f} chapas, \n"
        f"sobra/chapa={chapas_info['sobra_chapalt']*100:.2f}cm, \n"
        f"Fundo: {chapas_info['num_chapaf']:.0f} chapas, "
        f"sobra/chapa={chapas_info['sobra_chapaf']*100:.2f}cm. \n"
        f"**Total Chapas (com margem): {chapas_info['num_chapatot']:.0f}**\n"
    )

    return f"{paineis_texto}\n{chapas_texto}"

def calcular_dimensoes_e_explicacao(respostas: dict):
    altura = float(respostas.get("Altura da Cabine", 0))
    largura_poco = float(respostas.get("Largura do Poço", 0))
    comprimento_poco = float(respostas.get("Comprimento do Poço", 0))
    modelo_porta = respostas.get("Modelo Porta", "")
    folhas_porta = respostas.get("Folhas Porta", "")
    contrapeso = respostas.get("Contrapeso", "")
    modelo = respostas.get("Modelo do Elevador", "")
    capacidade_original = float(respostas.get("Capacidade", 0))

    # Altura
    altura = float(respostas.get("Altura da Cabine", 0))
    explicacao_altura = (
        f"**Altura**: informada pelo usuário, valor final={altura:.2f}m; \n"
    )

    # Largura
    largura = largura_poco
    sub_largura = 0.42 if largura_poco <= 1.5 else 0.48
    largura -= sub_largura
    contrapeso_texto = ""
    if contrapeso == "Lateral":
        largura -= 0.23
        contrapeso_texto = ", contrapeso lateral (subtrai 0,23m)"
    explicacao_largura = (
        f"**Largura**: poço={largura_poco:.2f}m, "
        f"subtrai={sub_largura:.2f}m{contrapeso_texto}, "
        f"valor final={largura:.2f}m; \n"
    )

    # Comprimento
    comprimento = comprimento_poco - 0.10
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
    
    porta_texto = ""
    if ajuste_porta > 0:
        comprimento -= ajuste_porta
        porta_texto = f", porta {modelo_porta} (subtrai {ajuste_porta:.3f}m)"

    if contrapeso == "Traseiro":
        comprimento -= 0.23
        porta_texto += ", contrapeso traseiro (subtrai 0,23m)"

    explicacao_comprimento = (
        f"**Comprimento**: poço={comprimento_poco:.2f}m, subtrai=0.10m{porta_texto}, "
        f"valor final={comprimento:.2f}m; \n"
    )
    # Capacidade
    if "Passageiro" in modelo:
        capacidade_cabine = capacidade_original * 80
        explicacao_capacidade = f"**Capacidade**: {capacidade_original} pessoas * 80 kg = {capacidade_cabine:.2f} kg; \n"
    else:
        capacidade_cabine = capacidade_original
        explicacao_capacidade = f"**Capacidade**: {capacidade_cabine:.2f} kg; \n"

    # Novo cálculo para Tração Cabine
    tracao_cabine = capacidade_cabine / 2 + 500
    explicacao_tracao = f"**Tração**: (Capacidade Cabine / 2) + 500 = {tracao_cabine:.2f} kg.\n"


    # Explicação completa
    explicacao_completa = (
        f"**Cabine**:\n"
        f"{explicacao_altura}{explicacao_largura}{explicacao_comprimento}"
        f"{explicacao_capacidade}{explicacao_tracao}"
    )

    # Criar dicionário com as variáveis de dimensionamento
    dimensionamento = {
        "cab": {
            "altura": altura,
            "largura": largura,
            "compr": comprimento,
            "capacidade": capacidade_cabine,
            "tracao": tracao_cabine,
            "chp": {
                "corpo": 0,  # Será calculado posteriormente
                "piso": 0    # Será calculado posteriormente
            },
            "pnl": {
                "lateral": 0,  # Será calculado posteriormente
                "fundo": 0,    # Será calculado posteriormente
                "teto": 0      # Será calculado posteriormente
            }
        }
    }

    # Calcular chapas e painéis
    chapas_info = calcular_chapas_cabine(altura, largura, comprimento)
    if isinstance(chapas_info, dict):
        dimensionamento["cab"]["chp"]["corpo"] = chapas_info["num_chapatot"]
        dimensionamento["cab"]["pnl"]["lateral"] = chapas_info["num_paineis_lateral"]
        dimensionamento["cab"]["pnl"]["fundo"] = chapas_info["num_paineis_fundo"]
        dimensionamento["cab"]["pnl"]["teto"] = chapas_info["num_paineis_teto"]

        explicacao_chapas = formatar_demanda_placas(chapas_info)
        explicacao_completa += f"\n{explicacao_chapas}"
    else:
        explicacao_completa += f"\nErro no cálculo de chapas: {chapas_info}"

    return dimensionamento, explicacao_completa

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
        explicacoes[codigo_chapa] = f"{todos_custos[codigo_chapa].descricao}: {componentes[codigo_chapa]} unidades (corpo da cabine)"

    # Parafusos
    qtd_parafusos = (13 * dimensionamento['cab']['pnl']['lateral'] + 
                     2 * dimensionamento['cab']['pnl']['fundo'] + 
                     2 * dimensionamento['cab']['pnl']['teto'])
    
    if "FE01" in todos_custos:
        componentes["FE01"] = qtd_parafusos
        explicacoes["FE01"] = f"{todos_custos['FE01'].descricao}: {qtd_parafusos} unidades (13 por painel lateral, 2 por painel de fundo e teto)"

    # Grupo Chapa - Chapa Piso Cabine
    
    piso_conta = respostas.get("Piso", "")
    
    if piso_conta == "Por conta da empresa":
        codigo_chapa_piso = "CH02"
    elif piso_conta == "Por conta do cliente":
        codigo_chapa_piso = "CH03"
    else:
        codigo_chapa_piso = None

    if codigo_chapa_piso and codigo_chapa_piso in todos_custos:
        qtd_chapas_piso = dimensionamento['cab']['chp']['piso']
        componentes[codigo_chapa_piso] = qtd_chapas_piso
        explicacoes[codigo_chapa_piso] = f"{todos_custos[codigo_chapa_piso].descricao}: {qtd_chapas_piso} unidades (piso da cabine)"

        # Parafusos para o piso
        qtd_parafusos_piso = 13 * qtd_chapas_piso
        if "FE01" in todos_custos:
            componentes["FE01"] = componentes.get("FE01", 0) + qtd_parafusos_piso
            explicacoes["FE01"] = explicacoes.get("FE01", "") + f"\nParafusos adicionais para o piso: {qtd_parafusos_piso} unidades"

    # Grupo Chapa - Chapa Piso Cabine

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
            explicacoes[codigo_chapa_cobertura] = f"{todos_custos[codigo_chapa_cobertura].descricao}: {qtd_chapas_cobertura} unidades (piso de cobertura)"

            # Parafusos para o piso de cobertura
            qtd_parafusos_cobertura = 13 * qtd_chapas_cobertura
            if "FE01" in todos_custos:
                componentes["FE01"] = componentes.get("FE01", 0) + qtd_parafusos_cobertura
                explicacoes["FE01"] = explicacoes.get("FE01", "") + f"\nParafusos adicionais para o piso de cobertura: {qtd_parafusos_cobertura} unidades"

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
        explicacoes[codigo_travessa] = f"{todos_custos[codigo_travessa].descricao}: {qtd_travessa} unidades, comprimento {comp_travessa:.2f}m cada"

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
        explicacoes[codigo_longarina] = f"{todos_custos[codigo_longarina].descricao}: {qtd_longarina} unidades, comprimento {comp_longarina:.2f}m cada"

    # Parafusos para chassi
    if "FE02" in todos_custos:
        componentes["FE02"] = 65
        explicacoes["FE02"] = f"{todos_custos['FE02'].descricao}: 65 unidades (para o chassi)"

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
            f"{todos_custos[codigo_perfil_externo].descricao}: {qtd_perfil_externo} unidades, "
            f"2 com comprimento {comp_perfil_externo_largura:.2f}m e "
            f"2 com comprimento {comp_perfil_externo_comprimento:.2f}m"
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
            f"{todos_custos[codigo_perfil_interno].descricao}: {qtd_perfil_interno} unidades, "
            f"comprimento {comp_perfil_interno:.2f}m cada"
        )

    # Parafusos para plataforma
    qtd_parafusos_plataforma = 24 + (4 * qtd_perfil_interno)
    if "FE02" in todos_custos:
        componentes["FE02"] = componentes.get("FE02", 0) + qtd_parafusos_plataforma
        explicacoes["FE02"] = explicacoes.get("FE02", "") + (
            f"\nParafusos adicionais para a plataforma: {qtd_parafusos_plataforma} unidades "
            f"(24 + 4 * {qtd_perfil_interno} perfis internos)"
        )

    # Grupo TRAÇÃO - Motor

    acionamento = respostas.get("Acionamento", "")

    if acionamento.lower() == "hidráulico":
        if "MO01" in todos_custos:
            componentes["MO01"] = 1
            explicacoes["MO01"] = f"{todos_custos['MO01'].descricao}: 1 unidade (acionamento hidráulico)"

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
        explicacoes["PE13"] = f"{todos_custos['PE13'].descricao}: {qtd_polias} unidade(s)"

    # Cabo de aço (PE14)
    comp_cabo = comprimento_poco
    if tracao == "2x1":
        comp_cabo = 2 * comprimento_poco
    comp_cabo += 5  # 5 metros adicionais

    if "PE14" in todos_custos:
        componentes["PE14"] = comp_cabo
        explicacoes["PE14"] = f"{todos_custos['PE14'].descricao}: {comp_cabo:.2f} metros"

    # Travessa da polia (PE15)
    if qtd_polias > 1:
        comp_travessa = largura_cabine / 2
        if "PE15" in todos_custos:
            componentes["PE15"] = 1
            explicacoes["PE15"] = f"{todos_custos['PE15'].descricao}: 1 unidade, comprimento {comp_travessa:.2f}m"

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
        explicacoes[contrapeso_tipo] = f"{todos_custos[contrapeso_tipo].descricao}: 1 unidade"

    # Pedra
    if contrapeso_tipo in ["PE16", "PE17"]:
        pedra_tipo = "PE19"
        qtd_pedras = int(tracao_cabine / 45)
    else:
        pedra_tipo = "PE20"
        qtd_pedras = int(tracao_cabine / 75)

    if pedra_tipo in todos_custos:
        componentes[pedra_tipo] = qtd_pedras
        explicacoes[pedra_tipo] = f"{todos_custos[pedra_tipo].descricao}: {qtd_pedras} unidades"

    # Grupo TRAÇÃO - Guias
    
    altura_poco = float(respostas.get("Altura do Poço", 0))
    contrapeso = respostas.get("Contrapeso", "")
    pavimentos = int(respostas.get("Pavimentos", 0))

    # Guia do elevador (PE21)
    qtd_guia_elevador = round(altura_poco / 5 * 2)
    if "PE21" in todos_custos:
        componentes["PE21"] = qtd_guia_elevador
        explicacoes["PE21"] = f"{todos_custos['PE21'].descricao}: {qtd_guia_elevador} unidades"

    # Suporte guia (PE22)
    qtd_suporte_guia = round(altura_poco / 5 * 2)
    if "PE22" in todos_custos:
        componentes["PE22"] = qtd_suporte_guia
        explicacoes["PE22"] = f"{todos_custos['PE22'].descricao}: {qtd_suporte_guia} unidades"

    # Guia do contrapeso (PE23)
    if contrapeso:
        qtd_guia_contrapeso = round(altura_poco / 5 * 2)
        if "PE23" in todos_custos:
            componentes["PE23"] = qtd_guia_contrapeso
            explicacoes["PE23"] = f"{todos_custos['PE23'].descricao}: {qtd_guia_contrapeso} unidades"

    # Suporte guia do contrapeso (PE24)
    if contrapeso:
        qtd_suporte_guia_contrapeso = 4 + pavimentos * 2
        if "PE24" in todos_custos:
            componentes["PE24"] = qtd_suporte_guia_contrapeso
            explicacoes["PE24"] = f"{todos_custos['PE24'].descricao}: {qtd_suporte_guia_contrapeso} unidades"

    # Calcular o custo de cada componente e o custo total
    for codigo, quantidade in componentes.items():
        if codigo in todos_custos:
            custo_unitario = todos_custos[codigo].valor
            custo_total_item = quantidade * custo_unitario
            custos[codigo] = custo_total_item
            custo_total += custo_total_item
            explicacoes[codigo] += f" - Custo: R$ {custo_total_item:,.2f}"

    return componentes, explicacoes, custos, custo_total, todos_custos
