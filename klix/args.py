import argparse
from typing import Optional, Sequence

class CLIArgsParser:
    def __init__(self, app_name: str, app_version: str, app_description: str):
        self.parser = argparse.ArgumentParser(
            prog=app_name,
            description=app_description,
            add_help=False # We will add custom help handling later
        )
        self.parser.add_argument(
            "-v", "--version", action="version", version=f"%(prog)s {app_version}"
        )
        self.parser.add_argument(
            "--config", help="Path to a custom configuration file."
        )
        self.parser.add_argument(
            "--debug", action="store_true", help="Enable debug mode."
        )

    def parse_args(self, args: Optional[Sequence[str]] = None):
        return self.parser.parse_args(args=args)

    def add_argument(self, *args, **kwargs):
        self.parser.add_argument(*args, **kwargs)

    def add_argument_group(self, *args, **kwargs):
        return self.parser.add_argument_group(*args, **kwargs)