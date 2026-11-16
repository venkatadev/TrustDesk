"""Amazon Bedrock implementation of LLMClient, using the Converse API (same call for any model)."""

DEFAULT_MAX_TOKENS = 1024


class BedrockClient:
    def __init__(self, model_id: str, region: str | None = None, runtime=None, max_tokens: int = DEFAULT_MAX_TOKENS):
        """`model_id` is required and never guessed: pin the exact model version you have approved.

        `runtime` is a boto3 'bedrock-runtime' client; it is created here unless one is passed in.
        """
        if not model_id:
            raise ValueError("a Bedrock model id is required")
        if runtime is None:
            import boto3  # imported here so the rest of TrustDesk works without AWS set up

            runtime = boto3.client("bedrock-runtime", region_name=region)
        self.model_id = model_id
        self.max_tokens = max_tokens
        self._runtime = runtime

    def complete(self, system: str, prompt: str) -> str:
        response = self._runtime.converse(
            modelId=self.model_id,
            system=[{"text": system}],
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": self.max_tokens, "temperature": 0},  # 0: repeatable answers
        )
        blocks = response["output"]["message"]["content"]
        text = "".join(block["text"] for block in blocks if "text" in block).strip()
        if not text:
            raise RuntimeError(f"model {self.model_id} returned no text")
        return text
