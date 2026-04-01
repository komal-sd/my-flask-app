resource "aws_secretsmanager_secret" "rds_password" {
  name        = "${var.project_name}-rds-password"
  description = "RDS database password"
}

resource "aws_secretsmanager_secret_version" "rds_password" {
  secret_id     = aws_secretsmanager_secret.rds_password.id
  secret_string = var.rds_password
}