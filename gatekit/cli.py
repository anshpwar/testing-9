"""Command line: check a gateway config.   python -m gatekit.cli check CONFIG.ini"""
import argparse
import sys

from . import config


def main(argv=None, out=None):
    out = out or sys.stdout
    ap = argparse.ArgumentParser(prog="gatekit")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("file")
    args = ap.parse_args(argv)
    try:
        with open(args.file) as fh:
            router, keys = config.load(fh.read())
    except config.ConfigError as exc:
        out.write(f"invalid config: {exc}\n")
        return 2
    out.write(f"ok: {len(router.routes)} routes, {len(keys._clients)} clients\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
