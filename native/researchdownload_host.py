"""Entry point for the ResearchDownload native messaging host.

The host follows the Chrome native messaging protocol. Messages are
received from ``stdin`` as a four-byte little-endian length prefix
followed by a UTF-8 encoded JSON payload. Responses are written to
``stdout`` using the same framing.

The implementation is intentionally simple but fully functional. It
supports a handful of diagnostic commands that make it easy to validate
the browser integration without needing the final business logic in
place. The commands that are currently recognised are:

``ping``
    Responds with ``{"type": "pong"}`` and echoes any ``payload`` field.
``echo``
    Returns the supplied ``payload`` verbatim.
``get_version``
    Provides the host version as ``{"type": "version", "version": ...}``.
``get_manifest``
    Emits the manifest JSON that the host was launched with (when
    ``--manifest`` is provided).
``shutdown``
    Replies with ``{"type": "shutdown", "status": "ok"}`` and stops the
    host loop.

Additional commands can be layered on top of :class:`NativeMessagingHost`
by extending :meth:`NativeMessagingHost._handle_message`.
"""
from __future__ import annotations

import argparse
import json
import logging
import struct
import sys
from pathlib import Path
from typing import Any, BinaryIO, Tuple

HOST_VERSION = "0.1.0"


RequestId = str | int | None


class NativeMessagingProtocolError(RuntimeError):
    """Raised when the input stream does not follow the messaging protocol."""


class NativeMessagingHost:
    """Minimal native messaging host implementation.

    Parameters
    ----------
    input_stream:
        Binary stream to read messages from (typically ``sys.stdin.buffer``).
    output_stream:
        Binary stream to write messages to (typically ``sys.stdout.buffer``).
    manifest:
        Optional manifest data loaded from JSON. Required to service the
        ``get_manifest`` command.
    max_message_bytes:
        Upper bound for any single message body. Messages that exceed the
        limit raise :class:`NativeMessagingProtocolError`.
    """

    def __init__(
        self,
        input_stream: BinaryIO,
        output_stream: BinaryIO,
        manifest: dict[str, Any] | None = None,
        *,
        max_message_bytes: int = 2_097_152,
    ) -> None:
        self._input = input_stream
        self._output = output_stream
        self._manifest = manifest
        self._max_message_bytes = max_message_bytes

    def run(self) -> int:
        """Process messages until EOF or a ``shutdown`` command is received."""

        while True:
            try:
                raw_payload = self._read_message_bytes()
            except NativeMessagingProtocolError as exc:
                logging.error("Protocol error: %s", exc)
                self._send_error("protocol_error", str(exc))
                return 1

            if raw_payload is None:
                logging.debug("EOF reached; shutting down host loop")
                return 0

            try:
                message = json.loads(raw_payload.decode("utf-8"))
            except json.JSONDecodeError as exc:
                logging.warning("Received invalid JSON payload: %s", exc)
                self._send_error(
                    "invalid_json",
                    f"Failed to decode JSON payload: {exc}",
                )
                continue

            request_id = message.get("requestId")
            if not isinstance(request_id, (str, int)):
                request_id = None

            try:
                response, should_exit = self._handle_message(message, request_id)
            except Exception as exc:  # pragma: no cover - defensive guard
                logging.exception("Unhandled error while processing message")
                self._send_error(
                    "internal_error",
                    "Unhandled error while processing message.",
                    request_id=request_id,
                )
                continue

            if response is not None:
                self._send_message(response, request_id=request_id)

            if should_exit:
                logging.info("Shutdown command processed; exiting host loop")
                return 0

    def _read_message_bytes(self) -> bytes | None:
        """Read a single message from ``stdin``.

        Returns ``None`` when EOF is reached before the length prefix. Raises
        :class:`NativeMessagingProtocolError` if the stream terminates before
        the declared message length is satisfied.
        """

        raw_length = self._input.read(4)
        if raw_length == b"":
            return None
        if len(raw_length) < 4:
            raise NativeMessagingProtocolError(
                "Unexpected EOF while reading message length prefix"
            )

        message_length = struct.unpack("<I", raw_length)[0]
        if message_length > self._max_message_bytes:
            raise NativeMessagingProtocolError(
                f"Message length {message_length} exceeds maximum of "
                f"{self._max_message_bytes} bytes"
            )

        payload = self._read_exact(message_length)
        return payload

    def _read_exact(self, size: int) -> bytes:
        """Read exactly ``size`` bytes from the input stream."""

        remaining = size
        chunks = bytearray()
        while remaining > 0:
            chunk = self._input.read(remaining)
            if chunk == b"":
                raise NativeMessagingProtocolError(
                    "Unexpected EOF while reading message body"
                )
            chunks.extend(chunk)
            remaining -= len(chunk)
        return bytes(chunks)

    def _handle_message(
        self, message: Any, request_id: RequestId
    ) -> Tuple[dict[str, Any] | None, bool]:
        """Implement the ResearchDownload host command set."""

        if not isinstance(message, dict):
            self._send_error(
                "invalid_payload",
                "Expected JSON object payload.",
                request_id=request_id,
            )
            return None, False

        command = message.get("command")
        if not isinstance(command, str):
            self._send_error(
                "missing_command",
                "Message must include a string 'command' field.",
                request_id=request_id,
            )
            return None, False

        logging.debug("Processing command '%s'", command)

        if command == "ping":
            return {
                "type": "pong",
                "payload": message.get("payload"),
            }, False

        if command == "echo":
            return {
                "type": "echo",
                "payload": message.get("payload"),
            }, False

        if command == "get_version":
            return {"type": "version", "version": HOST_VERSION}, False

        if command == "get_manifest":
            if self._manifest is None:
                self._send_error(
                    "manifest_unavailable",
                    "Host was started without a manifest path.",
                    request_id=request_id,
                )
                return None, False
            return {"type": "manifest", "manifest": self._manifest}, False

        if command == "shutdown":
            return {"type": "shutdown", "status": "ok"}, True

        self._send_error(
            "unknown_command",
            f"Unsupported command: {command}",
            request_id=request_id,
        )
        return None, False

    def _send_message(self, payload: dict[str, Any], request_id: RequestId) -> None:
        """Encode *payload* and write it to the output stream."""

        message = dict(payload)
        if request_id is not None:
            message.setdefault("requestId", request_id)

        encoded = json.dumps(message, ensure_ascii=False).encode("utf-8")
        header = struct.pack("<I", len(encoded))
        self._output.write(header)
        self._output.write(encoded)
        self._output.flush()

    def _send_error(
        self,
        code: str,
        message: str,
        *,
        request_id: RequestId = None,
    ) -> None:
        """Send a structured error response."""

        error_body = {
            "type": "error",
            "error": {
                "code": code,
                "message": message,
            },
        }
        self._send_message(error_body, request_id=request_id)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments for the host launcher."""

    parser = argparse.ArgumentParser(
        description="Run the ResearchDownload native messaging host",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help=(
            "Optional path to the native messaging manifest. Required when "
            "using the 'get_manifest' command."
        ),
    )
    parser.add_argument(
        "--log-level",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        default="WARNING",
        help="Adjust the logging verbosity emitted to stderr.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=HOST_VERSION,
    )
    return parser.parse_args(argv)


def load_manifest(manifest_path: Path | None) -> dict[str, Any] | None:
    """Load manifest JSON from ``manifest_path`` when provided."""

    if manifest_path is None:
        return None
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest_data, dict):
        raise ValueError("Manifest JSON must be an object")
    return manifest_data


def configure_logging(level: str) -> None:
    numeric_level = getattr(logging, level.upper(), logging.WARNING)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s %(levelname)s %(message)s",
        stream=sys.stderr,
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging(args.log_level)

    manifest: dict[str, Any] | None = None
    try:
        manifest = load_manifest(args.manifest)
    except FileNotFoundError as exc:
        logging.error("%s", exc)
        return 2
    except ValueError as exc:
        logging.error("%s", exc)
        return 3

    host = NativeMessagingHost(
        sys.stdin.buffer,
        sys.stdout.buffer,
        manifest=manifest,
    )

    try:
        return host.run()
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received; shutting down host")
        return 0


if __name__ == "__main__":
    sys.exit(main())
