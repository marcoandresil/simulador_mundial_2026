def calcular_pontuacao_jogador(stats):
    """
    Calcula a nota SofaScore do jogador com base nas suas estatísticas acumuladas ou do jogo.
    Aplica limites e pesos calibrados para evitar a inflação de notas (demasiados 10s).
    """
    jogos = stats.get("jogos_disputados", 1)
    if jogos == 0:
        return 6.0

    # Obter métricas médias por jogo para uma avaliação justa
    golos = stats.get("golos", 0) / jogos
    assistencias = stats.get("assistencias", 0) / jogos
    remates_baliza = stats.get("remates_baliza", 0) / jogos
    passes_decisivos = stats.get("passes_decisivos", 0) / jogos
    cortes = stats.get("cortes_ganhos", 0) / jogos
    intercecoes = stats.get("intercecoes", 0) / jogos
    alivios = stats.get("alivios", 0) / jogos
    faltas = stats.get("faltas_cometidas", 0) / jogos

    # Percentagem de passes
    p_detalhe = stats.get("passes", {})
    passes_ganhos = p_detalhe.get("completos", 0)
    passes_totais = p_detalhe.get("totais", 1)
    pct_passes = (passes_ganhos / passes_totais) if passes_totais > 0 else 0.70

    # 1. Nota Base de um jogador que entra em campo
    nota = 6.5

    # 2. Bónus Ofensivos (Pesos calibrados e não lineares)
    # Golos e assistências dão um bom bónus, mas o segundo golo adiciona menos que o primeiro
    nota += (golos * 1.2) if golos <= 1 else (1.2 + (golos - 1) * 0.8)
    nota += (assistencias * 0.9) if assistencias <= 1 else (0.9 + (assistencias - 1) * 0.6)
    
    nota += remates_baliza * 0.25
    nota += passes_decisivos * 0.40

    # 3. Bónus Defensivos / Construção
    nota += cortes * 0.30
    nota += intercecoes * 0.25
    nota += alivios * 0.10
    
    # Bónus por eficácia de passe (apenas se mantiver uma boa média de passes por jogo)
    if pct_passes > 0.85:
        nota += 0.3
    elif pct_passes < 0.65:
        nota -= 0.4

    # 4. Penalizações Disciplinares e Erros
    nota -= faltas * 0.15
    
    # Se houver registo de cartões nas estatísticas do jogador
    nota -= stats.get("amarelos", 0) * 0.20 / jogos
    nota -= stats.get("vermelhos", 0) * 1.0 / jogos

    # 5. Normalização e teto rigoroso
    # Arredondamento a uma casa decimal, garantindo que fica entre 3.0 e 10.0
    nota = round(nota, 1)
    
    if nota > 10.0:
        nota = 10.0
    elif nota < 3.0:
        nota = 3.0
        
    return nota