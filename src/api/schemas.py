# Validar o payload que a API vai receber e formatar a resposta que ela vai entregar. 
# Usar os schemas do Pydantic para garantir tipagem estática e documentação automática no Swagger (/docs).

from pydantic import BaseModel, Field
from typing import List, Dict, Any

class SearchRequest(BaseModel):
    query: str = Field(..., description="A pergunta ou termo jurídico para a busca semântica.")
    k: int = Field(default=2, ge=1, le=10, description="Número de trechos relevantes a serem retornados.")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "cláusula de rescisão contratual e penalidades",
                "k": 2
            }
        }

class ContractMetadata(BaseModel):
    contract_id: str
    agency_name: str
    estimated_value: float
    risk_level: str

class SearchResultItem(BaseModel):
    content: str = Field(..., description="Trecho do contrato recuperado pelo banco vetorial.")
    score: float = Field(..., description="Score de distância semântica (menor é mais próximo).")
    metadata: Dict[str, Any] = Field(..., description="Metadados extraídos do Data Lakehouse.")

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]