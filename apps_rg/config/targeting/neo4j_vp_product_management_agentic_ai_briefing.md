Neo4j — VP of Product Management, Agentic AI targeting brief
| TBD | $340,000-$460,000 | Reports to CPO/CEO (direct report level, TBD) |

=== STRATEGIC MANDATE ===
- Neo4j is the graph database category creator; 84 of the Fortune 100 are customers (per company data)
- Core positioning: knowledge graph as the grounding layer that prevents LLM hallucination in enterprise AI
- Aura Agent launched Feb 2026 at $0.35/active agent hour (March 2026 pricing); usage-based PLG model
- Cypher 25 (v2026.01+): native in-index vector filtering — key architectural differentiator vs. pure vector DBs
- Dual license model: GPLv3 community edition + commercial Enterprise captures PLG-to-enterprise funnel
- BSL licensing shift in competing graph DBs (ArangoDB 100GB cap, FalkorDB source-available) creates moat

=== LEADERSHIP ===
- Emil Eifrem: CEO and co-founder; category-creation and developer-community-first strategy
- Direct manager: TBD (VP PM reports to CPO or CEO; no public appointment confirmed for this role)
- Engineering leadership: deep graph + AI integration team; LangChain and LlamaIndex maintainer relationships

=== TECH & AI PLATFORM ===
- Aura Agent: multi-step ReAct loop agent; defaults to Gemini Flash 2.5; MCP server deploy in one click
- Cypher 25 in-index filtering: HNSW metadata predicate during index traversal — low latency at scale
- LangChain neo4j (v0.9.0, Mar 2026): graph queries, chat history, hybrid vector indexing for LangGraph
- langgraph-checkpoint-neo4j: persists agent state and conversation checkpoints directly in graph nodes
- LlamaIndex integration: LlamaParse → Neo4jPropertyGraphStore → VectorContextRetriever + TextToCypherRetriever
- AWS: native AgentCore CDK templates; AuraDB Pro on AWS Marketplace; Bedrock Titan entity extraction
- Azure: AI Foundry + Copilot Studio integration; AuraDB Pro on Azure Marketplace with Private Link
- GCP: Google ADK + Neo4jMemoryService; Vertex AI text-embedding-004 for vector optimization
- Pinecone, Milvus, pgvector (at <50M chunks): primary vector-only alternatives; struggle at multi-hop queries

=== BUSINESS CONTEXT (JD alignment hooks) ===
- Developer-led adoption: PLG motion drives free-to-paid conversion; Aura Free → Aura Pro → Enterprise arc
- Enterprise buyers: data teams evaluate on RAG accuracy, multi-hop retrieval, and hyperscaler marketplace billing
- GTM motion: co-sell with AWS, Azure, GCP marketplace revenue + direct enterprise sales to Fortune 100
- LangChain, LlamaIndex, MCP ecosystem: framework integrations are the developer adoption on-ramp
- Graph + RAG positioning: when vector DB fails multi-hop lookups, Neo4j is the structured alternative
- Community: world's largest graph community per company claim; open-source developer flywheel

=== EXEC SUMMARY FRAMING (not proof) ===
- Lead angle: own the product strategy that makes Neo4j the default knowledge-graph layer in enterprise agentic AI
- Mirror Emil Eifrem's category-creation lens — this role defines how graphs become foundational to AI stacks
- Core trade-off: PLG developer velocity vs. enterprise governance; open-source community vs. paid Aura tiers
- 12-month win: Aura Agent at scale with usage-based revenue growth and named hyperscaler co-sell wins
