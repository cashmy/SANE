import argparse
import json
from collections.abc import Sequence

from app.db.session import SessionLocal
from app.services.workflow import (
    EmailAccountNotFoundError,
    reclassify_sources_for_account,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Recompute classifier fields for stored source rows in a single "
            "mailbox without scanning Gmail or mutating provider data."
        )
    )
    parser.add_argument(
        "--account-id",
        type=int,
        required=True,
        help="EmailAccount.id to reclassify from local stored source rows.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    db = SessionLocal()
    try:
        summary = reclassify_sources_for_account(
            db,
            email_account_id=args.account_id,
        )
    except EmailAccountNotFoundError as exc:
        print(str(exc))
        return 1
    finally:
        db.close()

    print(json.dumps(summary.as_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
