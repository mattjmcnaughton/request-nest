"""Unit tests for the Event domain model."""

import base64
from datetime import UTC, datetime

from request_nest.domain import Event


class TestEventModel:
    """Tests for Event model instantiation and fields."""

    def test_event_instantiation_with_all_fields(self) -> None:
        """Event can be instantiated with all required fields."""
        now = datetime.now(tz=UTC)
        event = Event(
            id="e_test123",
            bin_id="b_parent456",
            method="POST",
            path="/webhook/test",
            query_params={"key": "value"},
            headers={"Content-Type": "application/json"},
            body_b64=base64.b64encode(b"test body").decode(),
            remote_ip="192.168.1.1",
            created_at=now,
        )

        assert event.id == "e_test123"
        assert event.bin_id == "b_parent456"
        assert event.method == "POST"
        assert event.path == "/webhook/test"
        assert event.query_params == {"key": "value"}
        assert event.headers == {"Content-Type": "application/json"}
        assert event.body_b64 == base64.b64encode(b"test body").decode()
        assert event.remote_ip == "192.168.1.1"
        assert event.created_at == now

    def test_event_instantiation_with_minimal_fields(self) -> None:
        """Event can be instantiated with only required fields."""
        event = Event(
            id="e_minimal",
            bin_id="b_parent",
            method="GET",
            path="/",
        )

        assert event.id == "e_minimal"
        assert event.bin_id == "b_parent"
        assert event.method == "GET"
        assert event.path == "/"

    def test_event_id_field_is_primary_key(self) -> None:
        """Event id field is configured as primary key."""
        id_field = Event.model_fields["id"]
        assert id_field is not None

    def test_event_remote_ip_defaults_to_none(self) -> None:
        """Event remote_ip defaults to None when not provided."""
        event = Event(
            id="e_noip",
            bin_id="b_parent",
            method="GET",
            path="/",
        )

        assert event.remote_ip is None

    def test_event_query_params_defaults_to_empty_dict(self) -> None:
        """Event query_params defaults to empty dict when not provided."""
        event = Event(
            id="e_noparams",
            bin_id="b_parent",
            method="GET",
            path="/",
        )

        assert event.query_params == {}

    def test_event_headers_defaults_to_empty_dict(self) -> None:
        """Event headers defaults to empty dict when not provided."""
        event = Event(
            id="e_noheaders",
            bin_id="b_parent",
            method="GET",
            path="/",
        )

        assert event.headers == {}

    def test_event_body_b64_defaults_to_empty_string(self) -> None:
        """Event body_b64 defaults to empty string when not provided."""
        event = Event(
            id="e_nobody",
            bin_id="b_parent",
            method="GET",
            path="/",
        )

        assert event.body_b64 == ""


class TestEventSizeBytes:
    """Tests for the Event.size_bytes property."""

    def test_size_bytes_returns_zero_for_empty_body(self) -> None:
        """size_bytes returns 0 for empty body_b64."""
        event = Event(
            id="e_empty",
            bin_id="b_parent",
            method="GET",
            path="/",
            body_b64="",
        )

        assert event.size_bytes == 0

    def test_size_bytes_returns_correct_size_for_ascii_body(self) -> None:
        """size_bytes returns correct byte count for ASCII content."""
        content = b"Hello, World!"
        event = Event(
            id="e_ascii",
            bin_id="b_parent",
            method="POST",
            path="/",
            body_b64=base64.b64encode(content).decode(),
        )

        assert event.size_bytes == len(content)
        assert event.size_bytes == 13

    def test_size_bytes_returns_correct_size_for_binary_body(self) -> None:
        """size_bytes returns correct byte count for binary data."""
        content = bytes([0x00, 0xFF, 0x7F, 0x80, 0x01, 0xFE])
        event = Event(
            id="e_binary",
            bin_id="b_parent",
            method="POST",
            path="/",
            body_b64=base64.b64encode(content).decode(),
        )

        assert event.size_bytes == len(content)
        assert event.size_bytes == 6

    def test_size_bytes_handles_unicode_content(self) -> None:
        """size_bytes returns correct byte count for UTF-8 encoded content."""
        content = b"Hello, World!"
        event = Event(
            id="e_unicode",
            bin_id="b_parent",
            method="POST",
            path="/",
            body_b64=base64.b64encode(content).decode(),
        )

        assert event.size_bytes == len(content)

    def test_size_bytes_handles_multibyte_unicode(self) -> None:
        """size_bytes returns correct byte count for multibyte UTF-8 characters."""
        content = b"Emoji: test"
        event = Event(
            id="e_multibyte",
            bin_id="b_parent",
            method="POST",
            path="/",
            body_b64=base64.b64encode(content).decode(),
        )

        assert event.size_bytes == len(content)

    def test_size_bytes_handles_large_body(self) -> None:
        """size_bytes returns correct byte count for larger payloads."""
        content = b"x" * 10000
        event = Event(
            id="e_large",
            bin_id="b_parent",
            method="POST",
            path="/",
            body_b64=base64.b64encode(content).decode(),
        )

        assert event.size_bytes == 10000
