import type { Service } from "../types/Service"
import ec2Icon from "../assets/images/aws-ec2.webp"
import lambdaIcon from "../assets/images/aws-lambda.webp"
import s3Icon from "../assets/images/aws-s3.webp"
import dynamodbIcon from "../assets/images/aws-dynamodb.webp"
import cloudfrontIcon from "../assets/images/aws-cloudfront.webp"

export const services = [
  "ec2",
  "lambda",
  "s3",
  "dynamodb",
  "cloudfront"
] as const

// Asterisk means ue1-only
export const serviceLabels: Record<Service, string> = {
  ec2: "EC2",
  lambda: "Lambda",
  s3: "S3",
  dynamodb: "DDB",
  cloudfront: "CF*"
}

export const serviceIcons: Record<Service, string> = {
  ec2: ec2Icon,
  lambda: lambdaIcon,
  s3: s3Icon,
  dynamodb: dynamodbIcon,
  cloudfront: cloudfrontIcon
}
