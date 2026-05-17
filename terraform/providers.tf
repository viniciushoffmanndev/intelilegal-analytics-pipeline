# Configuração dos provedores e travas de versão
# Este arquivo define quem é o provedor da nuvem e garante que a equipe inteira use a mesma versão do Terraform.

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = "Intelilegal Analytics"
      ManagedBy = "Terraform"
      Owner     = "Vinicius Hoffmann"
    }
  }
}
