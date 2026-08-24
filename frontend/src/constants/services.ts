import type { Service } from "../types/Service"
import ec2Icon from "../assets/images/aws-ec2.webp"
import lambdaIcon from "../assets/images/aws-lambda.webp"
import s3Icon from "../assets/images/aws-s3.webp"
import dynamodbIcon from "../assets/images/aws-dynamodb.webp"
import cloudfrontIcon from "../assets/images/aws-cloudfront.webp"

export const services = [
  "EC2",
  "Lambda",
  "S3",
  "DynamoDB",
  "CloudFront"
] as const

// Asterisk means ue1-only
export const serviceLabels: Record<Service, string> = {
  EC2: "EC2",
  Lambda: "Lambda",
  S3: "S3",
  DynamoDB: "DDB",
  CloudFront: "CF*"
}

export const serviceIcons: Record<Service, string> = {
  EC2: ec2Icon,
  Lambda: lambdaIcon,
  S3: s3Icon,
  DynamoDB: dynamodbIcon,
  CloudFront: cloudfrontIcon
}
