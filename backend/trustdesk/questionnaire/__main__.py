"""Command line: answer a questionnaire file from a folder of policy documents.

    uv run python -m trustdesk.questionnaire SOURCE DEST --policies POLICY_DIR
"""

import argparse
import os
import sys

from trustdesk.knowledge.store import PolicyStore, set_policy_store
from trustdesk.llm.bedrock import BedrockClient
from trustdesk.llm.drafting import llm_drafter, set_drafter
from trustdesk.questionnaire.process import answer_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="trustdesk.questionnaire", description=__doc__.split("\n")[0])
    parser.add_argument("source", help="questionnaire to read (.csv or .xlsx)")
    parser.add_argument("dest", help="where to write the answered copy (same file type)")
    parser.add_argument("--policies", required=True, help="folder of .txt/.md policy documents")
    parser.add_argument(
        "--model-id",
        default=os.environ.get("TRUSTDESK_MODEL_ID"),
        help="Bedrock model id to draft with (or env TRUSTDESK_MODEL_ID); omit to copy policy text verbatim",
    )
    parser.add_argument("--region", default=os.environ.get("AWS_REGION"), help="AWS region for Bedrock")
    args = parser.parse_args(argv)

    if args.model_id:
        set_drafter(llm_drafter(BedrockClient(args.model_id, region=args.region)))

    store = PolicyStore.from_directory(args.policies)
    if not store.chunks:
        print(f"No .txt or .md policy text found in {args.policies}", file=sys.stderr)
        return 1
    set_policy_store(store)

    state = answer_file(args.source, args.dest)
    summary = ", ".join(f"{n} {status}" for status, n in sorted(state.counts.items())) or "no questions"
    print(f"Wrote {args.dest}: {summary}")
    for result in state.results:
        if result.status != "ready":
            print(f"  needs attention ({result.status}): {result.question}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
