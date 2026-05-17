# O motor do PySpark

import os
import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, when
from pyspark.sql.types import StringType, FloatType

class LegalDataPipeline:
    """
    Pipeline de Big Data para ingestão, limpeza e normalização 
    de contratos públicos em larga escala utilizando PySpark.
    """
    def __init__(self, app_name: str = "IntelilegalContractPipeline"):
        self.spark = (SparkSession.builder
                      .appName(app_name)
                      .config("spark.sql.warehouse.dir", "spark-warehouse")
                      .master("local[*]")  # Utiliza todos os cores da máquina local
                      .getOrCreate())
        
    @staticmethod
    @udf(returnType=StringType())
    def clean_legal_text(text: str) -> str:
        """
        UDF (User Defined Function) customizada para higienização de jargões,
        remoção de quebras de linha excessivas e caracteres especiais de contratos.
        """
        if not text:
            return ""
        # Remove quebras de página, tabulações e múltiplos espaços
        text = re.sub(r'[\r\n\t]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        # Remove caracteres especiais mantendo a acentuação e pontuação essencial
        text = re.sub(r'[^\w\s\d.,;:\-\/]', '', text)
        return text.strip()

    @staticmethod
    @udf(returnType=FloatType())
    def extract_contract_value(text: str) -> float:
        """
        Regex escalável para capturar padrões financeiros comuns em contratos (ex: R$ 150.000,00)
        """
        if not text:
            return 0.0
        match = re.search(r'(?:R\$\s?|VALOR:\s?)([\d\.]+,\d{2})', text, re.IGNORECASE)
        if match:
            value_str = match.group(1).replace('.', '').replace(',', '.')
            try:
                return float(value_str)
            except ValueError:
                return 0.0
        return 0.0

    def run_pipeline(self, input_path: str, output_path: str):
        """
        Executa o fluxo completo de ETL: Ingestão, Transformação e Escrita.
        """
        print(f"[*] Iniciando leitura dos dados brutos de: {input_path}")
        
        # 1. Ingestão (Extract) - Simulando leitura do Data Lake
        raw_df = self.spark.read.option("multiline", "true").json(input_path)

        # 2. Transformação (Transform) - Otimização e Profiling de Dados
        processed_df = raw_df \
            .withColumn("cleaned_content", self.clean_legal_text(col("raw_content"))) \
            .withColumn("estimated_value", self.extract_contract_value(col("raw_content"))) \
            .withColumn("risk_level", when(col("estimated_value") > 1000000.0, "HIGH")
                                     .when(col("estimated_value") > 100000.0, "MEDIUM")
                                     .otherwise("LOW")) \
            .select("contract_id", "agency_name", "estimated_value", "risk_level", "cleaned_content")

        print("[*] Transformações aplicadas com sucesso. Esquema resultante:")
        processed_df.printSchema()

        # 3. Escrita (Load) - Salvando em Parquet colunar de alta performance
        print(f"[*] Salvando dados otimizados em formato Parquet em: {output_path}")
        processed_df.write.mode("overwrite").parquet(output_path)
        print("[+] Pipeline de processamento em lote concluído com sucesso!")

if __name__ == "__main__":
    # Caminhos locais mapeados para desenvolvimento rápido
    INPUT_DATA = os.path.join("data", "raw_contracts.json")
    OUTPUT_DATA = os.path.join("data", "processed_contracts")

    # Garante que a pasta 'data' exista localmente para testes
    os.makedirs("data", exist_ok=True)

    # Executa a arquitetura do job
    pipeline = LegalDataPipeline()
    # Nota: Em produção, este método receberia caminhos do S3 provisionados pelo Terraform
    # pipeline.run_pipeline("s3://...", "s3://...")