from quantizer import Quantize
from constants import *
import argparse


parser = argparse.ArgumentParser(description="Quantize a set of midi files.")
parser.add_argument(
    "-p",
    dest="progress",
    action="store_const",
    default=False,
    const=True,
    help="Enables progressbar (default: False)",
)

parser.add_argument(
    "-r",
    dest="recursive",
    action="store_const",
    default=False,
    const=True,
    help="Recursively goes through subfolders of input_path (default: False)",
)

parser.add_argument(
    "-s",
    dest="stats",
    action="store_const",
    default=False,
    const=True,
    help="Display some stats about the quantization. (default: False)",
)

parser.add_argument(
    "-i",
    dest="input_path",
    default="data/default/",
    help='Sets the input path (default: "data/default/")',
)

parser.add_argument(
    "-o",
    dest="output_path",
    default="data/quantized/",
    help='Sets the output path (default: "data/quantized/")',
)

parser.add_argument(
    "-n",
    dest="note_type",
    default=SIXTY_FOURTH_NOTE,
    help='Sets quater notes per beat (default: "1/64")',
)


def main():
    args = parser.parse_args().__dict__
    quantize = Quantize(
        args["input_path"], args["output_path"], args["recursive"], args["progress"]
    )
    quantize.quantize(args["note_type"], args["stats"])


main()
