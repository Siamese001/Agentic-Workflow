========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: C0_Context_Engine
Canonical file: Anthropic RAG Best Practices.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: Anthropic RAG Best Practices.md
Owner summary: C0 retrieval/evidence engine. Owns retrieval planning, fetch/hydration, graph expansion, shaping, verification, evidence contract, and weak-support refinement. Does not answer or assemble prompts.

GLOBAL NO-OVERLAP LAW
- 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission.
- 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics.
- 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence.
- 00X owns traceability and no-loss mapping only.
- 01 Intake owns request envelope validation and identity/session/tenant baseline only.
- 02 L1 owns advisory interpretation and planning only.
- 03 L0/L3 owns deterministic route selection and optional workflow orchestration only.
- C0 owns retrieval/evidence contracts only.
- PA owns prompt packet construction only.
- 04 L2 owns bounded execution and sealing only.
- 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only.
- 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only.
- 99 owns proof harnesses only; it does not own runtime behavior.

REFERENCE POINTERS
- Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/
- Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/
- Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/
- Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md
- End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/
========================================================================================================================

**Bottom line:** Anthropic’s own guidance points to a very specific RAG pattern for Claude: **do not default to RAG**, use **full-context + prompt caching** when the corpus is small enough, and when you do need RAG, use **contextualized hybrid retrieval + reranking + citation-aware prompt assembly**, then validate it with task-specific evals. ([Anthropic][1])

## 1. Anthropic’s first decision point: maybe do **not** use RAG

Anthropic explicitly says that if your knowledge base is **under about 200,000 tokens**, you can often skip RAG and put the whole knowledge base directly into the prompt. They pair that recommendation with **prompt caching**, which they say can reduce latency by **more than 2x** and costs by **up to 90%** for reusable prompt prefixes. That is a big deal, because a lot of teams build retrieval systems they do not actually need. ([Anthropic][1])

So the first architectural question is not “how do I build RAG?” It is: **does this corpus justify retrieval at all, or can I get a simpler and more reliable system with long context and caching?** Anthropic’s docs lean harder toward that simplification than most generic RAG advice does. ([Anthropic][1])

## 2. If you do need RAG, Anthropic’s strongest retrieval recommendation is **Contextual Retrieval**

Anthropic’s official retrieval research says traditional RAG often fails because chunking strips away the context needed for retrieval. Their recommended fix is **Contextual Retrieval**, which combines **Contextual Embeddings** and **Contextual BM25**. In their published results, this reduced failed retrievals by **49%**, and by **67% when combined with reranking**. ([Anthropic][1])

What that means in practice is:

1. Split documents into chunks, usually **no more than a few hundred tokens**.
2. Use Claude to generate a **short chunk-specific context** grounded in the whole document.
3. Prepend that context to the chunk before indexing it for both embeddings and BM25.
4. At query time, retrieve using both semantic and lexical search, combine the results, dedupe, then rerank before generation. ([Anthropic][1])

That is the clearest “best practice” signal from Anthropic’s RAG-specific material. If you only take one retrieval idea from their docs, take that one. ([Anthropic][1])

## 3. The retrieval stack Anthropic points toward

Anthropic’s retrieval writeup describes a hybrid pipeline: use **embeddings** for semantic similarity, **BM25** for exact lexical matches, combine them with **rank fusion**, and then pass only the best chunks to Claude. They also show a reranking pattern where an initial broad retrieval is narrowed before generation. In their example, they retrieved the top **150** candidates, reranked, and then passed the top **20** chunks into generation. Anthropic also notes that more chunks are not always better and says to **experiment on your own use case**. ([Anthropic][1])

So the working Anthropic-style baseline is:

* **Hybrid retrieval**, not vector-only.
* **Contextualized chunks**, not raw chunks.
* **Broad first-pass recall + reranking**, not “top-5 vectors and pray.”
* **Eval-driven K selection**, not a fixed chunk count copied from a blog. ([Anthropic][1])

## 4. How Anthropic wants you to structure the prompt Claude actually sees

Anthropic’s long-context prompting docs are unusually concrete here. For large document inputs, they recommend putting the **longform data at the top of the prompt** and the **query at the end**. They say this can improve response quality by **up to 30%** in complex multi-document cases. They also recommend wrapping documents with **XML tags** and metadata like `<document>`, `<document_content>`, and `<source>`, and explicitly asking Claude to **quote relevant parts first** before answering so it grounds itself in the source material. ([Claude API Docs][2])

That leads to a very practical prompt shape:

* **system:** role and global behavior
* **documents/context:** at the top, with XML structure and metadata
* **task/query:** at the bottom
* **grounding instruction:** quote or cite before synthesizing
* **answer instruction:** concise, bounded, source-grounded output ([Claude API Docs][3])

Anthropic also says to use the **system prompt for role framing** and keep the task-specific request in the **user turn**. ([Claude API Docs][3])

## 5. Provenance is not optional: use Claude’s native citation features

Anthropic’s citations docs say Claude can provide **detailed citations** for document-based answers, and their newer **search result content blocks** bring “web-search quality” citations into custom RAG systems. For RAG apps where trust matters, this is the official path instead of inventing your own citation format. ([Claude API Docs][4])

Two implementation details matter a lot:

* **Plain text docs** are automatically chunked into sentences for citation.
* **Custom content documents** give you control over citation granularity and do **no additional chunking**. Anthropic specifically notes that if you want Claude to cite your own RAG chunks precisely, you should pass them in ways that preserve the chunk boundaries you care about. ([Claude API Docs][4])

That means if you want citations to map back cleanly to your retrieval units, do not just dump everything into one giant document block. Use **custom content documents or carefully segmented plain text documents** so the citation boundaries line up with your retrieval units. ([Claude API Docs][4])

## 6. One important Anthropic constraint most teams miss

Anthropic’s docs say **citations and structured outputs are incompatible**. If you enable citations and also require strict JSON schema output, the API returns an error. ([Claude API Docs][4])

So for high-trust RAG systems, the safer design is often **two-pass**:

1. **Grounded answer pass with citations.**
2. **Post-processing pass** that converts the cited answer into JSON or another strict structure if you need machine-readable output. ([Claude API Docs][4])

That separation keeps provenance and schema control from fighting each other.

## 7. Prompt caching should be part of the RAG design, not a later optimization

Anthropic’s caching docs say to put **static content** like tool definitions, system instructions, context, and examples at the **beginning** of the prompt, then mark the end of the reusable section with `cache_control`. They also note the default cache lifetime is **5 minutes**, with an optional **1-hour** cache for longer-running workflows. ([Claude API Docs][5])

This matters in two RAG places:

* **Long-context apps** where the same reference corpus is reused across turns.
* **Contextual retrieval preprocessing**, where the same full document is reused while generating context for many chunks. Anthropic explicitly calls out prompt caching as what makes contextual retrieval cheap enough to use at scale. ([Anthropic][1])

If you are building Claude-based RAG and not planning cache boundaries from day one, you are likely overspending.

## 8. When to use thinking, tool use, and multi-agent search

Anthropic’s docs say **adaptive/extended thinking** is useful for **multi-step tool use**, complex reasoning, and longer-horizon agent loops. They also document **interleaved thinking**, where Claude reasons between tool calls. But there are real constraints: with thinking enabled, tool choice must stay at `auto` or `none`, and you must preserve the returned thinking blocks correctly across tool turns. ([Claude API Docs][6])

Anthropic’s research team also says multi-agent systems are best for **breadth-first queries** where multiple lines of investigation can be pursued in parallel. In their internal eval, a multi-agent setup outperformed a single-agent setup by **90.2%** on that research task class. But they also warn that multi-agent systems burn many more tokens, are not a fit for tightly interdependent tasks, and are economically justified only when the task value supports the added cost. ([Anthropic][7])

So the best-practice rule is:

* **Simple QA over known documents:** standard RAG or full-context.
* **Multi-step search / hard synthesis:** thinking + tools.
* **Parallel, breadth-first research:** orchestrator + subagents, but only when the task really deserves it. ([Claude API Docs][3])

## 9. Model choice: Anthropic’s advice is to start cheaper, then earn your way up

Anthropic’s model-selection docs recommend starting with a **faster, cheaper model**, testing thoroughly, and upgrading only when evals show clear gaps. Their latest prompting docs also position **Opus** as the right choice for the hardest long-horizon and deep research tasks, while the faster model tier is better when turnaround time and cost matter more. ([Claude API Docs][8])

That suggests a sane deployment pattern:

* Use a **cheap model tier** for chunk contextualization, metadata generation, and easy retrieval-time transforms.
* Use a **stronger reasoning model** only for the final synthesis or hard multi-step search paths. ([Anthropic][1])

## 10. Anthropic’s evaluation advice maps cleanly onto RAG

Anthropic says success criteria should be **specific** and **measurable**, and that most applications need **multidimensional evaluation** rather than one score. They explicitly call out criteria like **context utilization, latency, and price**, and recommend task-specific evals that mirror real-world distributions. They also favor automation where possible and note that **volume beats small handcrafted eval sets** when you can grade reliably. ([Claude API Docs][9])

For a Claude-based RAG system, that means your eval suite should at minimum cover:

* **Retrieval relevance / context utilization**
* **Answer fidelity to source**
* **Citation correctness**
* **Latency**
* **Cost**
* **Failure modes on edge cases** like exact-match IDs, partial matches, stale docs, and ambiguous queries. ([Claude API Docs][9])

## 11. What I would actually build if I were following Anthropic closely

Here is the practical blueprint I would use:

1. **Check corpus size first.** If the working set is small enough, use **full-context + prompt caching** and skip RAG. ([Anthropic][1])
2. If RAG is needed, chunk documents into **small coherent units**, then use Claude to generate **50-100 token chunk context** from the whole document. ([Anthropic][1])
3. Index the contextualized chunks into **both embeddings and BM25**. ([Anthropic][1])
4. At query time, do **hybrid retrieval + fusion**, retrieve broadly, then **rerank** before generation. ([Anthropic][1])
5. Assemble prompts with **documents first, query last**, and use **XML tags + metadata**. ([Claude API Docs][2])
6. Ask Claude to **quote or cite source material before synthesis**. ([Claude API Docs][2])
7. Use **native citations** or **search result blocks** instead of hand-rolled provenance. ([Claude API Docs][10])
8. If you need strict JSON, do it in a **second pass**, because citations and strict structured outputs cannot coexist in one call. ([Claude API Docs][4])
9. Use **adaptive thinking** only where it materially improves multi-step tool reasoning. ([Claude API Docs][3])
10. Add **subagents** only for genuinely parallel research problems, not by default. ([Anthropic][7])
11. Tune everything against **evals**, not intuition. ([Claude API Docs][9])

## 12. The biggest anti-patterns, based on Anthropic’s material

The clearest mistakes to avoid are:

* Building RAG when **long-context + caching** would be simpler and better. ([Anthropic][1])
* Using **vector-only retrieval** when the query contains exact identifiers, codes, or terminology better handled by BM25. ([Anthropic][1])
* Sending chunks to Claude without **contextualization**, metadata, or XML structure. ([Anthropic][1])
* Stuffing too many weak chunks into the prompt instead of **reranking** and curating. ([Anthropic][1])
* Trying to get **strict JSON + native citations** in one response. ([Claude API Docs][4])
* Turning on **multi-agent orchestration** for tasks that are not actually breadth-first or parallelizable. ([Anthropic][7])
* Treating evaluation as a one-dimensional score instead of a tradeoff across quality, context use, latency, and price. ([Claude API Docs][9])

If you want, I’ll turn this into a **production-ready Claude RAG design spec** with an exact ingestion pipeline, retrieval pipeline, prompt template, and eval rubric.

[1]: https://www.anthropic.com/research/contextual-retrieval "Contextual Retrieval in AI Systems \ Anthropic"
[2]: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/long-context-tips "Prompting best practices - Claude API Docs"
[3]: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts "Prompting best practices - Claude API Docs"
[4]: https://docs.anthropic.com/en/docs/build-with-claude/citations "Citations - Claude API Docs"
[5]: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching?ss_ad_code=usecase3 "Prompt caching - Claude API Docs"
[6]: https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking "Building with extended thinking - Claude API Docs"
[7]: https://www.anthropic.com/engineering/built-multi-agent-research-system "How we built our multi-agent research system \ Anthropic"
[8]: https://docs.anthropic.com/en/docs/about-claude/models/choosing-a-model "Choosing the right model - Claude API Docs"
[9]: https://docs.anthropic.com/en/docs/test-and-evaluate/define-success "Define success criteria and build evaluations - Claude API Docs"
[10]: https://docs.anthropic.com/en/docs/build-with-claude/search-results "Search results - Claude API Docs"
