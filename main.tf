Here's the updated Terraform code without using `aws_s3_bucket_public_access_block` resource:


# main.tf
resource "aws_s3_bucket" "b" {
  bucket = "my-company-sensitive-data-bucket"

  # Block public access settings
  acl    = "private"
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
    expose_headers  = []
    max_age_seconds = 3000
  }

  lifecycle {
    prevent_destroy = true
  }
}


This updated code configures the bucket with private ACL and sets up CORS to allow only GET requests from any origin. The `prevent_destroy` lifecycle block prevents accidental deletion of the bucket.