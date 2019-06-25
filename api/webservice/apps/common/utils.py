import h5py
import os


def check_hdf5_file(filename, hdf5_paths):
    """
    Checks if a file is a valid HDF5 file and contains a set of paths.

    @param hdf5_paths List of paths to check exist in the HDF5 file
    """
    # Ignore files that do not have a .nxs extension
    if os.path.splitext(filename)[-1] not in ['.nxs']:
        return False

    try:
        # Open the NeXus file
        with h5py.File(filename, 'r') as f:
            for p in hdf5_paths:
                if p not in f:
                    return False
            return True
    except IOError:
        # If we can't open the NeXus file just assume it isn't valid
        # (even in the case where it is valid and just in use elsewhere we
        # couldn't use this file anyway)
        return False


def is_file_a_data_file(filename):
    """
    Checks if a file is valid raw tomography data.

    File is valid if:
        - Filename has .nxs extension
        - File is a valid HDF5 file
    """
    # TODO: can this check be improved? (e.g. checking for specific entries)
    return check_hdf5_file(filename, [])


def is_file_a_process_list(filename):
    """
    Checks if a file is a process list.

    File is valid if:
        - Filename has .nxs extension
        - File is a valid HDF5 file
        - HDF5 path /entry/plugin is present in file
    """
    return check_hdf5_file(filename, ['/entry/plugin'])


def validate_file(filename, pred):
    """
    Checks that a file exists and passes a validation step.
    """
    if not filename:
        return False

    if not os.path.exists(filename):
        return False

    return pred(filename)
