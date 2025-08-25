"""
タイトル生成サービス
30文字以内のアプリタイトルを生成するサービス
"""

from typing import List, Dict, Any, Optional
from app.utils.exceptions import TextGenerationError
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class TitleGenerator:
    """タイトル生成クラス"""

    def __init__(self):
        self.max_length = 30  # 最大文字数
        self.separator = " - "  # 区切り文字
        self.min_app_name_length = 3  # 最小アプリ名長
        self.max_app_name_length = 15  # 最大アプリ名長

    def generate_title(
        self,
        primary_keyword: str,
        app_base_name: str,
        language: str = "ja"
    ) -> str:
        """
        タイトルを生成

        Args:
            primary_keyword: 主要キーワード
            app_base_name: アプリ基本名
            language: 言語（"ja" or "en"）

        Returns:
            生成されたタイトル
        """
        try:
            # 入力データの検証
            self._validate_inputs(primary_keyword, app_base_name)

            # 主要キーワードを処理
            processed_keyword = self._process_primary_keyword(primary_keyword, language)

            # アプリ基本名を処理
            processed_app_name = self._process_app_name(app_base_name, language)

            # 区切り文字を取得
            separator = self._get_separator(language)

            # タイトルを構築
            title = self._build_title(processed_keyword, separator, processed_app_name)

            # 最終検証
            self._validate_title(title)

            logger.info(f"タイトルを生成しました: {title}")

            return title

        except Exception as e:
            logger.error(f"タイトル生成中にエラーが発生しました: {str(e)}")
            raise TextGenerationError(f"タイトル生成に失敗しました: {str(e)}")

    def _validate_inputs(self, primary_keyword: str, app_base_name: str) -> bool:
        """入力データを検証"""
        if not primary_keyword or not primary_keyword.strip():
            raise TextGenerationError("主要キーワードが空です")

        if not app_base_name or not app_base_name.strip():
            raise TextGenerationError("アプリ基本名が空です")

        if len(primary_keyword) > self.max_length:
            raise TextGenerationError(f"主要キーワードが長すぎます: {len(primary_keyword)}文字")

        if len(app_base_name) > self.max_length:
            raise TextGenerationError(f"アプリ基本名が長すぎます: {len(app_base_name)}文字")

        return True

    def _process_primary_keyword(self, keyword: str, language: str) -> str:
        """主要キーワードを処理"""
        # 空白除去と正規化
        processed = keyword.strip()

        # 言語に応じた処理
        if language == "ja":
            # 日本語の場合、全角文字を半角に変換
            processed = self._convert_fullwidth_to_halfwidth(processed)
        else:
            # 英語の場合、大文字小文字を調整
            processed = self._normalize_english_keyword(processed)

        # 特殊文字の除去
        processed = self._remove_special_chars(processed)

        return processed

    def _process_app_name(self, app_name: str, language: str) -> str:
        """アプリ基本名を処理"""
        # 空白除去と正規化
        processed = app_name.strip()

        # 言語に応じた処理
        if language == "ja":
            # 日本語の場合、全角文字を半角に変換
            processed = self._convert_fullwidth_to_halfwidth(processed)
        else:
            # 英語の場合、タイトルケースに変換
            processed = self._to_title_case(processed)

        # 特殊文字の除去
        processed = self._remove_special_chars(processed)

        # 長さの調整
        if len(processed) > self.max_app_name_length:
            processed = self._truncate_app_name(processed, self.max_app_name_length)

        return processed

    def _convert_fullwidth_to_halfwidth(self, text: str) -> str:
        """全角文字を半角に変換"""
        # 全角英数字を半角に変換
        fullwidth_chars = "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"
        halfwidth_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

        conversion_table = str.maketrans(fullwidth_chars, halfwidth_chars)
        return text.translate(conversion_table)

    def _normalize_english_keyword(self, keyword: str) -> str:
        """英語キーワードを正規化"""
        # 小文字に変換
        normalized = keyword.lower()
        # 各単語の最初の文字を大文字に
        normalized = normalized.title()
        return normalized

    def _to_title_case(self, text: str) -> str:
        """タイトルケースに変換"""
        return text.title()

    def _remove_special_chars(self, text: str) -> str:
        """特殊文字を除去"""
        # 禁止文字を除去
        forbidden_chars = ['<', '>', '&', '"', "'", '\\', '/', '|', '*', '?', ':', ';']
        for char in forbidden_chars:
            text = text.replace(char, '')

        # 連続する空白を単一の空白に
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def _truncate_app_name(self, app_name: str, max_length: int) -> str:
        """アプリ名を切り詰め"""
        if len(app_name) <= max_length:
            return app_name

        # 単語境界で切り詰め
        truncated = app_name[:max_length]
        last_space = truncated.rfind(' ')

        if last_space > 0:
            return truncated[:last_space]

        return truncated

    def _get_separator(self, language: str) -> str:
        """言語に応じた区切り文字を取得"""
        separators = {
            "ja": " - ",
            "en": " - "
        }
        return separators.get(language, self.separator)

    def _build_title(self, keyword: str, separator: str, app_name: str) -> str:
        """タイトルを構築"""
        # 区切り文字の長さを考慮してタイトルを構築
        title = f"{keyword}{separator}{app_name}"

        # 30文字制限をチェック
        if len(title) > self.max_length:
            # アプリ名を短縮
            available_length = self.max_length - len(keyword) - len(separator)
            if available_length >= self.min_app_name_length:
                app_name = self._truncate_app_name(app_name, available_length)
                title = f"{keyword}{separator}{app_name}"
            else:
                # キーワードのみでタイトルを構築
                title = keyword[:self.max_length]

        return title

    def _validate_title(self, title: str) -> bool:
        """タイトルを検証"""
        if not title:
            raise TextGenerationError("タイトルが空です")

        if len(title) > self.max_length:
            raise TextGenerationError(f"タイトルが長すぎます: {len(title)}文字")

        # 禁止文字のチェック
        forbidden_chars = ['<', '>', '&', '"', "'"]
        for char in forbidden_chars:
            if char in title:
                raise TextGenerationError(f"タイトルに禁止文字が含まれています: {char}")

        return True


class MultilingualTitleProcessor:
    """多言語対応タイトル処理クラス"""

    def __init__(self):
        self.language_rules = {
            "ja": {
                "separator": " - ",
                "max_keyword_length": 12,
                "max_app_name_length": 15,
                "case_sensitive": False
            },
            "en": {
                "separator": " - ",
                "max_keyword_length": 15,
                "max_app_name_length": 12,
                "case_sensitive": True
            }
        }

    def process_title_for_language(self, keyword: str, app_name: str, language: str) -> tuple[str, str]:
        """言語に応じたタイトル処理"""
        rules = self.language_rules.get(language, self.language_rules["en"])

        # キーワードの処理
        processed_keyword = self._process_keyword_for_language(keyword, rules)

        # アプリ名の処理
        processed_app_name = self._process_app_name_for_language(app_name, rules)

        return processed_keyword, processed_app_name

    def _process_keyword_for_language(self, keyword: str, rules: Dict[str, Any]) -> str:
        """言語に応じたキーワード処理"""
        processed = keyword.strip()

        # 長さ制限
        if len(processed) > rules["max_keyword_length"]:
            processed = processed[:rules["max_keyword_length"]]

        # 大文字小文字の処理
        if not rules["case_sensitive"]:
            processed = processed.lower()

        return processed

    def _process_app_name_for_language(self, app_name: str, rules: Dict[str, Any]) -> str:
        """言語に応じたアプリ名処理"""
        processed = app_name.strip()

        # 長さ制限
        if len(processed) > rules["max_app_name_length"]:
            processed = processed[:rules["max_app_name_length"]]

        # 大文字小文字の処理
        if rules["case_sensitive"]:
            processed = processed.title()

        return processed


class TitleGenerationService:
    """統合タイトル生成サービス"""

    def __init__(self):
        self.generator = TitleGenerator()
        self.processor = MultilingualTitleProcessor()

    def generate_title(
        self,
        primary_keyword: str,
        app_base_name: str,
        language: str = "ja"
    ) -> Dict[str, Any]:
        """
        タイトルを生成（統合処理）

        Args:
            primary_keyword: 主要キーワード
            app_base_name: アプリ基本名
            language: 言語

        Returns:
            生成結果
        """
        try:
            # 入力データの検証
            if not primary_keyword or not app_base_name:
                raise TextGenerationError("主要キーワードまたはアプリ基本名が空です")

            # 言語に応じた処理
            processed_keyword, processed_app_name = self.processor.process_title_for_language(
                primary_keyword, app_base_name, language
            )

            # タイトルを生成
            title = self.generator.generate_title(
                processed_keyword, processed_app_name, language
            )

            # 結果を構築
            result = {
                'title': title,
                'length': len(title),
                'primary_keyword': primary_keyword,
                'app_base_name': app_base_name,
                'language': language,
                'generated_at': datetime.now().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"タイトル生成サービスでエラーが発生しました: {str(e)}")
            raise TextGenerationError(f"タイトル生成に失敗しました: {str(e)}")
