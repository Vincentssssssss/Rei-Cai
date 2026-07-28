def build_citations(hits: list[dict]) -> list[dict]:
    citations: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for hit in hits:
        source = hit["source"]
        excerpt = hit["text"].strip()
        key = (source, excerpt)
        if key in seen:
            continue
        seen.add(key)
        citations.append(
            {
                "source": source,
                "excerpt": excerpt,
                "score": hit.get("score"),
            }
        )
    return citations
