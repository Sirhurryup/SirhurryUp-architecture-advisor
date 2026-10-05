# AWS Account Boundaries

SirhurryUp uses separate AWS accounts to maintain clear workload boundaries.

## Sirhurryup

The Sirhurryup account contains legacy and personal portfolio workloads, including docdott.com.

## SirhurryUp Managed Websites

Client production workloads belong in the SirhurryUp Managed Websites account.

Client websites and related production resources must not be deployed in the management account.

## SirhurryUp Management

The SirhurryUp Management account is reserved for AWS Organizations management and governance.

Client production workloads must never be deployed in this account.
