import json
import os

def carregar_dados_mundial(caminho_ficheiro):
    """Lê o JSON do Mundial e consolida as estatísticas acumuladas por jogador."""
    if not os.path.exists(caminho_ficheiro):
        return None

    with open(caminho_ficheiro, 'r', encoding='utf-8') as f:
        dados_json = json.load(f)
    
    dados_consolidados = {}

    for jogo in dados_json.get("jogos", []):
        for jog in jogo.get("estatisticas_jogadores", []):
            nome = jog["nome"]
            
            duelos_g = jog["duelos"]["solo_ganhos"] + jog["duelos"]["aereos_ganhos"]
            duelos_t = jog["duelos"]["solo_totais"] + jog["duelos"]["aereos_totais"]
            
            if nome in dados_consolidados:
                dados_consolidados[nome]["jogos_disputados"] += 1
                dados_consolidados[nome]["minutos_jogados"] += jog["minutos_jogados"]
                dados_consolidados[nome]["golos"] += jog["golos"]
                dados_consolidados[nome]["assistencias"] += jog["assistencias"]
                dados_consolidados[nome]["cortes_ganhos"] += jog["cortes_ganhos"]
                dados_consolidados[nome]["passes_completos"] += jog["passes"]["completos"]
                dados_consolidados[nome]["passes_totais"] += jog["passes"]["totais"]
                dados_consolidados[nome]["duelos_ganhos"] += duelos_g
                dados_consolidados[nome]["duelos_totais"] += duelos_t
            else:
                dados_consolidados[nome] = {
                    "posicao": jog["posicao"],
                    "equipa": jog["equipa"],
                    "jogos_disputados": 1,
                    "minutos_jogados": jog["minutos_jogados"],
                    "golos": jog["golos"],
                    "assistencias": jog["assistencias"],
                    "cortes_ganhos": jog["cortes_ganhos"],
                    "passes_completos": jog["passes"]["completos"],
                    "passes_totais": jog["passes"]["totais"],
                    "duelos_ganhos": duelos_g,
                    "duelos_totais": duelos_t
                }
            
    return dados_consolidados


def carregar_estatisticas_equipas(caminho_ficheiro):
    """Lê o JSON do Mundial e gera a tabela classificativa geral acumulada das equipas."""
    if not os.path.exists(caminho_ficheiro):
        return None

    with open(caminho_ficheiro, 'r', encoding='utf-8') as f:
        dados_json = json.load(f)
    
    equipas_consolidadas = {}

    for jogo in dados_json.get("jogos", []):
        eq1, eq2 = jogo["equipas"][0], jogo["equipas"][1]
        golos_eq1, golos_eq2 = map(int, jogo["resultado"].split("-"))
        sc = jogo.get("estatisticas_coletivas", {})

        # Inicializar chaves das equipas envolvidas se for a estreia delas no torneio
        for eq in [eq1, eq2]:
            if eq not in equipas_consolidadas:
                equipas_consolidadas[eq] = {
                    "Jogos": 0, "Vitórias": 0, "Empates": 0, "Derrotas": 0,
                    "Golos Marcados": 0, "Golos Sofridos": 0, "Remates Totais": 0, "Cantos": 0
                }

        # Acumular dados da Equipa 1 (Casa)
        equipas_consolidadas[eq1]["Jogos"] += 1
        equipas_consolidadas[eq1]["Golos Marcados"] += golos_eq1
        equipas_consolidadas[eq1]["Golos Sofridos"] += golos_eq2
        if sc:
            equipas_consolidadas[eq1]["Remates Totais"] += sc["remates_totais"][0]
            equipas_consolidadas[eq1]["Cantos"] += sc["cantos"][0]

        # Acumular dados da Equipa 2 (Fora)
        equipas_consolidadas[eq2]["Jogos"] += 1
        equipas_consolidadas[eq2]["Golos Marcados"] += golos_eq2
        equipas_consolidadas[eq2]["Golos Sofridos"] += golos_eq1
        if sc:
            equipas_consolidadas[eq2]["Remates Totais"] += sc["remates_totais"][1]
            equipas_consolidadas[eq2]["Cantos"] += sc["cantos"][1]

        # Distribuir os resultados desportivos (Vitória/Empate/Derrota)
        if golos_eq1 > golos_eq2:
            equipas_consolidadas[eq1]["Vitórias"] += 1
            equipas_consolidadas[eq2]["Derrotas"] += 1
        elif golos_eq1 < golos_eq2:
            equipas_consolidadas[eq2]["Vitórias"] += 1
            equipas_consolidadas[eq1]["Derrotas"] += 1
        else:
            equipas_consolidadas[eq1]["Empates"] += 1
            equipas_consolidadas[eq2]["Empates"] += 1

    # Construir a estrutura de lista final estruturada para exibição no Streamlit DataFrame
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

    # Ordenação canónica: Pontos -> Diferença de Golos -> Golos Marcados
    return sorted(tabela_final, key=lambda x: (x["P"], x["DG"], x["GM"]), reverse=True)