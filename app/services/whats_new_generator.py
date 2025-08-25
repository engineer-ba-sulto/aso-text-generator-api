"""
最新情報生成サービス
4000文字以内の最新情報テキストを生成するサービス
"""

from typing import List, Dict, Any, Optional
from app.utils.exceptions import TextGenerationError
from datetime import datetime
import re
import random
import logging

logger = logging.getLogger(__name__)


class WhatsNewGenerator:
    """最新情報生成クラス"""

    def __init__(self):
        self.max_length = 4000  # 最大文字数
        self.min_keyword_occurrences = 4  # 最小キーワード出現回数
        self.max_keyword_occurrences = 7  # 最大キーワード出現回数
        self.templates = self._load_templates()

    def generate_whats_new(
        self,
        primary_keyword: str,
        app_features: List[str],
        language: str = "ja"
    ) -> str:
        """
        最新情報を生成

        Args:
            primary_keyword: 主要キーワード
            app_features: アプリの特徴リスト
            language: 言語（"ja" or "en"）

        Returns:
            生成された最新情報
        """
        try:
            # 入力データの検証
            self._validate_inputs(primary_keyword, app_features)

            # テンプレートを取得
            template = self._get_template(language)

            # 主要キーワードを自然に組み込む
            content = self._integrate_keyword(template, primary_keyword, language)

            # アプリの特徴を組み込む
            content = self._integrate_features(content, app_features, language)

            # 文字数制限内に収める
            content = self._optimize_length(content)

            # 最終検証
            self._validate_content(content, primary_keyword)

            logger.info(f"最新情報を生成しました: {len(content)}文字")

            return content

        except Exception as e:
            logger.error(f"最新情報生成中にエラーが発生しました: {str(e)}")
            raise TextGenerationError(f"最新情報生成に失敗しました: {str(e)}")

    def _load_templates(self) -> Dict[str, str]:
        """テンプレートを読み込み"""
        return {
            "ja": self._get_japanese_template(),
            "en": self._get_english_template()
        }

    def _get_japanese_template(self) -> str:
        """日本語テンプレートを取得"""
        return """
【新機能・改善点】

{keyword_placeholder}

【主な変更点】
• パフォーマンスの向上
• ユーザーインターフェースの改善
• バグ修正と安定性の向上

【詳細】
{keyword_placeholder}を活用した新機能を追加しました。ユーザーの利便性を向上させるため、様々な改善を行っています。

{keyword_placeholder}に関する機能を強化し、より使いやすいアプリケーションを目指しています。

【今後の予定】
引き続き{keyword_placeholder}の機能向上に取り組み、ユーザーの皆様により良いサービスを提供してまいります。

ご利用いただき、ありがとうございます。
"""

    def _get_english_template(self) -> str:
        """英語テンプレートを取得"""
        return """
【New Features & Improvements】

{keyword_placeholder}

【Key Changes】
• Performance improvements
• Enhanced user interface
• Bug fixes and stability improvements

【Details】
We've added new features utilizing {keyword_placeholder}. Various improvements have been made to enhance user convenience.

We've strengthened the {keyword_placeholder} functionality to create a more user-friendly application.

【Future Plans】
We will continue to work on improving {keyword_placeholder} features to provide better service to our users.

Thank you for using our app.
"""

    def _validate_inputs(self, primary_keyword: str, app_features: List[str]) -> bool:
        """入力データを検証"""
        if not primary_keyword or not primary_keyword.strip():
            raise TextGenerationError("主要キーワードが空です")

        if not app_features:
            raise TextGenerationError("アプリの特徴リストが空です")

        if len(primary_keyword) > 50:
            raise TextGenerationError(f"主要キーワードが長すぎます: {len(primary_keyword)}文字")

        return True

    def _get_template(self, language: str) -> str:
        """言語に応じたテンプレートを取得"""
        template = self.templates.get(language)
        if not template:
            raise TextGenerationError(f"サポートされていない言語です: {language}")

        return template

    def _integrate_keyword(self, template: str, keyword: str, language: str) -> str:
        """主要キーワードを自然に組み込む"""
        # プレースホルダーを置換
        content = template.replace("{keyword_placeholder}", keyword)

        # キーワードの出現回数を調整
        content = self._adjust_keyword_occurrences(content, keyword, language)

        return content

    def _adjust_keyword_occurrences(self, content: str, keyword: str, language: str) -> str:
        """キーワードの出現回数を調整"""
        # 現在の出現回数をカウント
        current_count = content.count(keyword)

        if current_count < self.min_keyword_occurrences:
            # キーワードを追加
            content = self._add_keyword_occurrences(content, keyword, language, self.min_keyword_occurrences - current_count)
        elif current_count > self.max_keyword_occurrences:
            # キーワードを削減
            content = self._reduce_keyword_occurrences(content, keyword, self.max_keyword_occurrences)

        return content

    def _add_keyword_occurrences(self, content: str, keyword: str, language: str, count: int) -> str:
        """キーワードの出現回数を追加"""
        sentences = self._get_sentences(content, language)

        # 適切な位置にキーワードを含む文を追加
        for i in range(count):
            new_sentence = self._create_sentence_with_keyword(keyword, language)
            # 文の途中に挿入
            insert_position = len(sentences) // 2 + i
            if insert_position < len(sentences):
                sentences.insert(insert_position, new_sentence)
            else:
                sentences.append(new_sentence)

        return " ".join(sentences)

    def _reduce_keyword_occurrences(self, content: str, keyword: str, target_count: int) -> str:
        """キーワードの出現回数を削減"""
        # キーワードの位置を特定
        positions = []
        start = 0
        while True:
            pos = content.find(keyword, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1

        # 後半の出現を削除
        if len(positions) > target_count:
            positions_to_remove = positions[target_count:]
            # 後ろから削除（インデックスがずれないように）
            for pos in reversed(positions_to_remove):
                # キーワードを含む文全体を削除
                content = self._remove_sentence_at_position(content, pos)

        return content

    def _remove_sentence_at_position(self, content: str, position: int) -> str:
        """指定位置の文を削除"""
        # 文の境界を特定
        sentence_start = self._find_sentence_start(content, position)
        sentence_end = self._find_sentence_end(content, position)

        if sentence_start < sentence_end:
            return content[:sentence_start] + content[sentence_end:]

        return content

    def _find_sentence_start(self, content: str, position: int) -> int:
        """文の開始位置を特定"""
        # 前の文の終了記号を探す
        for i in range(position - 1, -1, -1):
            if content[i] in '.!?。！？':
                return i + 1
        return 0

    def _find_sentence_end(self, content: str, position: int) -> int:
        """文の終了位置を特定"""
        # 次の文の終了記号を探す
        for i in range(position, len(content)):
            if content[i] in '.!?。！？':
                return i + 1
        return len(content)

    def _create_sentence_with_keyword(self, keyword: str, language: str) -> str:
        """キーワードを含む文を作成"""
        if language == "ja":
            templates = [
                f"{keyword}の機能を強化しました。",
                f"{keyword}に関する新機能を追加しました。",
                f"{keyword}の使いやすさを向上させました。",
                f"{keyword}のパフォーマンスを改善しました。"
            ]
        else:
            templates = [
                f"We've enhanced the {keyword} functionality.",
                f"We've added new features related to {keyword}.",
                f"We've improved the usability of {keyword}.",
                f"We've optimized the performance of {keyword}."
            ]

        return random.choice(templates)

    def _get_sentences(self, content: str, language: str) -> List[str]:
        """文に分割"""
        if language == "ja":
            # 日本語の文分割
            sentences = re.split(r'[。！？]', content)
        else:
            # 英語の文分割
            sentences = re.split(r'[.!?]', content)

        return [s.strip() for s in sentences if s.strip()]

    def _integrate_features(self, content: str, features: List[str], language: str) -> str:
        """アプリの特徴を組み込む"""
        if not features:
            return content

        # 特徴を自然に組み込む
        feature_text = self._format_features(features, language)

        # 適切な位置に挿入
        if language == "ja":
            insert_marker = "【主な変更点】"
        else:
            insert_marker = "【Key Changes】"

        if insert_marker in content:
            content = content.replace(insert_marker, f"{insert_marker}\n{feature_text}")

        return content

    def _format_features(self, features: List[str], language: str) -> str:
        """特徴をフォーマット"""
        formatted_features = []

        for feature in features:
            if language == "ja":
                formatted_features.append(f"• {feature}")
            else:
                formatted_features.append(f"• {feature}")

        return "\n".join(formatted_features)

    def _optimize_length(self, content: str) -> str:
        """文字数制限内に収める"""
        if len(content) <= self.max_length:
            return content

        # 文単位で削減
        sentences = self._get_sentences(content, "ja")  # 言語は後で判定

        optimized_content = ""
        for sentence in sentences:
            if len(optimized_content + sentence) <= self.max_length:
                optimized_content += sentence + "。"
            else:
                break

        return optimized_content.strip()

    def _validate_content(self, content: str, keyword: str) -> bool:
        """コンテンツを検証"""
        if not content:
            raise TextGenerationError("最新情報が空です")

        if len(content) > self.max_length:
            raise TextGenerationError(f"最新情報が長すぎます: {len(content)}文字")

        # キーワードの出現回数をチェック
        keyword_count = content.count(keyword)
        if keyword_count < self.min_keyword_occurrences:
            raise TextGenerationError(f"キーワードの出現回数が少なすぎます: {keyword_count}回")

        if keyword_count > self.max_keyword_occurrences:
            raise TextGenerationError(f"キーワードの出現回数が多すぎます: {keyword_count}回")

        return True


class MultilingualWhatsNewProcessor:
    """多言語対応最新情報処理クラス"""

    def __init__(self):
        self.language_rules = {
            "ja": {
                "sentence_endings": ["。", "！", "？"],
                "bullet_points": "•",
                "max_sentence_length": 100,
                "min_sentence_length": 10
            },
            "en": {
                "sentence_endings": [".", "!", "?"],
                "bullet_points": "•",
                "max_sentence_length": 150,
                "min_sentence_length": 15
            }
        }

    def process_whats_new_for_language(self, content: str, language: str) -> str:
        """言語に応じた最新情報処理"""
        rules = self.language_rules.get(language, self.language_rules["en"])

        # 文の長さを調整
        content = self._adjust_sentence_lengths(content, rules)

        # フォーマットを統一
        content = self._normalize_format(content, rules)

        return content

    def _adjust_sentence_lengths(self, content: str, rules: Dict[str, Any]) -> str:
        """文の長さを調整"""
        sentences = self._split_sentences(content, rules["sentence_endings"])

        adjusted_sentences = []
        for sentence in sentences:
            if len(sentence) > rules["max_sentence_length"]:
                # 長い文を分割
                split_sentences = self._split_long_sentence(sentence, rules)
                adjusted_sentences.extend(split_sentences)
            elif len(sentence) < rules["min_sentence_length"]:
                # 短い文を結合または削除
                continue
            else:
                adjusted_sentences.append(sentence)

        return " ".join(adjusted_sentences)

    def _split_sentences(self, content: str, endings: List[str]) -> List[str]:
        """文に分割"""
        pattern = "|".join(map(re.escape, endings))
        sentences = re.split(f"({pattern})", content)

        # 文と終了記号を結合
        combined = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                combined.append(sentences[i] + sentences[i + 1])
            else:
                combined.append(sentences[i])

        return [s.strip() for s in combined if s.strip()]

    def _split_long_sentence(self, sentence: str, rules: Dict[str, Any]) -> List[str]:
        """長い文を分割"""
        # カンマや接続詞で分割
        parts = re.split(r'[,、]', sentence)

        if len(parts) <= 1:
            # 分割できない場合はそのまま返す
            return [sentence]

        # 各部分を適切な長さに調整
        result = []
        current_part = ""

        for part in parts:
            if len(current_part + part) <= rules["max_sentence_length"]:
                current_part += part + "、"
            else:
                if current_part:
                    result.append(current_part.rstrip("、"))
                current_part = part + "、"

        if current_part:
            result.append(current_part.rstrip("、"))

        return result

    def _normalize_format(self, content: str, rules: Dict[str, Any]) -> str:
        """フォーマットを統一"""
        # 箇条書きの統一
        content = re.sub(r'^[•·・]\s*', rules["bullet_points"] + " ", content, flags=re.MULTILINE)

        # 余分な空白を除去
        content = re.sub(r'\s+', ' ', content)

        return content.strip()


class WhatsNewGenerationService:
    """統合最新情報生成サービス"""

    def __init__(self):
        self.generator = WhatsNewGenerator()
        self.processor = MultilingualWhatsNewProcessor()

    def generate_whats_new(
        self,
        primary_keyword: str,
        app_features: List[str],
        language: str = "ja"
    ) -> Dict[str, Any]:
        """
        最新情報を生成（統合処理）

        Args:
            primary_keyword: 主要キーワード
            app_features: アプリの特徴リスト
            language: 言語

        Returns:
            生成結果
        """
        try:
            # 入力データの検証
            if not primary_keyword or not app_features:
                raise TextGenerationError("主要キーワードまたはアプリの特徴が空です")

            # 最新情報を生成
            content = self.generator.generate_whats_new(
                primary_keyword, app_features, language
            )

            # 言語に応じた処理
            processed_content = self.processor.process_whats_new_for_language(content, language)

            # 結果を構築
            result = {
                'whats_new': processed_content,
                'length': len(processed_content),
                'primary_keyword': primary_keyword,
                'keyword_occurrences': processed_content.count(primary_keyword),
                'language': language,
                'generated_at': datetime.now().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"最新情報生成サービスでエラーが発生しました: {str(e)}")
            raise TextGenerationError(f"最新情報生成に失敗しました: {str(e)}")
