from typing import List, Dict


def _serialize_item(data: Dict) -> Dict:
    for k, v in data.items():
        data[k] = v.isoformat() if hasattr(v, 'isoformat') else v
    if data.get("_sa_instance_state"):
        del data["_sa_instance_state"]
    return data


def _serialize_response(data: List[Dict]) -> List[Dict]:
    response_data = []
    for row in data:
        response_data.append(_serialize_item(row))
    return response_data
