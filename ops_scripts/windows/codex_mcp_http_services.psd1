@{
    SchemaVersion = 'codex-mcp-http-services/v1'
    Services = @{
        adg_sqlite = @{
            ServerId = 'adg_sqlite'
            TaskName = 'AgenticWorkflow-ADG-HTTP-MCP'
            Module = 'tools.mcp.launch_adg_sqlite_http_mcp'
            Host = '127.0.0.1'
            Port = 8765
            Path = '/mcp'
            Url = 'http://127.0.0.1:8765/mcp'
            HealthTool = 'adg_health'
            IdentityTool = 'adg_process_identity'
            ExpectedTransport = 'streamable-http'
            StatePath = 'artifacts/mcp/adg_sqlite_windows_runner.json'
            LauncherStatePath = 'artifacts/mcp_heartbeat/adg_sqlite_http_launcher.json'
            ServiceLogPath = 'artifacts/mcp/adg_sqlite_http_service.jsonl'
            StdoutLogPath = 'artifacts/mcp/adg_sqlite_http_stdout.log'
            StderrLogPath = 'artifacts/mcp/adg_sqlite_http_stderr.log'
            Dependencies = @(
                @{
                    Kind = 'tcp'
                    Name = 'redis'
                    Host = '127.0.0.1'
                    Port = 6379
                    Required = $true
                }
            )
            RestartPolicy = @{
                IntervalMinutes = 1
                Count = 255
                MultipleInstances = 'IgnoreNew'
                WatchdogIntervalMinutes = 1
                WatchdogDurationDays = 3650
            }
        }
        memory = @{
            ServerId = 'memory'
            TaskName = 'AgenticWorkflow-Memory-HTTP-MCP'
            Module = 'tools.mcp.launch_memory_http_mcp'
            Host = '127.0.0.1'
            Port = 8766
            Path = '/mcp'
            Url = 'http://127.0.0.1:8766/mcp'
            HealthTool = 'memory_health'
            IdentityTool = 'mem_process_identity'
            ExpectedTransport = 'streamable-http'
            StatePath = 'artifacts/mcp/memory_windows_runner.json'
            LauncherStatePath = 'artifacts/mcp_heartbeat/memory_http_launcher.json'
            ServiceLogPath = 'artifacts/mcp/memory_http_service.jsonl'
            StdoutLogPath = 'artifacts/mcp/memory_http_stdout.log'
            StderrLogPath = 'artifacts/mcp/memory_http_stderr.log'
            Dependencies = @(
                @{
                    Kind = 'tcp'
                    Name = 'redis'
                    Host = '127.0.0.1'
                    Port = 6379
                    Required = $true
                }
            )
            RestartPolicy = @{
                IntervalMinutes = 1
                Count = 255
                MultipleInstances = 'IgnoreNew'
                WatchdogIntervalMinutes = 1
                WatchdogDurationDays = 3650
            }
        }
    }
}
