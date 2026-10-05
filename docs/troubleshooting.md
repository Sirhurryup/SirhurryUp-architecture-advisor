# Website Troubleshooting

When a production website cannot be reached, troubleshoot the request path systematically.

Verify DNS resolution first.

Then verify that CloudFront is serving the expected distribution.

Verify the origin configuration and confirm that CloudFront can access the private S3 origin through Origin Access Control.

When recently deployed content is stale, verify the S3 object and determine whether a CloudFront invalidation is required.

Change one variable at a time and verify the result before continuing.
