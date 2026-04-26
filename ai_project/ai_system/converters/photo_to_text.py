async def convert(file_id: str, text: str | None = None) -> str:
    if file_id:
        return f"Описание фото: {None}, Запрос пользователя: {text}"
    raise ValueError("File_id cannot be empty if content_type is 'photo'")