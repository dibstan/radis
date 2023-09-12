import re


def sanitize_dirname(dirname):
    """Windows can't handle some file and folder names so we have to sanitize them."""
    dirname = dirname.strip()
    dirname = re.sub(r"(\<|\>|\:|\"|\/|\\|\||\?|\*)", "", dirname)
    dirname = re.sub(r"(\.+)$", "", dirname)
    return dirname


def sanitize_filename(filename):
    return sanitize_dirname(filename)
