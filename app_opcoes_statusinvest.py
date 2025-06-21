
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

letra_mes_call = {l: m for l, m in zip("ABCDEFGHIJKL", range(1,13))}
letra_mes_put  = {l: m for l, m in zip("MNOPQRSTUVWX", range(1,13))}

def terceira_sexta_feira(ano, mes):
    dia, contador = 1, 0
    while dia <= 31:
        dt = datetime(ano, mes, dia)
        if dt.weekday() == 4:
            contador += 1
            if contador == 3:
                return dt
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

def extrair_strike_statusinvest(ativo):
    base = ''.join(filter(str.isalpha, ativo[:-5]))
    url = f"https://statusinvest.com.br/acoes/{base}/derivativos"
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        tabela = soup.find("table")
        if tabela:
            linhas = tabela.find_all("tr")
            for linha in linhas:
                cols = [c.get_text(strip=True) for c in linha.find_all("td")]
                if cols and ativo in cols[0]:
                    return cols[2].replace("R$", "").replace(".", "").replace(",", ".")
    except:
        return "Erro"
    return "N/D"

st.title("Classificador de Opções B3 com Strike (StatusInvest)")

uploaded_file = st.file_uploader("📤 Envie o arquivo CSV com os ativos", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=None, engine="python")
    if "Ativo" in df.columns:
        with st.spinner("🔍 Processando ativos..."):
            df["Tipo de Opção"] = df["Ativo"].apply(lambda x: classificar_tipo_opcao(x[4].upper()) if len(x) >= 5 else "DESCONHECIDO")
            df["Data de Vencimento"] = df["Ativo"].apply(vencimento_opcao_b3)
            df["Strike"] = df["Ativo"].apply(extrair_strike_statusinvest)
        st.success("✅ Arquivo processado!")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Baixar arquivo com Strike", data=csv, file_name="ativos_com_strike.csv", mime="text/csv")
    else:
        st.error("❌ Coluna 'Ativo' não encontrada no CSV.")
