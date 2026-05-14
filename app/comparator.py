import json

class SHLComparator:
    def __init__(self, data_path='data/shl_catalog.json'):
        with open(data_path, 'r') as f:
            self.catalog = {item['name'].lower(): item for item in json.load(f)}

    def compare(self, names):
        """
        names: list of assessment names to compare
        """
        comparisons = []
        for name in names:
            item = self.catalog.get(name.lower())
            if item:
                comparisons.append(item)
        
        if len(comparisons) < 2:
            return "I need at least two valid SHL assessments to compare."

        # In a real scenario, this would be passed to an LLM with these details
        # For now, we structure the data for the agent
        return comparisons
