+------------------------------------------------------+------------------------------------------------------+
| NORMAL: SERIAL MCP CALL                              | BROKEN: MCP BATCHED WITH OTHER TOOLS                 |
+------------------------------------------------------+------------------------------------------------------+
| [ User asks ]                                        | [ User asks ]                                        |
| "Run MCP tool"                                       | "Run MCP tool + read_file + web/search"              |
|                                                      |                                                      |
|        |                                             |        |                                             |
|        v                                             |        v                                             |
| [ One tool call launched ]                           | [ Multiple tool calls launched together ]            |
|                                                      |                                                      |
|        |                                             |        |                                             |
|        v                                             |        v                                             |
| [ MCP client transport ]                             | [ MCP client transport ]                             |
| handles one stream cleanly                           | tries to juggle multiple streams at once             |
|                                                      |                                                      |
|        |                                             |        |                                             |
|        v                                             |        v                                             |
| [ ADG MCP server ]                                   | [ ADG MCP server ]       [ other tools ]             |
| receives request                                     | receives request         also running fine           |
|                                                      |                                                      |
|        |                                             |        |                                             |
|        v                                             |        v                                             |
| [ MCP result returns ]                               | [ transport race / stream closes early ]             |
|                                                      |                                                      |
|        |                                             |        +----------------------+                      |
|        v                                             |                               |                      |
| [ Success ]                                          |                               v                      |
|                                                      |                     [ non-MCP tools succeed ]        |
| MENTAL MODEL:                                        |                     [ MCP result canceled/dropped ]  |
| One librarian. One request.                          |                                                      |
| Clean handoff, clean return.                         |        |                                             |
|                                                      |        v                                             |
|                                                      | [ Looks like ADG hung ]                              |
|                                                      | but server is actually fine                          |
|                                                      |                                                      |
|                                                      | MENTAL MODEL:                                        |
|                                                      | The librarian answered,                              |
|                                                      | but the phone line got cut                           |
|                                                      | because too many calls were merged together.         |
+------------------------------------------------------+------------------------------------------------------+