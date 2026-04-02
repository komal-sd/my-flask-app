#=================== RDS SUBNET GROUP =====================
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = aws_subnet.private_rds[*].id

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}
# ================== RDS DATABASE ========================
resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-db"
  engine         = "postgres"
  engine_version = "15"

  instance_class    = var.rds_instance_class
  allocated_storage = var.rds_allocated_storage
  storage_encrypted = true

  db_name  = var.rds_database_name
  username = var.rds_username
  password = var.rds_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  multi_az            = var.rds_multi_az
  publicly_accessible = false
  skip_final_snapshot = true
  tags = {
    Name = "${var.project_name}-db"
  }

}