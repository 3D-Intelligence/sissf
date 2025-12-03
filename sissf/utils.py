import hashlib
import json
import uuid


class Dictionable:
    def to_dict(self):
        return {
            k: (v.to_dict() if hasattr(v, "to_dict") else v)
            for k, v in self.__dict__.items()
        }


def dict_to_uuid(data) -> uuid.UUID:
    # Convert dict to a stable string representation
    # Sort keys to ensure consistent ordering
    dict_str = json.dumps(data, sort_keys=True)

    # Create a hash of the string
    hash_object = hashlib.md5(dict_str.encode())

    # Convert hash to UUID
    return uuid.UUID(hash_object.hexdigest())
