import pandas as pd
from datetime import datetime
import streamlit as st
import matplotlib.pyplot as plt


def recencia_class(x, r, q_dict):
    if x <= q_dict[r][0.25]:
        return 'A'
    elif x <= q_dict[r][0.50]:
        return 'B'
    elif x <= q_dict[r][0.75]:
        return 'C'
    else:
        return 'D'


def freq_val_class(x, fv, q_dict):
    if x <= q_dict[fv][0.25]:
        return 'D'
    elif x <= q_dict[fv][0.50]:
        return 'C'
    elif x <= q_dict[fv][0.75]:
        return 'B'
    else:
        return 'A'


file_path = 'E:/Python/Projetos/streamlit/app-rfv-analysis/dados_input 1.csv'
df = pd.read_csv(file_path)
df['DiaCompra'] = pd.to_datetime(df['DiaCompra'], format='%Y-%m-%d')
dia_atual = df['DiaCompra'].max()

df_recencia = df.groupby('ID_cliente').agg(
    {'DiaCompra': lambda x: (dia_atual - x.max()).days}).reset_index()
df_recencia.columns = ['ID_cliente', 'Recencia']

df_frequencia = df.groupby('ID_cliente').agg(
    {'CodigoCompra': 'count'}).reset_index()
df_frequencia.columns = ['ID_cliente', 'Frequencia']

df_valor = df.groupby('ID_cliente').agg({'ValorTotal': 'sum'}).reset_index()
df_valor.columns = ['ID_cliente', 'Valor']

df_rfv = df_recencia.merge(df_frequencia, on='ID_cliente').merge(
    df_valor, on='ID_cliente')
quartis = df_rfv[['Recencia', 'Frequencia', 'Valor']
                 ].quantile(q=[0.25, 0.5, 0.75]).to_dict()

df_rfv['R_quartil'] = df_rfv['Recencia'].apply(
    recencia_class, args=('Recencia', quartis))
df_rfv['F_quartil'] = df_rfv['Frequencia'].apply(
    freq_val_class, args=('Frequencia', quartis))
df_rfv['V_quartil'] = df_rfv['Valor'].apply(
    freq_val_class, args=('Valor', quartis))

df_rfv['RFV_Score'] = df_rfv['R_quartil'] + \
    df_rfv['F_quartil'] + df_rfv['V_quartil']

dict_acoes = {
    'AAA': 'Enviar cupons de desconto, Pedir para indicar nosso produto pra algum amigo, Ao lançar um novo produto enviar amostras grátis pra esses.',
    'DDD': 'Churn! clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
    'DAA': 'Churn! clientes que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar',
    'CAA': 'Churn! clientes que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar',
    'BBB': 'Enviar e-mail de agradecimento, Oferecer upgrade ou produto complementar',
    'ABB': 'Enviar e-mail de agradecimento, Oferecer descontos em compras futuras',
    'AAB': 'Enviar e-mail de agradecimento, Oferecer amostras de novos produtos',
    'DCC': 'Oferecer descontos para incentivar compras',
    'CCC': 'Oferecer programa de fidelidade',
    'BCC': 'Enviar lembrete de produtos no carrinho, Oferecer descontos',
    'BBA': 'Enviar e-mail de agradecimento, Oferecer um programa de indicação',
    'CBB': 'Enviar amostras grátis, Oferecer desconto em próximos pedidos',
    'BCA': 'Enviar um brinde com a próxima compra, Oferecer um programa de recompensas',
    'ACC': 'Oferecer um desconto especial por tempo limitado, Enviar recomendações personalizadas',
    'CBA': 'Enviar um brinde de agradecimento, Oferecer um programa de fidelidade exclusivo',
    'ABB': 'Oferecer descontos em produtos complementares, Enviar novidades e lançamentos em primeira mão'
}

df_rfv['acoes de marketing/crm'] = df_rfv['RFV_Score'].map(dict_acoes)

st.set_page_config(page_title="Análise RFV e Ações de Marketing/CRM")
st.title('Análise RFV e Ações de Marketing/CRM')

st.markdown("""
### O que é RFV?
RFV significa Recência, Frequência e Valor. É uma técnica utilizada para analisar o comportamento dos clientes com base em três fatores:
- **Recência**: Quanto tempo passou desde a última compra do cliente.
- **Frequência**: Quantas vezes o cliente comprou durante um período específico.
- **Valor**: Quanto dinheiro o cliente gastou durante um período específico.

Com base nesses três fatores, podemos segmentar os clientes e criar estratégias de marketing personalizadas para cada segmento.
""")

st.subheader('Tabela RFV com Ações de Marketing/CRM')
st.dataframe(df_rfv.drop(columns=['acoes de marketing/crm']))

st.subheader('Top 10 Segmentos RFV')
rfv_distribution = df_rfv['RFV_Score'].value_counts().reset_index().head(10)
rfv_distribution.columns = ['RFV_Score', 'Count']
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(rfv_distribution['RFV_Score'], rfv_distribution['Count'])
plt.xticks(rotation=90)
plt.xlabel('RFV Score')
plt.ylabel('Count')
plt.title('Top 10 Segmentos RFV')
st.pyplot(fig)

st.subheader("Top 10 Clientes com Pontuação 'AAA' Ordenados pelo Valor")
df_rfv_aaa = df_rfv[df_rfv['RFV_Score'] == 'AAA'].sort_values(
    'Valor', ascending=False).head(10)
st.table(df_rfv_aaa[['ID_cliente', 'Valor', 'RFV_Score']])

st.subheader("Ações de Marketing/CRM por RFV_Score")
selected_score = st.selectbox(
    "Selecione o RFV_Score", options=df_rfv['RFV_Score'].unique())
filtered_df = df_rfv[df_rfv['RFV_Score'] == selected_score]
st.dataframe(filtered_df[['ID_cliente', 'Recencia',
             'Frequencia', 'Valor', 'acoes de marketing/crm']])
