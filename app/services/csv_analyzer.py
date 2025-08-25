"""
CSV分析サービス
CSVファイルの分析とデータ抽出を行うサービス
"""

from typing import Any, Dict, List

import pandas as pd

from app.models.csv_models import CSVData
from app.services.csv_validator import CSVValidator
from app.services.keyword_scorer import KeywordScoringService


class CSVAnalyzer:
    """CSVファイル分析クラス"""

    def __init__(self):
        """初期化"""
        self.validator = CSVValidator()
        self.scoring_service = KeywordScoringService()

    def analyze_csv(self, file_path: str) -> Dict[str, Any]:
        """
        CSVファイルを分析する

        Args:
            file_path: CSVファイルのパス

        Returns:
            分析結果の辞書
        """
        # CSV検証機能を使用してデータを読み込み・検証
        csv_data = self.validator.load_and_validate_csv(file_path)

        # キーワードスコアリングを実行
        scoring_results = self.scoring_service.score_keywords(csv_data.keywords)

        # 分析結果を返す
        return {
            "total_keywords": len(csv_data.keywords),
            "validated_data": csv_data,
            "scoring_results": scoring_results,
            "analysis_complete": True,
        }

    def extract_keywords(self, data: pd.DataFrame) -> List[str]:
        """
        データからキーワードを抽出する

        Args:
            data: 分析対象のデータフレーム

        Returns:
            抽出されたキーワードのリスト
        """
        pass
