async def convert(text: str) -> str:
    if text:
        return text
    raise ValueError("Text cannot be empty if content_type is 'text'.")