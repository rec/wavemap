"""Better struct"""
from argparse import Namespace
import struct

INT16 = 'H'
INT32 = 'I'

INT = INT16, INT32


class Structure:
    def __init__(self, **formats):
        self.formats = formats
        self.struct = struct.Struct('<' + ''.join(formats.values()))
        self.size = self.struct.size

    def pack(self, **kwargs):
        return self.struct.pack(*self._to_arg(kwargs))

    def pack_into(self, buffer, offset=0, **kwargs):
        return self.struct.pack_into(buffer, offset, *self._to_arg(kwargs))

    def unpack_from(self, buffer, offset=0):
        parts = self.struct.unpack_from(buffer, offset)
        return Namespace(**dict(zip(self.formats, parts)))

    def __add__(self, fmt):
        return __class__(**dict(self.formats, **fmt.formats))

    def _to_arg(self, kw):
        errors, args = [], []
        for name, fmt in self.formats.items():
            try:
                v = kw[name]
            except KeyError:
                errors.append(f'Unknown param {name}')
            else:
                if fmt in INT and not isinstance(v, int):
                    errors.append(f'Integer {name} had value {v!r}')
                elif fmt.endswith('s') and not isinstance(v, bytes):
                    errors.append(f'Bytes {name} had value {v!r}')
                else:
                    args.append(v)

        # We accept the unknown
        unknown = False and set(kw).difference(self.names)
        if unknown:
            s = '' if len(unknown) == 1 else 's'
            unknown = ', '.join(sorted(unknown))
            errors.append(f'Unknown argument{s}: {unknown}')
            raise ValueError(errors[-1])

        msg = '. '.join(errors)
        if msg:
            raise ValueError(msg)

        assert len(args) == len(
            self.formats
        ), f'{len(args)} == {len(self.formats)}'
        return args
