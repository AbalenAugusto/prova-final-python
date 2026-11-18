import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Painel IQVU - Belo Horizonte", layout="wide")

# ==============================================================================
# 1. CARREGAR OS DADOS  (TROQUE SÓ O NOME DO ARQUIVO)
# ==============================================================================
ARQUIVO = "bd_iqvu_1994_2016.csv"   # <<< nome EXATO do arquivo que está no GitHub (ex: "iqvu.csv" ou "iqvu.xlsx")

df = pd.read_csv("bd_iqvu_1994_2016.csv", sep=";", encoding="latin-1",
decimal=",")
df.columns = df.columns.str.replace("\ufeff", "", regex=False).str.strip()



# Garante que IQVU e ANO são números (caso venham como texto com vírgula)
for col in ["IQVU", "ANO", "Educacao", "Saude", "Habitacao", "Infraestrutura", "Cultura"]:
    if col in df.columns and df[col].dtype == object:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors="coerce")

# ==============================================================================
# 2. FILTRO (TROQUE OS BAIRROS / SÉRIE SE A PROVA PEDIR OUTROS)
# ==============================================================================
BAIRRO_1 = "Taquaril"
BAIRRO_2 = "Santa Ines"
COR_1 = "#FF6B6B"
COR_2 = "#00F5D4"
CORES = {BAIRRO_1: COR_1, BAIRRO_2: COR_2}

df_filtrado = df[
    (df["NOMEUP"].isin([BAIRRO_1, BAIRRO_2])) &
    (df["ï»¿SERIE"] == "SERIE HISTORICA")
].copy()

df_tabela = df_filtrado[["NOMEUP", "ANO", "IQVU"]]

# ==============================================================================
# 3. TÍTULO E BARRA LATERAL
# ==============================================================================
st.title(f"Painel Streamlit do IQVU de Belo Horizonte — {BAIRRO_1} e {BAIRRO_2}")

st.sidebar.header("Controles")
opcao = st.sidebar.radio("Selecione a visualização:", ["Tabela", "Gráficos"])

# ==============================================================================
# 4. TABELA OU GRÁFICOS
# ==============================================================================
if opcao == "Tabela":
    st.header("Tabela do IQVU (Série Histórica)")
    st.dataframe(df_tabela, use_container_width=True, hide_index=True)

elif opcao == "Gráficos":
    st.header(f"Gráficos do IQVU — {BAIRRO_1} e {BAIRRO_2}")

    # ---------- 1. LINHA — BAIRRO 1 ----------
    st.subheader(f"1. Gráfico de Linha — {BAIRRO_1}")
    df_b1 = df_tabela[df_tabela["NOMEUP"] == BAIRRO_1]
    fig1 = px.line(df_b1, x="ANO", y="IQVU", markers=True,
                   title=f"Evolução do IQVU — {BAIRRO_1}", template="plotly_dark")
    fig1.update_traces(line_color=COR_1, line_width=3, marker_size=8)
    fig1.update_xaxes(type="category")
    st.plotly_chart(fig1, use_container_width=True)

    # ---------- 2. LINHA — BAIRRO 2 ----------
    st.subheader(f"2. Gráfico de Linha — {BAIRRO_2}")
    df_b2 = df_tabela[df_tabela["NOMEUP"] == BAIRRO_2]
    fig2 = px.line(df_b2, x="ANO", y="IQVU", markers=True,
                   title=f"Evolução do IQVU — {BAIRRO_2}", template="plotly_dark")
    fig2.update_traces(line_color=COR_2, line_width=3, marker_size=8)
    fig2.update_xaxes(type="category")
    st.plotly_chart(fig2, use_container_width=True)

    # ---------- 3. BARRAS AGRUPADAS ----------
    st.subheader("3. Gráfico de Barras Agrupadas")
    fig3 = px.bar(df_tabela, x="ANO", y="IQVU", color="NOMEUP", barmode="group",
                  title="Comparativo Anual de IQVU (Barras Agrupadas)",
                  color_discrete_map=CORES, template="plotly_dark")
    fig3.update_xaxes(type="category")
    st.plotly_chart(fig3, use_container_width=True)

    # ---------- 4. BARRAS EMPILHADAS (dimensões do último ano) ----------
    st.subheader("4. Gráfico de Barras Empilhadas")
    dimensoes = [c for c in ["Educacao", "Saude", "Habitacao", "Infraestrutura", "Cultura"] if c in df_filtrado.columns]
    ultimo_ano = df_filtrado["ANO"].max()
    dados_empilhado = df_filtrado[df_filtrado["ANO"] == ultimo_ano].melt(
        id_vars="NOMEUP", value_vars=dimensoes, var_name="Dimensao", value_name="Valor"
    ).rename(columns={"NOMEUP": "Bairro"})
    fig4 = px.bar(dados_empilhado, x="Bairro", y="Valor", color="Dimensao", barmode="stack",
                  title=f"Composição do IQVU por Dimensão — {ultimo_ano} (Barras Empilhadas)",
                  template="plotly_dark")
    st.plotly_chart(fig4, use_container_width=True)

    # ---------- 5. PIZZA (último ano) ----------
    st.subheader("5. Gráfico de Pizza")
    dados_pizza = df_tabela[df_tabela["ANO"] == ultimo_ano].rename(columns={"NOMEUP": "Bairro"})
    fig5 = px.pie(dados_pizza, names="Bairro", values="IQVU", color="Bairro",
                  title=f"Proporção do IQVU entre os Bairros ({ultimo_ano})",
                  color_discrete_map=CORES, template="plotly_dark")
    fig5.update_traces(textinfo="percent+label+value")
    st.plotly_chart(fig5, use_container_width=True)

    # ---------- 6. RADAR (px.line_polar) ----------
    st.subheader("6. Gráfico de Radar (px.line_polar)")
    dados_radar = dados_empilhado.rename(columns={"Valor": "Nota"})
    fig6 = px.line_polar(dados_radar, r="Nota", theta="Dimensao", color="Bairro", line_close=True,
                         title=f"Perfil Multidimensional (Radar - {ultimo_ano})",
                         color_discrete_map=CORES, template="plotly_dark")
    fig6.update_traces(fill="toself")
    fig6.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])))
    st.plotly_chart(fig6, use_container_width=True)

    # ---------- 7. ÁREA ----------
    st.subheader("7. Gráfico de Área")
    fig7 = px.area(df_tabela, x="ANO", y="IQVU", color="NOMEUP",
                   title="Evolução em Área do IQVU",
                   color_discrete_map=CORES, template="plotly_dark")
    fig7.update_xaxes(type="category")
    st.plotly_chart(fig7, use_container_width=True)

    # ---------- 8. DISPERSÃO (BOLHAS) ----------
    st.subheader("8. Gráfico de Dispersão")
    fig8 = px.scatter(df_filtrado, x="Educacao", y="Saude", color="NOMEUP", size="IQVU",
                      hover_data=["ANO"], title="Dispersão: Educação vs Saúde (Tamanho = IQVU)",
                      color_discrete_map=CORES, template="plotly_dark")
    st.plotly_chart(fig8, use_container_width=True)

    # ---------- 9. BOXPLOT ----------
    st.subheader("9. Gráfico Boxplot")
    fig9 = px.box(df_tabela, x="NOMEUP", y="IQVU", color="NOMEUP", points="all",
                  title="Distribuição Estatística do IQVU (Boxplot)",
                  color_discrete_map=CORES, template="plotly_dark")
    st.plotly_chart(fig9, use_container_width=True)

# ==============================================================================
# 5. FONTE DOS DADOS (OBRIGATÓRIA)
# ==============================================================================
st.markdown("---")
st.caption("Fonte dos dados: dados abertos da Prefeitura de Belo Horizonte — https://dados.pbh.gov.br/")
