"""
CLEARLY — Sovereign Local RAG Command Line Interface (CLI)
Usage:
    python RAG/cli.py index <file_path> [--user-id <uuid>]
    python RAG/cli.py query "<question>" [--lang es|en] [--top-k 5]
    python RAG/cli.py stats
    python RAG/cli.py events-search "<query>" [--city Brampton]
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from RAG.pipeline.rag_service import rag_service
from RAG.storage.sqlite_vector_store import SQLiteVectorStore


def cmd_index(args):
    file_path = Path(args.file)
    if not file_path.is_file():
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8")
    result = rag_service.index_document(
        content=content,
        filename=file_path.name,
        user_id=args.user_id,
        critical_deadline=args.deadline,
        issuing_entity=args.issuer,
    )
    print(f"Document indexed successfully!")
    print(f"  Document ID:    {result.document_id}")
    print(f"  Filename:       {result.filename}")
    print(f"  SHA-256:        {result.file_sha256[:16]}...")
    print(f"  Chunks Created: {result.chunks_created}")
    print(f"  Total Tokens:   {result.total_tokens}")


def cmd_query(args):
    res = rag_service.query(
        user_query=args.question,
        top_k=args.top_k,
        language=args.lang,
    )
    print("\n" + "=" * 60)
    print(f"CLEARLY Sovereign RAG Response ({res.language.upper()}):")
    print("=" * 60)
    print(f"\n{res.answer}\n")
    print("-" * 60)
    print(f"Readability Score:    {res.readability.score} ({res.readability.grade_level})")
    print(f"Plain Language Met:   {'YES' if res.readability.is_plain_language else 'NO'}")
    print(f"Citations:            {res.citations}")
    print(f"Chunks Retrieved:     {len(res.retrieved_chunks)}")
    print(f"Requires Human Expert:{res.requires_human_expert}")
    if res.expert_reason:
        print(f"Expert Trigger:       {res.expert_reason}")
    if res.suggested_actions:
        print("\nSuggested Action Checklist:")
        for act in res.suggested_actions:
            print(f"  [ ] {act}")
    print("=" * 60)


def cmd_stats(args):
    store = rag_service.store
    with store.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM documents")
        docs_cnt = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM chunks")
        chunks_cnt = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM events")
        events_cnt = cur.fetchone()[0]

    print("\n" + "=" * 60)
    print("CLEARLY Sovereign SQLite Knowledge Base Statistics")
    print("=" * 60)
    print(f"Database Path:       {store.db_path}")
    print(f"sqlite-vec Active:   {'YES (vec0 enabled)' if store.has_sqlite_vec else 'NO (Python fallback)'}")
    print(f"Indexed Documents:   {docs_cnt}")
    print(f"Indexed Chunks:      {chunks_cnt}")
    print(f"Civic Events:        {events_cnt}")
    print("=" * 60)


def cmd_events_search(args):
    results = rag_service.store.search_events_hybrid(
        query_text=args.query,
        city=args.city,
        top_k=args.top_k,
    )
    print(f"\nFound {len(results)} events matching '{args.query}':")
    for idx, r in enumerate(results, start=1):
        ev = r.event
        print(f"\n{idx}. {ev.title} (Score: {r.score})")
        print(f"   City:     {ev.city} | Start: {ev.start_time}")
        print(f"   Cost:     {'GRATIS' if ev.is_free else ev.cost_notes}")
        print(f"   Summary:  {ev.description[:120]}...")


def main():
    parser = argparse.ArgumentParser(description="CLEARLY Sovereign Local RAG CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # index
    p_index = subparsers.add_parser("index", help="Index document into SQLite")
    p_index.add_argument("file", help="Path to text or markdown file")
    p_index.add_argument("--user-id", default=None, help="Owner user UUID")
    p_index.add_argument("--issuer", default=None, help="Issuing entity")
    p_index.add_argument("--deadline", default=None, help="Critical deadline date")
    p_index.set_defaults(func=cmd_index)

    # query
    p_query = subparsers.add_parser("query", help="Query local sovereign knowledge base")
    p_query.add_argument("question", help="User question")
    p_query.add_argument("--lang", default="es", choices=["es", "en"], help="Target language")
    p_query.add_argument("--top-k", type=int, default=5, help="Number of retrieved chunks")
    p_query.set_defaults(func=cmd_query)

    # stats
    p_stats = subparsers.add_parser("stats", help="Show SQLite database stats")
    p_stats.set_defaults(func=cmd_stats)

    # events-search
    p_ev = subparsers.add_parser("events-search", help="Search community events")
    p_ev.add_argument("query", help="Search query")
    p_ev.add_argument("--city", default=None, help="Filter by city (e.g. Brampton)")
    p_ev.add_argument("--top-k", type=int, default=5, help="Number of results")
    p_ev.set_defaults(func=cmd_events_search)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

