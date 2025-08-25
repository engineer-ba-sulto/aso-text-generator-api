"""
キーワードフィールド生成サービス
100文字以内のキーワードフィールドを生成するサービス
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models.csv_models import KeywordData
from app.services.keyword_selector import KeywordSelectionService
from app.utils.exceptions import TextGenerationError

logger = logging.getLogger(__name__)


class KeywordFieldGenerator:
    """キーワードフィールド生成クラス"""

    def __init__(self):
        self.max_length = 100  # 最大文字数
        self.separator = ", "  # キーワード区切り文字
        self.max_keywords = 10  # 最大キーワード数

    def generate_keyword_field(
        self,
        primary_keyword: str,
        candidate_keywords: List[Dict[str, Any]],
        language: str = "ja",
    ) -> str:
        """
        キーワードフィールドを生成

        Args:
            primary_keyword: 主要キーワード
            candidate_keywords: 候補キーワードのリスト
            language: 言語（"ja" or "en"）

        Returns:
            生成されたキーワードフィールド
        """
        try:
            # キーワードリストを準備
            keywords = self._prepare_keywords(primary_keyword, candidate_keywords)

            # 重複除去と正規化
            unique_keywords = self._remove_duplicates(keywords)

            # スコア順でソート
            sorted_keywords = self._sort_by_score(unique_keywords, candidate_keywords)

            # 100文字以内に収める
            optimized_keywords = self._optimize_length(sorted_keywords)

            # キーワードフィールドを構築
            keyword_field = self._build_keyword_field(optimized_keywords, language)

            # 最終検証
            self._validate_keyword_field(keyword_field)

            logger.info(f"キーワードフィールドを生成しました: {keyword_field}")

            return keyword_field

        except Exception as e:
            logger.error(f"キーワードフィールド生成中にエラーが発生しました: {str(e)}")
            raise TextGenerationError(
                f"キーワードフィールド生成に失敗しました: {str(e)}"
            )

    def _prepare_keywords(
        self, primary_keyword: str, candidate_keywords: List[Dict[str, Any]]
    ) -> List[str]:
        """キーワードリストを準備"""
        keywords = [primary_keyword]

        # 候補キーワードを追加（スコア上位から）
        for candidate in candidate_keywords[: self.max_keywords - 1]:
            keyword = candidate.get("keyword", "")
            if keyword and keyword != primary_keyword:
                keywords.append(keyword)

        return keywords

    def _remove_duplicates(self, keywords: List[str]) -> List[str]:
        """重複キーワードを除去"""
        seen = set()
        unique_keywords = []

        for keyword in keywords:
            normalized = self._normalize_keyword(keyword)
            if normalized not in seen:
                seen.add(normalized)
                unique_keywords.append(keyword)

        return unique_keywords

    def _normalize_keyword(self, keyword: str) -> str:
        """キーワードを正規化"""
        # 小文字化と空白除去
        normalized = keyword.lower().strip()
        # 特殊文字の除去
        normalized = re.sub(r"[^\w\s]", "", normalized)
        return normalized

    def _sort_by_score(
        self, keywords: List[str], candidate_keywords: List[Dict[str, Any]]
    ) -> List[str]:
        """スコア順でソート"""
        # 候補キーワードのスコア辞書を作成
        score_dict = {
            candidate["keyword"]: candidate["score"] for candidate in candidate_keywords
        }

        # 主要キーワードに最高スコアを設定
        if keywords:
            score_dict[keywords[0]] = 1.0

        # スコア順でソート（スコアが同じ場合は元の順序を保持）
        sorted_keywords = sorted(
            keywords, key=lambda k: score_dict.get(k, 0), reverse=True
        )

        return sorted_keywords

    def _optimize_length(self, keywords: List[str]) -> List[str]:
        """100文字以内に収めるように最適化"""
        optimized = []
        current_length = 0

        for keyword in keywords:
            # 区切り文字の長さを考慮
            separator_length = len(self.separator) if optimized else 0
            keyword_length = len(keyword)

            # 追加後の総文字数を計算
            total_length = current_length + separator_length + keyword_length

            if total_length <= self.max_length:
                optimized.append(keyword)
                current_length = total_length
            else:
                break

        return optimized

    def _build_keyword_field(self, keywords: List[str], language: str) -> str:
        """キーワードフィールドを構築"""
        if not keywords:
            raise TextGenerationError("キーワードが空です")

        # 言語に応じた区切り文字を設定
        separator = self._get_separator(language)

        # キーワードフィールドを構築
        keyword_field = separator.join(keywords)

        return keyword_field

    def _get_separator(self, language: str) -> str:
        """言語に応じた区切り文字を取得"""
        separators = {"ja": "、", "en": ", "}
        return separators.get(language, self.separator)

    def _validate_keyword_field(self, keyword_field: str) -> bool:
        """キーワードフィールドを検証"""
        if not keyword_field:
            raise TextGenerationError("キーワードフィールドが空です")

        if len(keyword_field) > self.max_length:
            raise TextGenerationError(
                f"キーワードフィールドが長すぎます: {len(keyword_field)}文字"
            )

        # 禁止文字のチェック
        forbidden_chars = ["<", ">", "&", '"', "'"]
        for char in forbidden_chars:
            if char in keyword_field:
                raise TextGenerationError(
                    f"キーワードフィールドに禁止文字が含まれています: {char}"
                )

        return True


class MultilingualKeywordProcessor:
    """多言語対応キーワード処理クラス"""

    def __init__(self):
        self.language_rules = {
            "ja": {
                "separator": "、",
                "max_keywords": 8,
                "min_keyword_length": 2,
                "max_keyword_length": 20,
            },
            "en": {
                "separator": ", ",
                "max_keywords": 10,
                "min_keyword_length": 3,
                "max_keyword_length": 25,
            },
        }

    def process_keywords_for_language(
        self, keywords: List[str], language: str
    ) -> List[str]:
        """言語に応じたキーワード処理"""
        rules = self.language_rules.get(language, self.language_rules["en"])

        processed_keywords = []

        for keyword in keywords:
            # キーワード長の調整
            if len(keyword) < rules["min_keyword_length"]:
                continue

            if len(keyword) > rules["max_keyword_length"]:
                keyword = self._truncate_keyword(keyword, rules["max_keyword_length"])

            processed_keywords.append(keyword)

            # 最大キーワード数に達したら終了
            if len(processed_keywords) >= rules["max_keywords"]:
                break

        return processed_keywords

    def _truncate_keyword(self, keyword: str, max_length: int) -> str:
        """キーワードを指定長で切り詰め"""
        if len(keyword) <= max_length:
            return keyword

        # 単語境界で切り詰め
        truncated = keyword[:max_length]
        last_space = truncated.rfind(" ")

        if last_space > 0:
            return truncated[:last_space]

        return truncated


class KeywordFieldGenerationService:
    """統合キーワードフィールド生成サービス"""

    def __init__(self):
        self.generator = KeywordFieldGenerator()
        self.processor = MultilingualKeywordProcessor()

    def generate_keyword_field(
        self, selection_result: Dict[str, Any], language: str = "ja"
    ) -> Dict[str, Any]:
        """
        キーワードフィールドを生成（統合処理）

        Args:
            selection_result: キーワード選定結果
            language: 言語

        Returns:
            生成結果
        """
        try:
            # 入力データの検証
            if not selection_result:
                raise TextGenerationError("キーワード選定結果が空です")

            primary_keyword = selection_result.get("primary_keyword", "")
            candidates = selection_result.get("candidates", [])

            if not primary_keyword:
                raise TextGenerationError("主要キーワードが設定されていません")

            # キーワードフィールドを生成
            keyword_field = self.generator.generate_keyword_field(
                primary_keyword, candidates, language
            )

            # 結果を構築
            result = {
                "keyword_field": keyword_field,
                "length": len(keyword_field),
                "primary_keyword": primary_keyword,
                "language": language,
                "generated_at": datetime.now().isoformat(),
            }

            return result

        except Exception as e:
            logger.error(
                f"キーワードフィールド生成サービスでエラーが発生しました: {str(e)}"
            )
            raise TextGenerationError(
                f"キーワードフィールド生成に失敗しました: {str(e)}"
            )

    def generate(
        self,
        keywords_data: List[Dict[str, Any]],
        primary_keyword: str,
        language: str = "ja",
    ) -> str:
        """
        統合エンドポイント用のキーワードフィールド生成メソッド

        Args:
            keywords_data: キーワードデータ
            primary_keyword: 主要キーワード
            language: 言語

        Returns:
            生成されたキーワードフィールド
        """
        return self.generate_keyword_field(primary_keyword, keywords_data, language)
