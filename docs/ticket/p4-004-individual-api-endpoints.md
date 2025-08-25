# P4-004: 個別 API エンドポイントの定義と実装

## 概要

各テキスト項目を個別に生成する API エンドポイントを実装します。これにより、ユーザーは必要な特定のテキスト項目のみを効率的に生成できるようになります。各エンドポイントは、必要な最小限の処理（CSV 分析、キーワード選定、該当テキスト生成）のみを実行します。

## 目標

- 個別 API エンドポイントの実装
- 効率的な処理フローの設計
- 多言語対応の個別エンドポイント
- 統一されたリクエスト・レスポンス形式

## 実装内容

### 1. 個別リクエストモデルの定義

```python
# app/models/request_models.py
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from fastapi import UploadFile

class KeywordFieldRequest(BaseModel):
    """キーワードフィールド生成のリクエストモデル"""
    csv_file: UploadFile
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")

    @validator('language')
    def validate_language(cls, v):
        if v not in ['ja', 'en']:
            raise ValueError('language must be either "ja" or "en"')
        return v

class TitleRequest(BaseModel):
    """タイトル生成のリクエストモデル"""
    primary_keyword: str = Field(..., description="主要キーワード")
    app_name: str = Field(..., description="アプリ名")
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")

    @validator('language')
    def validate_language(cls, v):
        if v not in ['ja', 'en']:
            raise ValueError('language must be either "ja" or "en"')
        return v

class SubtitleRequest(BaseModel):
    """サブタイトル生成のリクエストモデル"""
    primary_keyword: str = Field(..., description="主要キーワード")
    features: List[str] = Field(..., description="アプリの特徴リスト")
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")

    @validator('language')
    def validate_language(cls, v):
        if v not in ['ja', 'en']:
            raise ValueError('language must be either "ja" or "en"')
        return v

class DescriptionRequest(BaseModel):
    """概要生成のリクエストモデル"""
    primary_keyword: str = Field(..., description="主要キーワード")
    features: List[str] = Field(..., description="アプリの特徴リスト")
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")

    @validator('language')
    def validate_language(cls, v):
        if v not in ['ja', 'en']:
            raise ValueError('language must be either "ja" or "en"')
        return v

class WhatsNewRequest(BaseModel):
    """最新情報生成のリクエストモデル"""
    features: List[str] = Field(..., description="アプリの特徴リスト")
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")

    @validator('language')
    def validate_language(cls, v):
        if v not in ['ja', 'en']:
            raise ValueError('language must be either "ja" or "en"')
        return v
```

### 2. 個別エンドポイントの実装

```python
# app/api/v1/aso_endpoints.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List
from app.models.request_models import (
    KeywordFieldRequest, TitleRequest, SubtitleRequest,
    DescriptionRequest, WhatsNewRequest
)
from app.models.response_models import (
    KeywordFieldResponse, TitleResponse, SubtitleResponse,
    DescriptionResponse, WhatsNewResponse
)
from app.services.csv_analyzer import CSVAnalyzer
from app.services.keyword_selector import KeywordSelector
from app.services.keyword_field_generator import KeywordFieldGenerator
from app.services.title_generator import TitleGenerator
from app.services.subtitle_generator import SubtitleGenerator
from app.services.description_generator import DescriptionGenerator
from app.services.whats_new_generator import WhatsNewGenerator
from app.utils.response_builder import ResponseBuilder

router = APIRouter()

# キーワードフィールド生成エンドポイント
@router.post("/generate-keyword-field", response_model=KeywordFieldResponse)
async def generate_keyword_field(
    csv_file: UploadFile = File(...),
    language: str = Form(...),
    csv_analyzer: CSVAnalyzer = Depends(),
    keyword_selector: KeywordSelector = Depends(),
    keyword_field_generator: KeywordFieldGenerator = Depends(),
    response_builder: ResponseBuilder = Depends()
):
    """
    キーワードフィールド (100文字) を生成するエンドポイント

    - CSVファイルからキーワード分析を実行
    - 主要キーワードを自動選定
    - 指定された言語でキーワードフィールドを生成
    """
    try:
        # 言語パラメータの検証
        if language not in ['ja', 'en']:
            raise HTTPException(
                status_code=400,
                detail="language must be either 'ja' or 'en'"
            )

        # CSV分析とキーワード選定
        keywords_data = await csv_analyzer.analyze_csv(csv_file)
        primary_keyword = keyword_selector.select_primary_keyword(keywords_data)

        # キーワードフィールド生成
        keyword_field = await keyword_field_generator.generate(
            keywords_data, primary_keyword, language
        )

        # レスポンス構築
        return response_builder.build_keyword_field_response(
            keyword_field=keyword_field,
            language=language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"キーワードフィールド生成中にエラーが発生しました: {str(e)}"
        )

# タイトル生成エンドポイント
@router.post("/generate-title", response_model=TitleResponse)
async def generate_title(
    request: TitleRequest,
    title_generator: TitleGenerator = Depends(),
    response_builder: ResponseBuilder = Depends()
):
    """
    タイトル (30文字) を生成するエンドポイント

    - 主要キーワードとアプリ名からタイトルを生成
    - 指定された言語でタイトルを生成
    """
    try:
        title = await title_generator.generate(
            request.primary_keyword,
            request.app_name,
            request.language
        )

        return response_builder.build_title_response(
            title=title,
            language=request.language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"タイトル生成中にエラーが発生しました: {str(e)}"
        )

# サブタイトル生成エンドポイント
@router.post("/generate-subtitle", response_model=SubtitleResponse)
async def generate_subtitle(
    request: SubtitleRequest,
    subtitle_generator: SubtitleGenerator = Depends(),
    response_builder: ResponseBuilder = Depends()
):
    """
    サブタイトル (30文字) を生成するエンドポイント

    - 主要キーワードとアプリの特徴からサブタイトルを生成
    - 指定された言語でサブタイトルを生成
    """
    try:
        subtitle = await subtitle_generator.generate(
            request.primary_keyword,
            request.features,
            request.language
        )

        return response_builder.build_subtitle_response(
            subtitle=subtitle,
            language=request.language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"サブタイトル生成中にエラーが発生しました: {str(e)}"
        )

# 概要生成エンドポイント
@router.post("/generate-description", response_model=DescriptionResponse)
async def generate_description(
    request: DescriptionRequest,
    description_generator: DescriptionGenerator = Depends(),
    response_builder: ResponseBuilder = Depends()
):
    """
    概要 (4,000文字) を生成するエンドポイント

    - 主要キーワードとアプリの特徴から概要を生成
    - 指定された言語で概要を生成
    """
    try:
        description = await description_generator.generate(
            request.primary_keyword,
            request.features,
            request.language
        )

        return response_builder.build_description_response(
            description=description,
            language=request.language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"概要生成中にエラーが発生しました: {str(e)}"
        )

# 最新情報生成エンドポイント
@router.post("/generate-whats-new", response_model=WhatsNewResponse)
async def generate_whats_new(
    request: WhatsNewRequest,
    whats_new_generator: WhatsNewGenerator = Depends(),
    response_builder: ResponseBuilder = Depends()
):
    """
    最新情報 (4,000文字) を生成するエンドポイント

    - アプリの特徴から最新情報を生成
    - 指定された言語で最新情報を生成
    """
    try:
        whats_new = await whats_new_generator.generate(
            request.features,
            request.language
        )

        return response_builder.build_whats_new_response(
            whats_new=whats_new,
            language=request.language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"最新情報生成中にエラーが発生しました: {str(e)}"
        )
```

### 3. 効率的な処理フローの実装

```python
# app/services/individual_text_orchestrator.py
from typing import Dict, Any
from fastapi import UploadFile
from app.services.csv_analyzer import CSVAnalyzer
from app.services.keyword_selector import KeywordSelector
from app.services.keyword_field_generator import KeywordFieldGenerator
from app.services.title_generator import TitleGenerator
from app.services.subtitle_generator import SubtitleGenerator
from app.services.description_generator import DescriptionGenerator
from app.services.whats_new_generator import WhatsNewGenerator

class IndividualTextOrchestrator:
    """
    個別テキスト生成の効率的な処理フローを管理するオーケストレーター
    """

    def __init__(self):
        self.csv_analyzer = CSVAnalyzer()
        self.keyword_selector = KeywordSelector()
        self.keyword_field_generator = KeywordFieldGenerator()
        self.title_generator = TitleGenerator()
        self.subtitle_generator = SubtitleGenerator()
        self.description_generator = DescriptionGenerator()
        self.whats_new_generator = WhatsNewGenerator()

    async def generate_keyword_field(self, csv_file: UploadFile, language: str) -> str:
        """
        キーワードフィールド生成の効率的な処理フロー

        Args:
            csv_file: キーワードCSVファイル
            language: 生成言語

        Returns:
            str: 生成されたキーワードフィールド
        """
        # CSV分析とキーワード選定
        keywords_data = await self.csv_analyzer.analyze_csv(csv_file)
        primary_keyword = self.keyword_selector.select_primary_keyword(keywords_data)

        # キーワードフィールド生成
        return await self.keyword_field_generator.generate(
            keywords_data, primary_keyword, language
        )

    async def generate_title(self, primary_keyword: str, app_name: str, language: str) -> str:
        """
        タイトル生成の効率的な処理フロー

        Args:
            primary_keyword: 主要キーワード
            app_name: アプリ名
            language: 生成言語

        Returns:
            str: 生成されたタイトル
        """
        return await self.title_generator.generate(
            primary_keyword, app_name, language
        )

    async def generate_subtitle(self, primary_keyword: str, features: list, language: str) -> str:
        """
        サブタイトル生成の効率的な処理フロー

        Args:
            primary_keyword: 主要キーワード
            features: アプリの特徴リスト
            language: 生成言語

        Returns:
            str: 生成されたサブタイトル
        """
        return await self.subtitle_generator.generate(
            primary_keyword, features, language
        )

    async def generate_description(self, primary_keyword: str, features: list, language: str) -> str:
        """
        概要生成の効率的な処理フロー

        Args:
            primary_keyword: 主要キーワード
            features: アプリの特徴リスト
            language: 生成言語

        Returns:
            str: 生成された概要
        """
        return await self.description_generator.generate(
            primary_keyword, features, language
        )

    async def generate_whats_new(self, features: list, language: str) -> str:
        """
        最新情報生成の効率的な処理フロー

        Args:
            features: アプリの特徴リスト
            language: 生成言語

        Returns:
            str: 生成された最新情報
        """
        return await self.whats_new_generator.generate(
            features, language
        )
```

### 4. エンドポイントでのオーケストレーター使用

```python
# app/api/v1/aso_endpoints.py
from app.services.individual_text_orchestrator import IndividualTextOrchestrator

# キーワードフィールド生成エンドポイント（オーケストレーター使用版）
@router.post("/generate-keyword-field", response_model=KeywordFieldResponse)
async def generate_keyword_field(
    csv_file: UploadFile = File(...),
    language: str = Form(...),
    orchestrator: IndividualTextOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends()
):
    """キーワードフィールド生成エンドポイント"""
    try:
        keyword_field = await orchestrator.generate_keyword_field(csv_file, language)

        return response_builder.build_keyword_field_response(
            keyword_field=keyword_field,
            language=language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"キーワードフィールド生成中にエラーが発生しました: {str(e)}"
        )

# タイトル生成エンドポイント（オーケストレーター使用版）
@router.post("/generate-title", response_model=TitleResponse)
async def generate_title(
    request: TitleRequest,
    orchestrator: IndividualTextOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends()
):
    """タイトル生成エンドポイント"""
    try:
        title = await orchestrator.generate_title(
            request.primary_keyword,
            request.app_name,
            request.language
        )

        return response_builder.build_title_response(
            title=title,
            language=request.language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"タイトル生成中にエラーが発生しました: {str(e)}"
        )
```

## 実装手順

1. **個別リクエストモデルの作成**

   - `app/models/request_models.py`に各エンドポイント用のリクエストモデルを追加
   - 言語パラメータの検証機能を実装

2. **個別オーケストレーターの実装**

   - `app/services/individual_text_orchestrator.py`を作成
   - 各テキスト生成の効率的な処理フローを実装

3. **個別エンドポイントの実装**

   - `app/api/v1/aso_endpoints.py`に各エンドポイントを追加
   - 適切なリクエスト・レスポンスモデルを指定

4. **エラーハンドリングの実装**
   - 各エンドポイントでの適切なエラーハンドリング
   - 統一されたエラーレスポンス形式

## テスト項目

### 単体テスト

- [ ] 各リクエストモデルのバリデーションテスト
- [ ] 個別オーケストレーターの各メソッドのテスト
- [ ] 言語パラメータの検証テスト

### 統合テスト

- [ ] 各個別エンドポイントの動作テスト
- [ ] 日本語・英語での生成テスト
- [ ] エラーハンドリングのテスト

### パフォーマンステスト

- [ ] 個別エンドポイントの処理時間測定
- [ ] 統合エンドポイントとの性能比較
- [ ] メモリ使用量の確認

## 成功基準

- [ ] 各個別エンドポイントが正常に動作する
- [ ] 日本語・英語の両方で適切なテキストが生成される
- [ ] 効率的な処理フローが実現される
- [ ] エラーハンドリングが適切に機能する
- [ ] レスポンス形式が統一されている

## 技術要件

### 必須技術

- FastAPI
- Pydantic（リクエスト・レスポンスモデル）
- Python-multipart（ファイルアップロード）
- 既存の全サービスクラス

### 設計原則

- 単一責任の原則
- 効率的な処理フロー
- エラーハンドリングの統一
- レスポンス形式の一貫性

## 関連チケット

- **P4-001**: 統合 API エンドポイントの定義と実装
- **P4-002**: 統一された処理フローの構築
- **P4-003**: レスポンス形式の定義と実装
- **P4-005**: 個別エンドポイントの処理フロー最適化
- **P1-001**: CSV データモデルとバリデーション
- **P1-002**: キーワードスコアリング
- **P1-003**: 主要キーワードの自動選定

## 注意事項

- 効率的な処理フローの設計が重要
- 言語パラメータの一貫した引き渡し
- エラーハンドリングの統一性を保つ
- パフォーマンスを考慮した実装
