from pathlib import Path

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


model = SentenceTransformer("all-MiniLM-L6-v2")
docs_path = Path("docs")


def build_chunks():
    chunks = []

    for file_path in docs_path.glob("*.md"):
        text = file_path.read_text()
        paragraphs = text.split("\n\n")

        current_heading = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            if not paragraph:
                continue

            if paragraph.startswith("#"):
                current_heading = paragraph
                continue

            chunk_text = (
                f"{current_heading}\n\n{paragraph}"
                if current_heading
                else paragraph
            )

            chunks.append({
                "filename": file_path.name,
                "text": chunk_text,
            })

    return chunks


def retrieve(question, top_k=3):
    chunks = build_chunks()

    chunk_texts = [chunk["text"] for chunk in chunks]
    chunk_embeddings = model.encode(chunk_texts)

    question_embedding = model.encode(question)

    scores = cos_sim(
        question_embedding,
        chunk_embeddings
    )[0]

    results = []

    for chunk, score in zip(chunks, scores):
        results.append({
            "filename": chunk["filename"],
            "text": chunk["text"],
            "score": score.item(),
        })

    results.sort(
        key=lambda result: result["score"],
        reverse=True
    )

    return results[:top_k]