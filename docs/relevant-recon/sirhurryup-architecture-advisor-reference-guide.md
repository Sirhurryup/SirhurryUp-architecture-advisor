# SirhurryUp Architecture Advisor — Project Reference Guide

## Mission

Keep this file as the fast review guide for the **SirhurryUp Architecture Advisor** prototype.

The project demonstrates a grounded Retrieval-Augmented Generation (RAG) pipeline using:

- Python
- Sentence Transformers
- Semantic similarity
- Local Markdown documentation
- boto3
- Amazon Bedrock Runtime
- Amazon Nova Micro
- Relevance gating
- Grounding instructions

The goal is not to build a general chatbot. The goal is to answer architecture questions from **SirhurryUp's own documented evidence** and behave safely when that evidence is insufficient.

---

## The Mental Model

**Find the relevant information → add it to the question and rules → generate a response based on the evidence.**

### Retrieval

The application searches SirhurryUp documentation for chunks semantically related to the question.

### Augmentation

The application combines:

- the user's question,
- retrieved evidence,
- and grounding instructions.

### Generation

The assembled context is sent through Amazon Bedrock Runtime to Amazon Nova Micro.

The documentation is **not permanently added to Nova's knowledge**. It is supplied as context when the question is asked.

---

## Current Pipeline

```text
SirhurryUp Markdown Documentation
              ↓
        Document Chunking
              ↓
   Sentence Transformer Embeddings
              ↓
      Semantic Similarity
              ↓
      Relevance Threshold
              ↓
       Retrieved Evidence
              ↓
 Question + Evidence + Grounding Rules
              ↓
       Amazon Bedrock Runtime
              ↓
         Amazon Nova Micro
              ↓
        Grounded Response
```

### Responsibilities by Layer

| Layer | Responsibility |
| --- | --- |
| Markdown docs | Company knowledge/source of truth |
| Chunking | Break documentation into retrievable units |
| Sentence Transformers | Convert text into embeddings |
| Similarity ranking | Rank chunks relative to the question |
| Relevance gate | Stop weak evidence before generation |
| Grounding prompt | Tell Nova how it may use the evidence |
| Bedrock Runtime | Managed model invocation |
| Nova Micro | Generate the final grounded response |

---

## Project Files

```text
sirhurryup-architecture-advisor/
├── app/
│   ├── embeddings.py
│   ├── retrieval.py
│   └── rag.py
├── docs/
│   ├── aws-account-boundaries.md
│   ├── production-websites.md
│   ├── troubleshooting.md
│   └── screenshots/
├── .gitignore
├── README.md
└── requirements.txt
```

### `app/embeddings.py`

Explores text embeddings and how semantic representation works.

### `app/retrieval.py`

Loads the embedding model, chunks documentation, computes semantic similarity, ranks evidence, and participates in relevance filtering.

### `app/rag.py`

Coordinates retrieval, relevance gating, prompt construction, Bedrock invocation, and response display.

### `docs/`

The prototype knowledge base and build evidence.

---

## Grounding Rules

The generation layer is instructed to answer from the provided SirhurryUp documentation.

The important behavior is:

- If the documentation directly supports the answer, answer concisely from that evidence.
- Do not demand implementation details that the user did not ask for.
- If the documentation does not support the answer, say:

> “I don't have enough information in the documentation.”

Grounding is not merely about getting the model to answer correctly. It is also about controlling what happens when the answer is **not present**.

---

## Relevance Gate

Current prototype threshold:

```text
0.60
```

### Why it exists

A retriever normally returns its closest available matches even when none are truly useful.

Without a gate:

```text
Question
   ↓
Closest available chunks
   ↓
Model receives weak evidence
```

With the gate:

```text
Question
   ↓
Retrieve + score
   ↓
Does evidence meet threshold?
   ├── No  → Stop: insufficient retrieval evidence
   └── Yes → Send evidence to Nova
```

### Important

`0.60` is an **experimental prototype value**, not a universal confidence threshold.

A production system would need a larger evaluation set before choosing or defending a threshold.

---

## Two Failure Protections

### Layer 1 — Retrieval protection

**Weak retrieval → stop before generation.**

The application can refuse to call Bedrock when retrieved evidence does not meet the relevance threshold.

### Layer 2 — Generation protection

**Insufficient evidence at generation → refuse rather than invent.**

Even evidence that passes retrieval still has to support the requested answer.

This is defense in depth.

---

## Key Tests

### Supported Question

**Question**

> What does CloudFront use to access the private S3 bucket?

**Strong retrieved evidence**

The documentation states that CloudFront accesses the private S3 bucket through **Origin Access Control**.

**Expected grounded answer**

> CloudFront uses Origin Access Control to access the private S3 bucket.

### Unsupported Question

**Question**

> Which EC2 instance type should SirhurryUp use for its PostgreSQL database?

The documentation does not contain enough information to make that company-specific recommendation.

The desired behavior is refusal rather than invention.

---

## Most Important Retrieval Lesson

**Semantic similarity is not the same as answerability.**

An embedding model can correctly identify semantically related text while still ranking a less useful chunk above the clearest evidence.

Therefore:

```text
Successful retrieval code ≠ high-quality retrieval
```

Always inspect the retrieved evidence.

---

## Troubleshooting Model

Treat RAG as a pipeline:

```text
Question
   ↓
Retrieval
   ↓
Evidence
   ↓
Prompt / Grounding Rules
   ↓
Bedrock Request
   ↓
Nova
   ↓
Response
```

When something goes wrong, identify the failing boundary before changing code.

### Principle

**Debug the boundary, not the symptom.**

---

## Hidden Gems

### 1. AWS profiles are machine-local

A profile available on one Mac does not automatically exist on another.

Verify identity:

```bash
aws sts get-caller-identity --profile sirhurryup-sandbox
```

### 2. Authentication has boundaries

The AWS CLI authenticating successfully does not prove every Python credential dependency is ready.

The project exposed the need for AWS CRT support in the boto3/botocore credential path.

### 3. Region exists at multiple layers

A Bedrock client Region does not necessarily satisfy credential/provider Region requirements.

Prototype profile configuration:

```bash
aws configure set region us-east-1 --profile sirhurryup-sandbox
```

### 4. External dependencies can masquerade as application hangs

Sentence Transformers attempted to contact Hugging Face even though the model had already been downloaded.

The traceback revealed the boundary.

### 5. The LLM is not always the problem

Before changing the prompt or model, inspect:

- retrieved chunks,
- similarity scores,
- relevance gating,
- AWS identity,
- Region,
- dependency/network calls,
- Bedrock request path.

---

## Local Run Checklist

### Activate the environment

```bash
source .venv/bin/activate
```

### Verify AWS authentication

```bash
aws sts get-caller-identity --profile sirhurryup-sandbox
```

If temporary authentication has expired, authenticate again using the configured profile workflow.

### Run

```bash
python app/rag.py
```

### Observe

Do not look only at the final response.

Inspect:

1. The question.
2. Retrieved filenames/chunks.
3. Similarity scores.
4. Whether the relevance gate passed.
5. The final Nova response.

---

## Current Limitations

The prototype intentionally does **not** yet include:

- a vector database,
- automated document ingestion,
- reranking,
- generated-answer citations,
- user authentication,
- an API or web interface,
- production monitoring,
- a large evaluation dataset,
- production deployment.

These are possible future extensions, not missing requirements for the current proof of concept.

---

## Future Review Path

When returning to this project, resist adding complexity immediately.

### Review first

1. Explain RAG without notes.
2. Run one supported question.
3. Run one unsupported question.
4. Inspect retrieval scores.
5. Explain why the relevance gate exists.
6. Explain why `0.60` is provisional.
7. Trace the complete request path to Nova.
8. Revisit one hidden-gem troubleshooting incident.

### Then consider extensions

Potential next experiments:

- Build a repeatable evaluation question set.
- Measure retrieval quality instead of relying on isolated examples.
- Test alternative chunking strategies.
- Explore reranking.
- Add source citations to generated answers.
- Evaluate a vector database only when the knowledge-base size earns the complexity.
- Add an API/UI only after the retrieval behavior is trustworthy.

---

## Portfolio / Interview Explanation

### 30-second version

> I built a grounded RAG architecture advisor using Python, Sentence Transformers, Amazon Bedrock, and Nova Micro. It retrieves evidence from SirhurryUp's own Markdown documentation, applies a relevance gate, and gives Nova only the context and rules needed to answer. I also tested unsupported questions so the system could fail closed rather than invent architecture recommendations.

### What made the project interesting

> The biggest lesson was that successful semantic search does not guarantee useful evidence. I had retrieval working technically while the best answer ranked lower than a related chunk. That pushed me to separate retrieval quality from model quality and add a relevance gate before generation.

### Engineering principle

> A RAG system is a pipeline. Debug the pipeline, not just the model.

---

## Evidence Map

The repository contains eight screenshots preserving the build path:

1. Nova Micro model details.
2. Initial grounded Bedrock response.
3. Successful boto3 → Bedrock invocation.
4. Semantic retrieval quality failure.
5. High-quality semantic retrieval.
6. End-to-end RAG pipeline success.
7. Unsupported-knowledge grounding test.
8. Relevance-gate grounded-answer success.

The failure screenshots matter as much as the successful ones because they explain **why the architecture changed**.

---

## Final Principles Earned

- **Evidence before confidence.**
- **Semantic similarity is not answerability.**
- **Grounding controls both answering and refusing.**
- **Fail closed when unsupported advice carries business risk.**
- **A relevance threshold is an engineering hypothesis until evaluated.**
- **Inspect retrieval before blaming generation.**
- **Debug the boundary, not the symptom.**
- **RAG is a pipeline, not a single AI component.**
- **A polished response is only as trustworthy as the evidence behind it.**

## One-Line Recall

> **Find the relevant information, add it to the question and rules, and generate a response based on the evidence.**
