#!/usr/bin/env python3

import sys
from Bio import SeqIO
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
from collections import OrderedDict
from itertools import groupby
from pathlib import Path
from signal import signal, SIGPIPE, SIG_DFL

from Bio.SeqUtils.CheckSum import seguid


def parse_argv(argv):
	parser = ArgumentParser(
		description="compute the unique set of sequences",
		formatter_class=ArgumentDefaultsHelpFormatter
	)

	parser.add_argument(
		"file",
		type=FileType(),
		help="the sequence file"
	)
	parser.add_argument(
		"-fmt", "--fmt", default="fasta"
	)
	parser.add_argument(
		"-map", "--map", type=Path,
		help="the path prefix for the output files"
	)

	args = parser.parse_args(argv)

	return args


def main(argv):
	args = parse_argv(argv[1:])

	# aggregate sequences by unique hash
	with args.file as file:
		records = OrderedDict(
			(key, list(val)) for key, val in
			groupby(SeqIO.parse(file, args.fmt), key=lambda val: seguid(val.seq))
		)

	# map unique sequence index to unique hash
	if args.map:
		with args.map.open("w") as file:
			width = len(str(len(records)))
			print("idx", "key", "id", "description", sep="\t", file=file)
			for idx, ele in enumerate(records.items(), start=1):
				idx, key, val = f"{idx:0{width}d}", ele[0], ele[1]
				for record in val:
					print(idx, key, record.id, record.description, sep="\t", file=file)
					record.id, record.description = idx, ""

	# output unique sequences
	SeqIO.write((val[0] for val in records.values()), sys.stdout, args.fmt)

	return 0


if __name__ == "__main__":
	signal(SIGPIPE, SIG_DFL)
	sys.exit(main(sys.argv))