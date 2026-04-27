STATIC METHOD                                          INSTANCE METHOD
=====================                                  =====================

+----------------------------------+                   +----------------------------------+
| Stored on the class              |                   | Stored on the class definition   |
| but used like a utility          |                   | and runs on a specific object    |
+----------------+-----------------+                   +----------------+-----------------+
                 |                                                      |
                 v                                                      v
       +----------------------+                              +----------------------+
       | Call directly on     |                              | First create object  |
       | the class            |                              | from the class       |
       |                      |                              |                      |
       | TextDocumentLoader.  |                              | loader =             |
       | load(path)           |                              | TextDocumentLoader() |
       +----------+-----------+                              +----------+-----------+
                  |                                                     |
                  v                                                     v
       +----------------------+                              +----------------------+
       | No self              |                              | Call on object       |
       | no object needed     |                              |                      |
       |                      |                              | loader.load(path)    |
       +----------+-----------+                              +----------+-----------+
                  |                                                     |
                  v                                                     v
       +----------------------+                              +----------------------+
       | Cannot use instance  |                              | Python passes        |
       | data like            |                              | self automatically   |
       | self.config          |                              |                      |
       +----------+-----------+                              +----------+-----------+
                  |                                                     |
                  v                                                     v
       +----------------------+                              +----------------------+
       | Best for helper      |                              | Can use object data  |
       | or utility logic     |                              | like self.config,    |
       |                      |                              | self.cache, etc.     |
       +----------------------+                              +----------------------+


YOUR CASE
=========

+---------------------------------------------------+     +----------------------------------------------------+
| WRONG                                             |     | RIGHT                                              |
+---------------------------------------------------+     +----------------------------------------------------+
| TextDocumentLoader.load(file_path)                |     | loader = TextDocumentLoader()                      |
|                                                   |     | loader.load(file_path)                             |
+-----------------------------+---------------------+     +-----------------------------+----------------------+
                              |                                                       |
                              v                                                       v
                 +---------------------------+                           +---------------------------+
                 | Python thinks file_path   |                           | Python sets:              |
                 | is self                   |                           | self = loader             |
                 |                           |                           | file_path = actual path   |
                 +-------------+-------------+                           +-------------+-------------+
                               |                                                       |
                               v                                                       v
                 +---------------------------+                           +---------------------------+
                 | Missing real file_path    |                           | Method runs correctly     |
                 | argument or bad binding   |                           |                           |
                 +---------------------------+                           +---------------------------+


DECISION FLOW
=============

                    +--------------------------------------+
                    | Does the method need object data?    |
                    | like self.config / self.cache / etc. |
                    +-------------------+------------------+
                                        |
                          +-------------+-------------+
                          |                           |
                          v                           v
                   +--------------+            +--------------+
                   | YES          |            | NO           |
                   +------+-------+            +------+-------+
                          |                           |
                          v                           v
               +----------------------+    +------------------------+
               | INSTANCE METHOD      |    | STATIC METHOD          |
               | def load(self, path) |    | @staticmethod          |
               +----------------------+    | def load(path)         |
                                           +------------------------+