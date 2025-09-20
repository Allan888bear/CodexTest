"""Unit tests for the ResearchDownload native messaging host."""
from __future__ import annotations

import io
import json
import struct
import unittest
from typing import Any, Iterable, Tuple

from native.researchdownload_host import NativeMessagingHost


def _encode_messages(messages: Iterable[dict[str, Any]]) -> bytes:
    buffer = bytearray()
    for message in messages:
        payload = json.dumps(message).encode("utf-8")
        buffer.extend(struct.pack("<I", len(payload)))
        buffer.extend(payload)
    return bytes(buffer)


def _decode_messages(payload: bytes) -> list[dict[str, Any]]:
    stream = io.BytesIO(payload)
    decoded: list[dict[str, Any]] = []
    while True:
        header = stream.read(4)
        if header == b"":
            break
        length = struct.unpack("<I", header)[0]
        body = stream.read(length)
        decoded.append(json.loads(body.decode("utf-8")))
    return decoded


def _run_host(
    messages: Iterable[dict[str, Any]],
    *,
    manifest: dict[str, Any] | None = None,
) -> Tuple[int, list[dict[str, Any]]]:
    input_bytes = _encode_messages(messages)
    input_stream = io.BytesIO(input_bytes)
    output_stream = io.BytesIO()

    host = NativeMessagingHost(
        input_stream,
        output_stream,
        manifest=manifest,
    )
    exit_code = host.run()

    output_stream.seek(0)
    responses = _decode_messages(output_stream.read())
    return exit_code, responses


class NativeMessagingHostTests(unittest.TestCase):
    def test_ping_round_trip(self) -> None:
        exit_code, responses = _run_host([
            {"command": "ping", "requestId": "abc123", "payload": {"value": 42}},
        ])

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(responses), 1)
        self.assertEqual(
            responses[0],
            {
                "type": "pong",
                "payload": {"value": 42},
                "requestId": "abc123",
            },
        )

    def test_unknown_command_returns_error(self) -> None:
        exit_code, responses = _run_host([
            {"command": "does_not_exist", "requestId": 99},
        ])

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(responses), 1)
        self.assertEqual(
            responses[0],
            {
                "type": "error",
                "error": {
                    "code": "unknown_command",
                    "message": "Unsupported command: does_not_exist",
                },
                "requestId": 99,
            },
        )

    def test_get_manifest_requires_manifest(self) -> None:
        manifest = {"name": "com.yourorg.researchdownload"}
        exit_code, responses = _run_host([
            {"command": "get_manifest", "requestId": "m1"},
        ], manifest=manifest)

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            responses[0],
            {
                "type": "manifest",
                "manifest": manifest,
                "requestId": "m1",
            },
        )

    def test_shutdown_command_exits_loop(self) -> None:
        exit_code, responses = _run_host([
            {"command": "shutdown", "requestId": "done"},
        ])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            responses[0],
            {
                "type": "shutdown",
                "status": "ok",
                "requestId": "done",
            },
        )


if __name__ == "__main__":
    unittest.main()
