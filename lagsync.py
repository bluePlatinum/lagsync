import os


def get_depth(rootpath, path):
    """
    Get the depth of a given path. Only works if the given path is an
    abspath (os.path.abspath).

    :param rootpath: the root of the directory tree (relative to this the depth
        will be calculated)
    :type rootpath: str
    :param path: the path whose depth should be evaluated
    :type path: str
    :return: the depth of the given path
    :rtype: int
    """
    return path[len(rootpath) + len(os.path.sep):].count(os.path.sep)


def get_dirs(path, depth):
    """
    Return a list of all directories to be synced. It will recurse up to a
    depth given by the parameter `depth`.

    :param path: the root of the directory tree
    :type path: str
    :param depth: the recurse depth
    :type depth: int
    :return: list of directories to be synced
    :rtype: list
    """
    dirlist = list()
    path = os.path.abspath(path)

    for root, dirs, files in os.walk(path, topdown=True):
        current_depth = get_depth(path, root)
        if current_depth == depth - 1:
            dirlist.append(dirs)

    return dirlist

