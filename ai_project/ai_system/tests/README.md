# ai_system tests with caching

These tests support record/replay caching to avoid calling expensive AI or API functions.

## Modes
- replay (default): read cached responses and never call the producers
- record: call producers and write new cache files

Set mode using an env var or pytest flag:

```bash
TEST_CACHE_MODE=record pytest
TEST_CACHE_MODE=replay pytest
pytest --cache-mode=record
pytest --cache-mode=replay
```

Cache files are stored in `ai_system/tests/cassettes/`.
