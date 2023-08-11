from flashcard.server import WebUX
import argparse
from flashcard.logic import file_maker, range_maker, TOTAL_QUESTIONS


def parseargs():
    parser = argparse.ArgumentParser("flash-cards")
    parser.add_argument(
        "--filename",
        "-i",
        type=file_maker,
        default=None,
        help="load questions from a file, ignoring tables, max-int, and operators",
    )
    parser.add_argument(
        "--tables",
        "-T",
        type=range_maker,
        default="0-10",
        help="list of tables to construct. (eg. '0,1,2,10-12')",
    )
    parser.add_argument(
        "--total",
        "-N",
        type=int,
        default=TOTAL_QUESTIONS,
        help="Total number of flash cards to show",
    )
    parser.add_argument(
        "--wait_time",
        "-w",
        type=int,
        default=-1,
        help="Time waiting on answer, -1 for infinite",
    )
    parser.add_argument(
        "--operators",
        "-o",
        type=str,
        default="*",
        help="List of flash card operators. (eg. '-+x/÷')",
    )
    parser.add_argument("--repeat", choices=["end", "next", "none"], default="end")
    parser.add_argument("--no_hints", action="store_true", default=False)
    return parser.parse_args()


if __name__ == "__main__":
    args = parseargs()
    args.practice_data = args.filename or []
    args.filename = None
    WebUX(args).main()
