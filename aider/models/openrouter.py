import tiktoken

from .model import Model

cached_model_details = None


import openai

class OpenRouterModel(Model):
    OPENROUTER_BASE_URL = "https://api.openrouter.ai"

    def __init__(self, client, name):
        if name == "mixtral-8x7B":
            name = "mistralai/mixtral-8x7b"
            self.max_context_tokens = 32 * 1024  # 32 known tokens
            # Ensure the client is using openrouter.ai base URL for this model
            client.base_url = self.OPENROUTER_BASE_URL
        elif name.startswith("gpt-4") or name.startswith("gpt-3.5-turbo"):
            name = "openai/" + name
            # Ensure the client is using the default OpenAI base URL for other models
            client.base_url = openai.api_base

        self.name = name
        self.edit_format = edit_format_for_model(name)
        self.use_repo_map = self.edit_format == "diff"

        # TODO: figure out proper encodings for non openai models
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        global cached_model_details
        if cached_model_details is None:
            cached_model_details = client.models.list().data
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
