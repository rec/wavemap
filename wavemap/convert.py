import numpy as np


def convert(arr, dtype, force_copy=False):
    """
    Converts a numpy array or matrix that represents audio data to another
    type, scaling and shifting as necessary

    ARGUMENTS
      arr
        a numpy darry representing an audio signal

      dtype
        the numpy dtype to convert
    """
    new_t = np.dtype(dtype)
    old_t = arr.dtype

    if new_t == old_t:
        return np.copy(arr) if force_copy else arr

    old_int = 'int' in str(old_t)
    new_int = 'int' in str(new_t)

    if not (new_int or old_int):
        # Convert between floats
        return arr.astype(new_t)

    if not new_int:  # Convert ints to floats
        ii = np.iinfo(old_t)

        result = arr.astype(new_t)
        result *= 2 / (ii.max - ii.min)
        result -= (ii.max + ii.min) / (ii.max - ii.min)

        return result

    if not old_int:  # Convert floats to ints
        ii = np.iinfo(new_t)

        result = (ii.max - ii.min) / 2 * arr
        result += (ii.max + ii.min) / 2

        # Arithmetic is uncertain and overs audible.
        np.clip(result, ii.min, ii.max, out=result)
        np.round(result, out=result)

        return result.astype(new_t)

    # Convert between two int types
    bits_delta = 8 * (new_t.itemsize - old_t.itemsize)
    if bits_delta < 0:
        result = (arr >> -bits_delta).astype(new_t)
    else:
        result = arr.astype(new_t)
        if bits_delta:
            result <<= bits_delta
            # Remove the DC offset from e.g. mapping 0x80:0x7f to 0x8000:0x7F00
            result += 1 << (bits_delta - 1)

    # Convert signed to unsigned or vice versa
    old_i = np.iinfo(old_t)
    new_i = np.iinfo(new_t)

    if (not old_i.min) != (not new_i.min):
        result += new_i.min or 1 + new_i.max // 2

    return result


def normalize(arr):
    _normalize(arr, True)


def prevent_clipping(arr):
    _normalize(arr, False)


def _normalize(arr, always):
    level = max(np.amax(arr), -np.amin(arr))
    if always or level > 1:
        arr.multiply(arr, level, out=arr)
