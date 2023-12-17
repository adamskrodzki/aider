import tiktoken

from .model import Model

cached_model_details = None


import openai

class OpenRouterModel(Model):
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/"

    def __init__(self, client, name):
        global cached_model_details
        if name == "mistralai/mixtral-8x7b":
            name = "mistralai/mixtral-8x7b-instruct"
            self.max_context_tokens = 32 * 1024  # 32 known tokens
            # Ensure the client is using openrouter.ai base URL for this model
            client.base_url = self.OPENROUTER_BASE_URL
            cached_model_details = None
        elif name.startswith("gpt-4") or name.startswith("gpt-3.5-turbo"):
            name = "openai/" + name
            # Ensure the client is using the default OpenAI base URL for other models
            client.base_url = openai.api_base

        self.name = name
        self.edit_format = edit_format_for_model(name)
        self.use_repo_map = self.edit_format == "diff"

        # TODO: figure out proper encodings for non openai models
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        import json

        def serialize_model_details(details):
            try:
                # Attempt to serialize the model details directly
                return json.dumps(details, default=lambda o: o.__dict__)
            except TypeError:
                # If the above fails, manually construct a dictionary
                return json.dumps({'id': details.id, 'context_length': details.context_length, 'pricing': details.pricing})

        print("Checking if cached_model_details needs to be refetched...")
        if cached_model_details is None:
            print("Refetching model details...", client.base_url)
            cached_model_details = client.models.list().data
        if client.base_url == self.OPENROUTER_BASE_URL:
            # Deserialize the JSON strings into Python objects
            deserialized_details = [json.loads(detail) for detail in serialized_details]
            print("Deserialized cached model details!", deserialized_details)
            # Use the deserialized objects to find the model details
            found = next(
                (details for details in deserialized_details if details.get("id") == name), None
            )
        else:
            found = next(
                (details for details in cached_model_details if details.get("id") == name), None
            )

        if found:
            self.max_context_tokens = int(found.get("context_length"))
            self.prompt_price = round(float(found.get("pricing").get("prompt")) * 1000, 6)
            self.completion_price = round(float(found.get("pricing").get("completion")) * 1000, 6)

        else:
            raise ValueError(f"invalid openrouter model: {name}")


# TODO run benchmarks and figure out which models support which edit-formats
def edit_format_for_model(name):
    if any(str in name for str in ["gpt-4", "claude-2", "mistralai/mixtral-8x7b"]):
        return "diff"

    return "whole"
