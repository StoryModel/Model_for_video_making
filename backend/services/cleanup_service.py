import os
import shutil


def delete_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        return True

    return False


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        return True

    return False


def clean_temp_files(project_folder):
    temp_items = [
        "chunks"
    ]

    deleted = []

    for item in temp_items:
        path = os.path.join(project_folder, item)

        if os.path.isdir(path):
            shutil.rmtree(path)
            deleted.append(path)

        elif os.path.isfile(path):
            os.remove(path)
            deleted.append(path)

    return deleted