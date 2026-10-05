import boto3
from botocore.exceptions import ClientError

from retrieval import retrieve


# AWS CONFIGURATION
PROFILE_NAME = "sirhurryup-sandbox"
REGION = "us-east-1"
MODEL_ID = "amazon.nova-micro-v1:0"


# USER QUESTION
question = "Which EC2 instance type should SirhurryUp use for its PostgreSQL database?"


# RETRIEVE RELEVANT EVIDENCE
results = retrieve(question, top_k=3)

retrieved_context = "\n\n".join(
    result["text"] for result in results
)


# GROUNDING INSTRUCTIONS
system_prompt = """
Answer using only the provided SirhurryUp documentation.

If the documentation does not contain enough information,
say: "I don't have enough information in the documentation."
"""


# AUGMENT THE QUESTION WITH RETRIEVED CONTEXT
prompt = f"""
CONTEXT:
{retrieved_context}

QUESTION:
{question}
"""


# CREATE AWS SESSION
session = boto3.Session(profile_name=PROFILE_NAME)

client = session.client(
    "bedrock-runtime",
    region_name=REGION
)


# INVOKE AMAZON NOVA MICRO
try:
    response = client.converse(
        modelId=MODEL_ID,

        system=[
            {
                "text": system_prompt
            }
        ],

        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],

        inferenceConfig={
            "maxTokens": 200,
            "temperature": 0.0
        }
    )

    answer = response["output"]["message"]["content"][0]["text"]

    print("\nQUESTION:")
    print(question)

    print("\nRETRIEVED EVIDENCE:")

    for index, result in enumerate(results, start=1):
        print(
            f"\n{index}. "
            f"{result['filename']} "
            f"(score: {result['score']:.4f})"
        )
        print(result["text"])

    print("\nNOVA RESPONSE:")
    print(answer)


except ClientError as error:
    print("\nBEDROCK ERROR:")
    print(error)