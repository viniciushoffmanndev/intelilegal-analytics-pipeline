# Este será o cérebro da nossa ingestão de IA com OpenAI oficial.

import os
import glob
import chromadb  # Importado para garantir estabilidade do cliente no Docker
from langchain_community.document_loaders import PySparkDataFrameLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma  # Nova importação atualizada
from langchain_openai import OpenAIEmbeddings
from pyspark.sql import SparkSession

class VectorStorageJob:
    """
    Componente de MLOps responsável por ler dados do Data Lakehouse,
    fragmentar textos legais e indexá-los no Banco Vetorial ChromaDB usando OpenAI.
    """
    def __init__(self, db_path: str = ".chroma"):
        self.db_path = db_path
        # Inicializa o Spark local apenas para ler o Parquet de forma compatível
        self.spark = SparkSession.builder \
            .appName("IntelilegalVectorIngestion") \
            .master("local[*]") \
            .getOrCreate()
            
        # Configura o fragmentador de texto especializado para documentos legais
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,       # Tamanho ideal de caracteres por bloco para contratos
            chunk_overlap=50,     # Sobreposição para não perder o contexto entre blocos
            length_function=len,
            is_separator_regex=False
        )

    def run_ingestion(self, parquet_dir: str):
        """
        Executa o pipeline de IA: Leitura Parquet -> Chunking -> Vector Storage via OpenAI.
        """
        print(f"[*] Lendo dados processados pelo Spark de: {parquet_dir}")
        
        # 1. Carrega o Parquet gerado na etapa anterior
        df = self.spark.read.parquet(parquet_dir)
        
        # 2. Utiliza o utilitário do LangChain para converter o DataFrame em Documentos
        loader = PySparkDataFrameLoader(self.spark, df, page_content_column="cleaned_content")
        documents = loader.load()
        print(f"[+] {len(documents)} contratos carregados do Data Lakehouse.")

        # 3. Executa o Text Chunking
        print("[*] Aplicando fragmentação de texto (Text Chunking)...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"[+] Fragmentação concluída: gerados {len(chunks)} blocos de texto.")

        # 4. Inicializa o Modelo de Embeddings oficial e o Banco Vetorial
        print("[*] Inicializando Banco Vetorial ChromaDB local com OpenAI Embeddings...")
        
        try:
            # Instancia o gerador oficial da OpenAI (consome da OPENAI_API_KEY do ambiente)
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            
            # Cria o cliente persistente nativo idêntico ao da API
            persistent_client = chromadb.PersistentClient(path=self.db_path)
            
            # Inicializa o banco vetorial acoplado ao cliente estável
            vector_db = Chroma(
                client=persistent_client,
                embedding_function=embeddings
            )
            
            # Adiciona os documentos em lote na coleção
            vector_db.add_documents(documents=chunks)
            print(f"[+] Sucesso! Banco vetorial persistido e indexado via OpenAI em: {self.db_path}")
            
        except Exception as e:
            print(f"[-] Erro crítico na indexação vetorial: {str(e)}")

if __name__ == "__main__":
    # Caminhos locais integrados com a saída do pipeline do Spark
    PARQUET_INPUT = os.path.join("data", "processed_contracts")
    VECTOR_DB_DIR = ".chroma"

    job = VectorStorageJob(db_path=VECTOR_DB_DIR)
    job.run_ingestion(parquet_dir=PARQUET_INPUT)