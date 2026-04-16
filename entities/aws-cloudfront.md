---     
title: Amazon CloudFront
created: 2026-04-16
updated: 2026-04-16
type: entity
tags: [aws, cloud, cdn, content-delivery]     
sources: [raw/articles/aws-cloudfront-2026.md]  
---  
# Amazon CloudFront
  
Amazon CloudFront is a fast, secure, and programmable CDN that delivers data, videos, applications, and APIs globally with low latency and high transfer speeds.
  
## Key Features
  
### Performance and Global Reach
- **750+ globally dispersed Points of Presence (PoPs)**
- Intelligent routing to reduce latency  
- Edge termination, gRPC, and WebSockets support
  
### Security
- Built-in AWS Shield Standard (DDoS protection, no extra cost)
- Traffic encryption, field-level encryption, VPC origins
- Compliance with security standards
  
### Cost Optimization
- **Zero fees** for data transfer from AWS origins to CloudFront
- Request consolidation reduces origin costs
- Flexible pricing options
  
### Edge Programmability
Run custom code at the edge without managing servers.
  
## Primary Use Cases
  
| Use Case | Capabilities |
|----------|--------------|
| Web Delivery | Built-in compression, millisecond global reach |
| API Acceleration | Optimized for dynamic content |
| Video Streaming | Integration with AWS Media Services |
| Software Distribution | Automatic scaling for patches, games, IoT OTA |
  
## Customer Success
  
- **Zalando:** 100k transactions per second
- **SuperCell:** 250 million monthly users, low latency gaming
- **NBCUniversal:** Most live-streamed Super Bowl in history
- **Atlassian:** Increased security and performance
  
## Related Services
  
- [[aws-s3|S3]] — Origin for static content
- [[aws-lambda|Lambda@Edge]] — Custom logic at edge locations
- [[aws-shield|AWS Shield]] — DDoS protection (built into CloudFront)
- [[aws-route53|Route 53]] — DNS routing to CloudFront
  
## References
  
- [CloudFront Product Page](https://aws.amazon.com/cloudfront/)
- [CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
