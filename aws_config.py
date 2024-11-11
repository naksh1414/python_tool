import boto3

# AWS configuration
region = 'ap-south-1'
# Provide your AWS credentials here (hardcoded)
aws_access_key_id = 'AKIAS74TL3RIJTIIUJ7R'
aws_secret_access_key = 'qOSvs61cB7CIVENvc5gbOcekTBASj2C1ptqExYgI'

# S3 client with hardcoded credentials
s3 = boto3.client(
    's3',
    region_name=region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# DynamoDB resource with hardcoded credentials
dynamodb = boto3.resource(
    'dynamodb',
    region_name=region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# DynamoDB Users Table
users_table = dynamodb.Table('Users')
