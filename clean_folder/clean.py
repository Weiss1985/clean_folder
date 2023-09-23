import os
import shutil
import re
import zipfile
import rarfile
from transliterate import translit

def normalize(filename):
    # Транслітерація кирилічних символів на латинську
    normalized_name = translit(filename, 'ru', reversed=True)
    # Заміна всіх символів, крім літер латинського алфавіту та цифр, на "_"
    normalized_name = re.sub(r'[^a-zA-Z0-9_.]', '_', normalized_name)
    return normalized_name

def unpack_archive(archive_path, target_folder):
    """Розпаковує архів у вказану теку."""
    try:
        if zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(target_folder)
        elif rarfile.is_rarfile(archive_path):
            with rarfile.RarFile(archive_path, 'r') as rar_ref:
                rar_ref.extractall(target_folder)
    except Exception as e:
        print(f"Failed to unpack archive {archive_path}: {e}")

def sort_files(folder_path):
    # Список відомих розширень для кожної категорії
    known_extensions = {
        'images': ('JPEG', 'PNG', 'JPG', 'SVG'),
        'video': ('AVI', 'MP4', 'MOV', 'MKV'),
        'documents': ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'),
        'audio': ('MP3', 'OGG', 'WAV', 'AMR'),
        'archives': ('ZIP', 'GZ', 'TAR', 'RAR'),
    }

    # Створення папок для кожної категорії
    for category in known_extensions:
        os.makedirs(os.path.join(folder_path, category), exist_ok=True)

    unknown_extensions = set()  # Сет для невідомих розширень

    for root, _, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            extension = filename.split('.')[-1].upper()

            # Перевірка, чи відоме розширення
            moved = False
            for category, extensions in known_extensions.items():
                if extension in extensions:
                    # Перейменування та переміщення файлу до відповідної папки
                    new_name = normalize(filename)
                    new_path = os.path.join(folder_path, category, new_name)
                    shutil.move(file_path, new_path)
                    moved = True
                    break

            if not moved:
                # Файл має невідоме розширення
                unknown_extensions.add(extension)

    # Видалення порожніх папок
    for root, dirs, _ in os.walk(folder_path, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            if not os.listdir(folder_path):
                os.rmdir(folder_path)

    # Розпакування архівів та переміщення файлів з вкладених тек в корінь
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            extension = filename.split('.')[-1].upper()
            
            if extension in known_extensions['archives']:
                # Розпакування архіву
                unpack_archive(file_path, root)
                # Видалення розпакованого архіву
                os.remove(file_path)

    return known_extensions, list(unknown_extensions)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage in folder thet you want clean clean-folder")
    else:
        folder_path = sys.argv[1]
        known_extensions, unknown_extensions = sort_files(folder_path)

        print("Known Extensions:")
        for category, ext_list in known_extensions.items():
            print(f"{category}: {', '.join(ext_list)}")

        print("\nUnknown Extensions:")
        print(', '.join(unknown_extensions))
