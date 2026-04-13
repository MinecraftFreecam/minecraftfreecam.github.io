import re
import tomllib
from os import environ
from pathlib import Path
from typing import TextIO
from mkdocs.exceptions import PluginError


FREECAM_DIRS = [
    Path(it)
    for it in [environ.get("FREECAM_DIR"), "freecam", "../freecam", "../Freecam"]
    if it is not None
]
FREECAM_TAG_PATTERN = re.compile(r"<!--\s*freecam:(\w+)\s*-->")
WEBSITE_START_PATTERN = re.compile(r'<!--\s*website:start\s+id="(\w+)"\s*-->')
WEBSITE_END_PATTERN = re.compile(r"<!--\s*website:(?:end|stop)\s*-->")
_state = {}


def _load_state(directory: Path) -> bool:
    """
    Attempt to load Freecam assets from a directory.
    Returns True on success, False if expected files are missing.
    """
    readme = directory / "README.md"
    metadata = directory / "metadata.toml"
    if not readme.is_file() or not metadata.is_file():
        return False
    with open(readme, "r") as f:
        _state["readme_sections"] = _extract_sections(f)
    with open(metadata, "rb") as f:
        _state["metadata"] = tomllib.load(f)
    return True


def _extract_sections(file: TextIO) -> dict[str, str]:
    """
    Extract <!-- website:start id="foo" --> … <!-- website:end -->
    blocks from a Markdown or HTML file.
    """
    sections = {}
    current_id = None
    current_lines: list[str] = []

    for line in file:
        stripped = line.strip()

        if current_id is None:
            match = WEBSITE_START_PATTERN.fullmatch(stripped)
            if match:
                current_id = match.group(1)
        else:
            if WEBSITE_END_PATTERN.fullmatch(stripped):
                sections[current_id] = "".join(current_lines)
                current_id = None
                current_lines = []
            else:
                current_lines.append(line)

    if current_id is not None:
        raise ValueError(f'Unclosed website:start block with id="{current_id}"')

    return sections


def on_serve(server, config, builder):
    """
    Called when the serve command is used.
    It only runs once, after the first build finishes.
    https://www.mkdocs.org/dev-guide/plugins/#on_serve
    """
    directory = _state.get("watch")
    if directory:
        server.watch(str(directory), builder)


def on_pre_build(config):
    """
    Load Freecam files into _state.

    Called before starting the build.
    https://www.mkdocs.org/dev-guide/plugins/#on_pre_build
    """
    for directory in FREECAM_DIRS:
        if directory.is_dir() and _load_state(directory):
            _state["watch"] = directory
            return

    looked = "\n".join(f"  - {d}" for d in FREECAM_DIRS)
    raise PluginError(
        f"Freecam assets not found. Looked in:\n{looked}\n"
        "Set FREECAM_DIR if it is located somewhere else."
    )


def on_page_markdown(markdown, page, config, files):
    """
    Inject Freecam's readme sections into markdown content.

    Called after the page's markdown is loaded from file.
    https://www.mkdocs.org/dev-guide/plugins/#on_page_markdown
    """
    sections = _state.get("readme_sections", {})
    lines = []
    for line in markdown.splitlines(keepends=True):
        stripped = line.strip()
        match = FREECAM_TAG_PATTERN.fullmatch(stripped)
        if match:
            tag = match.group(1)
            if tag in sections:
                lines.append(sections[tag])
                continue
        lines.append(line)
    return "".join(lines)


def on_page_context(context, page, config, nav):
    """
    Load Freecam's metadata into template context.

    Called after the context for a page is created.
    https://www.mkdocs.org/dev-guide/plugins/#on_page_context
    """
    context["freecam"] = _state.get("metadata", {})
    return context
