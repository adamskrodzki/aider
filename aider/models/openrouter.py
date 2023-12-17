import tiktoken

from .model import Model

cached_model_details = None


import openai

class OpenRouterModel(Model):
    OPENROUTER_BASE_URL = "https://api.openrouter.ai"

    def __init__(self, client, name):
        print(f"Initializing OpenRouterModel with name: {name}")
        global cached_model_details
        if name == "mixtral-8x7B":
            name = "mistralai/mixtral-8x7b"
            self.max_context_tokens = 32 * 1024  # 32 known tokens
            # Ensure the client is using openrouter.ai base URL for this model
            client.base_url = self.OPENROUTER_BASE_URL
            cached_model_details = None
            print("Using mixtral-8x7B")
        elif name.startswith("gpt-4") or name.startswith("gpt-3.5-turbo"):
            print("Using openAI")
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
            print("Refetching model details...")
            cached_model_details = client.models.list().data
        serialized_details = [serialize_model_details(detail) for detail in cached_model_details]
        print("Serialized cached model details!", serialized_details)
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
