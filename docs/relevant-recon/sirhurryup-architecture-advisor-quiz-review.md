# SirhurryUp Architecture Advisor — Quiz Review

## Purpose

This review captures the core concepts tested during the project closeout. Use it to rehearse the *why* behind the architecture, not merely the vocabulary.

## Core Mental Model

**Find the relevant information → add it to the question and rules → generate a response based on the evidence.**

That is the working mental model for:

1. **Retrieval** — find evidence relevant to the question.
2. **Augmentation** — combine the question, retrieved evidence, and grounding instructions.
3. **Generation** — ask the foundation model to produce an answer from that supplied context.

---

## Review Questions and Answers

### 1. What is the main purpose of retrieval in this RAG system?

**Answer:** Find the documentation most relevant to the user's question.

Retrieval is upstream of the model. Its job is not to write the answer. It selects evidence that can support the answer.

### 2. What does augmentation add to the process?

**Answer:** It combines the original question with retrieved evidence and grounding rules before generation.

This is what gives the model company-specific context at request time without permanently adding that documentation to the model's knowledge.

### 3. What is generation responsible for?

**Answer:** Producing a response based on the question, evidence, and instructions it receives.

In this prototype, Amazon Nova Micro performs generation through Amazon Bedrock Runtime.

### 4. Why does the SirhurryUp documentation remain the source of truth?

**Answer:** The goal is not to accept a plausible model answer. The answer should be supported by SirhurryUp's documented architecture decisions.

A fluent response is not automatically a trustworthy response.

### 5. What did the retrieval-quality failure teach us?

**Answer:** **Semantic similarity is not the same as answerability.**

A chunk can be semantically related to a question without containing the clearest evidence needed to answer it.

### 6. Why inspect retrieved evidence before blaming the foundation model?

**Answer:** A weak generated answer may begin with weak evidence upstream.

Debug the path:

**Question → Retrieval → Evidence → Prompt → Model → Response**

### 7. Why was Nova saying “I don't have enough information in the documentation” considered a success?

**Answer:** The documentation did not support the requested PostgreSQL EC2 recommendation. Nova followed the grounding instructions instead of inventing a company-specific answer.

The system correctly preferred refusal over unsupported confidence.

### 8. Why add a relevance gate if the model can already refuse?

**Answer:** Weak evidence should not necessarily reach the generation layer at all.

The prototype uses two protections:

- **Weak retrieval → stop before generation.**
- **Insufficient evidence at generation → refuse rather than invent.**

### 9. What does the `0.60` threshold mean?

**Answer:** It is an experimental prototype threshold based on a small set of observed tests.

It is **not** a universal RAG threshold and should not be treated as production-ready without a larger evaluation dataset.

### 10. What engineering tradeoff did we choose?

**Answer:** Tolerate an occasional false refusal rather than risk false confidence.

For an internal architecture advisor, an unsupported recommendation can be more harmful than admitting the documentation is insufficient.

### 11. Why is RAG better understood as a pipeline rather than “the AI”?

**Answer:** The final response depends on several independent boundaries: local Python, embeddings, retrieval, credentials, SDK behavior, Bedrock Runtime, the model, and network dependencies.

A failure at one boundary can surface as a problem somewhere else.

### 12. What is the troubleshooting principle earned from the project?

**Answer:** **Debug the boundary, not the symptom.**

Use evidence such as tracebacks, retrieved chunks, similarity scores, identity checks, and request paths to locate the actual failing layer.

---

## Hidden Gems to Remember

### AWS CLI profiles are local

A profile configured on one development machine does not automatically exist on another.

Verify identity before making AWS calls:

```bash
aws sts get-caller-identity --profile sirhurryup-sandbox
```

### CLI authentication and boto3 readiness are separate concerns

Successful AWS CLI authentication did not automatically mean the Python SDK environment had everything required to consume the credentials. The project exposed an AWS CRT dependency during troubleshooting.

### Region can matter at multiple layers

Configuring `us-east-1` for the Bedrock client did not satisfy every Region requirement involved in credential handling. The AWS profile also needed a Region configured.

### A cached model may still attempt network access

Sentence Transformers attempted to contact Hugging Face even though the embedding model had already been downloaded. Explicit cached/local loading removed that unnecessary dependency during normal execution.

---

## Explain It Without Jargon

If someone asks what you built:

> I built a small architecture advisor that searches SirhurryUp's own documentation for relevant evidence, combines that evidence with the user's question and rules, and sends the grounded context to Amazon Nova Micro through Amazon Bedrock. If the evidence is too weak, the application can stop rather than manufacture an answer.

If someone asks what you learned:

> RAG is a pipeline. Retrieval quality matters before generation ever begins, and a polished model response is only as trustworthy as the evidence and rules supplied to it.

## Mastery Check

You are ready to explain this project when you can answer these without notes:

- Why is semantic similarity not enough?
- Why did the unsupported PostgreSQL question represent a successful test?
- What happens before Nova is called?
- Why does the relevance gate exist?
- Why is `0.60` provisional?
- What does “fail closed” mean in this project?
- Where would you look first if a generated answer is poor?
- What does “debug the boundary, not the symptom” mean in practice?
Explain It Without Jargon
If someone asks what you built:
I built a small architecture advisor that searches SirhurryUp's own documentation for relevant evidence, combines that evidence with the user's question and rules, and sends the grounded context to Amazon Nova Micro through Amazon Bedrock. If the evidence is too weak, the application can stop rather than manufacture an answer.

If someone asks what you learned:
RAG is a pipeline. Retrieval quality matters before generation ever begins, and a polished model response is only as trustworthy as the evidence and rules supplied to it.

Mastery Check
You are ready to explain this project when you can answer these without notes:
- Why is semantic similarity not enough?
- Why did the unsupported PostgreSQL question represent a successful test?
- What happens before Nova is called?
- Why does the relevance gate exist?
- Why is 0.60 provisional?
- What does “fail closed” mean in this project?
- Where would you look first if a generated answer is poor?
- What does “debug the boundary, not the symptom” mean in practice?
