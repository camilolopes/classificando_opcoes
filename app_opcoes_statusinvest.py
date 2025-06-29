
import streamlit as st
import pandas as pd
from datetime import datetime

letra_mes_call = {l: m for l, m in zip("ABCDEFGHIJKL", range(1,13))}
letra_mes_put  = {l: m for l, m in zip("MNOPQRSTUVWX", range(1,13))}

def terceira_sexta_feira(ano, mes):
    dia, contador = 1, 0
    while dia <= 31:
        try:
            dt = datetime(ano, mes, dia)
            if dt.weekday() == 4:
                contador += 1
                if contador == 3:
                    return dt
        except:
            break
        dia += 1
    return None

def classificar_tipo_opcao(letra):
    if letra in letra_mes_call: return "CALL"
    if letra in letra_mes_put:  return "PUT"
    return "DESCONHECIDO"

def vencimento_opcao_b3(ativo):
    if len(ativo) < 5: return "N/A"
    letra = ativo[4].upper()
    tipo = classificar_tipo_opcao(letra)
    mes = letra_mes_call.get(letra) if tipo == "CALL" else letra_mes_put.get(letra)
    if not mes: return "N/A"
    hoje, ano = datetime.today(), datetime.today().year
    if mes < hoje.month or (mes == hoje.month and hoje.day > 21): ano += 1
    dt = terceira_sexta_feira(ano, mes)
    return dt.strftime("%d/%m/%Y") if dt else "N/A"

st.title("📊 Classificador de Opções B3 (sem strike)")

uploaded_files = st.file_uploader("📤 Envie um ou mais arquivos CSV com os ativos", type="csv", accept_multiple_files=True)
if uploaded_files:
    dfs = []
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")
        if "Ativo" in df.columns:
            dfs.append(df)
        else:
            st.error(f"❌ Coluna 'Ativo' não encontrada no arquivo: {uploaded_file.name}")

    if dfs:
        full_df = pd.concat(dfs, ignore_index=True)
        with st.spinner("🔍 Processando ativos..."):
            full_df["Tipo de Opção"] = full_df["Ativo"].apply(lambda x: classificar_tipo_opcao(x[4].upper()) if len(x) >= 5 else "DESCONHECIDO")
            full_df["Data de Vencimento"] = full_df["Ativo"].apply(vencimento_opcao_b3)
        st.success("✅ Arquivos processados com sucesso!")
        st.dataframe(full_df)
        csv = full_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Baixar arquivo classificado", data=csv, file_name="ativos_classificados.csv", mime="text/csv")
