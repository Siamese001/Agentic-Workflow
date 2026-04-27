# STAGE 0: INITIALIZATION & CONTEXT LOADING - DETAILED
## The EL's Domain: Setup Before Reasoning Begins

---

## 🕴️ WHO IS THE EL (ENGAGEMENT LEADER)?

The EL (Engagement Leader) is the master coordinator of the entire reasoning pipeline. They run the consulting war room from setup through final delivery.

### EL's Role in Stage 0:
- **Receives tokens** from tokenizer/embedding layer (doesn't create them)
- **Analyzes token complexity** to scope the project (domain count, clustering)
- **Adds positional encoding** to each token's embedding vector
- **Decides strategically**: How many CoT consultants, ToT specialists, SC reviewers
- **Seats all tokens** in the war room with their full vectors
- **Locks in all toggles** (temperature, max tokens, compliance rules)
- **Audits the perimeter** to ensure everyone is ready
- **DOES NOT REASON YET** - just structural oversight and scoping
- **Paces around scanning** the setup before saying: "Let's begin."

---

## 📊 THE THREE LAYERS OF CONTROL

### 🏗️ INFRASTRUCTURE LAYER (Hard Constraints - Architecture-Locked)

| Parameter | Value | Who Sets It | When | Can EL Change? |
|-----------|-------|-------------|------|----------------|
| **MAX_TOKENS (Context)** | 1024 | Architecture | Training time | ❌ No |
| **Embedding Dimensions** | 12,000 | Architecture | Training time | ❌ No |
| **Number of Layers** | 32 | Architecture | Training time | ❌ No |
| **Attention Heads** | 16 | Architecture | Training time | ❌ No |

**Analogy:** The hotel was built with 1024 rooms, 32 floors, 12K-key security. The EL can't add a 1025th room or extra floor. That's construction.

### ⚙️ CONFIGURATION LAYER (Soft Constraints - User/System-Locked)

| Parameter | Default | Who Sets It | When | Can EL Change? |
|-----------|---------|-------------|------|----------------|
| **TEMPERATURE** | 0.7 | User/API | Before infer | ❌ No |
| **TOP_K** | 50 | User/API | Before infer | ❌ No |
| **TOP_P** | 0.95 | User/API | Before infer | ❌ No |
| **MAX_OUTPUT_TOKENS** | 512 | User/API | Before infer | ❌ No |

**Note:** MAX_OUTPUT_TOKENS (new tokens to generate) ≠ MAX_TOKENS (context window)

**Analogy:** Conference organizer tells hotel: "Keep room at 68°F. No changes." EL (floor manager) enforces this but can't adjust the thermostat.

### 🕴️ EL STRATEGIC DECISIONS (Dynamic Choices - Inferred from Tokens)

| Decision | Based On | Measurement | When | Output |
|----------|----------|-------------|------|--------|
| **# CoT Spines** | Domain count, token spread, complexity | Semantic clustering of 12K-dim embeddings | Stage 0 (after receiving tokens) | 1-4 consultants |
| **# ToT Branches** | Entropy threshold, ambiguity score | Attention entropy during Stage 1 | After Slide 2 (if >0.75) | 0-6 specialists |
| **# SC Reviewers** | Confidence spread, domain diversity | Vote consistency needs | Stage 3 (Reflexion setup) | 3-7 independent |
| **Which tokens get high attention** | Q·K·V similarity scores | Softmax over attention weights | During attention (Stage 1+) | Dynamic per layer |

---

## 🏢 THE TRANSFORMER HALLWAY: Token Reception Process

### Before the EL enters the war room:

1. **User submits prompt** → "Analyze Amerant Bank's $50M AI investment portfolio across regulatory compliance, market positioning, operational feasibility, legal risk, and competitive landscape."

2. **TOKENIZER (Check-in Desk)** breaks it into tokens:
   ```
   "Analyze"     → Token ID #3421
   "Amerant"     → Token ID #8124
   "Bank"        → Token ID #12904
   "$50M"        → Token ID #8932
   "AI"          → Token ID #5647
   "investment"  → Token ID #2847
   "portfolio"   → Token ID #6182
   ... (846 tokens total)
   ```

3. **EMBEDDING LAYER (Keycard System)** assigns each token a 12,000-dim vector:

   ```
   Transformer Hallway Structure:
   ┌───────────────────────────────────────────────────────────────────────┐
   │ Token 1 ("Analyze")  → [0.23, 0.67, 0.12, ..., 0.88] (12,000 dims)  │
   │ Token 2 ("Amerant")  → [0.91, 0.32, 0.77, ..., 0.44] (12,000 dims)  │
   │ Token 3 ("Bank")     → [0.93, 0.28, 0.81, ..., 0.66] (12,000 dims)  │
   │ Token 4 ("$50M")     → [0.82, 0.71, 0.39, ..., 0.55] (12,000 dims)  │
   │ Token 5 ("AI")       → [0.76, 0.84, 0.52, ..., 0.91] (12,000 dims)  │
   │ Token 6 ("investment") → [0.79, 0.68, 0.44, ..., 0.73] (12,000 dims)│
   │ ...                                                                   │
   │ Token 846            → [0.44, 0.67, 0.33, ..., 0.12] (12,000 dims)  │
   └───────────────────────────────────────────────────────────────────────┘
   ```

   **KEY POINT:** Each token occupies a FULL ROW (not a single column). Every token carries its ENTIRE 12,000-dimensional embedding vector.

---

## 🔍 THE EL'S SCOPING PROCESS

### 4. EL receives these 846 pre-encoded tokens and begins analysis:

#### STEP 1: Token Clustering (Domain Detection)
The EL scans the embedding vectors and clusters tokens by semantic similarity:

```python
Semantic Clusters Detected:
{
  "finance": ["$50M", "investment", "portfolio", "revenue", "capital"],
  "risk": ["market", "competition", "downside", "volatility"],
  "legal": ["regulatory", "compliance", "oversight", "SEC"],
  "operations": ["team", "infrastructure", "execution", "timeline"],
  "strategy": ["growth", "positioning", "opportunity", "expansion"]
}

Domain Count: 5 distinct clusters
Token Spread: 0.82 (high variance in embedding space)
Cross-Domain Tokens: 47 tokens bridge multiple clusters
Ambiguity Tokens: 12 tokens have multiple interpretations
```

#### STEP 2: Calculate Complexity Score

```
Complexity Score Formula:
= (Domain Count × 0.4) + (Token Spread × 0.3) + 
  (Cross-Dependencies × 0.2) + (Ambiguity × 0.1)

For this prompt:
= (5 × 0.4) + (0.82 × 0.3) + (47/846 × 0.2) + (12/846 × 0.1)
= 2.0 + 0.246 + 0.011 + 0.001
= 2.26 (MODERATE-HIGH complexity)
```

#### STEP 3: Map Complexity → Resource Allocation

| Complexity Score | Domain Count | CoT Spines | Rationale |
|------------------|--------------|------------|-----------|
| 0.0 - 1.0 | 1-2 domains | 1 CoT Spine | Single consultant can handle |
| 1.0 - 2.0 | 2-3 domains | 2 CoT Spines | Need strategic + tactical view |
| 2.0 - 3.0 | 4-5 domains | 3 CoT Spines | Need strategic + risk + specialist |
| 3.0+ | 6+ domains | 4+ CoT Spines | Highly complex, need full panel |

**For this prompt (Complexity = 2.26, Domains = 5):**

EL Decision:
- ✅ **3 CoT Spines** (Strategic Planner, Risk Analyst, Operations Lead)
- ✅ **4 ToT Specialists reserved** (Compliance, Legal, Finance, Technical)
- ✅ **5 SC Reviewers prepared** (for final voting stage)

#### STEP 4: Add Positional Encoding

```
Token 2 ("Amerant"):
💡 Affinity Row (Embedding):  [0.91, 0.87, 0.77, 0.66, ...]  (12,000 dims)
🎟️ Seat Badge (Position):     [0.01, -0.03, 0.00, 0.02, ...] (12,000 dims)
➕ Final Vector:              [0.92, 0.84, 0.77, 0.68, ...]  (12,000 dims)
```

The positional encoding ADDS location metadata to the token's identity. The token still has its FULL dimensional vector—it's not confined to a single column.

---

## ⚙️ Configuration:
- **Temperature:** [VALUE]
- **ToT Branches:** [VALUE]
- **CoT Min Paths:** [VALUE]
- **Min ToT Depth:** [VALUE]
- **ToT Ambiguity Threshold:** [VALUE]
- **Reflexion Enabled:** [YES/NO] at stages [1,2,3,4]
- **RAG Type:** [Internal/External/Hybrid]

## 🔥 Input Query: "[INSERT QUERY]"

---

## 🎪 CONTEXT WINDOW - WAR ROOM SETUP

### 🏟️ Capacity: [MAX_TOKENS] | Current: [USED_TOKENS]

### JUNIOR ANALYSTS 🧑‍💼 (Tokens) Get Seated:

| Token | Affinity Row 💡 (Trait Profile) | Seat Badge 🎟️ (Position) | Final Vector | Status |
|-------|----------------------------------|---------------------------|--------------|--------|
| "Analyze" | ID #3421: [0.23, 0.67, 0.12, ...] (12,000 dims) | Seat 0 [0.00, 0.01, ...] | [0.23, 0.67, 0.12, ...] (12,000 dims) | ✅ Seated |
| "Amerant" | ID #8124: [0.91, 0.32, 0.77, ...] (12,000 dims) | Seat 1 [0.01, -0.01, ...] | [0.92, 0.31, 0.77, ...] (12,000 dims) | ✅ Seated |
| "Bank" | ID #12904: [0.93, 0.28, 0.81, ...] (12,000 dims) | Seat 2 [0.01, -0.01, ...] | [0.94, 0.27, 0.81, ...] (12,000 dims) | ✅ Seated |
| "$50M" | ID #8932: [0.82, 0.71, 0.39, ...] (12,000 dims) | Seat 3 [0.01, -0.01, ...] | [0.83, 0.70, 0.39, ...] (12,000 dims) | ✅ Seated |
| "AI" | ID #5647: [0.76, 0.84, 0.52, ...] (12,000 dims) | Seat 4 [0.01, -0.01, ...] | [0.77, 0.83, 0.52, ...] (12,000 dims) | ✅ Seated |
| "investment" | ID #2847: [0.79, 0.68, 0.44, ...] (12,000 dims) | Seat 5 [0.01, -0.01, ...] | [0.80, 0.67, 0.44, ...] (12,000 dims) | ✅ Seated |
| "portfolio" | ID #6182: [0.81, 0.73, 0.48, ...] (12,000 dims) | Seat 6 [0.01, -0.01, ...] | [0.82, 0.72, 0.48, ...] (12,000 dims) | ✅ Seated |
| ... | ... | ... | ... | 846 total tokens |

**Context Window:** 🏟️ 1024 seats total, 846 filled (CUR: 82.6%)

**NOTE:** Each token's "Final Vector" = Affinity Row (embedding) + Seat Badge (positional encoding). Each token retains its FULL 12,000-dimensional identity—they are not confined to a single dimension.

### CoT PATH ASSIGNMENTS (Baseline - Always Active):
- 🪙 CoT-1: [PERSONA_TYPE_1] ID:[####] 🎟️ Seat 0
  - Persona: [PERSONA_DESC_1] (e.g., "Strategic Planner")
  - Focus: [EXPERTISE_1]

- 🪙 CoT-2: [PERSONA_TYPE_2] ID:[####] 🎟️ Seat 1
  - Persona: [PERSONA_DESC_2] (e.g., "Risk Analyst")
  - Focus: [EXPERTISE_2]

- 🪙 CoT-3: [PERSONA_TYPE_3] ID:[####] 🎟️ Seat 2
  - Persona: [PERSONA_DESC_3] (e.g., "Technical Expert")
  - Focus: [EXPERTISE_3]

### SPECIALIST ANALYSTS (ToT - 🔴 IDLE until ambiguity spike):
- 🔴 ToT-A (Sp 0-2): [SPECIALIST_GROUP_1]
  - Persona: [SPECIALIST_PERSONA_A] (e.g., "Compliance Officer")
  - Focus: [SPECIALTY_A]
- 🔴 ToT-B (Sp 3-5): [SPECIALIST_GROUP_2]
  - Persona: [SPECIALIST_PERSONA_B] (e.g., "Financial Modeler")
  - Focus: [SPECIALTY_B]
- 🔴 ToT-C (Sp 6-8): [SPECIALIST_GROUP_3]
  - Persona: [SPECIALIST_PERSONA_C] (e.g., "Operations Manager")
  - Focus: [SPECIALTY_C]
- 🔴 ToT-D (Sp 9-11): [SPECIALIST_GROUP_4]
  - Persona: [SPECIALIST_PERSONA_D] (e.g., "Market Researcher")
  - Focus: [SPECIALTY_D]

---

## EL 🕴️ STAGE 0 STATUS CHECKPOINT

| Checkpoint | Status | Set By |
|------------|--------|--------|
| 💡 Tokens Received (Affinity Rows) | ✅ 846 tokens with 12K-dim vectors | Tokenizer + Embedding Layer |
| 🔍 Token Clustering Complete | ✅ 5 domains detected | EL Analysis |
| 📊 Complexity Score Calculated | ✅ 2.26 (MODERATE-HIGH) | EL Analysis |
| 🎟️ Positional Encoding Added | ✅ Complete | EL |
| 🏟️ Context Window Capacity | ✅ 846/1024 seats filled (82.6%) | Architecture (1024 max) |
| 🌡️ Temperature Locked | ✅ [VALUE] (deterministic) | User/System Config |
| 🔐 MAX_TOKENS Enforced | ✅ 1024 | Architecture |
| 🕴️ CoT Consultants Allocated | ✅ [N] (Strategic + Risk + Ops/Tech) | EL DECISION (based on complexity) |
| 🌿 ToT Specialists Reserved | ✅ [M] branches on standby | EL DECISION (based on domain count) |
| 🗳️ SC Reviewers Prepared | ✅ [K] reviewers ready | EL DECISION (based on voting needs) |
| Q·K·V Flow Status | ⌛ OFF (attention not yet activated) | EL (activates in Stage 1) |
| Entropy | N/A (no attention weights exist yet) | |
| Anchor Drift | N/A | |
| Head Diversity | N/A | |

**EL Decision:** "Setup complete. All analysts seated. [N] consultants assigned. [M] specialists reserved. [K] reviewers prepared. Toggles locked. Room is sealed but silent. Time to activate attention."

---

## 🎬 CONSULTING ANALOGY 💼

### OUTSIDE THE WAR ROOM:
- Conference organizer (user) sets rules: "Temperature = [VALUE]. Max capacity = 1024 guests."
- The tokenizer breaks the brief into 846 talking points.
- The embedding layer gives each talking point a full 12,000-dimensional profile.

### THE EL ENTERS THE WAR ROOM AND WALKS THE HALLWAY:

[Reviews first 100 token profiles]
"Lots of finance terms: investment, portfolio, $50M, capital..."

[Reviews next 200 tokens]
"Risk signals: market volatility, competition, downside..."

[Reviews next 200 tokens]
"Legal/compliance: regulatory, SEC, oversight, audit..."

[Reviews next 200 tokens]
"Operations: team structure, infrastructure, timeline, execution..."

[Reviews final 146 tokens]
"Strategy: growth opportunity, market positioning, expansion..."

[Pauses at whiteboard]

### EL ANALYSIS:
- Domain diversity: HIGH (5 clusters)
- Token spread: 0.82 (quite dispersed)
- Cross-domain dependencies: 47 tokens bridge multiple themes
- Ambiguity: 12 tokens could mean multiple things
- Complexity Score: 2.26 → MODERATE-HIGH

[Writes on whiteboard]

**"PROJECT SCOPING COMPLETE:**
- [N] Senior Consultants (CoT Spines) for core narrative
- [M] Specialists (ToT Branches) for [domains]
- [K] Independent Reviewers (SC) for final voting stage"

**CANNOT CHANGE:**
- Room temperature (locked by organizer at [VALUE])
- Room capacity (locked by building code at 1024)
- Guest profiles (already issued by check-in)

[Positions everyone, adds seat badges to all résumés, locks the floor plan]

**The EL nods: "Setup complete. Activate attention."**

---

**[STAGE 0 COMPLETE]**
**Output:** War room ready with [N] CoT + [M] ToT + [K] SC allocated
**Next:** Stage 1 - Foundation Consensus (Q·K·V activation begins)
