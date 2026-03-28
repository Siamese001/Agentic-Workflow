====================================================================================================
PIPELINE 1: INGESTION (HAPPENS BEFORE ANY USER QUERY)
====================================================================================================

[ REAL DOCUMENT SOURCE ]
  (PDF / DB / SharePoint / Web Fetch / Logs)
        |
        v
+-------------------------------+
| 1. DOCUMENT LOADER            |
| - read file / API / DB        |
+-------------------------------+
        |
        v
+-------------------------------+
| 2. TEXT EXTRACTION            |
| - PDF parsing / OCR           |
+-------------------------------+
        |
        v
+-------------------------------+
| 3. CLEANING / NORMALIZATION   |
| - remove noise                |
| - normalize formatting        |
+-------------------------------+
        |
        v
+-------------------------------+
| 4. CHUNKING                   |
| - split into smaller units    |
|                               |
| Example:                      |
| A: "Client ABC experienced..."|
| B: "due to fraud rule..."     |
+-------------------------------+
        |
        v
+-------------------------------+
| 5. METADATA ATTACHMENT        |
| - doc_id, page, source        |
+-------------------------------+
        |
        v
+-------------------------------+
| 6. TOKENIZATION (EMBED MODEL) |
| - convert chunk → tokens      |
+-------------------------------+
        |
        v
+-------------------------------+
| 7. EMBEDDING                  |
| - tokens → vector             |
| - [0.21, -0.33, 0.77, ...]    |
+-------------------------------+
        |
        v
+------------------------------------------------------+
| 8. VECTOR DATABASE STORAGE                           |
|                                                      |
| STORES:                                              |
| - embedding vector                                   |
| - chunk text                                         |
| - metadata                                           |
|                                                      |
| Example record:                                      |
| (vector_A → "Client ABC experienced..." , doc_id=001) |
+------------------------------------------------------+
        |
        v
+----------------------------------+
| 9. ORIGINAL DOC STORAGE          |
| (S3 / Blob / Filesystem / DB)    |
+----------------------------------+

-------------------- END INGESTION --------------------



====================================================================================================
PIPELINE 2: QUERY TIME (HAPPENS AFTER INGESTION)
====================================================================================================

[ USER QUERY ]
"Why did denied claims increase for Client ABC?"
        |
        v
+-------------------------------+
| 1. QUERY NORMALIZATION        |
+-------------------------------+
        |
        v
+-------------------------------+
| 2. TOKENIZATION (EMBED MODEL) |
| ["Why","did","denied",...]    |
+-------------------------------+
        |
        v
+-------------------------------+
| 3. EMBEDDING                  |
| q_vector = [0.25, -0.31,...]  |
+-------------------------------+
        |
        v
+------------------------------------------------------+
| 4. VECTOR SEARCH (ANN / similarity)                  |
| Compare q_vector vs ALL stored chunk vectors         |
+------------------------------------------------------+
        |
        v
+-------------------------------+
| 5. SIMILARITY SCORES          |
| A → 0.94                      |
| B → 0.91                      |
| C → 0.42                      |
+-------------------------------+
        |
        v
+-------------------------------+
| 6. RANKING                    |
| Sort by score descending      |
+-------------------------------+
        |
        v
+-------------------------------+
| 7. TOP-K SELECTION            |
| K=2 → [A, B]                 |
+-------------------------------+
        |
        v
+------------------------------------------------------+
| 8. RETRIEVE PAYLOAD                                  |
| Return chunk TEXT + metadata                         |
|                                                      |
| "Client ABC experienced..."                          |
| "due to fraud rule..."                               |
+------------------------------------------------------+
        |
        v
+------------------------------------------------------+
| 9. CONTEXT ASSEMBLY                                  |
|                                                      |
| Context:                                             |
| - Chunk A                                            |
| - Chunk B                                            |
|                                                      |
| Question:                                            |
| Why did denied claims increase?                      |
+------------------------------------------------------+
        |
        v
+-------------------------------+
| 10. LLM TOKENIZATION          |
| (SECOND TOKENIZATION PASS)    |
+-------------------------------+
        |
        v
+-------------------------------+
| 11. LLM GENERATION            |
+-------------------------------+
        |
        v
+-------------------------------+
| 12. FINAL ANSWER              |
| "Due to fraud rule..."        |
+-------------------------------+

====================================================================================================
KEY SEPARATION (THIS IS THE WHOLE GAME)
====================================================================================================

INGESTION PIPELINE:
- creates chunks
- creates embeddings
- stores them
- happens BEFORE query

QUERY PIPELINE:
- never creates chunks
- only searches existing ones
- retrieves + answers

====================================================================================================
CORE TRUTH
====================================================================================================

NO INGESTION → NO CHUNKS → NO VECTOR DB → NO RAG