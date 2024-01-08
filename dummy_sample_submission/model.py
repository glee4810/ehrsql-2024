import json
 
class model():
    def __init__(self):
       pass

    def generate(self, input_data):
        """
        Arguments:
            input_data: list of python dictionaries containing 'id' and 'input'
        Returns:
            labels: python dictionary containing sql prediction or 'null' values associated with ids
        """
        labels = {}

        for sample in input_data:
            labels[sample["id"]] = "null"

        return labels