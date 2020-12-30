from . import constants
from . import raw
from .layout import PCM, NON_PCM, FMT_PCM, FMT_NON_PCM
import numpy as np

CHUNK_HEADER = 8
DEFAULT_SAMPLE_RATE = 44100


class WriteMap(raw.RawMap):
    """"Memory-map a new wave file"""

    def __new__(
        cls, filename, dtype, shape, sample_rate, roffset=0, warn=raw.warn
    ):
        """
        ARGUMENTS
          roffset:
            How many bytes in the file after the WAV data chunk
        """
        dtype = np.dtype(dtype)

        if issubclass(dtype.type, np.integer):
            wFormatTag = constants.WAVE_FORMAT_PCM
            layout = PCM
            fmt_layout = FMT_PCM
        else:
            wFormatTag = constants.WAVE_FORMAT_IEEE_FLOAT
            layout = NON_PCM
            fmt_layout = FMT_NON_PCM

        channel_count = 1 if len(shape) == 1 else min(shape)
        frame_count = max(shape)

        sample_bytes = dtype.itemsize
        frame_bytes = sample_bytes * channel_count
        total_frame_bytes = frame_bytes * frame_count
        pad = total_frame_bytes % 2

        self = raw.RawMap.__new__(
            cls,
            filename=filename,
            dtype=dtype,
            mode='w+',
            shape=shape,
            offset=layout.size,
            roffset=roffset + pad,
            warn=warn,
        )

        self.file_size = layout.size + total_frame_bytes + pad
        self.sample_rate = sample_rate

        layout.pack_into(
            self._mmap,
            ckIDRiff=b'RIFF',
            cksizeRiff=self.file_size - CHUNK_HEADER,
            WAVEID=b'WAVE',
            ckIDFmt=b'fmt ',
            cksizeFmt=fmt_layout.size - CHUNK_HEADER,
            wFormatTag=wFormatTag,
            nChannels=channel_count,
            nSamplesPerSec=sample_rate,
            nAvgBytesPerSec=sample_rate * frame_bytes,
            nBlockAlign=frame_bytes,
            wBitsPerSample=sample_bytes * 8,
            cbSize=0,  # Non PCM
            ckIDFact=b'fact',
            cksizeFact=4,
            dwSampleLength=channel_count * frame_count,
            ckIDData=b'data',
            cksizeData=total_frame_bytes,
        )

        return self

    @classmethod
    def new_like(
        cls, filename, arr, sample_rate=None, roffset=None, warn=raw.warn
    ):
        if sample_rate is None:
            sample_rate = getattr(arr, 'sample_rate', DEFAULT_SAMPLE_RATE)

        if roffset is None:
            roffset = getattr(arr, 'roffset', 0)

        from pathlib import Path

        assert not Path(filename).exists(), str(filename)
        wm = cls(filename, arr.dtype, arr.shape, sample_rate, roffset, warn)
        np.copyto(dst=wm, src=arr, casting='no')
        return wm
