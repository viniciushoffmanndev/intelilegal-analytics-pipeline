# Definição dos recursos de infraestrutura (Buckets e IAM)
# Buckets de armazenamento e a política de acesso que o código Python vai usar depois.

# 1. Bucket S3 para Ingestão de Dados do Spark (Data Lakehouse Raw Zone)
resource "aws_s3_bucket" "data_lake" {
  bucket        = "${var.project_name}-${var.environment}-data-lake"
  force_destroy = true # Permite deletar no ambiente de dev mesmo se houver dados

}

# 2. Habilitar versionamento no bucket (Boa prática de Arquitetura de Dados)
resource "aws_s3_bucket_versioning" "data_lake_versioning" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

# 3. Bloquear acesso público ao bucket (MLSecOps e Segurança de Dados)
resource "aws_s3_bucket_public_access_block" "data_lake_privacy" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 4. IAM Role para a Aplicação Python/FastAPI e Spark
resource "aws_iam_role" "app_execution_role" {
  name = "${var.project_name}-${var.environment}-app-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com" # Ou ecs-tasks.amazonaws.com dependendo do deploy
        }
      }
    ]
  })
}

# 5. Política de Acesso Restrito ao Bucket (Princípio do Menor Privilégio)
resource "aws_iam_policy" "bucket_access_policy" {
  name        = "${var.project_name}-${var.environment}-s3-policy"
  description = "Permite leitura e escrita estrita no bucket do pipeline"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Resource = [
          aws_s3_bucket.data_lake.arn,
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      }
    ]
  })
}

# 6. Vincula a Política de Acesso à Role de Execução
resource "aws_iam_role_policy_attachment" "attach_s3_policy" {
  role       = aws_iam_role.app_execution_role.name
  policy_arn = aws_iam_policy.bucket_access_policy.arn
}
