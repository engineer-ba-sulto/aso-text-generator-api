# P4-002: 統一された処理フローの構築

## 概要

統合APIエンドポイントで使用する統一された処理フローを構築し、リクエストで受け取った`language`パラメータを後続の全サービスに引き渡し、最終的な出力が指定された一つの言語になるように一連の処理フローを実装します。

## 目標

- 統一された処理フローの設計と実装
- 言語パラメータの一貫した引き渡し
- エラーハンドリングの統一
- 処理の効率化と最適化

## 実装内容

### 1. 処理フローオーケストレーターの実装

```python
# app/services/aso_text_orchestrator.py
from typing import List, Dict, Any
from fastapi import UploadFile
from app.services.csv_analyzer import CSVAnalyzer
from app.services.keyword_selector import KeywordSelector
from app.services.keyword_field_generator import KeywordFieldGenerator
from app.services.title_generator import TitleGenerator
from app.services.subtitle_generator import SubtitleGenerator
from app.services.description_generator import DescriptionGenerator
from app.services.whats_new_generator import WhatsNewGenerator
from app.models.response_models import ASOTextGenerationResponse
from app.utils.exceptions import ASOTextGenerationError

class ASOTextOrchestrator:
    """
    ASOテキスト生成の処理フローを統括するオーケストレーター
    """
    
    def __init__(self):
        self.csv_analyzer = CSVAnalyzer()
        self.keyword_selector = KeywordSelector()
        self.keyword_field_generator = KeywordFieldGenerator()
        self.title_generator = TitleGenerator()
        self.subtitle_generator = SubtitleGenerator()
        self.description_generator = DescriptionGenerator()
        self.whats_new_generator = WhatsNewGenerator()
    
    async def generate_all_texts(
        self,
        csv_file: UploadFile,
        app_name: str,
        features: List[str],
        language: str
    ) -> ASOTextGenerationResponse:
        """
        全ASOテキスト項目を生成する統合処理フロー
        
        Args:
            csv_file: キーワードCSVファイル
            app_name: アプリ名
            features: アプリの特徴リスト
            language: 生成言語 (ja/en)
            
        Returns:
            ASOTextGenerationResponse: 生成された全テキスト項目
            
        Raises:
            ASOTextGenerationError: テキスト生成中のエラー
        """
        try:
            # ステップ1: CSV分析とキーワード選定
            keywords_data = await self._analyze_csv_and_select_keywords(csv_file)
            primary_keyword = keywords_data['primary_keyword']
            
            # ステップ2: 並列でテキスト生成（パフォーマンス向上）
            text_results = await self._generate_texts_parallel(
                keywords_data, primary_keyword, app_name, features, language
            )
            
            # ステップ3: レスポンスの構築
            return ASOTextGenerationResponse(
                keyword_field=text_results['keyword_field'],
                title=text_results['title'],
                subtitle=text_results['subtitle'],
                description=text_results['description'],
                whats_new=text_results['whats_new'],
                language=language
            )
            
        except Exception as e:
            raise ASOTextGenerationError(f"テキスト生成中にエラーが発生しました: {str(e)}")
    
    async def _analyze_csv_and_select_keywords(self, csv_file: UploadFile) -> Dict[str, Any]:
        """
        CSV分析と主要キーワード選定を実行
        
        Args:
            csv_file: キーワードCSVファイル
            
        Returns:
            Dict[str, Any]: 分析結果と主要キーワード
        """
        # CSV分析
        keywords_data = await self.csv_analyzer.analyze_csv(csv_file)
        
        # 主要キーワード選定
        primary_keyword = self.keyword_selector.select_primary_keyword(keywords_data)
        
        return {
            'keywords_data': keywords_data,
            'primary_keyword': primary_keyword
        }
    
    async def _generate_texts_parallel(
        self,
        keywords_data: Dict[str, Any],
        primary_keyword: str,
        app_name: str,
        features: List[str],
        language: str
    ) -> Dict[str, str]:
        """
        テキスト生成を並列実行（パフォーマンス向上）
        
        Args:
            keywords_data: キーワード分析データ
            primary_keyword: 主要キーワード
            app_name: アプリ名
            features: アプリの特徴リスト
            language: 生成言語
            
        Returns:
            Dict[str, str]: 生成された各テキスト項目
        """
        import asyncio
        
        # 並列実行するタスクを定義
        tasks = [
            # キーワードフィールド生成
            self.keyword_field_generator.generate(
                keywords_data, primary_keyword, language
            ),
            # タイトル生成
            self.title_generator.generate(
                primary_keyword, app_name, language
            ),
            # サブタイトル生成
            self.subtitle_generator.generate(
                primary_keyword, features, language
            ),
            # 概要生成
            self.description_generator.generate(
                primary_keyword, features, language
            ),
            # 最新情報生成
            self.whats_new_generator.generate(
                features, language
            )
        ]
        
        # 並列実行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 結果の検証とエラーハンドリング
        if any(isinstance(result, Exception) for result in results):
            raise ASOTextGenerationError("一部のテキスト生成でエラーが発生しました")
        
        return {
            'keyword_field': results[0],
            'title': results[1],
            'subtitle': results[2],
            'description': results[3],
            'whats_new': results[4]
        }
```

### 2. エンドポイントでのオーケストレーター使用

```python
# app/api/v1/aso_endpoints.py
from app.services.aso_text_orchestrator import ASOTextOrchestrator

@router.post("/generate-aso-texts", response_model=ASOTextGenerationResponse)
async def generate_aso_texts(
    request: ASOTextGenerationRequest,
    orchestrator: ASOTextOrchestrator = Depends()
):
    """
    ASOテキストを一括生成するエンドポイント
    """
    return await orchestrator.generate_all_texts(
        csv_file=request.csv_file,
        app_name=request.app_name,
        features=request.features,
        language=request.language
    )
```

### 3. 言語パラメータ検証の強化

```python
# app/utils/language_validator.py
from typing import Literal
from pydantic import validator

LanguageType = Literal['ja', 'en']

class LanguageValidator:
    """言語パラメータの検証と管理"""
    
    SUPPORTED_LANGUAGES = ['ja', 'en']
    
    @classmethod
    def validate_language(cls, language: str) -> LanguageType:
        """
        言語パラメータを検証
        
        Args:
            language: 検証する言語パラメータ
            
        Returns:
            LanguageType: 検証済みの言語パラメータ
            
        Raises:
            ValueError: 無効な言語パラメータの場合
        """
        if language not in cls.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported languages: {cls.SUPPORTED_LANGUAGES}"
            )
        return language
    
    @classmethod
    def get_language_name(cls, language: LanguageType) -> str:
        """
        言語コードから言語名を取得
        
        Args:
            language: 言語コード
            
        Returns:
            str: 言語名
        """
        language_names = {
            'ja': '日本語',
            'en': 'English'
        }
        return language_names.get(language, language)
```

### 4. 処理フローのログ機能

```python
# app/utils/flow_logger.py
import logging
from typing import Dict, Any
from datetime import datetime

class FlowLogger:
    """処理フローのログ記録"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_flow_start(self, language: str, app_name: str):
        """処理フロー開始のログ"""
        self.logger.info(
            f"ASO text generation flow started - Language: {language}, App: {app_name}"
        )
    
    def log_step_completion(self, step_name: str, duration: float):
        """ステップ完了のログ"""
        self.logger.info(f"Step '{step_name}' completed in {duration:.2f}s")
    
    def log_flow_completion(self, total_duration: float):
        """処理フロー完了のログ"""
        self.logger.info(f"ASO text generation flow completed in {total_duration:.2f}s")
    
    def log_error(self, step_name: str, error: Exception):
        """エラーのログ"""
        self.logger.error(f"Error in step '{step_name}': {str(error)}")
```

## 実装手順

1. **オーケストレータークラスの作成**
   - `app/services/aso_text_orchestrator.py`を作成
   - 統一された処理フローを実装

2. **言語検証機能の実装**
   - `app/utils/language_validator.py`を作成
   - 言語パラメータの検証機能を実装

3. **ログ機能の実装**
   - `app/utils/flow_logger.py`を作成
   - 処理フローのログ記録機能を実装

4. **エンドポイントの更新**
   - オーケストレーターを使用するように更新
   - エラーハンドリングの改善

5. **既存サービスクラスの確認**
   - 各サービスクラスが`language`パラメータを受け取れることを確認
   - 必要に応じて修正

## テスト項目

### 単体テスト
- [ ] オーケストレーターの各メソッドのテスト
- [ ] 言語検証機能のテスト
- [ ] ログ機能のテスト

### 統合テスト
- [ ] 完全な処理フローのテスト
- [ ] 並列処理の動作確認
- [ ] エラーハンドリングのテスト

### パフォーマンステスト
- [ ] 並列処理による性能向上の確認
- [ ] 処理時間の測定
- [ ] メモリ使用量の確認

## 成功基準

- [ ] 統一された処理フローが正常に動作する
- [ ] 言語パラメータが一貫して引き渡される
- [ ] 並列処理による性能向上が実現される
- [ ] エラーハンドリングが適切に機能する
- [ ] ログが適切に記録される

## 技術要件

### 必須技術
- asyncio（並列処理）
- logging（ログ機能）
- Pydantic（型検証）
- 既存の全サービスクラス

### 設計原則
- 単一責任の原則
- 依存性注入
- エラーハンドリングの統一
- パフォーマンス最適化

## 関連チケット

- **P4-001**: 統合APIエンドポイントの定義と実装
- **P4-003**: レスポンス形式の定義と実装
- **P0-005**: エラーハンドリング（基盤）
- **P1-001**: CSVデータモデルとバリデーション
- **P1-002**: キーワードスコアリング
- **P1-003**: 主要キーワードの自動選定

## 注意事項

- 並列処理による性能向上を重視
- エラーハンドリングの統一性を保つ
- ログの適切な記録を確保
- 言語パラメータの一貫した引き渡しが重要
