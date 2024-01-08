import json
 
class model():
    def __init__(self):
       pass

    def generate(self, data, prompt=None, tables=None):
        """
        Arguments:
            data: list of python dictionaries containing 'id' and 'question'
            prompt: list of prompts if any
            tables: database schema if any
        Returns:
            labels: python dictionary containing sql prediction or 'null' values associated with ids
        """
        labels = {}

        for sample in data:
            labels[sample["id"]] = "null"

        return labels