========================================================================================================
LAZY LOADER                                   | SILENT SWALLOWER
========================================================================================================
Purpose                                       | Purpose
---------------------------------------------|-----------------------------------------
Delay expensive initialization until needed   | Hide errors (usually unintentionally)

Behavior                                      | Behavior
---------------------------------------------|-----------------------------------------
First access triggers controlled load         | Exception occurs during operation
Object then cached for future use             | try/except suppresses the failure
Errors propagate normally                     | Error disappears silently

Execution Flow                                | Execution Flow
---------------------------------------------|-----------------------------------------
Client                                        | Client
  |                                           |   |
  v                                           |   v
Check "loaded?"                               | Operation executes
  |                                           |   |
  +----YES----> Return cached instance        |   v
  |                                           | Exception raised
  NO                                          |   |
  |                                           |   v
  v                                           | try:
Load dependency                               |     do_work()
(module/model/service)                        | except:
  |                                           |     pass
  v                                           |   |
Cache instance                                |   v
  |                                           | Return None / partial state
  v                                           |
Return object                                 |

System Effect                                 | System Effect
---------------------------------------------|-----------------------------------------
Improves startup performance                  | Masks root causes
Deterministic behavior                        | Produces misleading system health
Transparent failure behavior                  | Breaks observability and debugging

Code Pattern                                  | Code Pattern
---------------------------------------------|-----------------------------------------
if obj is None:                               | try:
    obj = load()                              |     do_work()
return obj                                    | except Exception:
                                              |     pass
========================================================================================================
