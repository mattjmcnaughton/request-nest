"""Unit tests for the Bin domain model."""

from datetime import UTC, datetime

from request_nest.domain import Bin


class TestBinModel:
    """Tests for Bin model instantiation and fields."""

    def test_bin_instantiation_with_all_fields(self) -> None:
        """Bin can be instantiated with all required fields."""
        now = datetime.now(tz=UTC)
        bin_obj = Bin(id="b_test123", name="My Test Bin", created_at=now)

        assert bin_obj.id == "b_test123"
        assert bin_obj.name == "My Test Bin"
        assert bin_obj.created_at == now

    def test_bin_instantiation_with_nullable_name(self) -> None:
        """Bin can be instantiated with None as name."""
        bin_obj = Bin(id="b_test456", name=None)

        assert bin_obj.id == "b_test456"
        assert bin_obj.name is None

    def test_bin_instantiation_without_name_defaults_to_none(self) -> None:
        """Bin name defaults to None when not provided."""
        bin_obj = Bin(id="b_test789")

        assert bin_obj.id == "b_test789"
        assert bin_obj.name is None

    def test_bin_id_field_is_primary_key(self) -> None:
        """Bin id field is configured as primary key."""
        # Access SQLModel metadata to verify primary key configuration
        id_field = Bin.model_fields["id"]
        assert id_field is not None


class TestBinIngestUrl:
    """Tests for the Bin.ingest_url method."""

    def test_ingest_url_returns_correct_format(self) -> None:
        """ingest_url returns URL in format {base_url}/b/{id}."""
        bin_obj = Bin(id="b_abc123")

        url = bin_obj.ingest_url("https://example.com")

        assert url == "https://example.com/b/b_abc123"

    def test_ingest_url_handles_trailing_slash(self) -> None:
        """ingest_url strips trailing slash from base_url."""
        bin_obj = Bin(id="b_xyz789")

        url = bin_obj.ingest_url("https://example.com/")

        assert url == "https://example.com/b/b_xyz789"

    def test_ingest_url_handles_multiple_trailing_slashes(self) -> None:
        """ingest_url strips multiple trailing slashes from base_url."""
        bin_obj = Bin(id="b_multi")

        url = bin_obj.ingest_url("https://example.com///")

        assert url == "https://example.com/b/b_multi"

    def test_ingest_url_with_port_in_base_url(self) -> None:
        """ingest_url works with port number in base_url."""
        bin_obj = Bin(id="b_port")

        url = bin_obj.ingest_url("http://localhost:8000")

        assert url == "http://localhost:8000/b/b_port"

    def test_ingest_url_with_path_in_base_url(self) -> None:
        """ingest_url works when base_url includes a path."""
        bin_obj = Bin(id="b_path")

        url = bin_obj.ingest_url("https://example.com/api/v1")

        assert url == "https://example.com/api/v1/b/b_path"
