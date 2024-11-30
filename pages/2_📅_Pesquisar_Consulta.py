import streamlit as st
import plotly.express as px
import pandas as pd
import os

st.set_page_config(page_title="Pesquisar Consulta", page_icon=":calendar:")

st.title(":calendar: Pesquisar Consulta")

st.write("""
    Pesquisa por uma data no menu a esquerda.
""")


df_path = os.path.join(os.getcwd(), "data", "iot_metrics.csv")
df_discomfort = pd.read_csv(df_path, sep=",", encoding="utf-8", quotechar='"')
df_discomfort["created_date"] = pd.to_datetime(df_discomfort["created_date"])
df_discomfort["created_date_formated"] = df_discomfort["created_date"].dt.strftime('%d/%m/%Y')

if len(df_discomfort) < 3:
    st.warning("Não há dados suficientes para exibir a análise.")
    st.stop()  

st.sidebar.title("Selecionar Data")
selected_date = st.sidebar.date_input(
    "Selecione a data:",
    value=pd.Timestamp.now().date()
)
pd.options.mode.copy_on_write = True
selected_date_formated = selected_date.strftime('%d/%m/%Y')
df_discomfort_filtered = df_discomfort[df_discomfort["created_date"].dt.date == selected_date]
df_discomfort_filtered["progress"] = df_discomfort_filtered["discomfort"].round(2).astype("float32")
new_order = ["created_date_formated", "session", "discomfort", "progress", "created_date"]
df_discomfort_filtered = df_discomfort_filtered[new_order]

if df_discomfort_filtered.empty:
    st.warning(f"Sem dados para a data {selected_date_formated}.")
    st.stop()  

st.markdown(f":point_right: Data selecionada: **{selected_date_formated}**")

st.write(f"## :eight_spoked_asterisk: Dados coletados")
st.write("""
    Visualização de métricas e progresso.
""")

col1_dados_coletados, col2_dados_coletados = st.columns([2, 1.5])

col1_dados_coletados.data_editor(
    df_discomfort_filtered.drop(columns=["created_date"]),
    column_config={
        "progress": st.column_config.ProgressColumn(
            "Progresso Geral",
            help="Melhora por consulta",
            format=" ",
            min_value=0.0,
            max_value=5.0
        ),
        "session": st.column_config.Column(
            "Sessão",
            help="Número da sessão"
        ),
        "created_date_formated": st.column_config.Column(
            "Data",
            help="Data da medição",
        ),
        "discomfort": st.column_config.Column(
            "Métrica",
            help="Métrica de desconforto",
        ),
    },
    hide_index=True,
    disabled=True
)

progress_mean = df_discomfort_filtered["progress"].mean()
progress_mean_normalized = (progress_mean / 5.0) * 100

col2_dados_coletados.metric("Situação atual", f"{progress_mean:.2f}")
col2_dados_coletados.markdown(f"""
    <div style="width: 40%; background-color: #92D2AE; border-radius: 10px; height: 10px;">
        <div style="
            width: {progress_mean_normalized}%; 
            background-color: #2C6E49; 
            height: 100%; 
            border-radius: 10px;">
        </div>
    </div>
""", unsafe_allow_html=True)

st.write(f"## :eight_spoked_asterisk: Fazer download")
st.write("""
    Se desejar, faça o download dos dados coletados.
""")

column_mapping = {
    "session": "Sessão",
    "created_date_formated": "Data"
}

reverse_mapping = {v: k for k, v in column_mapping.items()}

selected_columns = st.multiselect(
    "Escolher campos para acompanhar os dados de progresso:", 
    options=list(column_mapping.values()),
    default=list(column_mapping.values())
)

real_columns = [reverse_mapping[col] for col in selected_columns]
real_columns.append("progress")

rename_columns = {"progress": "Progresso"}
rename_columns.update(column_mapping)

df_discomfort_download = df_discomfort_filtered[real_columns]
df_discomfort_download = df_discomfort_download.rename(columns=rename_columns)

csv = df_discomfort_download.to_csv(index=False).encode('utf-8')

st.markdown("")

col1_download, col2_download = st.columns([1, 4])
st.write("##### :arrow_down: Baixar arquivo")

st.download_button(
    label="Download",
    data=csv,
    file_name=f"metricas_{selected_date.strftime('%d%m%Y')}.csv",
    mime="text/csv"
)