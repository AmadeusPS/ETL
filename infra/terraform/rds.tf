# ---------------------------------------------------------------------------
# Security group for RDS
# ---------------------------------------------------------------------------
resource "aws_security_group" "rds" {
  name   = "${var.project}-rds-sg"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
    description     = "PostgreSQL from ECS tasks"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---------------------------------------------------------------------------
# RDS Subnet Group
# ---------------------------------------------------------------------------
resource "aws_db_subnet_group" "main" {
  name       = "${var.project}-db-subnet"
  subnet_ids = module.vpc.private_subnets
}

# ---------------------------------------------------------------------------
# RDS PostgreSQL instance  (swap for aws_rds_cluster for Aurora Serverless v2)
# ---------------------------------------------------------------------------
resource "aws_db_instance" "main" {
  identifier        = "${var.project}-${var.environment}"
  engine            = "postgres"
  engine_version    = "16"
  instance_class    = "db.t4g.micro"   # Scale up as needed
  allocated_storage = 20
  storage_encrypted = true

  db_name  = "pricewatch"
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  multi_az            = false  # Set true for production HA
  publicly_accessible = false
  skip_final_snapshot = true   # Set false for production

  backup_retention_period = 7
  deletion_protection     = false  # Set true for production

  tags = { Project = var.project, Environment = var.environment }
}

output "rds_endpoint" {
  value = aws_db_instance.main.endpoint
}
