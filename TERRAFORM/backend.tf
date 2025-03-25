terraform{
    backend "s3" {
      bucket = "my-tf-state-bucket-hackathon1"
      region = "us-east-1"
      key = "product/product.tfstate"
    }
}