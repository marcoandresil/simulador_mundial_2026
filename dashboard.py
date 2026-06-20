import streamlit as st
import plotly.express as px
import json
import random
import os
from data_parser import carregar_dados_mundial, carregar_estatisticas_equipas
from stats import calcular_pontuacao_jogador

# Configuração da página Web do Streamlit
st.set_page_config(page_title="Simulador Mundial 2026", layout="wide")

caminho_json = "/mnt/c/Users/MarcoSil/OneDrive - QFree/Documents/Estudo/POS/DataAnalysis/dados_mundial.json"

pool_jogadores = {
    "Portugal": [
        {"nome": "Cristiano Ronaldo", "posicao": "Avançado"},
        {"nome": "Bruno Fernandes", "posicao": "Médio"},
        {"nome": "Rafael Leão", "posicao": "Avançado"},
        {"nome": "Rúben Dias", "posicao": "Defesa"},
        {"nome": "João Cancelo", "posicao": "Defesa"}
    ],
    "França": [
        {"nome": "Kylian Mbappé", "posicao": "Avançado"},
        {"nome": "Antoine Griezmann", "posicao": "Médio"},
        {"nome": "Ousmane Dembélé", "posicao": "Avançado"},
        {"nome": "William Saliba", "posicao": "Defesa"},
        {"nome": "Theo Hernández", "posicao": "Defesa"}
    ],
    "Brasil": [
        {"nome": "Vinícius Jr", "posicao": "Avançado"},
        {"nome": "Rodrygo", "posicao": "Avançado"},
        {"nome": "Lucas Paquetá", "posicao": "Médio"},
        {"nome": "Marquinhos", "posicao": "Defesa"},
        {"nome": "Éder Militão", "posicao": "Defesa"}
    ],
    "Argentina": [
        {"nome": "Lionel Messi", "posicao": "Avançado"},
        {"nome": "Julián Álvarez", "posicao": "Avançado"},
        {"nome": "Alexis Mac Allister", "posicao": "Médio"},
        {"nome": "Cristian Romero", "posicao": "Defesa"},
        {"nome": "Nicolás Otamendi", "posicao": "Defesa"}
    ],
    "Uruguai": [
        {"nome": "Darwin Núñez", "posicao": "Avançado"},
        {"nome": "Federico Valverde", "posicao": "Médio"},
        {"nome": "Facundo Pellistri", "posicao": "Avançado"},
        {"nome": "Ronald Araújo", "posicao": "Defesa"},
        {"nome": "José Giménez", "posicao": "Defesa"}
    ]
}

def simular_metricas_jogador(nome, posicao, equipa):
    is_avancado = posicao == "Avançado"
    is_defesa = posicao == "Defesa"
    
    golos = random.choices([0, 1, 2], weights=[60, 32, 8])[0] if is_avancado else random.choices([0, 1], weights=[95, 5])[0]
    assist = random.choices([0, 1], weights=[80, 20])[0]
    cortes = random.randint(4, 7) if is_defesa else random.randint(0, 2)
    passes_t = random.randint(35, 65)
    passes_c = int(passes_t * random.uniform(0.75, 0.93))

    return {
        "nome": nome, "posicao": posicao, "equipa": equipa, "minutos_jogados": 90,
        "golos": golos, "assistencias": assist, "cortes_ganhos": cortes,
        "passes": {"completos": passes_c, "totais": passes_t},
        "duelos": {
            "solo_ganhos": random.randint(2, 5), "solo_totais": random.randint(6, 9),
            "aereos_ganhos": random.randint(1, 3), "aereos_totais": random.randint(4, 6)
        }
    }

# --- CONTROLADOR CENTRAL ---
with open(caminho_json, 'r', encoding='utf-8') as f:
    dados_raiz = json.load(f)

idx_proximo = dados_raiz.get("proximo_jogo_index", 0)
calendario = dados_raiz.get("jogos_calendario", [])

# --- LAYOUT CENTRADO ---
margem_esq, centro, margem_dir = st.columns([1, 4, 1])

with centro:
    st.title("⚽ Central de Simulação ao Vivo - Mundial 2026")

    if "ultimo_resultado" in st.session_state:
        st.info(st.session_state["ultimo_resultado"])

    # --- CONTROLO DO TORNEIO ---
    if idx_proximo < len(calendario):
        jogo_atual = calendario[idx_proximo]
        
        st.markdown(f"""
        <div style="background-color:#f0f2f6; padding:15px; border-radius:10px; margin-bottom:15px;">
            <h4 style="margin:0; color:#31333F;">Próximo Confronto Agendado:</h4>
            <p style="font-size:22px; margin:5px 0 0 0; font-weight:bold; color:#ff4b4b;">
                ⚽ {jogo_atual['equipas'][0]} vs {jogo_atual['equipas'][1]} 
                <span style="font-size:14px; font-weight:normal; color:#555;">({jogo_atual['fase']})</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⚡ Simular Próximo Jogo e Processar Stats"):
            eq1, eq2 = jogo_atual['equipas'][0], jogo_atual['equipas'][1]
            
            stats_jogadores_eq1 = [simular_metricas_jogador(j["nome"], j["posicao"], eq1) for j in pool_jogadores.get(eq1, [])]
            stats_jogadores_eq2 = [simular_metricas_jogador(j["nome"], j["posicao"], eq2) for j in pool_jogadores.get(eq2, [])]
            
            total_golos_eq1 = sum(p["golos"] for p in stats_jogadores_eq1)
            total_golos_eq2 = sum(p["golos"] for p in stats_jogadores_eq2)
            resultado_final = f"{total_golos_eq1}-{total_golos_eq2}"
            
            tot_passes_c_eq1 = sum(p["passes"]["completos"] for p in stats_jogadores_eq1)
            tot_passes_t_eq1 = sum(p["passes"]["totais"] for p in stats_jogadores_eq1)
            tot_passes_c_eq2 = sum(p["passes"]["completos"] for p in stats_jogadores_eq2)
            tot_passes_t_eq2 = sum(p["passes"]["totais"] for p in stats_jogadores_eq2)
            
            stats_coletivas = {
                "xg": [round(total_golos_eq1 * random.uniform(0.5, 0.9) + 0.15, 2), round(total_golos_eq2 * random.uniform(0.5, 0.9) + 0.15, 2)],
                "posse": random.choice([[52, 48], [45, 55], [50, 50], [58, 42], [41, 59]]),
                "remates_totais": [random.randint(8, 17), random.randint(8, 17)],
                "remates_baliza": [total_golos_eq1 + random.randint(1, 3), total_golos_eq2 + random.randint(1, 3)],
                "grandes_oportunidades": [total_golos_eq1 + random.randint(0, 1), total_golos_eq2 + random.randint(0, 1)],
                "cantos": [random.randint(2, 7), random.randint(2, 7)],
                "passes_detalhe": [[tot_passes_c_eq1, tot_passes_t_eq1], [tot_passes_c_eq2, tot_passes_t_eq2]],
                "amarelos": [random.randint(0, 3), random.randint(0, 3)]
            }
            
            novo_jogo = {
                "id_jogo": jogo_atual["id_jogo"],
                "fase": jogo_atual["fase"],
                "equipas": [eq1, eq2],
                "resultado": resultado_final,
                "estatisticas_coletivas": stats_coletivas,
                "estatisticas_jogadores": stats_jogadores_eq1 + stats_jogadores_eq2
            }
            
            dados_raiz["jogos"].append(novo_jogo)
            dados_raiz["proximo_jogo_index"] += 1
            
            with open(caminho_json, 'w', encoding='utf-8') as f:
                json.dump(dados_raiz, f, indent=2, ensure_ascii=False)
                
            st.session_state["ultimo_resultado"] = f"📢 **FIM DO JOGO!** O confronto entre **{eq1}** e **{eq2}** terminou com o resultado de **{resultado_final}**!"
            st.rerun()
    else:
        st.warning("🏆 Todos os jogos do calendário do Mundial foram simulados!")
        if st.button("🔄 Resetar Torneio"):
            dados_raiz["proximo_jogo_index"] = 0
            dados_raiz["jogos"] = []
            if "ultimo_resultado" in st.session_state:
                del st.session_state["ultimo_resultado"]
            with open(caminho_json, 'w', encoding='utf-8') as f:
                json.dump(dados_raiz, f, indent=2, ensure_ascii=False)
            st.rerun()

    st.markdown("---")

    # --- LEITURA E CONSTRUÇÃO DAS ABAS ---
    dados_jogadores = carregar_dados_mundial(caminho_json)

    if dados_jogadores:
        aba_geral, aba_jogos = st.tabs(["📊 Estatísticas Gerais & Rankings", "📜 Histórico de Jogos Realizados"])

        # ABA 1: CONSOLIDADO GERAL
        with aba_geral:
            col_g1, col_g2 = st.columns([1, 1])
            with col_g1:
                st.header("🏆 Ranking de Performance Médio")
                ranking = []
                for nome, stats in dados_jogadores.items():
                    nota = calcular_pontuacao_jogador(stats)
                    ranking.append({"Jogador": nome, "Nota Média": nota, "Jogos": stats["jogos_disputados"], "Posição": stats["posicao"]})
                
                ranking = sorted(ranking, key=lambda x: x["Nota Média"], reverse=True)
                st.dataframe(ranking, width="stretch")

            with col_g2:
                st.header("👤 Detalhes do Jogador")
                jogador_selecionado = st.selectbox("Escolha o jogador para inspecionar:", list(dados_jogadores.keys()))

                if _stats := dados_jogadores.get(jogador_selecionado):
                    nota = calcular_pontuacao_jogador(_stats)
                    st.metric(label=f"Rating Médio de {jogador_selecionado}", value=f"{nota} / 10.0", delta=f"{_stats['jogos_disputados']} jogos")

                    metricas_visuais = {
                        "Golos": _stats["golos"], "Assistências": _stats["assistencias"],
                        "Cortes": _stats["cortes_ganhos"], "Duelos Ganhos": _stats["duelos_ganhos"]
                    }
                    fig = px.bar(x=list(metricas_visuais.keys()), y=list(metricas_visuais.values()), 
                                 labels={'x': 'Métrica', 'y': 'Total Acumulado'}, title=f"Ações Acumuladas - {jogador_selecionado}",
                                 color=list(metricas_visuais.keys()), color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig, width="stretch")

        # ABA 2: HISTÓRICO SOFASCORE
        with aba_jogos:
            lista_jogos_realizados = dados_raiz.get("jogos", [])
            
            if not lista_jogos_realizados:
                st.info("Ainda não foram realizados jogos neste torneio.")
            else:
                opcoes_jogos = {f"{j['id_jogo']} - {j['equipas'][0]} {j['resultado']} {j['equipas'][1]} ({j['fase']})": j for j in lista_jogos_realizados}
                jogo_escolhido_str = st.selectbox("Selecione um jogo para ver a ficha de partida:", list(opcoes_jogos.keys()))
                
                jogo_selected_dados = opcoes_jogos[jogo_escolhido_str]
                eq1, eq2 = jogo_selected_dados['equipas'][0], jogo_selected_dados['equipas'][1]
                
                st.markdown("---")
                st.subheader(f"🏟️ Ficha de Jogo: {eq1} vs {eq2}")
                st.markdown(f"**Resultado Final:** {jogo_selected_dados['resultado']} | **Fase:** {jogo_selected_dados['fase']}")
                
                st.markdown("### 📊 Principais")
                sc = jogo_selected_dados.get("estatisticas_coletivas")
                
                def renderizar_barra_sofascore(label, val1, val2, txt1=None, txt2=None):
                    v1 = float(val1)
                    v2 = float(val2)
                    total = v1 + v2 if (v1 + v2) > 0 else 1
                    p1 = (v1 / total) * 100
                    p2 = (v2 / total) * 100
                    t1 = str(val1) if txt1 is None else txt1
                    t2 = str(val2) if txt2 is None else txt2
                    
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; font-family: sans-serif; font-size: 14px;">
                        <span style="font-weight: bold; min-width: 50px; text-align: left;">{t1}</span>
                        <span style="color: #1f1f1f; font-weight: 500;">{label}</span>
                        <span style="font-weight: bold; min-width: 50px; text-align: right;">{t2}</span>
                    </div>
                    <div style="display: flex; width: 100%; height: 8px; background-color: #e0e0e0; border-radius: 4px; margin-bottom: 15px; overflow: hidden;">
                        <div style="display: flex; justify-content: flex-end; width: 50%; height: 100%; background-color: #e0e0e0; border-right: 1px solid #fff;">
                            <div style="width: {p1}%; height: 100%; background-color: #0c2340; border-radius: 4px 0 0 4px;"></div>
                        </div>
                        <div style="display: flex; justify-content: flex-start; width: 50%; height: 100%; background-color: #e0e0e0; border-left: 1px solid #fff;">
                            <div style="width: {p2}%; height: 100%; background-color: #ff4b4b; border-radius: 0 4px 4px 0;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                col_s1, col_s2, col_s3 = st.columns([1, 3, 1])
                with col_s2:
                    renderizar_barra_sofascore("Golos esperados (xG)", sc["xg"][0], sc["xg"][1])
                    renderizar_barra_sofascore("Posse de bola", sc["posse"][0], sc["posse"][1], f"{sc['posse'][0]}%", f"{sc['posse'][1]}%")
                    renderizar_barra_sofascore("Total remates", sc["remates_totais"][0], sc["remates_totais"][1])
                    renderizar_barra_sofascore("Remates à baliza", sc["remates_baliza"][0], sc["remates_baliza"][1])
                    
                    gov1, gov2 = sc.get("grandes_oportunidades", [0, 0])[0], sc.get("grandes_oportunidades", [0, 0])[1]
                    renderizar_barra_sofascore("Grandes oportunidades", gov1, gov2)
                    renderizar_barra_sofascore("Cantos", sc["cantos"][0], sc["cantos"][1])
                    
                    p_det = sc.get("passes_detalhe", [[400, 500], [400, 500]])
                    pct1 = int((p_det[0][0] / p_det[0][1] * 100) if p_det[0][1] > 0 else 0)
                    pct2 = int((p_det[1][0] / p_det[1][1] * 100) if p_det[1][1] > 0 else 0)
                    txt_p1 = f"{pct1}%<br><span style='font-size:11px; color:#666;'>({p_det[0][0]}/{p_det[0][1]})</span>"
                    txt_p2 = f"{pct2}%<br><span style='font-size:11px; color:#666;'>({p_det[1][0]}/{p_det[1][1]})</span>"
                    renderizar_barra_sofascore("Passes", pct1, pct2, txt_p1, txt_p2)
                    
                    renderizar_barra_sofascore("Cartões amarelos", sc["amarelos"][0], sc["amarelos"][1])

                st.markdown("---")
                st.markdown("### 🏃 Performance Individual dos Jogadores")
                
                stats_da_partida = []
                for jog_match in jogo_selected_dados["estatisticas_jogadores"]:
                    duelos_g_match = jog_match["duelos"]["solo_ganhos"] + jog_match["duelos"]["aereos_ganhos"]
                    duelos_t_match = jog_match["duelos"]["solo_totais"] + jog_match["duelos"]["aereos_totais"]
                    
                    stats_fake_single = {
                        "posicao": jog_match["posicao"], "jogos_disputados": 1, "golos": jog_match["golos"],
                        "assistencias": jog_match["assistencias"], "cortes_ganhos": jog_match["cortes_ganhos"],
                        "passes_completos": jog_match["passes"]["completos"], "passes_totais": jog_match["passes"]["totais"],
                        "duelos_ganhos": duelos_g_match, "duelos_totais": duelos_t_match
                    }
                    nota_do_jogo = calcular_pontuacao_jogador(stats_fake_single)
                    
                    stats_da_partida.append({
                        "Jogador": jog_match["nome"],
                        "Seleção": jog_match["equipa"],
                        "Posição": jog_match["posicao"],
                        "Nota no Jogo": nota_do_jogo,
                        "Golos": jog_match["golos"],
                        "Assistências": jog_match["assistencias"],
                        "Cortes": jog_match["cortes_ganhos"],
                        "Passes Certos": f"{jog_match['passes']['completos']}/{jog_match['passes']['totais']}"
                    })
                
                stats_da_partida = sorted(stats_da_partida, key=lambda x: x["Nota no Jogo"], reverse=True)
                st.dataframe(stats_da_partida, width="stretch")
    else:
        st.info("Aguardando a simulação do primeiro jogo para gerar estatísticas.")

# --- RODAPÉ ACADÉMICO ---
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #777; font-size: 12px; font-family: sans-serif; padding: 10px;">
        📊 <b>Desenvolvido como projeto prático na vertente de Data Analysis</b><br>
        🛡️ PGCibersegurança — Pós-Graduação em Cibersegurança | Universidade Lusófona
    </div>
    """, 
    unsafe_allow_html=True
)