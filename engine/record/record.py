from typing import List
from engine.record.schema import TableSchema


class Record:
    """
    Encodes and decodes records according to a TableSchema.
    Uses simple length-prefixed binary encoding.
    """

    def __init__(self, schema: TableSchema):
        self.schema = schema

    def encode(self, row: List) -> bytes:
        """
        Encode a row into bytes.
        Raises ValueError if row invalid.
        """
        if not self.schema.validate_row(row):
            raise ValueError("Row does not match schema")
        encoded = bytearray()
        for value in row:
            if value is None:
                encoded.append(0)  # null marker
            else:
                encoded.append(1)  # not null
                if isinstance(value, int):
                    encoded += value.to_bytes(8, "big", signed=True)
                elif isinstance(value, float):
                    import struct

                    encoded += struct.pack(">d", value)
                elif isinstance(value, str):
                    b = value.encode("utf-8")
                    encoded += len(b).to_bytes(2, "big") + b
                else:
                    raise TypeError(f"Unsupported column type: {type(value)}")
        return bytes(encoded)

    def decode(self, data: bytes) -> List:
        """
        Decode bytes back into a row.
        Returns list of values.
        """
        row = []
        idx = 0
        for col in self.schema.columns:
            if idx >= len(data):
                raise ValueError("Data too short to decode")
            null_flag = data[idx]
            idx += 1
            if null_flag == 0:
                row.append(None)
                continue
            if col.dtype == int:
                row.append(int.from_bytes(data[idx : idx + 8], "big", signed=True))
                idx += 8
            elif col.dtype == float:
                import struct

                row.append(struct.unpack(">d", data[idx : idx + 8])[0])
                idx += 8
            elif col.dtype == str:
                length = int.from_bytes(data[idx : idx + 2], "big")
                idx += 2
                row.append(data[idx : idx + length].decode("utf-8"))
                idx += length
            else:
                raise TypeError(f"Unsupported column type: {col.dtype}")
        return row
