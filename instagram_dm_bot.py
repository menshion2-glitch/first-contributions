"""Simple Instagram DM auto-responder.

This script uses the `instagrapi` client to log into Instagram and send
automated responses to direct messages based on keyword matching.

Usage:
    python instagram_dm_bot.py --username <username>

You will be prompted for your password unless one is provided with the
`--password` flag or the `INSTAGRAM_PASSWORD` environment variable.

Rules can be configured with a JSON file that contains a list of rules in the
form:

[
    {
        "keywords": ["hello", "hi"],
        "response": "Hello! Thanks for reaching out.",
        "case_sensitive": false
    }
]

If no file is provided, a small default rule set will be used.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional

try:
    from instagrapi import Client
    from instagrapi.mixins.direct import DirectThread
except ImportError as exc:  # pragma: no cover - runtime safeguard
    raise SystemExit(
        "The 'instagrapi' package is required to run this script. "
        "Install it with 'pip install instagrapi'."
    ) from exc


LOGGER = logging.getLogger(__name__)


@dataclass
class AutoReplyRule:
    """Defines how to respond to a message that contains certain keywords."""

    keywords: List[str]
    response: str
    case_sensitive: bool = False

    def matches(self, text: str) -> bool:
        haystack = text if self.case_sensitive else text.lower()
        needles = self.keywords if self.case_sensitive else [k.lower() for k in self.keywords]
        return any(keyword in haystack for keyword in needles)


@dataclass
class AutoReplyConfig:
    """Container for the auto-responder configuration."""

    rules: List[AutoReplyRule] = field(default_factory=list)
    default_response: Optional[str] = None
    poll_interval: float = 30.0

    @classmethod
    def from_json(cls, path: Path) -> "AutoReplyConfig":
        data = json.loads(path.read_text())
        rules = [AutoReplyRule(**raw_rule) for raw_rule in data.get("rules", data)]
        return cls(
            rules=rules,
            default_response=data.get("default_response"),
            poll_interval=float(data.get("poll_interval", 30.0)),
        )


class InstagramAutoResponder:
    """Automates responding to Instagram DMs based on keyword matching."""

    def __init__(self, client: Client, config: AutoReplyConfig) -> None:
        self.client = client
        self.config = config
        self._responded_to: set[str] = set()

    def run(self) -> None:
        LOGGER.info("Starting DM auto-responder loop (interval=%ss)", self.config.poll_interval)
        try:
            while True:
                self.process_threads()
                time.sleep(self.config.poll_interval)
        except KeyboardInterrupt:
            LOGGER.info("Stopping auto-responder")

    def process_threads(self) -> None:
        threads: Iterable[DirectThread] = self.client.direct_threads()
        for thread in threads:
            if not thread.messages:
                continue
            latest_message = thread.messages[0]
            if latest_message.item_id in self._responded_to:
                continue
            if latest_message.user_id == self.client.user_id:
                continue
            if not latest_message.text:
                continue

            response = self._choose_response(latest_message.text)
            if response:
                LOGGER.info(
                    "Replying to '%s' from user %s with '%s'",
                    latest_message.text,
                    latest_message.user_id,
                    response,
                )
                self.client.direct_send(response, thread_id=thread.id)
                self._responded_to.add(latest_message.item_id)

    def _choose_response(self, text: str) -> Optional[str]:
        for rule in self.config.rules:
            if rule.matches(text):
                return rule.response
        return self.config.default_response


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Instagram DM auto responder")
    parser.add_argument("--username", required=True, help="Instagram username")
    parser.add_argument("--password", help="Instagram password (optional)")
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to JSON config describing auto-response rules",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=None,
        help="Override the poll interval defined in the config file",
    )
    return parser


def load_config(path: Optional[Path], poll_interval_override: Optional[float]) -> AutoReplyConfig:
    if path and path.exists():
        config = AutoReplyConfig.from_json(path)
    else:
        config = AutoReplyConfig(
            rules=[
                AutoReplyRule(keywords=["hello", "hi"], response="Hey there! How can I help you today?"),
                AutoReplyRule(keywords=["pricing", "cost"], response="Our pricing info is available at https://example.com/pricing"),
                AutoReplyRule(keywords=["thanks", "thank you"], response="You're welcome! Let me know if you need anything else."),
            ],
            default_response="Thanks for your message! We'll get back to you soon.",
        )
    if poll_interval_override is not None:
        config.poll_interval = poll_interval_override
    return config


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    LOGGER.setLevel(logging.INFO)
    LOGGER.addHandler(handler)


def main(argv: Optional[Iterable[str]] = None) -> int:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args(argv)

    password = args.password or os.getenv("INSTAGRAM_PASSWORD")
    if not password:
        try:
            password = input("Instagram password: ")
        except EOFError:  # pragma: no cover - interactive safeguard
            LOGGER.error("A password must be supplied either via --password or INSTAGRAM_PASSWORD")
            return 1

    config = load_config(args.config, args.poll_interval)

    client = Client()
    LOGGER.info("Logging into Instagram as %s", args.username)
    client.login(args.username, password)

    responder = InstagramAutoResponder(client, config)
    responder.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
