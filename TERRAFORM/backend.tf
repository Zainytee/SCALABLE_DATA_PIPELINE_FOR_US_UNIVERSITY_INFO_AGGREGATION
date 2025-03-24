terraform{
    backend "s3" {
      bucket = "my-tf-state-bucket-hackathon"
      region = "eu-central-1"
      key = "product/product.tfstate"
    }
}