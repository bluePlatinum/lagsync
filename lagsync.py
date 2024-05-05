import os
import subprocess


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
    return path[len(rootpath):].count(os.path.sep)


def get_sync(path, depth):
    """
    Return a list of all directories and files to be synced. It will recurse up
    to a depth given by the parameter `depth`.

    :param path: the root of the directory tree
    :type path: str
    :param depth: the recurse depth
    :type depth: int
    :return: list of directories to be synced
    :rtype: list
    """
    dirlist = list()
    filelist = list()
    path = os.path.abspath(path)

    for root, dirs, files in os.walk(path, topdown=True):
        current_depth = get_depth(path, root)
        if current_depth == depth - 1:
            if len(dirs) != 0:
                for dir in dirs:
                    abspath = os.path.join(root, dir)
                    dirlist.append(abspath[len(path)+len(os.path.sep):])
            if len(files) != 0:
                for file in files:
                    abspath = os.path.join(root, file)
                    filelist.append(abspath[len(path)+len(os.path.sep):])

    return dirlist, filelist


def perform_sync(source, destination, dirlist, filelist, options,
                 max_retries=10, *args, **kwargs):
    """
    Perform the syncronization with rsync.

    :param source: the source directory
    :type source: str
    :param destination: the destination to sync to
    :type destination: str
    :param dirlist: The list of all directories to be synched. Needs to be a
        list of paths relative to src.
    :type dirlist: list
    :param filelist: The list of all files to be synched. Needs to be a list of
        paths relative to src.
    :param options: The options to pass to rsync.
    :type options: str
    :param max_retries: the maximum amount of retries before the job fails
    :type max_retries: int
    :return: None
    """
    try:
        dry_run = kwargs['dry_run']
    except KeyError:
        dry_run = False

    sync_objects = dirlist + filelist

    remote, remote_dir = destination.split(":")

    for sync_object in sync_objects:
        src = os.path.join(source, sync_object)
        dst = os.path.join(remote_dir, sync_object)

        if not dry_run:
            retry = 0
            proc = subprocess.run(["rsync", f"{options} {src} {remote}:{dst}"])

            while proc.returncode != 0:
                retry += 1
                proc = subprocess.run(["rsync",
                                       f"{options} {src} {remote}:{dst}"])
                if retry >= max_retries:
                    print(f"Reached maximum amount of retries "
                          f"({max_retries=}). Sync job {sync_object} failed. "
                          f"Aborting.")
                    break

        else:
            print(f"rsync {options} {src} {remote}:{dst}")
