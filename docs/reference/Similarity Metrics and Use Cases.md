
┌──────────────────────────────┬──────────────────────────────┬──────────────────────────────────────┬────────────────────────────────────────────┐
│ METRIC                       │ COMPARES                     │ SIMPLE EXAMPLE                       │ BEST USE                                   │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────────────┼────────────────────────────────────────────┤
│ Jaccard                      │ Set overlap                  │ {a,b,c} vs {b,c,d} = 2/4             │ Tags, tokens, shingles, dedupe             │
│ Dice / Sørensen-Dice          │ Set overlap, overlap-heavy   │ {a,b,c} vs {b,c,d} = 2*2/(3+3)      │ Near-duplicate text, fuzzy chunk overlap   │
│ Overlap coefficient           │ Containment overlap          │ {b,c} vs {a,b,c,d} = 2/2 = 1.0      │ “Is smaller set contained in larger one?”  │
│ MinHash                       │ Estimated Jaccard            │ Fast sketch of document shingles     │ Large-scale duplicate detection            │
│ Cosine similarity             │ Vector direction             │ [1,1,0] vs [2,2,0] = same direction │ Embeddings, semantic retrieval             │
│ Dot product                   │ Vector alignment + magnitude │ [1,1] · [3,3] = 6                   │ Dense retrieval when vector size matters   │
│ Euclidean distance            │ Straight-line vector distance│ (0,0) to (3,4) = 5                  │ Numeric features, geometry-like distance   │
│ Manhattan distance            │ Grid / coordinate distance   │ (0,0) to (3,4) = 7                  │ Sparse features, grid-like comparisons     │
│ TF-IDF cosine                 │ Weighted keyword vectors     │ “river bank” vs “bank by river”     │ Classic lexical search                     │
│ BM25                          │ Keyword relevance score      │ Query “river bank” ranks matching doc│ Search engines, sparse retrieval           │
│ Levenshtein distance          │ Edit distance between strings│ “kitten” -> “sitting” = 3 edits     │ Typos, names, fuzzy text matching          │
│ Jaro-Winkler                  │ String similarity, prefixes  │ “Martha” vs “Marhta” = high         │ Person names, company names, contacts      │
│ Hamming distance              │ Position-wise differences    │ 101110 vs 100100 = 2 differences    │ Equal-length strings, hashes, bit vectors  │
│ KL divergence                 │ Distribution difference      │ Model P vs model Q token probs      │ Comparing probability distributions        │
│ JS divergence                 │ Symmetric distribution diff  │ Safer KL-style comparison           │ Topic/model distributions, bounded compare │
│ Hellinger distance            │ Distribution geometry        │ Compare two normalized histograms   │ Probabilities, histograms                  │
│ Spearman correlation          │ Rank-order similarity        │ Ranker A vs Ranker B ordering       │ Comparing ranked lists                     │
│ Kendall tau                   │ Pairwise ranking agreement   │ How many item pairs agree/disagree  │ Ranking stability, evaluator agreement     │
│ NDCG                          │ Ranked relevance quality     │ Best results near top = high score  │ Search / RAG evaluation                    │
│ MRR                           │ First correct result rank    │ First right answer at rank 3 = 1/3  │ QA retrieval, answer lookup                │
│ SimRank                       │ Graph structural similarity  │ Nodes similar if neighbors similar  │ Knowledge graphs, entity similarity        │
│ Graph edit distance           │ Graph transformation cost    │ Edits needed to make graph A = B    │ Workflow graphs, dependency graphs         │
│ Path overlap                  │ Shared graph paths           │ Same entities connected by path     │ GraphRAG, lineage, dependency tracing      │
└──────────────────────────────┴──────────────────────────────┴──────────────────────────────────────┴────────────────────────────────────────────┘

FAST CHOICE RULE

Same explicit items?           -> Jaccard / Dice / Overlap
Same meaning?                  -> Cosine / Dot product over embeddings
Same keywords?                 -> BM25 / TF-IDF cosine
Same spelling-ish string?      -> Levenshtein / Jaro-Winkler
Same numeric location?         -> Euclidean / Manhattan
Same probability shape?        -> KL / JS / Hellinger
Same ranking behavior?         -> Spearman / Kendall / NDCG / MRR
Same graph structure/path?     -> SimRank / Graph edit distance / Path overlap
```
