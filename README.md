<p align="center">
  <img src="https://img.shields.io/badge/PYTHON-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FASTAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/APACHE%20SPARK-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white" />
  <img src="https://img.shields.io/badge/CHROMADB-007ACC?style=for-the-badge&logo=googlecloud&logoColor=white" />
  <img src="https://img.shields.io/badge/OPENAI%20API-412991?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/DOCKER-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/TERRAFORM-7B42BC?style=for-the-badge&logo=terraform&logoColor=white" />
</p>

<h2 align="center">✨ Intelilegal Analytics Pipeline ✨</h2>

<p align="center">
  Este projeto representa um pipeline analítico robusto e de ponta a ponta, meticulosamente desenvolvido para fornecer inteligência jurídica avançada e capacidade de busca semântica em grandes volumes de contratos. Ele orquestra tecnologias de ponta, começando com o Apache Spark (via PySpark) para a engenharia, limpeza e processamento eficiente de dados contratuais brutos em larga escala. Os dados resultantes são então transformados em embeddings vetoriais de alta dimensão, aproveitando os poderosos modelos de linguagem grande (LLM) da OpenAI, e subsequentemente indexados de forma otimizada em um banco de dados vetorial local, o ChromaDB. A camada de aplicação é exposta através de uma API de alta performance construída com FastAPI, que facilita consultas semânticas em tempo real, fornecendo resultados com métricas precisas de relevância e proximidade matemática. Para garantir um ambiente de desenvolvimento local previsível, isolado e consistente, toda a infraestrutura do ecossistema é conteinerizada utilizando Docker e automatizada com Docker Compose, aderindo rigorosamente aos padrões de MLOps e DevOps.
</p>

---

## 🔥 Features

- ⚡ **Processamento de Dados Massivo**: Engenharia, limpeza e processamento de grandes volumes de dados contratuais brutos utilizando Apache Spark (via PySpark).
- 🧠 **Busca Semântica Avançada**: Geração de embeddings vetoriais de alta dimensão com modelos LLM da OpenAI para buscas contextuais em contratos.
- 🗄️ **Indexação Vetorial Eficiente**: Armazenamento e indexação de embeddings em um banco de dados vetorial ChromaDB para recuperação rápida.
- 🚀 **API de Alta Performance**: Camada de aplicação robusta construída com FastAPI para consultas semânticas em tempo real.
- 📊 **Métricas de Relevância**: Consultas que retornam resultados baseados em métricas de relevância e proximidade matemática.
- 🐳 **Infraestrutura Conteinerizada**: Todo o ecossistema gerenciado e orquestrado via Docker e Docker Compose para isolamento e portabilidade.
- ⚙️ **Padrões MLOps/DevOps**: Adesão a práticas rigorosas de MLOps e DevOps para um ciclo de desenvolvimento local previsível e eficiente.

---

## 📸 Screenshot

<table align="center">
  <tr>
    <td colspan="2"><img src="./public/001.PNG" width="100%"/></td>
  </tr>
  <tr>
    <td><img src="./public/002.PNG" width="100%"/></td>
    <td><img src="./public/003.PNG" width="100%"/></td>
  </tr>
  <tr>
    <td><img src="./public/005.PNG" width="100%"/></td>
    <td><img src="./public/004.PNG" width="100%"/></td>
  </tr>
</table>

---

## 🛠️ Setup & Run

```bash
# 1. Clone o repositório
git clone https://github.com/viniciushoffmanndev/intelilegal-analytics-pipeline.git
cd intelilegal-analytics-pipeline

# 2. Configure suas variáveis de ambiente no arquivo .env
# Certifique-se de adicionar sua OPENAI_API_KEY lá dentro

# 3. Suba todo o ecossistema e inicialize o servidor automaticamente via Docker Compose
docker compose up -d --build

# 4. Acesse a documentação interativa da API (Swagger) direto no seu navegador ou VS Code:
# http://localhost:8000/docs
```

## 🔑 Environment Variables

To run this project, you will need to add the following environment variables to your .env file:
```
OPENAI_API_KEY=sua_chave_da_openai_aqui
ENVIRONMENT=dev
```

---

## 💬 Feedback

Sinta-se à vontade para se conectar comigo ou enviar feedbacks via [LinkedIn](https://www.linkedin.com/in/viniciushoffmanndev). Vamos construir algo incrível juntos!

---

## 📄 License

This project is licensed under the MIT License.