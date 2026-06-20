import json
import os

def inicializar_torneio():
    caminho_json = r"C:\Users\MarcoSil\OneDrive - QFree\Documents\Estudo\POS\DataAnalysis\dados_mundial.json"

    # Calendário fixo de 3 jornadas para simularmos à vez
    calendario_jogos = [
        {"id_jogo": "JOGO-01", "fase": "Jornada 1", "equipas": ["Portugal", "França"]},
        {"id_jogo": "JOGO-02", "fase": "Jornada 1", "equipas": ["Brasil", "Argentina"]},
        {"id_jogo": "JOGO-03", "fase": "Jornada 2", "equipas": ["Portugal", "Argentina"]},
        {"id_jogo": "JOGO-04", "fase": "Jornada 2", "equipas": ["Brasil", "França"]},
        {"id_jogo": "JOGO-05", "fase": "Jornada 3", "equipas": ["Uruguai", "Portugal"]},
        {"id_jogo": "JOGO-06", "fase": "Jornada 3", "equipas": ["França", "Argentina"]}
    ]

    estrutura_inicial = {
        "campeonato": "Mundial de Futebol 2026 - Simulação Dinâmica",
        "proximo_jogo_index": 0, # Indica qual é o próximo jogo a ser simulado
        "jogos_calendario": calendario_jogos,
        "jogos": [] # Começa vazio e vai recebendo os jogos simulados um a um
    }

    with open(caminho_json, 'w', encoding='utf-8') as f:
        json.dump(estrutura_inicial, f, indent=2, ensure_ascii=False)
    
    print("[SUCESSO] Torneio inicializado! Pronto para simular jogo a jogo no Dashboard.")

if __name__ == "__main__":
    inicializar_torneio()