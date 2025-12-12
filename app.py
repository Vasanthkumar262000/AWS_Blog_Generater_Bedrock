import boto3
import botocore.config
import os 
import json
from datetime import datetime


def aws_blog_generator(blogtopic:str)->str:
    prompt = f"""<s>[INST]Human: Write a detailed blog post about {blogtopic} in markdown 
    format with 100 words and it has to be clear and interesting."""


    body = {
        "prompt": prompt,
        "max_gen_len": 500,
        "temperature": 0.7,
        "top_p": 0.95,
    }

    try:
        bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1",
                                config=botocore.config.Config(
                                    read_timeout=300, retries={"max_attempts": 3}))
        
        response= bedrock.invoke_model(body=json.dumps(body),
            modelId="meta.llama3-8b-instruct-v1:0")
        
        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        blog_details = response_data['generation']

        return blog_details
    
    except Exception as e:
        print(f"Error generating blog post: {e}")
        return "Error generating blog post."
    

def save_blog_to_s3( s3_key, s3_bucket, generate_blog):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_blog)
        print(f"Blog post saved to s3://{s3_bucket}/{s3_key}")
    except Exception as e:
        print(f"Error saving blog post to S3: {e}")



def lambda_handler(event, context):
    # TODO implement
    event=json.loads(event['body'])
    blogtopic = event['blogtopic']

    generate_blog =aws_blog_generator(blogtopic=blogtopic)

    if generate_blog:
        current_time = datetime.now().strftime("%H:%M:%S")
        s3_key = f"blog-output/{current_time}.txt"
        s3_bucket="aws-blog-generator-using-bedrock"
        save_blog_to_s3(s3_key, s3_bucket,generate_blog)
    else:
        print("No blog generated.")

    return {
        'statusCode': 200,
        'body': json.dumps('Blog generation process completed.')
    }
        
        
