"""
サブタイトル生成サービス
30文字以内のサブタイトルを生成するサービス
"""

import re
from typing import Dict, List, Any

from loguru import logger

from app.services.gemini_generator import GeminiGenerator
from app.services.prompts import PromptManager


class SubtitleGenerator:
    """サブタイトル生成クラス"""

    def __init__(self, gemini_generator: GeminiGenerator):
        """
        初期化

        Args:
            gemini_generator: GeminiGeneratorインスタンス
        """
        self.gemini_generator = gemini_generator
        self.max_length = 30

    def generate_subtitle(self, app_info: dict, main_keyword: str, language: str = "ja") -> str:
        """
        サブタイトルを生成する

        Args:
            app_info: アプリ情報（名前、特徴、ターゲットユーザーなど）
            main_keyword: 主要キーワード（除外対象）
            language: 生成言語（"ja" or "en"）

        Returns:
            生成されたサブタイトル（30文字以内）
        """
        try:
            # プロンプトの準備
            prompt = self._prepare_prompt(app_info, main_keyword, language)
            
            # Gemini APIでサブタイトル生成
            raw_subtitle = self.gemini_generator.generate_subtitle(prompt, language)
            
            # 後処理
            subtitle = self._post_process_subtitle(raw_subtitle, main_keyword)
            
            # 品質チェック
            if not self._validate_subtitle(subtitle, main_keyword):
                logger.warning(f"Generated subtitle failed validation, regenerating: {subtitle}")
                return self._regenerate_subtitle(app_info, main_keyword, language)
            
            logger.info(f"Generated subtitle: '{subtitle}' ({len(subtitle)} characters)")
            return subtitle
            
        except Exception as e:
            logger.error(f"Error generating subtitle: {e}")
            raise

    def _prepare_prompt(self, app_info: dict, main_keyword: str, language: str) -> str:
        """
        プロンプトを準備する

        Args:
            app_info: アプリ情報
            main_keyword: 主要キーワード
            language: 言語

        Returns:
            準備されたプロンプト
        """
        app_name = app_info.get("name", "")
        app_features = app_info.get("features", "")
        target_audience = app_info.get("target_audience", "")
        
        return PromptManager.get_subtitle_prompt(
            language=language,
            app_name=app_name,
            app_features=app_features,
            main_keyword=main_keyword,
            target_audience=target_audience
        )

    def _post_process_subtitle(self, subtitle: str, main_keyword: str) -> str:
        """
        サブタイトルの後処理

        Args:
            subtitle: 生成されたサブタイトル
            main_keyword: 主要キーワード

        Returns:
            後処理されたサブタイトル
        """
        # 主要キーワードの除外
        subtitle = self._filter_keywords(subtitle, [main_keyword])
        
        # 文字数制限の調整
        subtitle = self._adjust_length(subtitle)
        
        # 基本的なクリーニング
        subtitle = self._clean_text(subtitle)
        
        return subtitle

    def _validate_subtitle(self, subtitle: str, main_keyword: str) -> bool:
        """
        サブタイトルの妥当性を検証する

        Args:
            subtitle: 検証対象のサブタイトル
            main_keyword: 主要キーワード

        Returns:
            妥当性の結果
        """
        # 文字数チェック
        if len(subtitle) > self.max_length:
            logger.warning(f"Subtitle too long: {len(subtitle)} characters")
            return False
        
        # 主要キーワードの除外チェック
        if self._contains_keyword(subtitle, main_keyword):
            logger.warning(f"Subtitle contains main keyword: {main_keyword}")
            return False
        
        # 空文字チェック
        if not subtitle.strip():
            logger.warning("Subtitle is empty")
            return False
        
        # 不適切なコンテンツチェック
        if self._contains_inappropriate_content(subtitle):
            logger.warning("Subtitle contains inappropriate content")
            return False
        
        return True

    def _adjust_length(self, subtitle: str, max_length: int = 30) -> str:
        """
        文字数制限に合わせてサブタイトルを調整する

        Args:
            subtitle: 調整対象のサブタイトル
            max_length: 最大文字数

        Returns:
            調整されたサブタイトル
        """
        if len(subtitle) <= max_length:
            return subtitle
        
        # 文字数制限を超える場合は切り詰める
        truncated = subtitle[:max_length]
        
        # 文の途中で切れないように調整
        last_period = truncated.rfind("。")
        if last_period > 0 and last_period > max_length * 0.5:
            return truncated[:last_period + 1]
        
        # 英語の場合はピリオドで調整
        last_dot = truncated.rfind(".")
        if last_dot > 0 and last_dot > max_length * 0.5:
            return truncated[:last_dot + 1]
        
        return truncated

    def _filter_keywords(self, text: str, keywords: List[str]) -> str:
        """
        テキストからキーワードを除外する

        Args:
            text: 対象テキスト
            keywords: 除外するキーワードのリスト

        Returns:
            キーワードが除外されたテキスト
        """
        filtered_text = text
        for keyword in keywords:
            if keyword:
                # 大文字小文字を区別せずに除外
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                filtered_text = pattern.sub("", filtered_text)
        
        # 余分な空白を削除
        filtered_text = re.sub(r'\s+', ' ', filtered_text).strip()
        
        return filtered_text

    def _contains_keyword(self, text: str, keyword: str) -> bool:
        """
        テキストにキーワードが含まれているかチェック

        Args:
            text: チェック対象のテキスト
            keyword: 検索するキーワード

        Returns:
            キーワードが含まれているかどうか
        """
        if not keyword:
            return False
        
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        return bool(pattern.search(text))

    def _clean_text(self, text: str) -> str:
        """
        テキストをクリーニングする

        Args:
            text: クリーニング対象のテキスト

        Returns:
            クリーニングされたテキスト
        """
        # 余分な空白を削除
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 先頭・末尾の句読点を削除
        text = re.sub(r'^[。、，．,.]', '', text)
        text = re.sub(r'[。、，．,.]$', '', text)
        
        return text

    def _contains_inappropriate_content(self, text: str) -> bool:
        """
        不適切なコンテンツが含まれているかチェック

        Args:
            text: チェック対象のテキスト

        Returns:
            不適切なコンテンツが含まれているかどうか
        """
        # 基本的な不適切な単語のチェック（実際の実装ではより詳細なリストを使用）
        inappropriate_words = [
            "不適切", "inappropriate", "spam", "スパム", "詐欺", "fraud"
        ]
        
        for word in inappropriate_words:
            if word.lower() in text.lower():
                return True
        
        return False

    def _regenerate_subtitle(self, app_info: dict, main_keyword: str, language: str) -> str:
        """
        サブタイトルを再生成する

        Args:
            app_info: アプリ情報
            main_keyword: 主要キーワード
            language: 言語

        Returns:
            再生成されたサブタイトル
        """
        try:
            # より厳格なプロンプトで再生成
            prompt = self._prepare_strict_prompt(app_info, main_keyword, language)
            raw_subtitle = self.gemini_generator.generate_subtitle(prompt, language)
            subtitle = self._post_process_subtitle(raw_subtitle, main_keyword)
            
            if self._validate_subtitle(subtitle, main_keyword):
                return subtitle
            
            # フォールバック: 基本的なサブタイトルを生成
            return self._generate_fallback_subtitle(app_info, language)
            
        except Exception as e:
            logger.error(f"Error regenerating subtitle: {e}")
            return self._generate_fallback_subtitle(app_info, language)

    def _prepare_strict_prompt(self, app_info: dict, main_keyword: str, language: str) -> str:
        """
        より厳格なプロンプトを準備する

        Args:
            app_info: アプリ情報
            main_keyword: 主要キーワード
            language: 言語

        Returns:
            厳格なプロンプト
        """
        base_prompt = self._prepare_prompt(app_info, main_keyword, language)
        
        strict_instruction = """
        
        重要: 以下の制約を厳格に守ってください:
        1. 必ず30文字以内にしてください
        2. 主要キーワード「{keyword}」は絶対に含めないでください
        3. アプリの価値を簡潔に表現してください
        4. 魅力的で覚えやすい表現にしてください
        """.format(keyword=main_keyword)
        
        return base_prompt + strict_instruction

    def _generate_fallback_subtitle(self, app_info: dict, language: str) -> str:
        """
        フォールバック用のサブタイトルを生成する

        Args:
            app_info: アプリ情報
            language: 言語

        Returns:
            フォールバックサブタイトル
        """
        app_name = app_info.get("name", "")
        app_features = app_info.get("features", "")
        
        if language == "ja":
            # 日本語のフォールバック
            if app_features:
                # 特徴から短い表現を生成
                features_list = app_features.split("、")[:2]  # 最初の2つの特徴を使用
                subtitle = "、".join(features_list)
                if len(subtitle) > self.max_length:
                    subtitle = subtitle[:self.max_length-1] + "…"
                return subtitle
            else:
                return "便利なアプリ"
        else:
            # 英語のフォールバック
            if app_features:
                features_list = app_features.split(",")[:2]
                subtitle = ", ".join(features_list)
                if len(subtitle) > self.max_length:
                    subtitle = subtitle[:self.max_length-3] + "..."
                return subtitle
            else:
                return "Useful App"
