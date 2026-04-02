# Task Management API — AWS DevOps Portfolio Project

A production-ready REST API built with Flask and deployed on AWS using modern DevOps practices. This project demonstrates end-to-end infrastructure automation, containerization, and CI/CD pipelines.

---

## Live Demo

**Base URL:** `http://task-management-alb-1477417359.ap-south-1.elb.amazonaws.com`

```bash
curl http://task-management-alb-1477417359.ap-south-1.elb.amazonaws.com/health
# {"status":"healthy","timestamp":"..."}
```

---

## Architecture

```
Developer pushes code to GitHub
          │
          ▼
  GitHub Actions (CI/CD)
  ┌─────────────────────┐
  │ 1. Build Docker image│
  │ 2. Push to ECR       │
  │ 3. Deploy to ECS     │
  └─────────────────────┘
          │
          ▼
    AWS Infrastructure
  ┌─────────────────────────────────────────┐
  │                                         │
  │   Internet                              │
  │       │                                 │
  │       ▼                                 │
  │  ALB (Load Balancer)                    │
  │  ap-south-1a  │  ap-south-1b            │
  │       │                                 │
  │       ▼                                 │
  │  ECS Fargate (2 containers)             │
  │  [Flask + Gunicorn]                     │
  │       │                                 │
  │       ▼                                 │
  │  RDS PostgreSQL (private subnet)        │
  │                                         │
  └─────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Application** | Python, Flask, SQLAlchemy, Gunicorn |
| **Database** | AWS RDS PostgreSQL |
| **Containerization** | Docker |
| **Container Registry** | AWS ECR |
| **Container Orchestration** | AWS ECS Fargate |
| **Load Balancer** | AWS ALB |
| **Infrastructure as Code** | Terraform |
| **CI/CD** | GitHub Actions |
| **Secrets Management** | AWS Secrets Manager |
| **Monitoring & Logging** | AWS CloudWatch |
| **Networking** | AWS VPC, Public/Private Subnets, NAT Gateway |

---

## Infrastructure Overview

All infrastructure is defined as code using Terraform (`infra/`):

| File | What it creates |
|---|---|
| `network.tf` | VPC, subnets, internet gateway, NAT gateway, route tables |
| `security_groups.tf` | Firewall rules for ALB, ECS, RDS |
| `ecr.tf` | Docker image registry with lifecycle policy |
| `ecs.tf` | ECS cluster, task definition, service, auto-scaling |
| `rds.tf` | PostgreSQL database in private subnet |
| `alb.tf` | Load balancer, target group, listener |
| `iam.tf` | IAM roles and policies for ECS |
| `secrets.tf` | Secrets Manager for database credentials |

---

## CI/CD Pipeline

Every push to `main` automatically:

1. Builds the Docker image
2. Pushes to ECR (tagged with commit SHA + `latest`)
3. Updates the ECS task definition with the new image
4. Deploys to ECS and waits for service stability

```yaml
push to main → build → push to ECR → update task def → deploy to ECS
```

---

## API Endpoints

### Health Check
```
GET /health
```
```json
{"status": "healthy", "timestamp": "2026-04-02T08:41:08.675145"}
```

### Create Task
```
POST /api/tasks
```
```json
// Request
{
  "title": "Setup CI/CD",
  "description": "Configure GitHub Actions",
  "priority": "high",
  "assigned_to": "komal"
}

// Response 201
{"id": 1, "title": "Setup CI/CD", "status": "pending", "message": "Task created successfully"}
```

### Get All Tasks
```
GET /api/tasks
```
```json
[
  {"id": 1, "title": "Setup CI/CD", "status": "pending", "priority": "high", "assigned_to": "komal", "created_at": "..."},
  {"id": 2, "title": "Write unit tests", "status": "pending", "priority": "medium", "assigned_to": "komal", "created_at": "..."}
]
```

### Get Single Task
```
GET /api/tasks/:id
```

### Update Task
```
PUT /api/tasks/:id
```
```json
// Request
{"status": "completed", "priority": "low"}

// Response 200
{"id": 1, "message": "Task updated successfully"}
```

### Delete Task
```
DELETE /api/tasks/:id
```
```json
{"message": "Task deleted successfully"}
```

### Task Statistics
```
GET /api/stats
```
```json
{"total_tasks": 3, "completed": 1, "pending": 1, "in_progress": 1}
```

---

## Project Structure

```
my-flask-app/
├── app/
│   ├── app.py                  # Flask application
│   ├── Dockerfile              # Container definition
│   ├── requirements.txt        # Python dependencies
│   └── task-definition.json    # ECS task definition template
├── infra/
│   ├── network.tf              # VPC and networking
│   ├── security_groups.tf      # Firewall rules
│   ├── ecr.tf                  # Container registry
│   ├── ecs.tf                  # Container orchestration
│   ├── rds.tf                  # Database
│   ├── alb.tf                  # Load balancer
│   ├── iam.tf                  # Permissions
│   ├── secrets.tf              # Secrets management
│   ├── outputs.tf              # Infrastructure outputs
│   ├── variables.tf            # Input variables
│   ├── providers.tf            # AWS provider config
│   └── terraform.tfvars        # Variable values
└── .github/
    └── workflows/
        └── deploy.yml          # CI/CD pipeline
```

---

## How to Deploy

### Prerequisites
- AWS CLI configured
- Terraform installed
- Docker installed

### 1. Clone the repo
```bash
git clone https://github.com/komal-sd/my-flask-app.git
cd my-flask-app
```

### 2. Deploy infrastructure
```bash
cd infra
terraform init
terraform apply
```

### 3. Add GitHub Secrets
In your GitHub repo settings → Secrets:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### 4. Push to main
```bash
git push origin main
```
GitHub Actions will build and deploy automatically.

---

## Key DevOps Concepts Demonstrated

- **Infrastructure as Code** — entire AWS infrastructure defined in Terraform, versioned in git
- **Containerization** — app packaged in Docker for consistent environments
- **CI/CD** — zero-touch deployments on every git push
- **Auto Scaling** — ECS scales containers based on CPU/memory usage
- **Security** — app runs in private subnets, only ALB is public-facing
- **Secrets Management** — no hardcoded credentials, using AWS Secrets Manager
- **Observability** — centralized logging with CloudWatch
- **High Availability** — deployed across 2 availability zones
