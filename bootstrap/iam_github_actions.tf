###########################################################################
################       G I T H U B   A C T I O N S        ################
###########################################################################

####----------------------------------------------------------####
####----  Provider OIDC do GitHub Actions para a AWS      ----####
####----------------------------------------------------------####
resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com"
  ]
}


####----------------------------------------------------------####
####----  Role assumida pelo GitHub Actions via OIDC      ----####
####----------------------------------------------------------####
resource "aws_iam_role" "github_actions_role" {
  name                 = "${var.app_name}-github-actions-role"
  max_session_duration = 3600

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"

      Principal = {
        Federated = aws_iam_openid_connect_provider.github.arn
      }

      Action = "sts:AssumeRoleWithWebIdentity"

      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }

        StringLike = {
          "token.actions.githubusercontent.com:sub" = "repo:carlafs1/website-s3-iac-cv:*"
        }
      }
    }]
  })
}


####------------------------------------------------------------------------####
####----  Permissões do GitHub Actions para executar o Terraform Apply  ----####
####------------------------------------------------------------------------####
resource "aws_iam_role_policy" "github_actions_terraform" {
  name = "${var.app_name}-github-actions-terraform-policy"
  role = aws_iam_role.github_actions_role.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "S3Efemero"
        Effect = "Allow"
        Action = [
          "s3:CreateBucket",
          "s3:GetBucketLocation",
          "s3:GetBucketAcl",
          "s3:GetBucketPolicy",
          "s3:GetBucketWebsite",
          "s3:GetBucketOwnershipControls",
          "s3:GetBucketPublicAccessBlock",
          "s3:GetBucketTagging",
          "s3:PutBucketTagging",
          "s3:GetBucketCORS",
          "s3:GetBucketVersioning",
          "s3:GetAccelerateConfiguration",
          "s3:GetBucketRequestPayment",
          "s3:GetBucketLogging",
          "s3:GetLifecycleConfiguration",
          "s3:GetReplicationConfiguration",
          "s3:GetEncryptionConfiguration",
          "s3:GetBucketObjectLockConfiguration",
          "s3:PutBucketPublicAccessBlock",
          "s3:PutBucketWebsite",
          "s3:PutObject",
          "s3:PutBucketPolicy",
          "s3:GetObject",
          "s3:GetObjectTagging",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::website-s3-iac-cv-efemero-*",
          "arn:aws:s3:::website-s3-iac-cv-efemero-*/*"
        ]
      },
      {
        Sid    = "LambdaCreate"
        Effect = "Allow"
        Action = [
          "lambda:CreateFunction",
          "lambda:GetFunction",
          "lambda:GetFunctionConfiguration",
          "lambda:GetFunctionCodeSigningConfig",
          "lambda:ListVersionsByFunction",
          "lambda:InvokeFunction",
          "lambda:GetPolicy"
        ]
        Resource = [
          "arn:aws:lambda:us-east-2:715428148112:function:website-s3-iac-cv-acesso",
          "arn:aws:lambda:us-east-2:715428148112:function:website-s3-iac-cv-controle"
        ]
      },
      {
        Sid      = "LambdaControlePermission"
        Effect   = "Allow"
        Action   = "lambda:AddPermission"
        Resource = "arn:aws:lambda:us-east-2:715428148112:function:website-s3-iac-cv-controle"
      },
      {
        Sid    = "EventBridgeLifecycle"
        Effect = "Allow"
        Action = [
          "events:PutRule",
          "events:DescribeRule",
          "events:ListTagsForResource",
          "events:PutTargets",
          "events:ListTargetsByRule"
        ]
        Resource = "arn:aws:events:us-east-2:715428148112:rule/website-s3-iac-cv-controle"
      },
      {
        Sid      = "PassAcessoLambdaRole"
        Effect   = "Allow"
        Action   = "iam:PassRole"
        Resource = "arn:aws:iam::715428148112:role/website-s3-iac-cv-acesso-lambda-role"
      },
      {
        Sid      = "ReadAcessoLambdaRole"
        Effect   = "Allow"
        Action   = "iam:GetRole"
        Resource = "arn:aws:iam::715428148112:role/website-s3-iac-cv-acesso-lambda-role"
      },
      {
        Sid      = "ReadSiteTimeoutParameter",
        Effect   =  "Allow",
        Action   =  "ssm:GetParameter"
        Resource = "arn:aws:ssm:us-east-2:715428148112:parameter/website-s3-iac-cv/site-timeout-minutes"
}
    ]
  })
}


####--------------------------------------------------------------------------####
####----  Permissões do GitHub Actions para executar o Terraform Destroy  ----####
####--------------------------------------------------------------------------####
resource "aws_iam_role_policy" "github_actions_terraform_destroy" {
  name = "${var.app_name}-github-actions-terraform-destroy-policy"
  role = aws_iam_role.github_actions_role.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "S3EfemeroDestroy"
        Effect = "Allow"
        Action = [
          "s3:DeleteBucketPolicy",
          "s3:DeleteBucketWebsite",
          "s3:DeleteObject",
          "s3:DeleteBucket",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::website-s3-iac-cv-efemero-*",
          "arn:aws:s3:::website-s3-iac-cv-efemero-*/*"
        ]
      },
      {
        Sid    = "LambdaDestroy"
        Effect = "Allow"
        Action = [
          "lambda:DeleteFunction",
          "lambda:RemovePermission",
          "lambda:GetFunction",
          "lambda:GetPolicy"
        ]
        Resource = [
          "arn:aws:lambda:us-east-2:715428148112:function:website-s3-iac-cv-acesso",
          "arn:aws:lambda:us-east-2:715428148112:function:website-s3-iac-cv-controle"
        ]
      },
      {
        Sid    = "EventBridgeDestroy"
        Effect = "Allow"
        Action = [
          "events:RemoveTargets",
          "events:DeleteRule",
          "events:DescribeRule",
          "events:ListTargetsByRule"
        ]
        Resource = "arn:aws:events:us-east-2:715428148112:rule/website-s3-iac-cv-controle"
      }
    ]
  })
}



################################################################################
################  T E R R A F O R M   R E M O T E   S T A T E  #################
################################################################################

####-----------------------------------------------------------------------####
####----  Permissões do GitHub Actions para acessar Terraform State     ----####
####-----------------------------------------------------------------------####
resource "aws_iam_role_policy" "github_actions_terraform_state" {
  name = "${var.app_name}-github-actions-terraform-state-policy"
  role = aws_iam_role.github_actions_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ListTerraformStateBucket"
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.terraform_state.arn
      },
      {
        Sid    = "ManageEfemeroTerraformState"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.terraform_state.arn}/efemero/terraform.tfstate"
      }
    ]
  })
}