"""
DCL Agent CLI — compile a DCL instruction into an InvocationContext
and print it as text frames (suitable for pasting into system_instruction).

Usage:
    dcl-agent compile --bundles <path1,path2,...> --instruction "EXTRACT Entity('x')"
    dcl-agent compile --bundles <path1,path2,...> --instruction-file <file.dcl>

Output modes (--output):
    frames    — print each frame with separator (default)
    concat    — concatenate all frames into a single string
"""

import argparse
import sys


def _build_agent(bundles_arg: str):
    from dcl_agent.agent import DCLAgent
    from dcl_agent.adapter.mock import MockLLMAdapter

    bundle_paths = [p.strip() for p in bundles_arg.split(",") if p.strip()]
    return DCLAgent(bundles=bundle_paths, adapter=MockLLMAdapter())


def cmd_compile(args):
    agent = _build_agent(args.bundles)

    if args.instruction_file:
        with open(args.instruction_file, encoding="utf-8") as f:
            instruction_text = f.read()
    else:
        instruction_text = args.instruction

    instruction = agent.parser.parse(instruction_text)
    context = agent.strategy.assemble(instruction, agent.registry)

    if args.output == "concat":
        result = "\n\n".join(
            f.content for f in context.frames if hasattr(f, "content")
        )
        print(result)
    else:  # frames
        for i, frame in enumerate(context.frames):
            if hasattr(frame, "content"):
                print(f"# --- Frame {i} ---")
                print(frame.content)
                print()


def cmd_registry(args):
    """List all loaded modules and aliases."""
    import json
    agent = _build_agent(args.bundles)
    registry = agent.get_registry()
    print("=== Aliases ===")
    print(json.dumps(registry._aliases, indent=2, ensure_ascii=False))
    print("\n=== Modules ===")
    for m in registry.list_modules():
        print(m)


def main():
    parser = argparse.ArgumentParser(
        prog="dcl-agent",
        description="DCL Agent CLI — compile DCL instructions into InvocationContext",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- compile ---
    p_compile = sub.add_parser("compile", help="Compile a DCL instruction")
    p_compile.add_argument(
        "--bundles", required=True,
        help="Comma-separated paths to DCL bundle directories"
    )
    p_compile.add_argument(
        "--instruction", default=None,
        help="DCL instruction string"
    )
    p_compile.add_argument(
        "--instruction-file", default=None,
        help="Path to a file containing the DCL instruction"
    )
    p_compile.add_argument(
        "--output", choices=["frames", "concat"], default="frames",
        help="Output format (default: frames)"
    )

    # --- registry ---
    p_registry = sub.add_parser("registry", help="List loaded modules and aliases")
    p_registry.add_argument(
        "--bundles", required=True,
        help="Comma-separated paths to DCL bundle directories"
    )

    args = parser.parse_args()
    if args.command == "compile":
        cmd_compile(args)
    elif args.command == "registry":
        cmd_registry(args)


if __name__ == "__main__":
    main()
