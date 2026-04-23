+-----------------------------------------------+-----------------------------------------------+
| CLI / HOOKS                                   | IMPORTS                                       |
+-----------------------------------------------+-----------------------------------------------+
| [ Outside trigger ]                           | [ Python code ]                               |
| pre-commit / shell / Windsurf / task runner   | another .py file                              |
|                 |                             |                 |                             |
|                 v                             |                 v                             |
|       python entry_script.py                  |       import helper_module                    |
|                 |                             |                 |                             |
|                 v                             |                 v                             |
|     ENTRY-POINT SCRIPT starts                 |     HELPER MODULE loads                       |
|                 |                             |                 |                             |
|                 |----------- may import ------+------ imported by ----------------------------|
|                 |                             |                                               |
|                 v                             |                                               |
|           main() runs                         |        def helper() / class X / constants     |
|                 |                             |                                               |
|                 v                             |                                               |
|      calls imported functions --------------->+-------> returns values / objects ------------|
|                 |                                                                     ^     |
|                 v                                                                     |     |
| stdout / stderr / files / side effects                                               |     |
+-----------------------------------------------+-----------------------------------------------+
| RELATIONSHIP                                  |                                               |
+-----------------------------------------------+-----------------------------------------------+
| CLI / hook = HOW execution STARTS             | import = HOW code is REUSED inside runtime    |
| CLI script is often the outer shell           | imported modules are often the inner parts    |
| Hook/CLI kicks off the program                | imports supply the building blocks it uses    |
+-----------------------------------------------+-----------------------------------------------+
| SIMPLE MENTAL MODEL                           |                                               |
+-----------------------------------------------+-----------------------------------------------+
| [ hook / shell ] -> [ entry script ] -> [ imports helpers ] -> [ work happens ]      |
+-----------------------------------------------+-----------------------------------------------+
| YOUR CASE                                     |                                               |
+-----------------------------------------------+-----------------------------------------------+
| .windsurf/scripts/                            | usually scanned first as EXECUTION TARGETS    |
| ops_scripts/                                  | then inspect what they IMPORT underneath      |
| tools/                                        | some may be entry points, some may be helpers |
+-----------------------------------------------+-----------------------------------------------+