# ==============================================================================
# CipherPage Infrastructure as Code - Terraform Outputs
# Conforms to SRS v2.2 OPS-05, OPS-07, OPS-11
# ==============================================================================

output "alb_dns_name" {
  description = "Public DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Route53 Hosted Zone ID for ALB alias mapping"
  value       = aws_lb.main.zone_id
}

output "ecs_cluster_name" {
  description = "ECS Fargate Cluster name"
  value       = aws_ecs_cluster.main.name
}

output "backend_service_name" {
  description = "ECS Backend FastAPI service name"
  value       = aws_ecs_service.backend.name
}

output "frontend_service_name" {
  description = "ECS Frontend Next.js service name"
  value       = aws_ecs_service.frontend.name
}

output "s3_course_assets_bucket" {
  description = "S3 Bucket name for course PDFs, videos, and materials"
  value       = aws_s3_bucket.course_assets.bucket
}

output "cloudwatch_log_groups" {
  description = "CloudWatch log groups created for service containers"
  value = {
    backend  = aws_cloudwatch_log_group.backend.name
    frontend = aws_cloudwatch_log_group.frontend.name
    celery   = aws_cloudwatch_log_group.celery.name
  }
}
