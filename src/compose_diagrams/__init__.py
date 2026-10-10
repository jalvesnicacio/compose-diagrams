from pathlib import Path

import yaml

from .diagram_builder import DiagramBuilder

FORMATS = ("png", "svg", "pdf", "jpg")
DIRECTIONS = ("TB", "BT", "LR", "RL")


class ComposeError(Exception):
    """The input is not a usable docker-compose file."""


def render(compose_file, output, outformat="png", direction="TB"):
    """Render the docker-compose file as a diagram image.

    `output` is the image path without extension. Returns the path of the
    generated image and the equivalent Diagram as Code script.
    """
    with open(compose_file) as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            raise ComposeError("invalid YAML: " + str(e))
    if not isinstance(data, dict) or not isinstance(data.get('services'), dict):
        raise ComposeError("no 'services' section found")

    diagram = (
        DiagramBuilder(data)
        .with_title()
        .with_services()
        .with_volumes()
        .with_networks()
        .build()
        )
    script = diagram.design(str(output), outformat, direction)
    return Path(str(output) + "." + outformat), script
