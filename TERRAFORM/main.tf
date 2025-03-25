#Creating an IAM USER for the project
resource "aws_iam_user" "dec" {
  name = "dec_hackhaton"
  path = "/"

  tags = {
    tag-key = "hackathon"
  }
}


#Creating an access key for the IAM user
resource "aws_iam_access_key" "dec" {
  user = aws_iam_user.dec.name
}


#Defining an IAM policy document
data "aws_iam_policy_document" "dec_s3" {
  statement {
    effect    = "Allow"
    actions   = ["s3:*"]
    resources = ["*"]
  }
}


#Attaching the policy to the IAM user
resource "aws_iam_user_policy" "dec_s3" {
  name   = "dec_policy"
  user   = aws_iam_user.dec.name
  policy = data.aws_iam_policy_document.dec_s3.json
}


#Create an s3 bucket to store terraform state file
resource "aws_s3_bucket" "dec_state_bucket" {
  bucket = "my-tf-state-bucket-hackathon20"

  tags = {
    Name        = "terraform_state bucket"
    Environment = "Dev"
  }
}


#Create an s3 bucket for the raw data
resource "aws_s3_bucket" "dec_data_bucket" {
  bucket = "my-tf-data-bucket-hackathon20"

  tags = {
    Name        = "Data Bucket"
    Environment = "Dev"
  }
}

#Creating console login for the IAM user

resource "aws_iam_user_login_profile" "hackathon_user_profile" {
  user    = aws_iam_user.dec.name
  password_reset_required = false
}

#To retrieve default password for the iam user

output "iam_user_password" {
  value = aws_iam_user_login_profile.hackathon_user_profile.password
  sensitive = true
}
