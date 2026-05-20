import streamlit as st
import pandas as pd
import boto3
from io import BytesIO

st.title("Intelilegal Analytics Pipeline")

# O Streamlit lê as credenciais das Secrets automaticamente se você usar o formato padrão
@st.cache_data(ttl=3600) # Faz cache por 1 hora para economizar requisições na AWS
def load_data_from_s3():
    s3 = boto3.client(
        's3',
        aws_access_key_id=st.secrets["aws"]["aws_access_key_id"],
        aws_secret_access_key=st.secrets["aws"]["aws_secret_access_key"],
        region_name=st.secrets["aws"]["aws_default_region"]
    )
    
    # Busca o arquivo tratado pelo seu pipeline do Docker/PySpark
    obj = s3.get_object(Bucket="intelilegal-analytics-dev-data-lake", Key="dados_tratados.parquet")
    df = pd.read_parquet(BytesIO(obj['Body'].read()))
    return df

try:
    df = load_data_from_s3()
    st.success("Dados carregados com sucesso do AWS S3!")
    st.dataframe(df.head()) # Exibe a tabela na tela
except Exception as e:
    st.error(f"Erro ao conectar no S3: {e}")