# Production Website Architecture

SirhurryUp production static websites use a private Amazon S3 bucket as the origin.

Amazon CloudFront provides public content delivery and accesses the private S3 bucket through Origin Access Control.

TLS certificates used with CloudFront are provisioned through AWS Certificate Manager in us-east-1.

Amazon Route 53 Alias records route the production domain to the CloudFront distribution.

Public access to the S3 bucket remains blocked.
