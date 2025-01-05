import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(layout="wide", page_title="Dashboard CNO")

# Estilo CSS personalizado
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #0066cc;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
    }
    .stPlotlyChart {
        height: 400px !important;
    }
    .dataframe {
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path, encoding="latin1")

# Carregar os dados
df1 = load_data("cno_areas.csv")
df2 = load_data("cno.csv")

@st.cache_data
def unify_dataframes(df1, df2):
    merged_df = pd.merge(df1, df2, on="CNO", how="outer")
    filtered_df = merged_df[merged_df["Situação"] == 2]
    estados_para_substituir = ['estado', 'PERNAMBUCO', 'EX', 'BUENO ARIES', 'CHUBUT', 'SÃO PAULO', 'CHILE']
    filtered_df['Estado'] = filtered_df['Estado'].replace(estados_para_substituir, None)
    return filtered_df

# Unificando DF
df_g = unify_dataframes(df1, df2)

@st.cache_data
def calculate_percentage_distribution(df_g):
    df_obras_por_destinacao = df_g['Destinação'].value_counts().reset_index()
    df_obras_por_destinacao.columns = ['Destinação', 'Número de Obras']
    total_obras = df_obras_por_destinacao['Número de Obras'].sum()
    df_obras_por_destinacao['Percentual'] = (df_obras_por_destinacao['Número de Obras'] / total_obras) * 100
    df_obras_por_destinacao['Percentual'] = df_obras_por_destinacao['Percentual'].round(2)
    return df_obras_por_destinacao

@st.cache_data
def calculate_percentage_by_state(df_g):
    df_cno_por_estado = df_g['Estado'].value_counts().reset_index()
    df_cno_por_estado.columns = ['Estado', 'Número de CNO']
    total_cnos = df_cno_por_estado['Número de CNO'].sum()
    df_cno_por_estado['Percentual'] = (df_cno_por_estado['Número de CNO'] / total_cnos) * 100
    df_cno_por_estado['Percentual'] = df_cno_por_estado['Percentual'].round(2)
    return df_cno_por_estado

@st.cache_data
def calculate_percentage_by_size(df_g):
    df_g['Categoria de Tamanho'] = pd.cut(df_g['Área total'],
                                          bins=[0, 500, 1000, 5000, 10000, 50000, float('inf')],
                                          labels=['Até 500 m²', 'Até 1.000 m²', '1.001-5.000 m²',
                                                  '5.001-10.000 m²', '10.001-50.000 m²', 'Acima de 50.000 m²'])
    df_obras_por_tamanho = df_g['Categoria de Tamanho'].value_counts().sort_index().reset_index()
    df_obras_por_tamanho.columns = ['Categoria de Tamanho', 'Número de Obras']
    total_obras = df_obras_por_tamanho['Número de Obras'].sum()
    df_obras_por_tamanho['Percentual'] = (df_obras_por_tamanho['Número de Obras'] / total_obras) * 100
    df_obras_por_tamanho['Percentual'] = df_obras_por_tamanho['Percentual'].round(2)
    return df_obras_por_tamanho

def format_number_br(number):
    return f"{int(number):,}".replace(",", ".")

# Título do Dashboard
st.title("Dashboard CNO")

# Container para métricas principais
with st.container():
    col1, col2, col3, col4 = st.columns(4)

    metrics = [
        ("Total de CNOs", len(df_g)),
        ("Destinações Únicas", df_g['Destinação'].nunique()),
        ("Área Total (MM de M²)", int(df_g['Área total'].sum() / 1000000)),
        ("Estados Únicos", df_g['Estado'].nunique())
    ]

    for i, (label, value) in enumerate(metrics, 1):
        with globals()[f'col{i}']:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{format_number_br(value)}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

# Gráficos e Tabelas
st.header("Análises Gráficas")

# Container para Distribuição de Tipos de Obra
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        df_obras_por_destinacao = calculate_percentage_distribution(df_g)
        fig_obras_por_destinacao = px.bar(
            df_obras_por_destinacao,
            x='Destinação',
            y='Número de Obras',
            title='Número de Obras por Destinação',
            labels={'Destinação': 'Tipo de Destinação', 'Número de Obras': 'Quantidade de Obras'},
            text='Percentual'
        )

        fig_obras_por_destinacao.update_traces(
            marker_color='blue',
            texttemplate='%{text:.2f}%',
            textposition='outside'
        )
        fig_obras_por_destinacao.update_layout(
            xaxis_title='Tipo de Destinação',
            yaxis_title='Quantidade de Obras',
            xaxis_tickangle=-45,
            margin=dict(t=50, b=100),
            height=500,
            yaxis_range=[0, df_obras_por_destinacao['Número de Obras'].max() * 1.15],
            showlegend=False,
            uniformtext=dict(minsize=8, mode='show')
        )

        st.plotly_chart(fig_obras_por_destinacao, use_container_width=True)

    with col2:
        st.subheader('Quantidades por Destinação')
        st.dataframe(df_obras_por_destinacao, height=400)

# Container para Número de CNO por Estado
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        df_cno_por_estado = calculate_percentage_by_state(df_g)
        fig_cno_por_estado = px.bar(
            df_cno_por_estado,
            x='Estado',
            y='Número de CNO',
            title='Número de CNO por Estado',
            labels={'Estado': 'Estado', 'Número de CNO': 'Quantidade de CNO'},
            text='Percentual'
        )

        fig_cno_por_estado.update_traces(
            marker_color='green',
            texttemplate='%{text:.2f}%',
            textposition='outside'
        )
        fig_cno_por_estado.update_layout(
            xaxis_title='Estado',
            yaxis_title='Quantidade de CNO',
            xaxis_tickangle=-45,
            margin=dict(t=50, b=100),
            height=500,
            yaxis_range=[0, df_cno_por_estado['Número de CNO'].max() * 1.15],
            showlegend=False,
            uniformtext=dict(minsize=8, mode='show')
        )

        st.plotly_chart(fig_cno_por_estado, use_container_width=True)

    with col2:
        st.subheader('CNO por Estado')
        st.dataframe(df_cno_por_estado, height=400)

# Container para Classificação pelo tamanho (m²) das obras
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        df_obras_por_tamanho = calculate_percentage_by_size(df_g)
        fig_obras_por_tamanho = px.bar(
            df_obras_por_tamanho,
            x='Categoria de Tamanho',
            y='Número de Obras',
            title='Número de Obras por Categoria de Tamanho',
            labels={'Categoria de Tamanho': 'Categoria de Tamanho', 'Número de Obras': 'Quantidade de Obras'},
            text='Percentual'
        )

        fig_obras_por_tamanho.update_traces(
            marker_color='purple',
            texttemplate='%{text:.2f}%',
            textposition='outside'
        )
        fig_obras_por_tamanho.update_layout(
            xaxis_title='Categoria de Tamanho',
            yaxis_title='Quantidade de Obras',
            xaxis_tickangle=-45,
            margin=dict(t=50, b=100),
            height=500,
            yaxis_range=[0, df_obras_por_tamanho['Número de Obras'].max() * 1.15],
            showlegend=False,
            uniformtext=dict(minsize=8, mode='show')
        )

        st.plotly_chart(fig_obras_por_tamanho, use_container_width=True)

    with col2:
        st.subheader('Obras por Tamanho')
        st.dataframe(df_obras_por_tamanho, height=400)
















