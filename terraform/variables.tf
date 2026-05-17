# Variáveis do projeto para evitar valores hardcoded
# Parâmetros mutáveis ficam aqui. Isso torna sua infraestrutura reutilizável para ambientes de Development, Staging ou Production.

variable "aws_region" {
  type        = string
  description = "Região da AWS onde os recursos serão provisionados"
  default     = "us-east-1"
}

variable "environment" {
  type        = string
  description = "Ambiente do deploy"
  default     = "dev"
}

variable "project_name" {
  type        = string
  description = "Nome base do projeto para nomear os recursos"
  default     = "intelilegal-analytics"
}
