import os
import re
import json
import openai
import tiktoken

def post_process(answer):
    answer = answer.replace('\n', ' ')
    answer = re.sub('[ ]+', ' ', answer)
    return answer

class model():
    def __init__(self):
        current_real_dir = os.path.dirname(os.path.realpath(__file__))
        target_dir = os.path.join(current_real_dir, 'sample_submission_chatgpt_api_key.json')

        if os.path.isfile(target_dir):
            with open(target_dir, 'rb') as f:
                openai.api_key = json.load(f)['key']
        if not os.path.isfile(target_dir) or openai.api_key == "":
            raise Exception("Error: no API key file found.")

    def set_api_key(self, api_key):
        """
        Arguments:
           api_key: the API key for OpenAI.
        """
        openai.api_key = api_key

    def ask_chatgpt(self, prompt, model="gpt-3.5-turbo-16k", temperature=0.0):
        response = openai.ChatCompletion.create(
                    model=model,
                    temperature=temperature,
                    messages=prompt
                )
        return response.choices[0]['message']['content']

    def generate(self, input_data):
        """
        Arguments:
            input_data: list of python dictionaries containing 'id' and 'input'
        Returns:
            labels: python dictionary containing sql prediction or 'null' values associated with ids
        """

        labels = {}

        for sample in input_data:
            answer = self.ask_chatgpt(sample['input'])            
            labels[sample["id"]] = post_process(answer)

        return labels