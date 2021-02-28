from argparse import ArgumentParser
import sys

parser = ArgumentParser()
subparsers = parser.add_subparsers()
###
# ? 定义参数
###
# extract subcommand
extract_cmd = subparsers.add_parser("extract", help="提取关键词或词组")
extract_cmd.add_argument("category", nargs="?", default=None)
extract_cmd.add_argument("line", nargs="?", default=None)
extract_cmd.add_argument("-f", help="文件名")
# parse subcommand
parse_cmd = subparsers.add_parser("parse", help="分析句子")
###
# ? 开始...
###
args = parser.parse_args()
# ! extract
if sys.argv[1] == "extract":
    if args.category and args.f:
        from extract import extract
        extract(file=args.f, category=args.category)
    if args.category and args.line:
        from extract import extract
        extract(line=args.line, category=args.category)
# ! parse
elif sys.argv[1] == "parse":
    line = input("input sentence:\n")
    from parse import parse
    parse(line)