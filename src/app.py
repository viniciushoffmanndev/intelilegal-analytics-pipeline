# Arquivo principal que o Uvicorn vai instanciar. 
# Deixar a estrutura básica pronta, com tratamento de CORS e um endpoint de health check

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router as api_router

app = FastAPI(
    title="Intelilegal Analytics Pipeline API",
    description="API de inteligência analítica e busca semântica em contratos jurídicos.",
    version="1.0.0",
)

# Configuração de CORS para permitir conexões do Frontend no futuro
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja para o domínio correto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vincula as rotas modulares da API
app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["System"])
async def health_check():
    """
    Endpoint simples para monitoramento do status da aplicação.
    """
    return {"status": "healthy", "environment": "development"}