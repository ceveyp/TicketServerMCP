from typing import List, Dict


def _serialize_item(data: Dict):
    for k, v in data.items():
        data[k] = v.isoformat() if hasattr(v, 'isoformat') else v
    if data.get("_sa_instance_state"):
        del data["_sa_instance_state"]


def _serialize_response(data: List[Dict]) -> List[Dict]:
    for row in data:
        _serialize_item(row)
    return data
