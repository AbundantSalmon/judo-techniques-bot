variable "region" {
  default     = "us-east-2"
  description = "AWS region to deploy to"
}

variable "env-location" {
  default     = "/secrets/"
  description = "Folder location of the .env file, including trailing slash"
}

variable "env-file-location" {
  default     = "/secrets/.env"
  description = "Full path location of the .env file, including trailing slash"
}
