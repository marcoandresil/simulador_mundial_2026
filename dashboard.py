import streamlit as st
import plotly.express as px
import json
import random
import os
import itertools
import pandas as pd
from data_parser import carregar_dados_mundial, carregar_estatisticas_equipas
from stats import calcular_pontuacao_jogador

# Configuração da página Web do Streamlit
st.set_page_config(page_title="Simulador Mundial 2026", layout="wide")

caminho_json = os.path.join(os.path.dirname(__file__), "dados_mundial.json")

# Pool global de jogadores por seleção
pool_jogadores = {
    "Portugal": [{"nome": "Cristiano Ronaldo", "posicao": "Avançado"}, {"nome": "Bruno Fernandes", "posicao": "Médio"}, {"nome": "Rúben Dias", "posicao": "Defesa"}],
    "França": [{"nome": "Kylian Mbappé", "posicao": "Avançado"}, {"nome": "Antoine Griezmann", "posicao": "Médio"}, {"nome": "William Saliba", "posicao": "Defesa"}],
    "Espanha": [{"nome": "Lamine Yamal", "posicao": "Avançado"}, {"nome": "Rodri", "posicao": "Médio"}, {"nome": "Dani Carvajal", "posicao": "Defesa"}],
    "Inglaterra": [{"nome": "Harry Kane", "posicao": "Avançado"}, {"nome": "Jude Bellingham", "posicao": "Médio"}, {"nome": "John Stones", "posicao": "Defesa"}],
    "Brasil": [{"nome": "Vinícius Jr", "posicao": "Avançado"}, {"nome": "Lucas Paquetá", "posicao": "Médio"}, {"nome": "Marquinhos", "posicao": "Defesa"}],
    "Argentina": [{"nome": "Lionel Messi", "posicao": "Avançado"}, {"nome": "Alexis Mac Allister", "posicao": "Médio"}, {"nome": "Cristian Romero", "posicao": "Defesa"}],
    "Uruguai": [{"nome": "Darwin Núñez", "posicao": "Avançado"}, {"nome": "Federico Valverde", "posicao": "Médio"}, {"nome": "Ronald Araújo", "posicao": "Defesa"}],
    "Alemanha": [{"nome": "Florian Wirtz", "posicao": "Avançado"}, {"nome": "Jamal Musiala", "posicao": "Médio"}, {"nome": "Antonio Rüdiger", "posicao": "Defesa"}]
}

# CORREÇÃO DEFINITIVA: Dicionário limpo apenas com emojis de texto puro para evitar erros de encoding no HTML
bandeiras = {
    "Portugal": "🇵🇹", 
    "França": "🇫🇷", 
    "Espanha": "🇪🇸", 
    "Inglaterra": "🏴",
    "Brasil": "🇧🇷", 
    "Argentina": "🇦🇷", 
    "Uruguai": "🇺🇺", 
    "Alemanha": "🇩🇪"
}

def simular_metricas_jogador(nome, posicao, equipa):
    is_avancado = posicao == "Avançado"
    is_defesa = posicao == "Defesa"
    
    # MELHORIA: Ajuste de pesos para garantir mais golos no torneio e menos 0-0
    if is_avancado:
        golos = random.choices([0, 1, 2, 3], weights=[45, 43, 10, 2])[0]
    elif posicao == "Médio":
        golos = random.choices([0, 1, 2], weights=[75, 22, 3])[0]
    else:
        golos = random.choices([0, 1], weights=[95, 5])[0]
        
    assist = random.choices([0, 1, 2], weights=[75, 22, 3])[0]
    cortes = random.randint(1, 4) if is_defesa else random.randint(0, 1)
    passes_t = random.randint(35, 65)
    passes_c = int(passes_t * random.uniform(0.60, 0.80))
    
    # --- NOVAS MÉTRICAS INDIVIDUAIS RICAS PARA ANÁLISE DE DADOS ---
    if is_avancado:
        rem_totais = random.randint(1, 6)
    elif posicao == "Médio":
        rem_totais = random.randint(0, 3)
    else:
        rem_totais = random.choices([0, 1], weights=[90, 10])[0]
        
    rem_baliza = min(rem_totais, random.randint(0, 3) if is_avancado else random.randint(0, 1))
    
    if is_defesa:
        # Posição defensiva tem mais interceções e alívios
        intercep = random.randint(0, 4)
        alivios = random.randint(1, 6)
    elif posicao == "Médio":
        intercep = random.randint(0, 3)
        alivios = random.randint(0, 2)
    else:
        intercep = random.choices([0, 1], weights=[80, 20])[0]
        alivios = random.choices([0, 1], weights=[90, 10])[0]
        
    p_decisivos = random.randint(0, 4) if posicao == "Médio" else random.randint(0, 2)
    
    faltas_cometidas = random.randint(0, 3) if is_defesa or posicao == "Médio" else random.randint(0, 1)

    return {
        "nome": nome, "posicao": posicao, "equipa": equipa, "minutos_jogados": 90,
        "golos": golos, "assistencias": assist, "cortes_ganhos": cortes,
        "passes": {"completos": passes_c, "totais": passes_t},
        "duelos": {"solo_ganhos": random.randint(1, 3), "solo_totais": random.randint(6, 10), "aereos_ganhos": random.randint(0, 2), "aereos_totais": random.randint(4, 7)},
        
        # INCLUSÃO DAS NOVAS MÉTRICAS RICAS
        "remates_totais": rem_totais,
        "remates_baliza": rem_baliza,
        "passes_decisivos": p_decisivos,
        "intercecoes": intercep,
        "alivios": alivios,
        "faltas_cometidas": faltas_cometidas
    }

# --- CONTROLADOR CENTRAL DE ARRANQUE ---
if "inicializado" not in st.session_state:
    selecoes = list(pool_jogadores.keys())
    random.shuffle(selecoes)
    grupo_a = selecoes[:4]
    grupo_b = selecoes[4:]
    
    st.session_state["definicao_grupos"] = {"Grupo A": grupo_a, "Grupo B": grupo_b}
    
    # Gerar todas as combinações de jogos para cada grupo
    comb_a = list(itertools.combinations(grupo_a, 2))
    comb_b = list(itertools.combinations(grupo_b, 2))
    
    # CORREÇÃO: Intercalar os jogos sequencialmente (A1, B1, A2, B2...)
    jogos_fase_grupos = []
    for idx in range(6):  # Cada grupo de 4 equipas gera exatamente 6 jogos
        # Jogo do Grupo A
        confronto_a = comb_a[idx]
        jogos_fase_grupos.append({
            "id_jogo": f"GA_{idx+1}", 
            "fase": f"Grupo A - Jogo {idx+1}", 
            "equipas": list(confronto_a)
        })
        # Jogo do Grupo B
        confronto_b = comb_b[idx]
        jogos_fase_grupos.append({
            "id_jogo": f"GB_{idx+1}", 
            "fase": f"Grupo B - Jogo {idx+1}", 
            "equipas": list(confronto_b)
        })
    
    dados_raiz = {"proximo_jogo_index": 0, "jogos_calendario": jogos_fase_grupos, "jogos": []}
    with open(caminho_json, 'w', encoding='utf-8') as f:
        json.dump(dados_raiz, f, indent=2, ensure_ascii=False)
    st.session_state["inicializado"] = True

with open(caminho_json, 'r', encoding='utf-8') as f:
    dados_raiz = json.load(f)

definicao_grupos = st.session_state["definicao_grupos"]
idx_proximo = dados_raiz.get("proximo_jogo_index", 0)
calendario = dados_raiz.get("jogos_calendario", [])
dados_equipas = obter_classificacao_com_zeros(dados_raiz, definicao_grupos)

# --- LAYOUT CENTRADO ---
margem_esq, centro, margem_dir = st.columns([1, 4, 1])

with centro:
    st.title("⚽ Central de Simulação: Grupos Aleatórios Pro")

    # --- ENQUADRAMENTO ACADÉMICO NO INÍCIO ---
    st.markdown(
        """
        <div style="background-color: #f8f9fa; padding: 12px 20px; border-radius: 8px; border-left: 5px solid #0c2340; margin-bottom: 25px; font-family: sans-serif;">
            <p style="margin: 0; font-size: 14px; color: #555; font-weight: 500;">📊 <b>Desenvolvido como projeto prático aplicado a Data Analysis</b></p>
            <p style="margin: 3px 0 0 0; font-size: 13px; color: #777;">🛡️ PGCibersegurança — Pós-Graduação em Cibersegurança | Universidade Lusófona</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    if "ultimo_resultado_html" in st.session_state:
        st.markdown(st.session_state["ultimo_resultado_html"], unsafe_allow_html=True)

    # --- LÓGICA DE PLAYOFFS DINÂMICOS ---
    if idx_proximo == 12 and len(calendario) == 12 and dados_equipas:
        tabela_A_ord = sorted([e for e in dados_equipas if e["Equipa"] in definicao_grupos["Grupo A"]], key=lambda x: (x["P"], x["DG"], x["GM"]), reverse=True)
        tabela_B_ord = sorted([e for e in dados_equipas if e["Equipa"] in definicao_grupos["Grupo B"]], key=lambda x: (x["P"], x["DG"], x["GM"]), reverse=True)
        
        if len(tabela_A_ord) >= 2 and len(tabela_B_ord) >= 2:
            eq1_A, eq2_A = tabela_A_ord[0]["Equipa"], tabela_A_ord[1]["Equipa"]
            eq1_B, eq2_B = tabela_B_ord[0]["Equipa"], tabela_B_ord[1]["Equipa"]
            
            calendario.append({ "id_jogo": "M1", "fase": "Meia-Final 1", "equipas": [eq1_A, eq2_B] })
            calendario.append({ "id_jogo": "M2", "fase": "Meia-Final 2", "equipas": [eq1_B, eq2_A] })
            
            dados_raiz["jogos_calendario"] = calendario
            with open(caminho_json, 'w', encoding='utf-8') as f:
                json.dump(dados_raiz, f, indent=2, ensure_ascii=False)
            st.rerun()

    if idx_proximo == 14 and len(calendario) == 14:
        jogos_realizados = dados_raiz.get("jogos", [])
        m1_jogo = next(j for j in jogos_realizados if j["id_jogo"] == "M1")
        m2_jogo = next(j for j in jogos_realizados if j["id_jogo"] == "M2")
        g1_m1, g2_m1 = map(int, m1_jogo["resultado"].split("-"))
        g1_m2, g2_m2 = map(int, m2_jogo["resultado"].split("-"))
        venc_m1 = m1_jogo["equipas"][0] if g1_m1 >= g2_m1 else m1_jogo["equipas"][1]
        venc_m2 = m2_jogo["equipas"][0] if g1_m2 >= g2_m2 else m2_jogo["equipas"][1]
        
        calendario.append({ "id_jogo": "F1", "fase": "Grande Final", "equipas": [venc_m1, venc_m2] })
        dados_raiz["jogos_calendario"] = calendario
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(dados_raiz, f, indent=2, ensure_ascii=False)
        st.rerun()

    # --- CONTROLO DO BOTÃO DE SIMULAÇÃO ---
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
        
        if st.button("⚡ Simular Jogo e Processar Stats"):
            eq1, eq2 = jogo_atual['equipas'][0], jogo_atual['equipas'][1]
            stats_j1 = [simular_metricas_jogador(j["nome"], j["posicao"], eq1) for j in pool_jogadores.get(eq1, [])]
            stats_j2 = [simular_metricas_jogador(j["nome"], j["posicao"], eq2) for j in pool_jogadores.get(eq2, [])]
            
            t_g1 = sum(p["golos"] for p in stats_j1)
            t_g2 = sum(p["golos"] for p in stats_j2)
            
            # CORREÇÃO DO BUG: Atribuir o golo de desempate dos Playoffs a um jogador real
            if idx_proximo >= 12 and t_g1 == t_g2:
                if random.choice([True, False]):
                    t_g1 += 1
                    # Escolhe um jogador de ataque/médio da equipa 1 para dar o golo
                    jogador_sortudo = random.choice([p for p in stats_j1 if p["posicao"] in ["Avançado", "Médio"]])
                    jogador_sortudo["golos"] += 1
                else:
                    t_g2 += 1
                    # Escolhe um jogador de ataque/médio da equipa 2 para dar o golo
                    jogador_sortudo = random.choice([p for p in stats_j2 if p["posicao"] in ["Avançado", "Médio"]])
                    jogador_sortudo["golos"] += 1
                
            res_final = f"{t_g1}-{t_g2}"
            
            marcadores_eq1 = [f"⚽ {p['nome']}" for p in stats_j1 for _ in range(p["golos"])]
            marcadores_eq2 = [f"⚽ {p['nome']}" for p in stats_j2 for _ in range(p["golos"])]
            
            html_marcadores_eq1 = f"<div style='font-size:12px; color:#555;'>{', '.join(marcadores_eq1)}</div>" if marcadores_eq1 else "<div style='font-size:12px; color:#aaa; font-style:italic;'>Sem golos</div>"
            html_marcadores_eq2 = f"<div style='font-size:12px; color:#555;'>{', '.join(marcadores_eq2)}</div>" if marcadores_eq2 else "<div style='font-size:12px; color:#aaa; font-style:italic;'>Sem golos</div>"
            
            # REMOVIDO: Limpeza de bandeiras no resultado final
            st.session_state["ultimo_resultado_html"] = f"""
            <div style="background-color: #fff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); padding: 16px; margin-bottom: 25px; font-family: sans-serif;">
                <div style="text-align: center; font-size: 11px; font-weight: bold; text-transform: uppercase; color: #718096; letter-spacing: 0.05em; margin-bottom: 8px;">📢 Resultado da Partida — {jogo_atual['fase']}</div>
                <div style="display: flex; align-items: center; justify-content: space-between; max-width: 500px; margin: 0 auto; padding: 5px 0;">
                    <div style="flex: 1; text-align: right; padding-right: 15px;">
                        <span style="font-size: 16px; font-weight: bold; color: #1a202c;">{eq1}</span>
                        {html_marcadores_eq1}
                    </div>
                    <div style="background-color: #1a202c; color: #fff; font-size: 20px; font-weight: bold; padding: 6px 16px; border-radius: 6px; letter-spacing: 2px; text-align: center; min-width: 80px;">
                        {res_final}
                    </div>
                    <div style="flex: 1; text-align: left; padding-left: 15px;">
                        <span style="font-size: 16px; font-weight: bold; color: #1a202c;">{eq2}</span>
                        {html_marcadores_eq2}
                    </div>
                </div>
            </div>
            """
            
            p_comp1, p_tot1 = random.randint(400, 600), random.randint(600, 700)
            p_comp2, p_tot2 = random.randint(100, 300), random.randint(300, 450)

            stats_coletivas = {
                "xg": [round(t_g1 * random.uniform(0.6, 0.9) + 0.17, 2), round(t_g2 * random.uniform(0.6, 0.9) + 0.13, 2)],
                "posse": random.choice([[79, 21], [65, 35], [55, 45]]),
                "remates_totais": [random.randint(15, 32), random.randint(5, 12)],
                "remates_baliza": [t_g1 + random.randint(2, 5), t_g2 + random.randint(0, 2)],
                "grandes_oportunidades": [t_g1 + random.randint(0, 2), t_g2], 
                "cantos": [random.randint(6, 14), random.randint(0, 4)],
                "passes_detalhe": [[p_comp1, p_tot1], [p_comp2, p_tot2]], 
                "amarelos": [random.randint(0, 2), random.randint(0, 3)],
                "vermelhos": [random.choices([0, 1], weights=[90, 10])[0], random.choices([0, 1], weights=[90, 10])[0]]
            }
            
            dados_raiz["jogos"].append({
                "id_jogo": jogo_atual["id_jogo"], "fase": jogo_atual["fase"], "equipas": [eq1, eq2], "resultado": res_final,
                "estatisticas_coletivas": stats_coletivas, "estatisticas_jogadores": stats_j1 + stats_j2
            })
            dados_raiz["proximo_jogo_index"] += 1
            with open(caminho_json, 'w', encoding='utf-8') as f:
                json.dump(dados_raiz, f, indent=2, ensure_ascii=False)
            st.rerun()
    else:
        st.success("🏆 O Torneio terminou! Temos um Campeão Mundial!")
        if st.button("🔄 Sorteador Pro: Novo Torneio e Grupos Sequenciais"):
            if "inicializado" in st.session_state: del st.session_state["inicializado"]
            if "ultimo_resultado_html" in st.session_state: del st.session_state["ultimo_resultado_html"]
            st.rerun()

    st.markdown("---")

    # --- LEITURA DAS FONTES DE DADOS ---
    dados_jogadores = carregar_dados_mundial(caminho_json)

    # --- LISTAGEM DAS ABAS ---
    aba_geral, aba_jogos = st.tabs(["📊 Tabelas Classificativas & Rankings", "📜 Histórico de Jogos"])

    with aba_geral:
        st.header("🏆 Classificação da Fase de Grupos")
        if dados_equipas:
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("🔹 Grupo A")
                df_A = [e for e in dados_equipas if e["Equipa"] in definicao_grupos["Grupo A"]]
                df_A = sorted(df_A, key=lambda x: (x["P"], x["DG"], x["GM"]), reverse=True)
                st.dataframe(pd.DataFrame(df_A), width="stretch", hide_index=True)
            with col_b:
                st.subheader("🔸 Grupo B")
                df_B = [e for e in dados_equipas if e["Equipa"] in definicao_grupos["Grupo B"]]
                df_B = sorted(df_B, key=lambda x: (x["P"], x["DG"], x["GM"]), reverse=True)
                st.dataframe(pd.DataFrame(df_B), width="stretch", hide_index=True)

        st.markdown("---")
        
        col_g1, col_g2 = st.columns([1.2, 0.8])
        with col_g1:
            st.header("🏅 Melhores Marcadores & Rankings")
            criterio = st.selectbox("Filtrar e ordenar métricas por:", ["Mais Golos", "Nota Média", "Mais Assistências"])
            
            ranking = []
            if dados_jogadores:
                for nome, stats in dados_jogadores.items():
                    ranking.append({
                        "Jogador": nome, "Seleção": stats.get("equipa", "Desconhecida"), "Nota Média": calcular_pontuacao_jogador(stats),
                        "Golos": stats.get("golos", 0), "Assistências": stats.get("assistencias", 0)
                    })
            
            if ranking:
                if criterio == "Mais Golos": ranking = sorted(ranking, key=lambda x: (x["Golos"], x["Nota Média"]), reverse=True); m_k = "Golos"; l_m = "Golos"
                elif criterio == "Mais Assistências": ranking = sorted(ranking, key=lambda x: (x["Assistências"], x["Nota Média"]), reverse=True); m_k = "Assistências"; l_m = "Assists"
                else: ranking = sorted(ranking, key=lambda x: x["Nota Média"], reverse=True); m_k = "Nota Média"; l_m = "Rating"

                # REMOVIDO: Tabela HTML sem qualquer tag ou referência a bandeiras
                html_tabela = '<div style="font-family: sans-serif; background-color: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; margin-top: 10px;">'
                for index, jog in enumerate(ranking[:10]):
                    pos = index + 1
                    selecao_nome = jog['Seleção']
                    v_e = f"{jog[m_k]}" if m_k != "Nota Média" else f"{jog[m_k]:.1f}"
                    
                    html_tabela += f'<div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border-bottom: 1px solid #f0f0f0;"><div style="display: flex; align-items: center; gap: 12px;"><span style="font-weight: bold; font-size: 14px; color: #7f8c8d; width: 20px; text-align: center;">{pos}</span><div style="width: 36px; height: 36px; background-color: #f0f2f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #475569;">{jog["Jogador"][0]}</div><div><span style="font-size: 15px; font-weight: 600; color: #1e293b;">{jog["Jogador"]}</span><div style="font-size: 12px; color: #64748b; margin-top: 2px;">{selecao_nome}</div></div></div><div><span style="font-size: 18px; font-weight: bold; color: #0c2340;">{v_e}</span> <span style="font-size: 11px; color: #94a3b8;">{l_m}</span></div></div>'
                html_tabela += "</div>"
                st.markdown(html_tabela, unsafe_allow_html=True)
            else:
                st.info("Aguardando golos e jogos para popular o ranking de jogadores.")

        with col_g2:
            st.header("👤 Detalhes do Jogador")
            if dados_jogadores:
                j_sel = st.selectbox("Escolha o jogador:", list(dados_jogadores.keys()))
                if _stats := dados_jogadores.get(j_sel):
                    st.metric(label=f"Rating de {j_sel}", value=f"{calcular_pontuacao_jogador(_stats)} / 10.0", delta=f"{_stats['jogos_disputados']} jogos")
                    m_v = {"Golos": _stats["golos"], "Assistências": _stats["assistencias"], "Cortes": _stats["cortes_ganhos"]}
                    st.plotly_chart(px.bar(x=list(m_v.keys()), y=list(m_v.values()), title="Ações Acumuladas"), width="stretch")
            else:
                st.info("Estatísticas individuais disponíveis após o primeiro jogo.")

    with aba_jogos:
        lista_r = dados_raiz.get("jogos", [])
        if not lista_r: 
            st.info("Nenhum jogo realizado até ao momento.")
        else:
            opc = {f"{j['fase']}: {j['equipas'][0]} {j['resultado']} {j['equipas'][1]}": j for j in lista_r}
            j_e = st.selectbox("Selecione a partida para ver os detalhes:", list(opc.keys()))
            j_d = opc[j_e]
            
            eq1, eq2 = j_d['equipas'][0], j_d['equipas'][1]
            st.markdown(f"### 🏟️ {eq1} vs {eq2}")
            st.caption(f"Fase do Torneio: {j_d['fase']} | Resultado Final: **{j_d['resultado']}**")
            
            sc = j_d.get("estatisticas_coletivas", {})
            if sc:
                st.markdown("#### **Principais**")
                
                def renderizar_barra_sofascore(label, val1, val2, txt1=None, txt2=None):
                    v1, v2 = float(val1), float(val2)
                    total = v1 + v2 if (v1 + v2) > 0 else 1
                    pct1, pct2 = (v1 / total) * 100, (v2 / total) * 100
                    
                    t1 = str(val1) if txt1 is None else txt1
                    t2 = str(val2) if txt2 is None else txt2
                    
                    cor1 = "#ff4b4b" if v1 >= v2 else "#1e293b"
                    cor2 = "#ff4b4b" if v2 >= v1 else "#1e293b"

                    st.markdown(f"""
                    <div style="font-family: sans-serif; margin-bottom: 12px; width: 100%; max-width: 600px; margin: 0 auto; padding: 6px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; font-size: 14px;">
                            <div style="font-weight: bold; color: #1e293b; min-width: 50px; text-align: left;">{t1}</div>
                            <div style="font-weight: 600; color: #475569; text-align: center;">{label}</div>
                            <div style="font-weight: bold; color: #1e293b; min-width: 50px; text-align: right;">{t2}</div>
                        </div>
                        <div style="display: flex; width: 100%; height: 6px; background-color: #f1f5f9; border-radius: 3px; overflow: hidden;">
                            <div style="width: 50%; display: flex; justify-content: flex-end; border-right: 2px solid #fff;">
                                <div style="width: {pct1}%; height: 100%; background-color: {cor1}; border-radius: 3px 0 0 3px;"></div>
                            </div>
                            <div style="width: 50%; display: flex; justify-content: flex-start; border-left: 2px solid #fff;">
                                <div style="width: {pct2}%; height: 100%; background-color: {cor2}; border-radius: 0 3px 3px 0;"></div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                xg1, xg2 = sc.get("xg", [0.0, 0.0])[0], sc.get("xg", [0.0, 0.0])[1]
                pos1, pos2 = sc.get("posse", [50, 50])[0], sc.get("posse", [50, 50])[1]
                rem1, rem2 = sc.get("remates_totais", [0, 0])[0], sc.get("remates_totais", [0, 0])[1]
                bal1, bal2 = sc.get("remates_baliza", [0, 0])[0], sc.get("remates_baliza", [0, 0])[1]
                opp1, opp2 = sc.get("grandes_oportunidades", [0, 0])[0], sc.get("grandes_oportunidades", [0, 0])[1]
                cnt1, cnt2 = sc.get("cantos", [0, 0])[0], sc.get("cantos", [0, 0])[1]
                
                p_det = sc.get("passes_detalhe", [[0,0], [0,0]])
                pct_p1 = int((p_det[0][0] / p_det[0][1] * 100) if p_det[0][1] > 0 else 0)
                pct_p2 = int((p_det[1][0] / p_det[1][1] * 100) if p_det[1][1] > 0 else 0)
                
                txt_passes1 = f"{pct_p1}% <span style='font-size:10px; color:#94a3b8;'>({p_det[0][0]}/{p_det[0][1]})</span>"
                txt_passes2 = f"{pct_p2}% <span style='font-size:10px; color:#94a3b8;'>({p_det[1][0]}/{p_det[1][1]})</span>"
                
                yel1, yel2 = sc.get("amarelos", [0, 0])[0], sc.get("amarelos", [0, 0])[1]
                red1, red2 = sc.get("vermelhos", [0, 0])[0], sc.get("vermelhos",http://googleusercontent.com/image_generation_content/2