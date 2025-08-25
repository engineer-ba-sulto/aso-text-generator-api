"""
CSV分析サービス
CSVファイルの分析とデータ抽出を行うサービス
"""

from typing import Any, Dict, List

import pandas as pd

from app.models.csv_models import CSVData
from app.services.csv_validator import CSVValidator
from app.services.keyword_scorer import KeywordScoringService
from app.services.keyword_selector import KeywordSelectionService


class CSVAnalyzer:
    """CSVファイル分析クラス"""

    def __init__(self):
        """初期化"""
        self.validator = CSVValidator()
        self.scoring_service = KeywordScoringService()
        self.selection_service = KeywordSelectionService()

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

        # 主要キーワードを選定
        selection_result = self.selection_service.select_primary_keyword(
            csv_data.keywords
        )

        # 統計情報を計算
        stats = self._calculate_statistics(csv_data)

        # CSVDataを辞書に変換
        validated_data_dict = {
            "total_keywords": len(csv_data.keywords),
            "keywords": [
                {
                    "keyword": k.keyword,
                    "ranking": k.ranking,
                    "popularity": k.popularity,
                    "difficulty": k.difficulty,
                }
                for k in csv_data.keywords
            ],
        }

        # 分析結果を返す
        return {
            "total_keywords": len(csv_data.keywords),
            "validated_data": validated_data_dict,
            "scoring_results": [result.model_dump() for result in scoring_results],
            "selection_result": (
                {
                    "primary_keyword": selection_result["primary_keyword"],
                    "primary_score": selection_result["primary_score"],
                    "primary_ranking": selection_result["primary_ranking"],
                    "primary_popularity": selection_result["primary_popularity"],
                    "primary_difficulty": selection_result["primary_difficulty"],
                    "component_scores": selection_result["component_scores"],
                    "candidates": selection_result["candidates"],
                    "total_keywords_analyzed": selection_result[
                        "total_keywords_analyzed"
                    ],
                }
                if selection_result
                else None
            ),
            "statistics": stats,
            "analysis_complete": True,
        }

    async def analyze_csv_upload(self, upload_file) -> Dict[str, Any]:
        """
        UploadFileからCSVファイルを分析する

        Args:
            upload_file: FastAPIのUploadFile

        Returns:
            分析結果の辞書
        """
        import os
        import tempfile

        # 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            content = await upload_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # CSV分析を実行
            return self.analyze_csv(temp_file_path)
        finally:
            # 一時ファイルを削除
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def _calculate_statistics(self, csv_data: CSVData) -> Dict[str, Any]:
        """統計情報を計算"""
        rankings = [k.ranking for k in csv_data.keywords]
        popularities = [k.popularity for k in csv_data.keywords]
        difficulties = [k.difficulty for k in csv_data.keywords]

        return {
            "ranking_stats": {
                "min": min(rankings),
                "max": max(rankings),
                "avg": sum(rankings) / len(rankings),
                "median": sorted(rankings)[len(rankings) // 2],
            },
            "popularity_stats": {
                "min": min(popularities),
                "max": max(popularities),
                "avg": sum(popularities) / len(popularities),
                "median": sorted(popularities)[len(popularities) // 2],
            },
            "difficulty_stats": {
                "min": min(difficulties),
                "max": max(difficulties),
                "avg": sum(difficulties) / len(difficulties),
                "median": sorted(difficulties)[len(difficulties) // 2],
            },
            "top_keywords": self._get_top_keywords(csv_data, 10),
            "low_difficulty_high_popularity": self._get_low_difficulty_high_popularity(
                csv_data, 5
            ),
        }

    def _get_top_keywords(self, csv_data: CSVData, count: int) -> List[Dict[str, Any]]:
        """上位キーワードを取得"""
        # ランキングでソート
        sorted_keywords = sorted(csv_data.keywords, key=lambda x: x.ranking)
        return [
            {
                "keyword": k.keyword,
                "ranking": k.ranking,
                "popularity": k.popularity,
                "difficulty": k.difficulty,
            }
            for k in sorted_keywords[:count]
        ]

    def _get_low_difficulty_high_popularity(
        self, csv_data: CSVData, count: int
    ) -> List[Dict[str, Any]]:
        """低難易度・高人気度のキーワードを取得"""
        # 難易度が低く、人気度が高いキーワードをソート
        sorted_keywords = sorted(
            csv_data.keywords, key=lambda x: (x.difficulty, -x.popularity)
        )
        return [
            {
                "keyword": k.keyword,
                "ranking": k.ranking,
                "popularity": k.popularity,
                "difficulty": k.difficulty,
            }
            for k in sorted_keywords[:count]
        ]

    def extract_keywords(self, data: pd.DataFrame) -> List[str]:
        """
        データからキーワードを抽出する

        Args:
            data: 分析対象のデータフレーム

        Returns:
            抽出されたキーワードのリスト
        """
        pass
