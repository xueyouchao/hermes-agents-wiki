---   
title: Amazon VPC
created: 2026-04-16
updated: 2026-04-16
type: entity
tags: [aws, cloud, networking, vpc]  
sources: [https://aws.amazon.com/vpc/]
---
# Amazon Virtual Private Cloud (VPC)

Amazon VPC allows users to define and launch AWS resources in a logically isolated virtual network. It provides full control over the virtual networking environment, including resource placement, connectivity, and security.

## Core Functionality

1. **Setup:** Define the virtual network in AWS console
2. **Resource Integration:** Add EC2, RDS, and other services to the VPC
3. **Connectivity:** Configure cross-account, cross-AZ, or cross-region communication

## Key Benefits

- **Enhanced Security:** Screen traffic, restrict instance access, monitor connections
- **Operational Efficiency:** Faster setup, management, and validation of virtual networks
- **Granular Control:** Customize IP ranges, subnets, and route tables

## Primary Use Cases

| Use Case | Description |
|----------|-------------|
| Simple Web Hosting | Websites with enforced security rules |
| Multi-tier Applications | Strict isolation between web, app, and database tiers |
| Hybrid Cloud | VPCs connected to on-premises data centers |

## Customer Success

- **Tableau:** Scale faster, improve SaaS resiliency
- **Atlassian:** 45% reduction in Bitbucket response times
- **Samsung Heavy Industries:** Connect shipping networks and route data traffic

## Related Services

- [[aws-ec2|EC2]] — Compute instances in VPC
- [[aws-rds|RDS]] — Databases in private subnets
- [[aws-vpc|Route 53]] — DNS within VPC (private DNS)
- [[aws-iam|IAM]] — Access control for VPC resources

## References

- [VPC Product Page](https://aws.amazon.com/vpc/)
- [VPC Documentation](https://docs.aws.amazon.com/vpc/)
