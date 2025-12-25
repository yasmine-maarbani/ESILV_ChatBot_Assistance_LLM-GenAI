from dataclasses import dataclass
from typing import List, Optional
import time
import inspect
import os

@dataclass
class LLMConfig:
    provider: str
    ollama_model: str
    vertex_model: str
    gcp_project_id: Optional[str] = None
    gcp_location: Optional[str] = None

def _normalize_vertex_model(name: str) -> str:
    if not name:
        return name
    n = name.strip()
    aliases = {
        "gemini-1.5-flash": "gemini-1.5-flash-001",
        "gemini-1.5-pro": "gemini-1.5-pro-002",
        "gemini-1.0-pro": "gemini-1.5-pro-002",
        "gemini-pro": "gemini-1.5-pro-002",
        "gemini-flash": "gemini-1.5-flash-001",
    }
    return aliases.get(n, n)

def _debug_enabled() -> bool:
    return os.getenv("DEBUG_LLM", "0").strip() in ("1", "true", "True")

def _log_debug(*args):
    if _debug_enabled():
        # Use print so logs show in console; Streamlit captures stdout
        print("[LLM DEBUG]", *args)

class LLMClient:
    def __init__(self, cfg: LLMConfig):
        self.cfg = cfg
        _log_debug("Init LLMClient", {"provider": cfg.provider, "ollama_model": cfg.ollama_model, "vertex_model": cfg.vertex_model, "project": cfg.gcp_project_id, "location": cfg.gcp_location})
                    
        # else:
        #     raise ValueError("Unknown LLM provider")

    def chat(self, messages: List[dict]) -> str:
        raise ValueError(f"You called the parent class LLMClient. You may call either OllamaClient or VertexClient instead (your provider is {self.cfg.provider}).")
        


class OllamaClient(LLMClient):
    def __init__(self, cfg: LLMConfig):
        super().__init__(cfg)
        import requests
        self._requests = requests
        self._base_url = "http://localhost:11434"
    
    def chat(self, messages: List[dict]) -> str:
        _log_debug("Chat called with provider:", self.cfg.provider)
        _log_debug("Messages:", messages)

        if self.cfg.provider == "ollama":
            # Ollama path unchanged
            payload = {"model": self.cfg.ollama_model, "messages": messages, "stream": False}
            _log_debug("Ollama payload:", payload)
            for attempt in range(2):  # one retry for cold start
                try:
                    resp = self._requests.post(
                        f"{self._base_url}/api/chat",
                        json=payload,
                        timeout=300,
                    )
                    _log_debug("Ollama HTTP status:", resp.status_code)
                    resp.raise_for_status()
                    data = resp.json()
                    ## debugger print
                    print("Ollama RAW JSON:", data)
                    if isinstance(data, dict):
                        if "message" in data and isinstance(data["message"], dict):
                            content = data["message"].get("content", "")
                            _log_debug("Ollama parsed content (message.content):", content)
                            if content:
                                return content
                        if "response" in data and isinstance(data["response"], str):
                            content = data["response"]
                            _log_debug("Ollama parsed content (response):", content)
                            return content
                    _log_debug("Ollama content empty or unknown shape")
                    return ""
                except self._requests.exceptions.ReadTimeout as e:
                    _log_debug("Ollama ReadTimeout on attempt", attempt + 1, "error:", str(e))
                    if attempt == 0:
                        time.sleep(2)
                        continue
                    raise
                except Exception as e:
                    _log_debug("Ollama exception:", repr(e))
                    raise
        else:
            raise ValueError(f"The LLM provider is {self.cfg.provider}, but you called OllamaClient.")


class VertexClient(LLMClient):
    def __init__(self, cfg: LLMConfig):
        super().__init__(cfg)
        from vertexai import init
        init(project=cfg.gcp_project_id, location=cfg.gcp_location)
    
    def chat(self, messages: List[dict]) -> str:
        _log_debug("Chat called with provider:", self.cfg.provider)
        _log_debug("Messages:", messages)

        if self.cfg.provider == "vertex":
            # Vertex-specific handling
            from vertexai.generative_models import GenerativeModel, Part, Content

            model_name = _normalize_vertex_model(self.cfg.vertex_model)
            _log_debug("Vertex normalized model:", model_name)

            # Collect system messages separately
            system_chunks: List[str] = []
            vertex_contents: List[Content] = []

            for m in messages:
                role = m.get("role", "user")
                text = m.get("content", "")
                if not text:
                    continue
                if role == "system":
                    system_chunks.append(text)
                else:
                    # Vertex roles: "user" and "model" (assistant -> model)
                    vertex_role = "user" if role == "user" else "model"
                    vertex_contents.append(Content(role=vertex_role, parts=[Part.from_text(text)]))

            system_instruction = "\n\n".join(system_chunks) if system_chunks else None
            _log_debug("Vertex system_instruction:", system_instruction)
            _log_debug("Vertex contents count:", len(vertex_contents))

            # Create model; some SDK versions accept system_instruction in constructor
            try:
                model = GenerativeModel(model_name, system_instruction=system_instruction) if system_instruction else GenerativeModel(model_name)
                _log_debug("Vertex model constructed with constructor system_instruction:", bool(system_instruction))
            except TypeError:
                _log_debug("Vertex constructor does not accept system_instruction; using plain constructor")
                model = GenerativeModel(model_name)

            # Feature-detect support for system_instruction in generate_content
            try:
                supports_sys_kw = "system_instruction" in inspect.signature(model.generate_content).parameters
            except Exception:
                supports_sys_kw = False
            _log_debug("Vertex generate_content supports system_instruction:", supports_sys_kw)

            # Fallback: if system_instruction not supported, prepend as first user message
            if system_instruction and not supports_sys_kw:
                prepend = Content(role="user", parts=[Part.from_text(f"System instructions:\n{system_instruction}")])
                vertex_contents.insert(0, prepend)
                _log_debug("Prepended system instructions as first user content")

            # Generate
            try:
                if system_instruction and supports_sys_kw:
                    resp = model.generate_content(vertex_contents, system_instruction=system_instruction)
                    # debugger print
                    print("response:", resp)
                    _log_debug("Vertex generate_content called with system_instruction kwarg")
                else:
                    resp = model.generate_content(vertex_contents)
                    print("response:", resp)
                    _log_debug("Vertex generate_content called without system_instruction kwarg")
            except Exception as e:
                _log_debug("Vertex generate_content exception:", repr(e))
                raise

            # Log raw response object (safe attribute access)
            try:
                _log_debug("Vertex response .text:", getattr(resp, "text", None))
                _log_debug("Vertex response .candidates:", getattr(resp, "candidates", None))
            except Exception:
                pass

            return getattr(resp, "text", "")

        else:
            raise ValueError(f"The LLM provider is {self.cfg.provider}, but you called VertexClient.")
