def convert(file_id: str, text: str = None) -> str:
    if file_id:
        return "текст документа"
    raise ValueError("File_id cannot be empty if content_type is 'document'")
