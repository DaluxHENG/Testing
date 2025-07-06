import aiofiles
import os
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings

async def save_uploaded_file(file: UploadFile, filename: str) -> str:
    """Save uploaded file to disk"""
    file_path = Path(settings.upload_dir) / filename
    
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return str(file_path)
    
    except Exception as e:
        raise Exception(f"Error saving file: {str(e)}")

def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    return os.path.getsize(file_path)

def delete_file(file_path: str) -> bool:
    """Delete file from disk"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return False