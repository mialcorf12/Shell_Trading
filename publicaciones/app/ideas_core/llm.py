"""Claude API client. Reads ANTHROPIC_API_KEY; model from CLAUDE_MODEL."""
from __future__ import annotations

import os

DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5")


class ClaudeClient:
    def __init__(self, model: str = DEFAULT_MODEL, max_tokens: int = 2000):
        import anthropic  # imported lazily so tests don't need the SDK

        self._client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens

    def rewrite(self, system: str, user: str) -> str:
        msg = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        if getattr(msg, "stop_reason", None) == "max_tokens":
            raise RuntimeError("la respuesta de la IA se cortó por el límite de tokens; el borrador queda intacto")
        return "".join(block.text for block in msg.content if block.type == "text")
