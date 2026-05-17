# Script de teste rápido e cirúrgico. Esse teste vai garantir que os embeddings foram gerados 
# corretamente e que o ChromaDB consegue recuperar trechos por proximidade semântica (relevância de contexto), 
# que é a base do padrão RAG (Retrieval-Augmented Generation).

import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

def test_vector_search():
    print("[*] Inicializando conexão com o ChromaDB via OpenAI...")
    
    # O LangChain vai buscar a variável OPENAI_API_KEY direto do SO do container
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("[-] ERRO: A variável de ambiente OPENAI_API_KEY não foi encontrada dentro do container!")
        print("[*] Variáveis disponíveis:", list(os.environ.keys()))
        return

    # Instancia o mesmo modelo de embedding usado na ingestão
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Conecta ao diretório persistido
    db = Chroma(
        persist_directory=".chroma", 
        embedding_function=embeddings
    )

    query = "cláusula de rescisão contratual e penalidades"
    print(f"\n[*] Disparando busca semântica para: '{query}'")
    
    # Executa a busca trazendo os 2 trechos mais próximos
    results = db.similarity_search_with_score(query, k=2)
    
    print("\n================ RESULTADOS ENCONTRADOS ================")
    if not results:
        print("[-] Nenhum documento condizente com a busca foi retornado.")
        return

    for doc, score in results:
        print(f"\n[Score de Distância: {score:.4f}]")
        print(f"Conteúdo: {doc.page_content[:200]}...")
        print(f"Metadados associados: {doc.metadata}")
    print("========================================================\n")

if __name__ == "__main__":
    test_vector_search()