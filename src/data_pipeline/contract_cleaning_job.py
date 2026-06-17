"""
Esse código é o "marco zero" do meu pipeline. É nele que o PySpark cria o DataFrame estruturado, limpa os textos e
gera os metadados, valores e riscos. Então Se houver qualquer divergência de tipos ou nomes de colunas aqui,
isso vai gerar um efeito dominó que quebra o banco vetorial, a API e o Streamlit.
"""
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, regexp_replace, regexp_extract, trim

class LegalDataPipeline:
    """
    Pipeline de Big Data para ingestão, limpeza e normalização de contratos públicos
    em larga escala utilizando PySpark nativo (JVM).
    """
    def __init__(self, app_name: str = "InteliLegalContractPipeline"):
        self.spark = (SparkSession.builder
                      .appName(app_name)
                      .config("spark.sql.warehouse.dir", "spark-warehouse")
                      .master("local[*]")
                      .getOrCreate())
    
    def run_pipeline(self, input_path: str, output_path: str):
        """
        Executa o fluxo completo de ETL utilizando apenas funções nativas da JVM - Catalyst
        """
        print(f"[*] Iniciando leitura dos dados brutos de: {input_path}")

        # Extração - Leitura do formato JSON Lines (raw_contracts.json)
        raw_df = self.spark.read.json(input_path)

        # Substitui quebras de linha/abas por espaço -> colapsa múltiplos espaços -> remove caracteres especiais -> trim()
        df_cleaned = raw_df.withColumn(
            "cleaned_content",
            trim(
                regexp_replace(
                    regexp_replace(
                        regexp_replace(col("raw_content"), r'[\r\n\t]+', ' '),
                        r'\s+', ' '
                    ),
                    r'[^\w\s\d.,;:\-\/]', ''
                )
            )
        )

        # Remove os pontos de milhar e converte a vírgula decimal em ponto para o Cast
        df_with_value = df_cleaned.withColumn(
            "extracted_value_str",
            regexp_extract(col("raw_content"), r'(?:R\$\s?|VALOR:\s?)([\d\.]+,\d{2})', 1)
        ).withColumn(
            "estimated_value",
            regexp_replace(
                regexp_replace(col("extracted_value_str"), r'\.', ''), 
                r',', '.'
            ).cast("float")
        )

        # Etapa C: Tratamento de Nulos, Classificação de Risco e Seleção Final
        processed_df = df_with_value.withColumn(
            "estimated_value",
            when(col("estimated_value").isNull(), 0.0).otherwise(col("estimated_value"))
        ).withColumn(
            "risk_level", 
            when(col("estimated_value") > 1000000.0, "HIGH")
            .when(col("estimated_value") > 100000.0, "MEDIUM")
            .otherwise("LOW")
        ).select("contract_id", "agency_name", "estimated_value", "risk_level", "cleaned_content")

        print("[*] Transformações aplicadas via JVM. Forçando exibição dos dados (.show()):")
        processed_df.show(truncate=40)

        print("[*] Esquema final do Data Lakehouse:")
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
    pipeline.run_pipeline(INPUT_DATA, OUTPUT_DATA)