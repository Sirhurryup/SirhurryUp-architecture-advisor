# SirhurryUp Architecture Advisor

A grounded Retrieval-Augmented Generation (RAG) prototype built to answer architecture questions using SirhurryUp's own technical documentation.

## The Business Problem

As technical documentation grows, finding the right information becomes harder. Engineers may know that an answer exists somewhere in the documentation but still have to search across multiple files to find it.

The SirhurryUp Architecture Advisor explores a different approach:

> Ask a question in natural language, retrieve relevant evidence from the company's documentation, and use a foundation model to generate an answer grounded in that evidence.

The goal is not to give the model unrestricted authority to answer architecture questions. The goal is to make company documentation the source of truth.

## What I Built

The prototype combines:

- Markdown documents as the initial knowledge source
- Sentence Transformers for local text embeddings
- Semantic similarity for document retrieval
- Python for retrieval and prompt assembly
- Amazon Bedrock for managed foundation-model access
- Amazon Nova Micro for text generation
- Grounding instructions that tell the model not to answer beyond the supplied documentation

The current request flow is:

Question → Embedding → Semantic Retrieval → Retrieved Evidence → Prompt Augmentation → Amazon Bedrock → Nova Micro → Grounded Answer

## How RAG Works in This Project

The Architecture Advisor uses three stages:

**Retrieval** — Find the SirhurryUp documentation most relevant to the user's question.

**Augmentation** — Combine the retrieved evidence with the user's question and the application's grounding instructions.

**Generation** — Send that assembled context through Amazon Bedrock to Nova Micro, which generates an answer based on the supplied evidence.

In short:

> Retrieve the relevant information → combine it with the rules and question → generate a grounded answer.

RAG does not retrain the foundation model on SirhurryUp documentation. It supplies relevant company knowledge to the model at request time.

## Hidden Gems: What the Happy Path Did Not Show

Building the pipeline exposed several lessons that were easy to miss when looking only at successful examples.

### AWS CLI Configuration Is Local

AWS CLI profiles configured on one computer do not automatically exist on another. Each development machine needs its own local AWS CLI configuration.

Before making AWS calls, verify the active identity:

```bash
aws sts get-caller-identity --profile sirhurryup-sandbox
```

### AWS CLI Authentication Does Not Automatically Mean boto3 Is Ready

The AWS CLI successfully authenticated with `aws login`, but the Python application initially failed when boto3 attempted to use the same login credentials.

The error revealed that the login credential provider required AWS CRT support:

```bash
pip install "botocore[crt]"
```

The important troubleshooting lesson was to identify the failing boundary before changing application code.

### Region Configuration Can Exist at Multiple Layers

The Bedrock Runtime client explicitly used `us-east-1`, but credential refresh still produced a `NoRegionError`.

The Sandbox profile also needed a Region:

```bash
aws configure set region us-east-1 --profile sirhurryup-sandbox
```

A Region configured for an AWS service client does not necessarily satisfy every SDK or authentication operation.

### Successful Retrieval Does Not Mean Good Retrieval

The semantic search code worked correctly but sometimes ranked weak evidence above the information that actually answered the question.

This demonstrated an important distinction:

> Semantic similarity is not the same as relevance or answerability.

Retrieval quality must therefore be evaluated independently from model quality.

### The LLM Is Not Always the Problem

A poor generated answer can begin with poor evidence upstream. Debugging a RAG system means examining the entire path:

Question → Retrieval → Evidence → Prompt → Model → Response

Blaming the model without inspecting retrieval can hide the actual failure.

### Grounding Can Prevent Unsupported Answers

When asked which EC2 instance type SirhurryUp should use for PostgreSQL, the retriever still returned its closest available chunks even though none answered the question.

Nova Micro responded:

> I don't have enough information in the documentation.

That refusal was desirable behavior. The model followed the grounding instructions rather than inventing an unsupported company recommendation.
