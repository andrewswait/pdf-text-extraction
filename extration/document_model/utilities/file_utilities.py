import os
import glob
import errno


def get_files_from_path(path: str, extension=None):
    cwd = os.getcwd()
    if path == '':
        path = cwd

    # Relative path
    if cwd not in path:
        path = os.path.join(cwd, path)
    # It is a single file
    if os.path.isfile(path):
        files = [path]
    else:  # It is a folder
        files = [file for file in glob.glob(path + "/*.*")]
    if extension:
        return [f for f in files if f.endswith(extension)]
    return files


def create_file_path(filename: str):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def create_path(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def get_filename_from_path(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def write_text_file(filename: str, content: str):
    create_file_path(filename)
    with open(filename, 'w+', encoding='utf-8') as f:
        f.write(content)
