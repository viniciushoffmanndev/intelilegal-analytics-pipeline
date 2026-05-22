import streamlit as st
import pandas as pd
import boto3
from io import BytesIO
import chromadb  # Adicionado para gerenciar o cliente de forma global

st.title("Intelilegal Analytics Pipeline")

# 1. GARANTE QUE O CHROMADB SÓ SEJA INICIALIZADO UMA VEZ (SINGLETON)
# Mesmo se o backend ou as rotas chamarem o Chroma, o Streamlit blinda a conexão aqui
@st.cache_resource
def get_chroma_client():
    try:
        # Aponta para a pasta onde a ai_engine persiste os dados
        return chromadb.PersistentClient(path="data/chroma_db")
    except Exception as e:
        st.warning(f"Aviso ao iniciar ChromaDB (Modo Isolado): {e}")
        return None

# Inicializa o cliente global na memória do contêiner para matar o erro de lock
chroma_client = get_chroma_client()


# 2. FUNÇÃO DE CARGA DO DATA LAKE (S3)
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
    
    # Lista os arquivos dentro da pasta do S3 para achar o arquivo gerado pelo Spark
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    
    if 'Contents' not in response:
        raise FileNotFoundError(f"Nenhum arquivo encontrado no caminho S3: {prefix}")
        
    # Procura pelo arquivo real que termina com .parquet
    parquet_key = None
    for obj in response['Contents']:
        if obj['Key'].endswith('.parquet'):
            parquet_key = obj['Key']
            break
            
    if not parquet_key:
        raise FileNotFoundError("Nenhum arquivo .parquet válido foi encontrado na pasta do S3.")
    
    # Busca o arquivo correto dinamicamente
    obj = s3.get_object(Bucket=bucket_name, Key=parquet_key)
    df = pd.read_parquet(BytesIO(obj['Body'].read()))
    return df

# 3. RENDERIZAÇÃO DA INTERFACE
try:
    df = load_data_from_s3()
    st.success("Dados carregados com sucesso do AWS S3!")
    st.dataframe(df) # Exibe a tabela completa com paginação nativa do Streamlit
except Exception as e:
    st.error(f"Erro real na execução: {e}")