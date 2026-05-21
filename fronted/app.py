import streamlit as st
import pandas as pd
import boto3
from io import BytesIO

st.title("Intelilegal Analytics Pipeline")

@st.cache_data(ttl=3600) # Faz cache por 1 hora para economizar requisições na AWS
def load_data_from_s3():
    s3 = boto3.client(
        's3',
        aws_access_key_id=st.secrets["aws"]["aws_access_key_id"],
        aws_secret_access_key=st.secrets["aws"]["aws_secret_access_key"],
        region_name=st.secrets["aws"]["aws_default_region"]
    )
    
    bucket_name = "intelilegal-analytics-dev-data-lake"
    prefix = "data/processed_contracts/"
    
    # 1. Lista os arquivos dentro da pasta do S3 para achar o arquivo gerado pelo Spark
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    
    if 'Contents' not in response:
        raise FileNotFoundError(f"Nenhum arquivo encontrado no caminho S3: {prefix}")
        
    # 2. Procura pelo arquivo real que termina com .parquet
    parquet_key = None
    for obj in response['Contents']:
        if obj['Key'].endswith('.parquet'):
            parquet_key = obj['Key']
            break
            
    if not parquet_key:
        raise FileNotFoundError("Nenhum arquivo .parquet válido foi encontrado na pasta do S3.")
    
    # 3. Busca o arquivo correto dinamicamente
    st.info(f"Carregando arquivo: {parquet_key.split('/')[-1]}")
    obj = s3.get_object(Bucket=bucket_name, Key=parquet_key)
    df = pd.read_parquet(BytesIO(obj['Body'].read()))
    return df

try:
    df = load_data_from_s3()
    st.success("Dados carregados com sucesso do AWS S3!")
    st.dataframe(df.head()) # Exibe a tabela na tela
except Exception as e:
    # Printa o erro EXATO que a AWS ou o Python dispararem, sem mascarar nada!
    st.error(f"Erro real na execução: {e}")