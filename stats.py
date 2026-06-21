def calcular_pontuacao_jogador(stats):
    posicao = stats.get("posicao", "Médio")
    jogos = stats.get("jogos_disputados", 1)

    if jogos < 1:
        jogos = 1

    # Nota base neutra de partida
    pontos = 6.0

    # Médias por jogo
    media_golos = stats.get("golos", 0) / jogos
    media_assist = stats.get("assistencias", 0) / jogos
    media_cortes = stats.get("cortes_ganhos", 0) / jogos
    media_key_passes = stats.get("passes_decisivos", 0) / jogos
    media_intercep = stats.get("intercecoes", 0) / jogos
    media_alivios = stats.get("alivios", 0) / jogos
    media_faltas = stats.get("faltas_cometidas", 0) / jogos

    # 1. Ponderação de Ataque (Golos e Criação)
    pontos += media_golos * 4.5
    pontos += media_assist * 1.5
    pontos += media_key_passes * 0.4  # Valoriza a criatividade do construtor de jogo

    if posicao == "Avançado" and media_golos > 0:
        pontos += 0.3 * media_golos

    # 2. Eficiência de Remate (Pontaria)
    remates_totais = stats.get("remates_totais", 0)
    if remates_totais > 0:
        pontaria = stats.get("remates_baliza", 0) / remates_totais
        # Se mais de metade dos remates vão à baliza, ganha bónus, caso contrário penaliza
        pontos += (pontaria - 0.5) * 0.8

    # 3. Ponderação de Defesa Avançada
    peso_defensivo = 1.0 if posicao == "Defesa" else 0.4
    pontos += media_cortes * (peso_defensivo * 0.5)
    pontos += media_intercep * (peso_defensivo * 0.4)
    pontos += media_alivios * (peso_defensivo * 0.2)

    # 4. Eficiência de Passe
    passes_totais = stats.get("passes_totais", 0)
    if passes_totais > 0:
        precisao_passe = stats.get("passes_completos", 0) / passes_totais
        pontos += (precisao_passe - 0.78) * 1.5

    # 5. Sucesso em Duelos Coletivos
    duelos_totais = stats.get("duelos_totais", 0)
    if duelos_totais > 0:
        sucesso_duelos = stats.get("duelos_ganhos", 0) / duelos_totais
        pontos += (sucesso_duelos - 0.5) * 1.0

    # 6. Malus por Disciplina/Faltas Cometidas
    # Ter uma média superior a 1.5 faltas por jogo começa a subtrair pontos à nota
    if media_faltas > 1.5:
        pontos -= (media_faltas - 1.5) * 0.3

    # Limites estritos da nota do SofaScore (1.0 a 10.0)
    nota_final = max(1.0, min(10.0, pontos))
    return round(nota_final, 2)