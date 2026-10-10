import base64
import re
from pathlib import Path

import yaml

from .diagram_builder import DiagramBuilder

FORMATS = ("png", "svg", "pdf", "jpg")
DIRECTIONS = ("TB", "BT", "LR", "RL")


class ComposeError(Exception):
    """The input is not a usable docker-compose file."""


def load(text):
    """Parse the text of a docker-compose file."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise ComposeError("invalid YAML: " + str(e))
    if not isinstance(data, dict) or not isinstance(data.get('services'), dict):
        raise ComposeError("no 'services' section found")
    return data


def render_data(data, output, outformat="png", direction="TB"):
    """Render parsed docker-compose data as a diagram image.

    `output` is the image path without extension. Returns the path of the
    generated image and the equivalent Diagram as Code script.
    """
    diagram = (
        DiagramBuilder(data)
        .with_title()
        .with_services()
        .with_volumes()
        .with_networks()
        .build()
        )
    script = diagram.design(str(output), outformat, direction)
    image = Path(str(output) + "." + outformat)
    if outformat == "svg":
        _embed_images(image)
    return image, script


def render(compose_file, output, outformat="png", direction="TB"):
    """Render the docker-compose file as a diagram image (see render_data)."""
    with open(compose_file) as stream:
        data = load(stream)
    return render_data(data, output, outformat, direction)


def _embed_images(svg_file):
    # Graphviz links the icons by their path on this machine; inline them so
    # the SVG also shows up in a browser and on other computers.
    def inline(match):
        icon = Path(match.group(1))
        if not icon.is_file():
            return match.group(0)
        encoded = base64.b64encode(icon.read_bytes()).decode("ascii")
        return 'xlink:href="data:image/png;base64,' + encoded + '"'

    svg = svg_file.read_text(encoding="utf-8")
    svg = re.sub(r'xlink:href="([^"]+\.png)"', inline, svg)
    svg_file.write_text(svg, encoding="utf-8")
