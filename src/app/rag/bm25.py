"""Busca lexical (por palavras) com o algoritmo BM25, feita só com a biblioteca padrão.

Diferente da busca por sentido (embeddings), o BM25 procura as mesmas palavras da
pergunta nos textos. Por isso é forte com termos exatos, como `app.routes` ou
`status_code`, e fraco quando a pergunta está em outro idioma.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict

TOKEN_RE = re.compile(r"[a-z0-9_]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


class BM25Index:
    def __init__(self, documents: list[str], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self.term_counts = [Counter(tokenize(doc)) for doc in documents]
        self.lengths = [sum(counts.values()) for counts in self.term_counts]
        self.average_length = sum(self.lengths) / len(documents) if documents else 0.0
        self.postings: dict[str, list[int]] = defaultdict(list)
        for doc_id, counts in enumerate(self.term_counts):
            for term in counts:
                self.postings[term].append(doc_id)
        total = len(documents)
        self.idf = {
            term: math.log(1 + (total - len(docs) + 0.5) / (len(docs) + 0.5))
            for term, docs in self.postings.items()
        }

    def search(self, query: str, limit: int) -> list[tuple[int, float]]:
        """Devolve (posição do documento, nota), da maior nota para a menor."""
        scores: dict[int, float] = defaultdict(float)
        for term in set(tokenize(query)):
            if term not in self.idf:
                continue
            for doc_id in self.postings[term]:
                count = self.term_counts[doc_id][term]
                norm = 1 - self.b + self.b * self.lengths[doc_id] / self.average_length
                scores[doc_id] += self.idf[term] * count * (self.k1 + 1) / (count + self.k1 * norm)
        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        return ranked[:limit]
