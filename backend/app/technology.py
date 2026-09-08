import re
from typing import Any

_VERSION_RE = re.compile(r"(?<![A-Za-z0-9])v?(\d+(?:\.\d+){1,3})(?![A-Za-z0-9])", re.IGNORECASE)
_CATEGORY_TAGS = {
    "cms": "CMS",
    "framework": "framework",
    "server": "server",
    "library": "library",
    "js": "library",
    "javascript": "library",
}
_ALIASES = {
    "apache": "Apache HTTP Server",
    "apache httpd": "Apache HTTP Server",
    "jquery": "jQuery",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "nginx": "Nginx",
    "php": "PHP",
    "reactjs": "React",
    "react.js": "React",
    "wordpress": "WordPress",
}


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or None


def _tags(item: dict[str, Any], info: dict[str, Any], metadata: dict[str, Any]) -> set[str]:
    values: list[Any] = []
    for container in (item, info, metadata):
        candidate = container.get("tags")
        if isinstance(candidate, list):
            values.extend(candidate)
        elif isinstance(candidate, str):
            values.extend(candidate.split(","))
    return {str(value).strip().lower() for value in values if str(value).strip()}


def _normalize_name(value: str) -> str:
    name = re.sub(r"\s+(?:version|technology|tech)\s+ detection$", "", value, flags=re.IGNORECASE)
    name = re.sub(r"\s+detected$", "", name, flags=re.IGNORECASE).strip(" -:")
    return _ALIASES.get(name.lower(), name)


def extract_technology(item: dict[str, Any]) -> dict[str, str | None] | None:
    info = item.get("info") if isinstance(item.get("info"), dict) else {}
    metadata = info.get("metadata") if isinstance(info.get("metadata"), dict) else {}
    tags = _tags(item, info, metadata)
    if "tech" not in tags and not tags.intersection({"technology", "cms", "framework", "server", "library"}):
        return None

    raw_name = next(
        (_text(metadata.get(key)) for key in ("technology", "product", "name") if _text(metadata.get(key))),
        None,
    )
    raw_name = raw_name or _text(info.get("name")) or _text(item.get("matcher-name")) or "Unknown technology"
    name = _normalize_name(raw_name)

    version = next(
        (_text(metadata.get(key)) for key in ("version", "technology-version", "product-version") if _text(metadata.get(key))),
        None,
    )
    version = version or _text(info.get("version")) or _text(item.get("version"))
    if version:
        version = _VERSION_RE.search(version).group(1) if _VERSION_RE.search(version) else version
    else:
        match = _VERSION_RE.search(raw_name)
        version = match.group(1) if match else None

    category = next((_CATEGORY_TAGS[tag] for tag in tags if tag in _CATEGORY_TAGS), "technology")
    return {"name": name, "version": version, "category": category, "source": "nuclei"}
