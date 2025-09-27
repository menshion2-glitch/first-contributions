"""Instagram DM auto responder.

This module implements a simple automation for responding to Instagram
Direct Messages (DMs) based on the content of the incoming message.
It uses the `instagrapi` package which provides a high level API for
Instagram.

Usage example:

>>> from instagram_dm_responder import KeywordResponder, DMResponder
>>> rules = [
...     KeywordResponder(keywords={"hello", "hi"}, response="Hey there!"),
...     KeywordResponder(keywords={"price", "cost"}, response="Our pricing starts at ..."),
... ]
>>> responder = DMResponder("your_username", "your_password", rules)
>>> responder.login()
>>> responder.run()

The script will poll the recent DM threads and send a response whenever
one of the configured keyword rules matches the most recent message from
a contact.

Note:
    This automation assumes that you own the Instagram account and that
    you comply with Instagram's terms of service. Excessive automation
    or spam-like behaviour can get your account restricted. Use at your
    own risk.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Iterable, Optional, Set

try:
    from instagrapi import Client
    from instagrapi.exceptions import LoginRequired
except ImportError as exc:  # pragma: no cover - dependency is optional at runtime
    raise SystemExit(
        "The instagrapi package is required for this script."
        " Install it with 'pip install instagrapi'."
    ) from exc


_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class KeywordResponder:
    """Represents an auto-reply rule based on matching keywords."""

    keywords: Set[str]
    response: str

    def matches(self, message_text: str) -> bool:
        """Return ``True`` if the message contains any keyword."""

        message_text_lower = message_text.lower()
        for keyword in self.keywords:
            if keyword.lower() in message_text_lower:
                return True
        return False


class DMResponder:
    """Listens to incoming Instagram direct messages and replies to them."""

    def __init__(
        self,
        username: str,
        password: str,
        responders: Iterable[KeywordResponder],
        *,
        poll_interval: float = 30.0,
        default_response: Optional[str] = None,
        session_path: Optional[str] = None,
    ) -> None:
        """Configure the responder.

        Args:
            username: Instagram username.
            password: Instagram password.
            responders: Collection of keyword based responders.
            poll_interval: How often (in seconds) to check for new DMs.
            default_response: Optional fallback reply when no rule matches.
            session_path: Optional path to store/load the client session.
        """

        self.username = username
        self.password = password
        self.responders = list(responders)
        self.poll_interval = poll_interval
        self.default_response = default_response
        self.session_path = session_path
        self.client = Client()
        self._replied_message_ids: Set[str] = set()

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

    def login(self) -> None:
        """Login to Instagram using the credentials provided."""

        if self.session_path and os.path.exists(self.session_path):
            _LOGGER.info("Loading Instagram session from %s", self.session_path)
            self.client.load_settings(self.session_path)

        try:
            self.client.login(self.username, self.password)
        except LoginRequired:
            _LOGGER.info("Session invalid, performing fresh login")
            self.client.login(self.username, self.password)

        if self.session_path:
            _LOGGER.info("Saving Instagram session to %s", self.session_path)
            self.client.dump_settings(self.session_path)

        _LOGGER.info("Logged in as @%s", self.username)

    def _find_response(self, message_text: str) -> Optional[str]:
        """Find the first matching response for a message."""

        for responder in self.responders:
            if responder.matches(message_text):
                return responder.response
        return self.default_response

    def _should_reply(self, message) -> bool:
        """Determine whether we should respond to the provided message."""

        if not message.text:
            return False

        if message.id in self._replied_message_ids:
            return False

        if message.user_id == self.client.user_id:
            return False

        return True

    def run(self) -> None:
        """Continuously poll the inbox and respond to new messages."""

        _LOGGER.info("Starting DM responder loop with %.1f second interval", self.poll_interval)
        while True:
            threads = self.client.direct_threads(amount=20)
            for thread in threads:
                if not thread.messages:
                    continue

                latest_message = thread.messages[0]
                if not self._should_reply(latest_message):
                    continue

                response = self._find_response(latest_message.text)
                if response is None:
                    continue

                _LOGGER.info(
                    "Responding to @%s in thread %s with message: %s",
                    latest_message.user_id,
                    thread.id,
                    response,
                )
                self.client.direct_answer(thread.id, response)
                self._replied_message_ids.add(latest_message.id)

            time.sleep(self.poll_interval)


def build_default_responder() -> DMResponder:
    """Factory helper that builds a responder from environment variables.

    Expected environment variables::

        IG_USERNAME -- Instagram username.
        IG_PASSWORD -- Instagram password.

    Optional environment variables::

        IG_SESSION_PATH -- Where to store the session settings JSON.
        IG_POLL_INTERVAL -- Poll interval (seconds).
        IG_DEFAULT_RESPONSE -- Fallback message when no rule matches.
    """

    username = os.environ["IG_USERNAME"]
    password = os.environ["IG_PASSWORD"]

    poll_interval = float(os.environ.get("IG_POLL_INTERVAL", "30"))
    default_response = os.environ.get("IG_DEFAULT_RESPONSE")
    session_path = os.environ.get("IG_SESSION_PATH")

    responders = [
        KeywordResponder({"hello", "hi", "hey"}, "Hey there! How can I help you today?"),
        KeywordResponder({"hours", "open", "time"}, "We're open Monday to Friday from 9am to 6pm."),
        KeywordResponder({"price", "cost", "pricing"}, "Check out our pricing at https://example.com/pricing"),
        KeywordResponder({"thanks", "thank you"}, "You're welcome!"),
    ]

    return DMResponder(
        username=username,
        password=password,
        responders=responders,
        poll_interval=poll_interval,
        default_response=default_response,
        session_path=session_path,
    )


if __name__ == "__main__":
    responder = build_default_responder()
    responder.login()
    responder.run()
