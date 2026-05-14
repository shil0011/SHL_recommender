import json
import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

class SHLRetriever:
    def __init__(self, data_path='data/shl_catalog.json', index_path='data/faiss_index'):
        self.data_path = data_path
        self.index_path = index_path
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_db = None
        self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self.index_path):
            print("Loading existing FAISS index...")
            self.vector_db = FAISS.load_local(self.index_path, self.embeddings, allow_dangerous_deserialization=True)
        else:
            print("Creating new FAISS index...")
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(f"Data file {self.data_path} not found. Run scraper first.")
            
            with open(self.data_path, 'r') as f:
                data = json.load(f)
            
            documents = []
            for item in data:
                content = f"{item['name']}: {item['description']}. Skills: {', '.join(item['skills_measured'])}. Roles: {', '.join(item['job_roles'])}"
                metadata = {
                    "name": item['name'],
                    "url": item['url'],
                    "test_type": item['test_type']
                }
                documents.append(Document(page_content=content, metadata=metadata))
            
            self.vector_db = FAISS.from_documents(documents, self.embeddings)
            self.vector_db.save_local(self.index_path)

    def retrieve(self, query, k=5):
        if not self.vector_db:
            return []
        results = self.vector_db.similarity_search(query, k=k)
        return [
            {
                "name": doc.metadata["name"],
                "url": doc.metadata["url"],
                "test_type": doc.metadata["test_type"],
                "relevance_summary": doc.page_content
            }
            for doc in results
        ]

if __name__ == "__main__":
    # Test retriever
    retriever = SHLRetriever()
    results = retriever.retrieve("Hiring a Java developer")
    for res in results:
        print(f"- {res['name']} ({res['test_type']})")
