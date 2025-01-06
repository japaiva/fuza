def valida_campos(nome_cliente: str, nome_empresa: str) -> bool:
    """Exemplo de função para validar se campos não estão vazios."""
    return bool(nome_cliente.strip() and nome_empresa.strip())

def calcula_custo_elevador(capacidade: float, pavimentos: int) -> float:
    """Exemplo de função para calcular custo de elevador (fictício)."""
    custo_basico = 10000
    custo_por_pavimento = 2000
    custo_por_kg = 50
    return custo_basico + (pavimentos * custo_por_pavimento) + (capacidade * custo_por_kg)
