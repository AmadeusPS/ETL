# ---------------------------------------------------------------------------
# EventBridge rules to trigger scraping 2x/day
# Invokes a Lambda that enqueues Celery task via Redis/SQS
# ---------------------------------------------------------------------------

resource "aws_cloudwatch_event_rule" "scrape_morning" {
  name                = "${var.project}-scrape-morning"
  description         = "Trigger scraping at 08:00 Lisbon (UTC+1)"
  schedule_expression = "cron(0 7 * * ? *)"  # 07:00 UTC = 08:00 WEST
}

resource "aws_cloudwatch_event_rule" "scrape_evening" {
  name                = "${var.project}-scrape-evening"
  description         = "Trigger scraping at 20:00 Lisbon (UTC+1)"
  schedule_expression = "cron(0 19 * * ? *)"  # 19:00 UTC = 20:00 WEST
}

# ---------------------------------------------------------------------------
# Lambda function that enqueues the Celery task
# (Lambda code lives in infra/lambda/trigger_scrape.py)
# ---------------------------------------------------------------------------
resource "aws_iam_role" "lambda_scrape" {
  name = "${var.project}-lambda-scrape"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_scrape.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Placeholder Lambda (package separately and upload to S3 before applying)
resource "aws_lambda_function" "trigger_scrape" {
  function_name = "${var.project}-trigger-scrape"
  role          = aws_iam_role.lambda_scrape.arn
  handler       = "trigger_scrape.handler"
  runtime       = "python3.12"
  filename      = "${path.module}/lambda_placeholder.zip"  # Replace with real package

  environment {
    variables = {
      REDIS_URL = "redis://<elasticache-endpoint>:6379/0"
    }
  }

  vpc_config {
    subnet_ids         = module.vpc.private_subnets
    security_group_ids = [aws_security_group.ecs_tasks.id]
  }
}

resource "aws_cloudwatch_event_target" "scrape_morning" {
  rule = aws_cloudwatch_event_rule.scrape_morning.name
  arn  = aws_lambda_function.trigger_scrape.arn
}

resource "aws_cloudwatch_event_target" "scrape_evening" {
  rule = aws_cloudwatch_event_rule.scrape_evening.name
  arn  = aws_lambda_function.trigger_scrape.arn
}

resource "aws_lambda_permission" "allow_eventbridge_morning" {
  statement_id  = "AllowEventBridgeMorning"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trigger_scrape.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scrape_morning.arn
}

resource "aws_lambda_permission" "allow_eventbridge_evening" {
  statement_id  = "AllowEventBridgeEvening"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trigger_scrape.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scrape_evening.arn
}
