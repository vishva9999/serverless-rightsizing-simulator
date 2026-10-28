from app.core.database import check_db_connection, engine


def test_database_check_structure():
    """Verify check_db_connection returns expected keys and types."""
    result = check_db_connection()
    assert isinstance(result, dict)
    assert "connected" in result
    assert "engine" in result
    assert "is_fallback" in result
    assert "message" in result
    assert isinstance(result["connected"], bool)


def test_engine_has_dialect():
    """Verify engine is instantiated and dialect is detected."""
    assert engine is not None
    assert hasattr(engine, "dialect")
