"""FarmGuard CLI — command-line entry point.

Provides subcommands for running the pipeline, validating config,
checking system health, and printing version info.
"""

from __future__ import annotations

import argparse
import sys

import farmguard
from farmguard.config import load_config, validate_config


def _cmd_run(args: argparse.Namespace) -> int:
    """Handle the ``run`` subcommand."""
    config_path: str = args.config
    source: str | None = args.source
    simulate: bool = args.simulate
    monitor: bool = args.monitor

    errors = validate_config(config_path)
    if errors:
        for err in errors:
            print(f"  ✗ {err}", file=sys.stderr)
        return 1

    cfg = load_config(config_path)
    if source:
        cfg.camera.source = source

    print(f"FarmGuard v{farmguard.__version__}")
    print(f"  Config    : {config_path}")
    print(f"  Source    : {cfg.camera.source}")
    print(f"  Simulate  : {simulate}")
    print(f"  Monitor   : {monitor}")
    print(f"  Detector  : {cfg.detector.model_path}")
    print(f"  Classifier: {cfg.classifier.model_path}")
    print()
    print("Pipeline ready. (Full runtime not yet implemented.)")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    """Handle the ``validate-config`` subcommand."""
    errors = validate_config(args.config)
    if errors:
        print("Configuration errors:")
        for err in errors:
            print(f"  ✗ {err}")
        return 1
    print(f"✓ Config is valid: {args.config}")
    return 0


def _cmd_version(_args: argparse.Namespace) -> int:
    """Handle the ``version`` subcommand."""
    print(f"farmguard {farmguard.__version__}")
    return 0


def _cmd_doctor(_args: argparse.Namespace) -> int:
    """Handle the ``doctor`` subcommand."""
    print("Doctor checks not yet implemented.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser."""
    parser = argparse.ArgumentParser(
        prog="farmguard",
        description="FarmGuard — Edge-AI farmland animal detection CLI",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # -- run -----------------------------------------------------------
    run_p = sub.add_parser("run", help="Run the detection pipeline")
    run_p.add_argument("--config", required=True, help="Path to YAML config")
    run_p.add_argument("--source", default=None, help="Video source override")
    run_p.add_argument("--simulate", action="store_true", help="Use simulation backends")
    run_p.add_argument("--monitor", action="store_true", help="Start monitoring server")
    run_p.set_defaults(func=_cmd_run)

    # -- validate-config -----------------------------------------------
    val_p = sub.add_parser("validate-config", help="Validate a config file")
    val_p.add_argument("--config", required=True, help="Path to YAML config")
    val_p.set_defaults(func=_cmd_validate)

    # -- version -------------------------------------------------------
    ver_p = sub.add_parser("version", help="Print version")
    ver_p.set_defaults(func=_cmd_version)

    # -- doctor --------------------------------------------------------
    doc_p = sub.add_parser("doctor", help="Run system health checks")
    doc_p.set_defaults(func=_cmd_doctor)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Exit code (0 = success).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

