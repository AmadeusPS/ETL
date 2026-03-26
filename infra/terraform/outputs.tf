output "api_url" {
  description = "ALB DNS name for the backend API"
  value       = "https://${aws_lb.api.dns_name}"
}

output "ecr_api_url" {
  description = "ECR repository URL for the API image"
  value       = aws_ecr_repository.api.repository_url
}

output "ecr_worker_url" {
  description = "ECR repository URL for the worker image"
  value       = aws_ecr_repository.worker.repository_url
}
