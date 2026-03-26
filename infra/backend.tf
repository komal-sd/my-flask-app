terraform {
  backend "s3" {
    bucket         = "task-management-tfstate-komal-1774522825"
    key            = "dev/terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
    use_lockfile   = true
  }
}
