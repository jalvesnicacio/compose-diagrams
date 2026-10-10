import argparse
import shutil
import sys
from pathlib import Path

from . import DIRECTIONS, FORMATS, ComposeError, render


def build_parser():
    parser = argparse.ArgumentParser(
        prog="compose-diagrams",
        description="Create an architecture diagram from a docker-compose file.",
    )
    parser.add_argument("compose_file", type=Path, nargs="?", help="path to the docker-compose YAML file")
    parser.add_argument(
        "-o", "--output", type=Path,
        help="output image path (default: the compose file name, in the current directory)",
    )
    parser.add_argument(
        "-f", "--format", choices=FORMATS,
        help="image format (default: taken from --output, or png)",
    )
    parser.add_argument(
        "-d", "--direction", choices=DIRECTIONS, default="TB",
        help="layout direction (default: TB, top to bottom)",
    )
    parser.add_argument(
        "--script", action="store_true",
        help="also print the equivalent Diagram as Code script",
    )
    web = parser.add_argument_group("web interface")
    web.add_argument(
        "--web", action="store_true",
        help="open the web interface in the browser (with compose_file loaded, if given)",
    )
    web.add_argument("--port", type=int, default=8000, help="port of the web interface (default: 8000)")
    web.add_argument("--no-browser", action="store_true", help="do not open the browser automatically")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.compose_file is None and not args.web:
        parser.error("a compose_file is required (or use --web)")
    if args.compose_file is not None and not args.compose_file.is_file():
        parser.error("file not found: " + str(args.compose_file))
    if shutil.which("dot") is None:
        sys.exit("error: Graphviz is not installed (the 'dot' command was not found). "
                 "See https://graphviz.org/download/")

    if args.web:
        from .web import serve
        initial = args.compose_file.read_text() if args.compose_file else ""
        try:
            serve(port=args.port, initial_compose=initial, open_browser=not args.no_browser)
        except OSError as e:
            sys.exit("error: could not start on port " + str(args.port) + " (" + str(e) + "). "
                     "Try another one with --port.")
        return

    output = args.output or Path(args.compose_file.stem)
    outformat = args.format
    suffix = output.suffix.lstrip(".").lower()
    if suffix in FORMATS:
        # "-o diagram.svg" already says the format
        outformat = outformat or suffix
        output = output.with_suffix("")
    outformat = outformat or "png"
    if output.parent != Path("."):
        output.parent.mkdir(parents=True, exist_ok=True)

    try:
        image, script = render(args.compose_file, output, outformat, args.direction)
    except ComposeError as e:
        sys.exit("error: " + str(args.compose_file) + ": " + str(e))

    if args.script:
        print(script)
    print(image, file=sys.stderr if args.script else sys.stdout)


if __name__ == "__main__":
    main()
