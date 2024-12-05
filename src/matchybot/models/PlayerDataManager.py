# /src/matchybot/models/PlayerDataManager.py

import os
import json
import logging

logger = logging.getLogger(__name__)

class PlayerDataManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self) -> None:
        is_exist = os.path.exists(self.file_path)

        # ファイルが存在しない場合
        if not is_exist:
            logger.warning(f"File not found: {self.file_path}")
            # ファイルを作成
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump({"players": []}, file, ensure_ascii=False, indent=4)
            logger.info(f"File created: {self.file_path}")
            # 空データをセット
            self.data = {"players": []}
        
        # 存在する場合
        with open(self.file_path, "r", encoding="utf-8") as file:
            self.data = json.load(file)
            logger.info(f"File loaded: {self.file_path}")

    def save_data(self, data: dict) -> None:
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            logger.info(f"File saved: {self.file_path}")

    def get_players(self) -> list:
        """プレイヤーリストを取得する"""
        return self.data.get("players", [])

    def get_player_by_id(self, player_id: str) -> dict | None:
        """
        指定されたIDのプレイヤー情報を取得する
        
        Args:
            player_id (str): プレイヤーのDiscord ID
            
        Returns:
            dict | None: プレイヤー情報。見つからない場合はNone
        """
        players = self.get_players()
        return next((player for player in players if player["id"] == player_id), None)

    def add_player(self, player_info: dict) -> None:
        """新しいプレイヤーを追加する"""
        self.data["players"].append(player_info)
        self.save_data(self.data)
