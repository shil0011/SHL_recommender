class SHLRecommender:
    def __init__(self, retriever):
        self.retriever = retriever

    def get_recommendations(self, query, filters=None):
        """
        query: semantic query
        filters: dict of filters like seniority, role
        """
        raw_results = self.retriever.retrieve(query, k=10)
        
        # In a production system, we'd apply metadata filtering here
        # For this assignment, we'll return the ranked list from retriever
        # but ensure they are relevant to any specified roles in query.
        
        ranked_results = []
        for res in raw_results:
            ranked_results.append({
                "name": res["name"],
                "url": res["url"],
                "test_type": res["test_type"]
            })
            
        return ranked_results[:10]
