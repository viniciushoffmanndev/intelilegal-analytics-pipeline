"""
Componente de MLOps responsável por ler os dados limpos do Data Lakehouse (Parquet),
fragmentar textos legais e indexá-los de forma idempotente no ChromaDB usando OpenAI.
"""
import os
import shutil
import pandas as pd
import chromadb
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

class VectorStorageJob:
    def __init__(self, db_path: str = ".chroma", collection_name: str = "legal_contracts"):
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Configura o fragmentador de texto especializado para documentos legais
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,       # Ajustado ligeiramente para acomodar melhor parágrafos jurídicos
            chunk_overlap=80,     # Maior sobreposição garante melhor preservação do contexto legal
            length_function=len,
            is_separator_regex=False
        )

    def run_ingestion(self, parquet_dir: str):
        """
        Executa o pipeline de IA de forma idempotente: Leitura Parquet -> Chunking -> Vector Ingestion.
        """
        print(f"[*] Lendo dados processados de: {parquet_dir}")
        
        # 1. Leitura de alta performance do Parquet sem subir uma JVM inteira do Spark
        # O pandas lê o diretório Parquet gerado pelo Spark nativamente através do pyarrow
        try:
            df = pd.read_parquet(parquet_dir)
        except Exception as e:
            print(f"[-] Erro ao ler arquivos Parquet: {str(e)}")
            return

        print(f"[+] {len(df)} contratos carregados do Data Lakehouse.")

        # 2. Conversão manual para objetos Document do LangChain injetando metadados ricos
        documents = []
        for _, row in df.iterrows():
            doc = Document(
                page_content=row["cleaned_content"],
                metadata={
                    "contract_id": str(row["contract_id"]),
                    "agency_name": str(row["agency_name"]),
                    "estimated_value": float(row["estimated_value"]),
                    "risk_level": str(row["risk_level"])
                }
            )
            documents.append(doc)

        # 3. Executa o Text Chunking
        print("[*] Aplicando fragmentação de texto (Text Chunking)...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"[+] Fragmentação concluída: gerados {len(chunks)} blocos de texto.")

        # 4. Inicializa o Modelo de Embeddings oficial e o Banco Vetorial
        print("[*] Inicializando Banco Vetorial ChromaDB local com OpenAI Embeddings...")
        
        try:
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            
            # Inicializa o cliente persistente do Chroma
            persistent_client = chromadb.PersistentClient(path=self.db_path)
            
            # GARANTIA DE IDEMPOTÊNCIA: Se a coleção já existir, nós a limpamos para evitar duplicações
            try:
                persistent_client.delete_collection(name=self.collection_name)
                print(f"[*] Coleção antiga '{self.collection_name}' limpa com sucesso.")
            except Exception:
                # Se a coleção não existia, apenas ignora o erro e segue em frente
                pass

            # Recria a coleção limpa acoplada ao LangChain
            vector_db = Chroma(
                client=persistent_client,
                collection_name=self.collection_name,
                embedding_function=embeddings
            )
            
            # Gera IDs determinísticos para rastreabilidade fina e depuração
            chunk_ids = [
                f"{chunk.metadata['contract_id']}_chunk_{i}" 
                for i, chunk in enumerate(chunks)
            ]
            
            # Adiciona os documentos em lote na coleção de forma segura
            print("[*] Enviando vetores para o ChromaDB via OpenAI API...")
            vector_db.add_documents(documents=chunks, ids=chunk_ids)
            print(f"[+] Sucesso! Banco vetorial persistido e indexado em: {self.db_path}")
            
        except Exception as e:
            print(f"[-] Erro crítico na indexação vetorial: {str(e)}")

if __name__ == "__main__":
    # Certifique-se de ter a variável de ambiente OPENAI_API_KEY configurada no terminal antes de rodar
    # ex no PowerShell: $env:OPENAI_API_KEY="sua-chave"
    
    PARQUET_INPUT = os.path.join("data", "processed_contracts")
    VECTOR_DB_DIR = ".chroma"

    job = VectorStorageJob(db_path=VECTOR_DB_DIR)
    job.run_ingestion(parquet_dir=PARQUET_INPUT)