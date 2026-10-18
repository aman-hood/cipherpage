# ==============================================================================
# CipherPage Infrastructure as Code - Terraform Variables
# Conforms to SRS v2.2 OPS-05, OPS-07, OPS-11
# ==============================================================================

variable "aws_region" {
  description = "Target AWS deployment region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Target deployment environment (staging, production)"
  type        = string
  default     = "staging"
}

variable "project_name" {
  description = "Project identifier for naming and tagging"
  type        = string
  default     = "cipherpage"
}

variable "vpc_cidr" {
  description = "CIDR block for the CipherPage VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets. Set false for ultra-low-cost staging."
  type        = bool
  default     = false
}

variable "neon_database_url_secret_arn" {
  description = "Secrets Manager ARN containing the owner-supplied Neon DATABASE_URL"
  type        = string
}

variable "firebase_admin_secret_arn" {
  description = "Secrets Manager ARN containing the Firebase Admin service-account JSON"
  type        = string
}

variable "firebase_project_id" {
  description = "Firebase project ID expected in verified Firebase ID tokens"
  type        = string
}

variable "allowed_origins" {
  description = "Exact HTTPS web origins allowed to call the API in this remote environment"
  type        = list(string)

  validation {
    condition     = length(var.allowed_origins) > 0 && alltrue([for origin in var.allowed_origins : can(regex("^https://[^/]+$", origin))])
    error_message = "Set at least one exact HTTPS frontend origin; wildcard and non-HTTPS origins are not allowed."
  }
}

variable "backend_cpu" {
  description = "Fargate CPU units for FastAPI backend (256, 512, 1024)"
  type        = number
  default     = 512
}

variable "backend_memory" {
  description = "Fargate Memory (MB) for FastAPI backend"
  type        = number
  default     = 1024
}

variable "frontend_cpu" {
  description = "Fargate CPU units for Next.js frontend"
  type        = number
  default     = 512
}

variable "frontend_memory" {
  description = "Fargate Memory (MB) for Next.js frontend"
  type        = number
  default     = 1024
}

variable "backend_image" {
  description = "ECR/Docker image URI for backend service"
  type        = string
  default     = "cipherpage-backend:latest"
}

variable "frontend_image" {
  description = "ECR/Docker image URI for frontend service"
  type        = string
  default     = "cipherpage-web:latest"
}

variable "monthly_budget_usd" {
  description = "AWS Budgets spending threshold in USD for cost alerts (OPS-11)"
  type        = number
  default     = 15
}

variable "alert_email" {
  description = "Notification email for AWS budget spending alerts"
  type        = string
  default     = "devops@cipherpage.com"
}
