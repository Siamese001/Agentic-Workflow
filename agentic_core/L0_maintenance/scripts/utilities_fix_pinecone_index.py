import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
load_dotenv()
api_key: Any = os.getenv('PINECONE_API_KEY')
pc: Any = Pinecone(api_key=api_key)
index_name: Any = 'canon-memory-l2'
if index_name in pc.list_indexes().names():
    pc.delete_index(index_name)
pc.create_index(name=index_name, dimension=384, metric='cosine', spec=ServerlessSpec(cloud='aws', region='us-east-1'))
