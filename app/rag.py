import boto3
from botocore.exceptions import ClientError

from retrieval import retrieve


# AWS CONFIGURATION
PROFILE_NAME = "sirhurryup-sandbox"
REGION = "us-east-1"
MODEL_ID = "amazon.nova-micro-v1:0"


# USER QUESTION
question = "What does CloudFront use to access the private S3 bucket?"


# RETRIEVE RELEVANT EVIDENCE
results = retrieve(question, top_k=3)

MIN_RELEVANCE_SCORE = 0.60

results = [
    result
    for result in results
    if result["score"] >= MIN_RELEVANCE_SCORE
]

if not results:
    print("\nINSUFFICIENT RETRIEVAL EVIDENCE")
    print(
        "No retrieved documentation met the "
        f"{MIN_RELEVANCE_SCORE:.2f} relevance threshold."
    )
    raise SystemExit

retrieved_context = "\n\n".join(
    result["text"] for result in results
)


# GROUNDING INSTRUCTIONS
system_prompt = """
    Answer the user's question using only the provided SirhurryUp documentation.

    If the documentation directly supports an answer, answer concisely
    using that evidence. Do not require additional implementation details
    unless the user asks for them.

    If the documentation does not support an answer,
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