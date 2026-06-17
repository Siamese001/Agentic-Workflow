=========================================================================================================
                          AGENTIC ARCHITECTURE: TELEMETRY GENERATION VS. UTILIZATION
=========================================================================================================

          [ WITHOUT OTEL MCP ]                                   [ WITH OTEL MCP ]
          "Sensors & Recorder"                         "Governed Interpreter & Console"

+---------------------------------------+            +---------------------------------------+
|          App / Agent Runtime          |            |          App / Agent Runtime          |
+---------------------------------------+            +---------------------------------------+
                    |                                                    |
                    | emits spans, logs, metrics                         | emits spans, logs, metrics
                    v                                                    v
+---------------------------------------+            +---------------------------------------+
|         OTEL Instrumentation          |            |         OTEL Instrumentation          |
+---------------------------------------+            +---------------------------------------+
                    |                                                    |
                    v                                                    v
+---------------------------------------+            +---------------------------------------+
|  Collector / Exporter / Backend Store |            |  Collector / Exporter / Backend Store |
+---------------------------------------+            +---------------------------------------+
                    |                                                    |
                    | raw telemetry stored                               | raw telemetry stored
                    v                                                    v
+---------------------------------------+            +---------------------------------------+
|      Durable / Queryable Store        |            |      Durable / Queryable Store        |
+---------------------------------------+            +---------------------------------------+
                    |                                                    ^
                    |                                                    | (reads, queries, aggregates)
                    | [X]                                                v
                    | Data exists, but                       +-----------------------+
                    | Codex is blind                       |    OTEL MCP SERVER    |
                    |                                        |  (Bounded Adapter &   |
                    v                                        |  Execution Surface)   |
+---------------------------------------+                    +-----------------------+
|         Codex / legacy editor            |                                ^
|     (Cannot easily use data)          |                                | (governed tool call)
+---------------------------------------+                                v
                                                     +---------------------------------------+
                                                     |         Codex / legacy editor            |
                                                     |  (Operationalizes the Telemetry)      |
                                                     +---------------------------------------+
                                                                         |
                                                                         | outputs higher-level answers:
                                                                         v
                                                     [ otel_status, anomalies, healing_chains, ]
                                                     [ policy_decisions, trace -> runtime ADG  ]
=========================================================================================================