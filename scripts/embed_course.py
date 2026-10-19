import os
import argparse
import pathlib
import sys
from typing import List

import openai
import psycopg2
from psycopg2.extras import execute_values

def get_openai_embeddings(texts: List[str], model: str = "text-embedding-3-large") -> List[List[float]]:
    """Call OpenAI embeddings API for a batch of texts and return embeddings."""
    response = openai.embeddings.create(input=texts, model=model)
    return [obj.embedding for obj in response.data]

def chunk_iterable(iterable, size):
    """Yield successive chunks from iterable of given size."""
    it = iter(iterable)
    while True:
        chunk = []
        try:
            for _ in range(size):
                chunk.append(next(it))
        except StopIteration:
            if chunk:
                yield chunk
            break
        yield chunk

def main():
    parser = argparse.ArgumentParser(description="Embed course markdown files into pgvector table")
    parser.add_argument("--source-dir", required=True, help="Directory containing course material files (markdown, txt, etc.)")
    parser.add_argument("--model", default="text-embedding-3-large", help="OpenAI embedding model name")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size for API requests")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        sys.stderr.write("[ERROR] OPENAI_API_KEY environment variable not set.\n")
        sys.exit(1)
    openai.api_key = os.getenv("OPENAI_API_KEY")

    source_path = pathlib.Path(args.source_dir).resolve()
    if not source_path.is_dir():
        sys.stderr.write(f"[ERROR] source-dir '{source_path}' is not a directory.\n")
        sys.exit(1)

    file_paths = list(source_path.rglob("*.md")) + list(source_path.rglob("*.txt"))
    if not file_paths:
        sys.stderr.write(f"[WARN] No .md or .txt files found under {source_path}. Exiting.\n")
        sys.exit(0)

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        sys.stderr.write("[ERROR] DATABASE_URL environment variable not set.\n")
        sys.exit(1)

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    for batch in chunk_iterable(file_paths, args.batch_size):
        titles, contents = [], []
        for fp in batch:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                sys.stderr.write(f"[WARN] Unable to read {fp}: {e}\n")
                continue
            titles.append(fp.stem.replace("_", " "))
            contents.append(content)
        if not contents:
            continue
        embeddings = get_openai_embeddings(contents, model=args.model)
        records = [(t, c, e) for t, c, e in zip(titles, contents, embeddings)]
        sql = """
            INSERT INTO course_docs (title, content, embedding)
            VALUES %s
            ON CONFLICT DO NOTHING;
        """
        execute_values(cur, sql, records, template="(%s, %s, %s::vector)")
        conn.commit()
        print(f"Inserted {len(records)} documents into course_docs")

    cur.close()
    conn.close()
    print("Embedding pipeline completed.")

if __name__ == "__main__":
    main()
