import numbers
import numpy as np


def convert(
    arr, dtype, normalize=False, prevent_clipping=False, force_copy=False
):
    """
    Converts a numpy array or matrix that represents audio data to another type
    """
    new_t = np.dtype(dtype)
    old_t = arr.dtype

    if new_t == old_t:
        return np.copy(arr) if force_copy else arr

    old_int = isinstance(old_t, numbers.Integral)
    new_int = isinstance(new_t, numbers.Integral)

    if not (new_int or old_int):
        return arr.astype(new_t)

    if not new_int:
        ii = np.iinfo(old_t)
        delta = ii.max - ii.min
        total = ii.max + ii.min

        result = arr.astype(new_t)
        result *= 2 / delta
        result -= total / delta
        return result

    if not old_int:
        ii = np.iinfo(new_t)
        delta = ii.max - ii.min
        total = ii.max + ii.min

        scale = delta / 2

        if normalize or prevent_clipping:
            level = max(np.amax(arr) / ii.max, -np.amin(arr) / ii.min)
            if level and (normalize or level > 1):
                scale /= level

        result = arr * scale
        result += total / 2

        # Arithmetic is uncertain and overs audible.
        np.clip(result, ii.min, ii.max, out=result)
        return result.astype(new_t)

    bits_delta = 8 * (new_t.itemsize - old_t.itemsize)
    if bits_delta >= 0:
        result = arr.astype(new_t)
        if bits_delta:
            result <<= bits_delta
    else:
        result = (arr << -bits_delta).astype(new_t)

    old_i = np.iinfo(old_t)
    new_i = np.iinfo(new_t)

    if (not old_i.min) != (not new_i.min):
        # Change of signedness
        result += -new_i.min or 1 + new_i.max // 2

    return result
