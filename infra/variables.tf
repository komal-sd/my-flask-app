#AWS Region
variable "aws_region" {
  description = "AWS region where resources will be created"
  type        = string
}

#Environment
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

#Project name
variable "project_name" {
  description = "Project name for resources naming"
  type        = string
}

# ============= VPC ================
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string

}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)

}

# ============ SUBNETS ============

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks"
  type        = list(string)

}

variable "private_ecs_subnet_cidrs" {
  description = "Private ECS subnet CIDR blocks"
  type        = list(string)

}

variable "private_rds_subnet_cidrs" {
  description = "Private RDS subnet CIDR blocks"
  type        = list(string)

}

# ============ ECS ============

variable "ecs_task_cpu" {
  description = "ECS task CPU units"
  type        = string
}

variable "ecs_task_memory" {
  description = "ECS task memory in MB"
  type        = string
}

variable "ecs_desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
}

variable "app_port" {
  description = "Application port"
  type        = number
}

variable "app_image" {
  description = "Docker image URL for ECS task"
  type        = string
}

# ============ RDS ============

variable "rds_instance_class" {
  description = "RDS instance type"
  type        = string
}

variable "rds_allocated_storage" {
  description = "RDS storage in GB"
  type        = number
}

variable "rds_username" {
  description = "RDS master username"
  type        = string
  sensitive   = true
}

variable "rds_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
}

variable "rds_database_name" {
  description = "RDS database name"
  type        = string
}

variable "rds_multi_az" {
  description = "Enable Multi-AZ for RDS"
  type        = bool
}
