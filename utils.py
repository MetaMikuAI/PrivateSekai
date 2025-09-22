import json
from pathlib import Path
from typing import Dict, Any, Union


def dict_to_pretty_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)

def load_json(file_path: Union[str, Path]) -> Dict[str, Any]: # TODO: 可能应换成实际的数据结构与数据库
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)