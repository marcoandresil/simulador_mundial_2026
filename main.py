def carregar_estatisticas_equipas(caminho_ficheiro):
    if not os.path.exists(caminho_ficheiro):
        return None

    with open(caminho_ficheiro, 'r', encoding='utf-8') as f:
        dados_json = json.load(f)
    
    equipas_consolidadas = {}

    for jogo in dados_json.get("jogos", []):
        eq1, eq2 = jogo["equipas"][0], jogo["equipas"][1]
        golos_eq1, golos_eq2 = map(int, jogo["resultado"].split("-"))
        sc = jogo.get("estatisticas_coletivas", {})

        # Inicializar equipas no dicionário se for o primeiro jogo delas
        for eq in [eq1, eq2]:
            if eq not in equipas_consolidadas:
                equipas_consolidadas[eq] = {
                    "Jogos": 0, "Vitórias": 0, "Empates": 0, "Derrotas": 0,
                    "Golos Marcados": 0, "Golos Sofridos": 0, "Remates Totais": 0, "Cantos": 0
                }

        # Atualizar dados da Equipa 1
        equipas_consolidadas[eq1]["Jogos"] += 1
        equipas_consolidadas[eq1]["Golos Marcados"] += golos_eq1
        equipas_consolidadas[eq1]["Golos Sofridos"] += golos_eq2
        if sc:
            equipas_consolidadas[eq1]["Remates Totais"] += sc["remates_totais"][0]
            equipas_consolidadas[eq1]["Cantos"] += sc["cantos"][0]

        # Atualizar dados da Equipa 2
        equipas_consolidadas[eq2]["Jogos"] += 1
        equipas_consolidadas[eq2]["Golos Marcados"] += golos_eq2
        equipas_consolidadas[eq2]["Golos Sofridos"] += golos_eq1
        if sc:
            equipas_consolidadas[eq2]["Remates Totais"] += sc["remates_totais"][1]
            equipas_consolidadas[eq2]["Cantos"] += sc["cantos"][1]

        # Atribuir pontos/resultados
        if golos_eq1 > golos_eq2:
            equipas_consolidadas[eq1]["Vitórias"] += 1
            equipas_consolidadas[eq2]["Derrotas"] += 1
        elif golos_eq1 < golos_eq2:
            equipas_consolidadas[eq2]["Vitórias"] += 1
            equipas_consolidadas[eq1]["Derrotas"] += 1
        else:
            equipas_consolidadas[eq1]["Empates"] += 1
            equipas_consolidadas[eq2]["Empates"] += 1

    # Calcular Pontos Finais e Diferença de Golos para ordenação
    tabela_final = []
    for nome_eq, stats in equipas_consolidadas.items():
        pontos = (stats["Vitórias"] * 3) + stats["Empates"]
        diff_golos = stats["Golos Marcados"] - stats["Golos Sofridos"]
        
        tabela_final.append({
            "Equipa": nome_eq,
            "P": pontos,
            "J": stats["Jogos"],
            "V": stats["Vitórias"],
            "E": stats["Empates"],
            "D": stats["Derrotas"],
            "GM": stats["Golos Marcados"],
            "GS": stats["Golos Sofridos"],
            "DG": diff_golos,
            "Remates": stats["Remates Totais"],
            "Cantos": stats["Cantos"]
        })

    # Ordenar por Pontos, Vitória e Diferença de Golos
    return sorted(tabela_final, key=lambda x: (x["P"], x["DG"], x["GM"]), reverse=True)