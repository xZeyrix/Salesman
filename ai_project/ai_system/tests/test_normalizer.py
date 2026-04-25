from ai_system.salesman import TextNormalizer


def test_text_normalizer_clean() -> None:
    normalizer = TextNormalizer()
    result = normalizer.clean("Hi!!! @@ $$ Привет")
    assert result == "Hi!!!   Привет"
