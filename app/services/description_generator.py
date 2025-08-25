"""
概要生成サービス
4,000文字以内のアプリ概要を生成するサービス
"""

import re
from typing import Any, Dict, List

from loguru import logger

from app.services.gemini_generator import GeminiGenerator
from app.services.prompts.en import EnglishPrompts
from app.services.prompts.ja import JapanesePrompts


class DescriptionGenerator:
    """概要生成クラス"""

    def __init__(self, gemini_generator: GeminiGenerator):
        """
        初期化

        Args:
            gemini_generator: Gemini API連携クラス
        """
        self.gemini_generator = gemini_generator
        self.max_length = 4000
        self.min_keyword_count = 4
        self.max_keyword_count = 7

    def generate_description(
        self, app_info: Dict[str, Any], main_keyword: str, language: str = "ja"
    ) -> str:
        """
        概要を生成する

        Args:
            app_info: アプリ情報（名前、特徴、ターゲットユーザー、機能など）
            main_keyword: 主要キーワード（4〜7回含める対象）
            language: 生成言語（"ja" or "en"）

        Returns:
            生成された概要（4,000文字以内）
        """
        try:
            # プロンプト準備
            prompt = self._prepare_prompt(app_info, main_keyword, language)

            # Gemini API呼び出し
            description = self.gemini_generator.generate_description(prompt, language)

            # 後処理
            description = self._post_process_description(description, main_keyword)

            # 品質チェック
            if not self._validate_description(description, main_keyword):
                logger.warning(
                    "Generated description failed validation, attempting regeneration"
                )
                # 再生成を試行
                description = self.gemini_generator.generate_description(
                    prompt, language
                )
                description = self._post_process_description(description, main_keyword)

            logger.info(
                f"Generated description: {len(description)} characters, keyword count: {self._check_keyword_density(description, main_keyword)}"
            )
            return description

        except Exception as e:
            logger.error(f"Error generating description: {e}")
            raise

    def generate(
        self,
        primary_keyword: str,
        features: List[str],
        language: str = "ja"
    ) -> str:
        """
        統合エンドポイント用の概要生成メソッド
        
        Args:
            primary_keyword: 主要キーワード
            features: アプリの特徴
            language: 言語
            
        Returns:
            生成された概要
        """
        app_info = {"features": features}
        return self.generate_description(app_info, primary_keyword, language)

    def _prepare_prompt(
        self, app_info: Dict[str, Any], main_keyword: str, language: str
    ) -> str:
        """
        プロンプトを準備する

        Args:
            app_info: アプリ情報
            main_keyword: 主要キーワード
            language: 言語

        Returns:
            プロンプト文字列
        """
        if language == "ja":
            prompt_template = JapanesePrompts.DESCRIPTION_GENERATION
        else:
            prompt_template = EnglishPrompts.DESCRIPTION_GENERATION

        # アプリ情報の抽出
        app_name = app_info.get("name", "")
        app_features = app_info.get("features", [])
        target_audience = app_info.get("target_audience", "")
        related_keywords = app_info.get("related_keywords", [])

        # リストを文字列に変換
        features_str = (
            ", ".join(app_features)
            if isinstance(app_features, list)
            else str(app_features)
        )
        keywords_str = (
            ", ".join(related_keywords)
            if isinstance(related_keywords, list)
            else str(related_keywords)
        )

        return prompt_template.format(
            app_name=app_name,
            app_features=features_str,
            main_keyword=main_keyword,
            related_keywords=keywords_str,
            target_audience=target_audience,
        )

    def _post_process_description(self, description: str, main_keyword: str) -> str:
        """
        生成された概要を後処理する

        Args:
            description: 生成された概要
            main_keyword: 主要キーワード

        Returns:
            後処理された概要
        """
        # 文字数制限の確認と調整
        description = self._adjust_length(description)

        # キーワード密度の最適化
        description = self._optimize_keyword_placement(description, main_keyword)

        return description

    def _validate_description(self, description: str, main_keyword: str) -> bool:
        """
        概要の品質を検証する

        Args:
            description: 概要
            main_keyword: 主要キーワード

        Returns:
            検証結果
        """
        # 文字数チェック
        if len(description) > self.max_length:
            logger.warning(
                f"Description exceeds max length: {len(description)} > {self.max_length}"
            )
            return False

        # キーワード密度チェック
        keyword_count = self._check_keyword_density(description, main_keyword)
        if (
            keyword_count < self.min_keyword_count
            or keyword_count > self.max_keyword_count
        ):
            logger.warning(
                f"Keyword count out of range: {keyword_count} (should be {self.min_keyword_count}-{self.max_keyword_count})"
            )
            return False

        # 基本的な品質チェック
        if len(description.strip()) < 100:
            logger.warning("Description too short")
            return False

        return True

    def _check_keyword_density(self, text: str, keyword: str) -> int:
        """
        キーワードの出現回数をチェックする

        Args:
            text: テキスト
            keyword: キーワード

        Returns:
            キーワードの出現回数
        """
        # 大文字小文字を区別しないで検索
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        matches = pattern.findall(text)
        return len(matches)

    def _adjust_length(self, description: str, max_length: int = 4000) -> str:
        """
        文字数制限に合わせて調整する

        Args:
            description: 概要
            max_length: 最大文字数

        Returns:
            調整された概要
        """
        if len(description) <= max_length:
            return description

        # 文単位で切り詰める
        sentences = re.split(r"[。！？]", description)
        adjusted_description = ""

        for sentence in sentences:
            if sentence.strip():
                test_description = adjusted_description + sentence + "。"
                if len(test_description) <= max_length:
                    adjusted_description = test_description
                else:
                    break

        # 最後の文が不完全な場合は削除
        if adjusted_description and not adjusted_description.endswith("。"):
            adjusted_description = adjusted_description.rstrip("。") + "。"

        # それでも制限を超える場合は強制的に切り詰める
        if len(adjusted_description) > max_length:
            adjusted_description = adjusted_description[: max_length - 3] + "..."

        return adjusted_description

    def _optimize_keyword_placement(self, text: str, keyword: str) -> str:
        """
        キーワードの配置を最適化する

        Args:
            text: テキスト
            keyword: キーワード

        Returns:
            最適化されたテキスト
        """
        current_count = self._check_keyword_density(text, keyword)

        # キーワード数が適切な範囲内の場合はそのまま返す
        if self.min_keyword_count <= current_count <= self.max_keyword_count:
            return text

        # キーワードが少ない場合は追加を試行
        if current_count < self.min_keyword_count:
            text = self._add_keywords(
                text, keyword, self.min_keyword_count - current_count
            )

        # キーワードが多い場合は削減を試行
        elif current_count > self.max_keyword_count:
            text = self._reduce_keywords(
                text, keyword, current_count - self.max_keyword_count
            )

        return text

    def _add_keywords(self, text: str, keyword: str, count: int) -> str:
        """
        キーワードを追加する

        Args:
            text: テキスト
            keyword: キーワード
            count: 追加する数

        Returns:
            キーワードが追加されたテキスト
        """
        # 文の区切りで分割
        sentences = re.split(r"([。！？])", text)
        modified_sentences = []

        added_count = 0
        for i in range(0, len(sentences), 2):  # 文と句読点をペアで処理
            if i + 1 < len(sentences):
                sentence = sentences[i]
                punctuation = sentences[i + 1]
            else:
                sentence = sentences[i]
                punctuation = ""

            if added_count >= count:
                modified_sentences.append(sentence)
                if punctuation:
                    modified_sentences.append(punctuation)
                continue

            # キーワードが含まれていない文に自然に追加
            if keyword.lower() not in sentence.lower() and len(sentence.strip()) > 5:
                # 文の途中に自然に挿入
                words = sentence.split()
                if len(words) > 2:
                    insert_pos = len(words) // 2
                    words.insert(insert_pos, keyword)
                    sentence = " ".join(words)
                    added_count += 1
            # キーワードが含まれている文でも、追加が必要な場合は重複を避けて追加
            elif added_count < count and len(sentence.strip()) > 10:
                # 文の最後に追加
                if not sentence.endswith(keyword):
                    sentence = sentence + " " + keyword
                    added_count += 1

            modified_sentences.append(sentence)
            if punctuation:
                modified_sentences.append(punctuation)

        # まだ追加が必要な場合は、文の最後に追加
        if added_count < count:
            remaining_count = count - added_count
            for _ in range(remaining_count):
                if modified_sentences:
                    # 最後の文に追加
                    last_sentence = modified_sentences[-1]
                    if not last_sentence.endswith(keyword):
                        modified_sentences[-1] = last_sentence + " " + keyword

        return "".join(modified_sentences)

    def _reduce_keywords(self, text: str, keyword: str, count: int) -> str:
        """
        キーワードを削減する

        Args:
            text: テキスト
            keyword: キーワード
            count: 削減する数

        Returns:
            キーワードが削減されたテキスト
        """
        # キーワードの位置を特定
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        matches = list(pattern.finditer(text))

        # 後ろから削除（文の構造を保つため）
        removed_count = 0
        for match in reversed(matches):
            if removed_count >= count:
                break

            start, end = match.span()
            # 前後の文脈を確認して削除が安全かチェック
            if self._is_safe_to_remove(text, start, end):
                text = text[:start] + text[end:]
                removed_count += 1

        return text

    def _is_safe_to_remove(self, text: str, start: int, end: int) -> bool:
        """
        キーワードの削除が安全かチェックする

        Args:
            text: テキスト
            start: 開始位置
            end: 終了位置

        Returns:
            削除が安全かどうか
        """
        # 文の境界を確認
        sentence_start = text.rfind("。", 0, start)
        sentence_end = text.find("。", end)

        if sentence_start == -1:
            sentence_start = 0
        if sentence_end == -1:
            sentence_end = len(text)

        sentence = text[sentence_start:sentence_end]

        # 文が短すぎる場合は削除しない
        if len(sentence.strip()) < 10:
            return False

        return True
