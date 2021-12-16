from unwarcit.unwarcit import Unwarcit
from unwarcit.util import get_version
import sys
from argparse import ArgumentParser, RawTextHelpFormatter


# ============================================================================
def main(args=None):
    if sys.version_info < (2, 7):
        print(
            "Unwarcit requires python >= 2.7, you are running {0}".format(
                sys.version.split(" ")[0]
            )
        )
        return 1

    parser = ArgumentParser(
        description="Unzip Warc and Wacz files into individual components"
    )

    parser.add_argument("--version", action="version", version=get_version())

    parser.add_argument("inputs", nargs="+", help="""Paths of files to be unpacked.""")

    parser.add_argument(
        "--output",
        help="""Path where the results will be placed. Default is 'output'.""",
        default="output",
    )

    arguments = parser.parse_args(args=args)

    return Unwarcit(arguments.inputs, arguments.output).unzip()


# ============================================================================
if __name__ == "__main__":
    res = main()
    sys.exit(res)
