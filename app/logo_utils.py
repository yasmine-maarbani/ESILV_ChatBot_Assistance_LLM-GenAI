import os

def resolve_logo_path(raw_path: str, app_dir: str) -> str | None:
    if not raw_path:
        return None
    # If it's a URL, return as-is
    if raw_path.startswith(("http://", "https://")):
        return raw_path
    # If absolute and exists, return
    if os.path.isabs(raw_path) and os.path.exists(raw_path):
        return raw_path
    # Try relative to CWD
    if os.path.exists(raw_path):
        return raw_path
    # Try relative to the app directory (where this module lives)
    candidate = os.path.join(app_dir, raw_path)
    if os.path.exists(candidate):
        return candidate
    # Try one level up (project root) if app is a subfolder
    parent_candidate = os.path.join(os.path.dirname(app_dir), raw_path)
    if os.path.exists(parent_candidate):
        return parent_candidate
    return None