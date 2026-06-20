def calcular_pontuacao_jogador(stats):
    posicao = stats.get("posicao", "Médio")
    jogos = stats.get("jogos_disputados", 1)
    
    if jogos < 1:
        jogos = 1
    
    # Nota base neutra
    pontos = 6.0
    
    # Médias por jogo
    media_golos = stats.get("golos", 0) / jogos
    media_assist = stats.get("assistencias", 0) / jogos
    media_cortes = stats.get("cortes_ganhos", 0) / jogos
    
    # --- NOVO PESO MASSIVO PARA GOLOS ---
    pontos += media_golos * 5.0  # Peso subiu para 5.0!
    pontos += media_assist * 1.5 
    
    # Bónus extra de posição para Avançados que cumprem o seu papel
    if posicao == "Avançado" and media_golos > 0:
        pontos += 0.5 * media_golos

    # Ponderação de defesa
    peso_corte = 0.5 if posicao == "Defesa" else 0.1
    pontos += media_cortes * peso_corte
    
    # Eficiência de passe
    passes_totais = stats.get("passes_totais", 0)
    if passes_totais > 0:
        precisao_passe = stats.get("passes_completos", 0) / passes_totais
        pontos += (precisao_passe - 0.8) * 1.2
    
    # Sucesso em duelos
    duelos_totais = stats.get("duelos_totais", 0)
    if duelos_totais > 0:
        sucesso_duelos = stats.get("duelos_ganhos", 0) / duelos_totais
        pontos += (sucesso_duelos - 0.5) * 0.8

    # Limites da nota
    nota_final = max(1.0, min(10.0, pontos))
    return round(nota_final, 2)