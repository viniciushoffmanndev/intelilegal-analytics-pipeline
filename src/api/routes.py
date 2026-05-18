# Ligar o ChromaDB ao endpoint da API. Toda vez que alguém bater na rota /analytics/search,
# o FastAPI vai usar os mesmos embeddings da OpenAI para buscar na base .chroma e devolver o JSON estruturado.

import os
import chromadb  # Import extra para garantir estabilidade do cliente no Docker
from fastapi import APIRouter, HTTPException, status
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma  # Nova importação atualizada
from src.api.schemas import SearchRequest, SearchResponse, SearchResultItem

router = APIRouter()

# Inicializa os Embeddings e a conexão com o ChromaDB no escopo global
try:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Opcional, mas altamente recomendado para Docker: cria um cliente persistente estável
    persist_dir = ".chroma"
    persistent_client = chromadb.PersistentClient(path=persist_dir)
    
    vector_db = Chroma(
        client=persistent_client,
        embedding_function=embeddings  # O langchain-chroma aceita 'embedding_function' via wrapper, mas injetar o client é mais seguro
    )
except Exception as e:
    print(f"[-] Erro ao conectar com a base vetorial Chroma: {str(e)}")
    vector_db = None


@router.post(
    "/analytics/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    tags=["Analytics Engine"]
)
async def semantic_search(payload: SearchRequest):
    """
    Executa uma busca semântica de alta precisão na base de contratos jurídicos
    utilizando embeddings gerados via OpenAI.
    """
    if vector_db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco vetorial não inicializado corretamente no servidor."
        )

    try:
        # Dispara a busca por similaridade trazendo o score de distância
        raw_results = vector_db.similarity_search_with_score(
            query=payload.query,
            k=payload.k
        )

        formatted_results = []
        for doc, score in raw_results:
            # Mapeia a estrutura do LangChain para o nosso schema de resposta
            item = SearchResultItem(
                content=doc.page_content,
                score=float(score),
                metadata=doc.metadata
            )
            formatted_results.append(item)

        return SearchResponse(
            query=payload.query,
            results=formatted_results
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao processar a busca semântica: {str(e)}"
        )