# Ambiente containerizado, nós fixamos o Python interno do container na versão exata exigida pelo Spark (3.10 ou 3.11),
# enquanto eu continuo usando o Python 3.13 na máquina física para escrever o código no VS Code.

# Utiliza uma imagem oficial do Python homologada para PySpark e ferramentas de IA
FROM python:3.11-slim

# Instala o Java (obrigatório para o Spark) e utilitários de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configura as variáveis de ambiente essenciais para o Java e Spark
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# O comando padrão mantém o container vivo para desenvolvimento ou execução de jobs
CMD ["bash"]