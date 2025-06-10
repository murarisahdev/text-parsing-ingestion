def guess_file_extension(content_type: str) -> str:
    if "pdf" in content_type:
        return ".pdf"
    elif "word" in content_type:
        return ".docx"
    elif "sheet" in content_type:
        return ".xlsx"
    return ""
