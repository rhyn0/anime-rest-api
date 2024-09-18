import argparse

from uvicorn import Config
from uvicorn import Server

from anime_rest_api.api import create_app


def get_args(arglist: list[str] | None = None) -> argparse.Namespace:
    """Parse given argslist and return our flags and settings."""
    parser = argparse.ArgumentParser(prog="anime_rest_api.main")

    network_group = parser.add_argument_group(
        "network",
        "Network Options for modifying server runtime",
    )
    network_group.add_argument(
        "--host",
        default="localhost",
        help="What host address to bind running process to listen for connections on",
        dest="host",
    )
    network_group.add_argument(
        "-p",
        "--port",
        default=8080,
        type=int,
        help="What port to listen for incoming connections on",
        dest="port",
    )

    return parser.parse_args(arglist)


def main(args: argparse.Namespace) -> None:
    """Use uvicorn to run the application.

    TODO: uvicorn might not be our best choice long term depending on deployment plans
    """
    app = create_app()
    uv_config = Config(app=app, host=args.host, port=args.port)

    server = Server(uv_config)
    server.run()


if __name__ == "__main__":
    args = get_args()
    main(args)
