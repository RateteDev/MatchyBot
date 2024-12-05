# /src/matchybot/models/RankDataManager.py

import os
import json
from typing import Dict, Any

class RankDataManager:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_data(self) -> Dict[str, Any]:
        """ランクデータを読み込む"""
        is_file_exist = os.path.exists(self.file_path)

        # ファイルが存在しない場合
        if not is_file_exist:
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        # ファイルを読み込む
        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)

