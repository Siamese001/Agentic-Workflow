          [ PATIENT ARRIVES ]                        [ SYSTEM INCIDENT OCCURS ]
        (The individual entity)                        (The specific failure)
                   |                                             |
                   v                                             v
+----------------------------------------+    +----------------------------------------+
|           Symptoms Reported            |    |       Failure Signals Collected        |
|                                        |    |                                        |
| * Cough, chest pain, fever             |    | * Stack traces (ImportError, etc.)    |
| * Patient history                      |    | * Invariant violations                 |
| * Age / risk factors                   |    | * Territory violations                 |
|                                        |    | * Test failures                        |
|                                        |    | * Repo context / file path             |
+----------------------------------------+    +----------------------------------------+
                   |                                             |
                   v                                             v
+----------------------------------------+    +----------------------------------------+
|    Medical Imaging (Symptom Scan)      |    |  Semantic Pattern Analysis (bge-m3)    |
|                                        |    |                                        |
| * X-ray / MRI                          |    | * Embedding model                      |
|                                        |    |                                        |
| INPUT TO EMBEDDING                     |    | INPUT TO EMBEDDING                     |
|                                        |    |                                        |
| "cough fever chest pain infection"     |    | "ImportError yaml config loader"      |
|                                        |    |                                        |
| OUTPUT                                 |    | OUTPUT                                 |
|                                        |    |                                        |
| symptom_vector = [v1..vN]               |    | failure_vector = [v1..vN]              |
+----------------------------------------+    +----------------------------------------+
                   |                                             |
                   v                                             v
+----------------------------------------+    +----------------------------------------+
|      Search Medical Case History       |    |  Search Similar Historical Incidents   |
|                                        |    |                                        |
| VECTOR SEARCH                          |    | VECTOR SEARCH                          |
|                                        |    |                                        |
| symptom_vector                         |    | failure_vector                         |
|                                        |    |                                        |
| RETURNS TOP MATCHES                    |    | RETURNS TOP MATCHES                    |
|                                        |    |                                        |
| Case A -> pneumonia                    |    | Incident A -> yaml dependency          |
| Case B -> bronchitis                   |    | Incident B -> path issue               |
| Case C -> infection                    |    | Incident C -> test config issue        |
+----------------------------------------+    +----------------------------------------+
                   |                                             |
                   v                                             v
+----------------------------------------+    +----------------------------------------+
|    Hospital Triage / Diagnostician     |    |        Healing Decision Engine         |
|                                        |    |                                        |
| USES RETRIEVED METADATA                |    | USES RETRIEVED METADATA                |
|                                        |    |                                        |
| * disease label                        |    | * violation type                       |
| * treatments used                      |    | * healer used                          |
| * doctor success rate                  |    | * patch applied                        |
| * patient outcomes                     |    | * success / failure                    |
|                                        |    | * cluster statistics                   |
|                                        |    |                                        |
| Determines disease + specialist        |    | Determines root cause + healer         |
+----------------------------------------+    +----------------------------------------+
                   |                                             |
                   v                                             v
+----------------------------------------+    +----------------------------------------+
|   Specialist Doctor (Agent) Assigned   |    |  Healing Agent (Specialist) Assigned   |
|                                        |    |                                        |
| * cardiologist                         |    | * DependencyRepairAgent                |
| * orthopedic                           |    | * ArchitectureGovernorAgent            |
| * infectious disease                   |    | * GravityRepairAgent                   |
|                                        |    | * TestRepairAgent                      |
|                                        |    |                                        |
| Treatment applied                      |    | Deterministic repair executed          |
|                                        |    |                                        |
| * antibiotics                          |    | * pip install pyyaml                   |
| * cast                                 |    | * modify config                        |
| * surgery                              |    | * patch code                           |
+----------------------------------------+    +----------------------------------------+
                   |                                             |
                   v                                             v
+----------------------------------------+    +----------------------------------------+
|      Case Stored in Hospital DB        |    |      Healing Event Stored in Memory    |
|                                        |    |                                        |
| VECTOR STORED                          |    | VECTOR STORED                          |
|                                        |    |                                        |
| symptom_vector                         |    | failure_vector                         |
|                                        |    |                                        |
| METADATA STORED                        |    | METADATA STORED                        |
|                                        |    |                                        |
| * symptoms text                        |    | * failure text                         |
| * diagnosis                            |    | * violation types                      |
| * doctor assigned                      |    | * healer used                          |
| * treatment                            |    | * repair action                        |
| * success / failure                    |    | * success / failure                    |
| * patient demographics                 |    | * repo location                        |
|                                        |    | * commit / patch summary               |
|                                        |    | * confidence score                     |
+----------------------------------------+    +----------------------------------------+
                   |                                             |
                   v                                             v
+----------------------------------------+    +----------------------------------------+
|            Medical Research            |    |          Meta-Learning System          |
|                                        |    |                                        |
| Uses vectors + metadata                |    | Uses vectors + metadata                |
|                                        |    |                                        |
| * cluster disease patterns             |    | * cluster failure patterns             |
| * best treatment per disease           |    | * best healer per failure type         |
| * best doctor per disease              |    | * success rate per agent cluster       |
| * detect recurring conditions          |    | * detect recurring regressions         |
| * improve triage protocols             |    | * improve routing decisions            |
+----------------------------------------+    +----------------------------------------+
