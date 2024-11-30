import streamlit as st
import plotly.express as px
import pandas as pd
import os

st.set_page_config(page_title="Visão Geral", page_icon=":hospital:")

st.title(":hospital: Visão Geral")

df_path = os.path.join(os.getcwd(), "data", "iot_metrics.csv")

df_discomfort = pd.read_csv(df_path, sep=",", encoding="utf-8", quotechar='"')

df_discomfort["created_date"] = pd.to_datetime(df_discomfort["created_date"])
df_discomfort = (
    df_discomfort
    .groupby(["session", df_discomfort["created_date"].dt.date])["discomfort"]
    .mean()
    .reset_index()
    .sort_values(by=["session", "created_date"], ascending=[True, True])

)
df_discomfort["progress"] = df_discomfort["discomfort"].round(2).astype("float32")

if len(df_discomfort) < 3:
    st.warning("Não há dados suficientes para exibir a análise.")
    st.stop()  


st.write("## :eight_spoked_asterisk: Métricas de progresso")
st.write("""
    As métricas a seguir apresentam insights sobre o tratamento do paciente. 
""")

last_mean_discomfort = df_discomfort["discomfort"].iloc[-1]
penultimate_mean_discomfort = df_discomfort["discomfort"].iloc[-2]
antepenultimate_mean_discomfort = df_discomfort["discomfort"].iloc[-3]
last_delta_discomfort = last_mean_discomfort - penultimate_mean_discomfort
penultimate_delta_discomfort = penultimate_mean_discomfort - antepenultimate_mean_discomfort
last_percentage_improvement = (last_delta_discomfort / penultimate_mean_discomfort) * 100
penultimate_percentage_improvement = ( penultimate_delta_discomfort/ antepenultimate_mean_discomfort) * 100
last_session = df_discomfort["session"].iloc[-1]
last_date_session = df_discomfort["created_date"].iloc[-1].strftime('%d/%m')

col1_metric, col2_metric, col3_metric, col4_metric = st.columns(4)
col1_metric.metric("Situação atual", last_mean_discomfort, last_delta_discomfort)
col2_metric.metric("Porcentagem de melhora", f"{last_percentage_improvement:.2f}%", f"{(last_percentage_improvement - penultimate_percentage_improvement):.2f}%")
col3_metric.metric("Quantidade de consultas", last_session)
col4_metric.metric("Última consulta", last_date_session)

st.write("## :eight_spoked_asterisk: Melhora ao longo do tempo")
st.write("""
    Este gráfico mostra a evolução do paciente com base nas consultas realizadas. 
""")

fig = px.line(df_discomfort, x="created_date", y="discomfort", title=None, markers=True)
fig.update_traces(line=dict(color="#2c6e49"))

fig.update_xaxes(
    tickformat="%Y-%m-%d",  
    title="Data",
    tickmode="array",
    tickvals=df_discomfort['created_date'],
    titlefont=dict(size=16, color="black"),  
    tickfont=dict(size=14, color="black"),
)

fig.update_yaxes(
    title="Progresso",
    titlefont=dict(size=16, color="black"),  
    tickfont=dict(size=14, color="black"),
    gridcolor="lightgray"
)

fig.update_traces(
    hovertemplate="<b>Data:</b> %{x}<br>"  
                + "<b>Progresso:</b> %{y:.2f}<br>"
                + "<extra></extra>"
)

st.plotly_chart(fig)