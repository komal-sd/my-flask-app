resource "aws_secretsmanager_secret" "rds_passwords" {
  name        = "${var.project_name}-rds-password"
  description = "RDS database password"
}

resource "aws_secretsmanager_secret_version" "rds_password" {
  secret_id     = aws_secretsmanager_secret.rds_passwords.id
  secret_string = var.rds_password
}