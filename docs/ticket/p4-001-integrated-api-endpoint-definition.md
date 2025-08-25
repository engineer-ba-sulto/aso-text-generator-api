# P4-001: 統合APIエンドポイントの定義と実装

## 概要

統合APIエンドポイント `POST /api/v1/generate-aso-texts` を実装し、1つのリクエストで全ASOテキスト項目（キーワードフィールド、タイトル、サブタイトル、概要、最新情報）を生成する機能を提供します。

## 目標

- 統合APIエンドポイントの実装
- 多言語対応（日本語・英語）の言語指定機能
- 統一されたリクエスト・レスポンス形式の定義
- 既存サービスクラスとの統合

## 実装内容

### 1. リクエストモデルの定義

```python
# app/models/request_models.py
class ASOTextGenerationRequest(BaseModel):
    csv_file: UploadFile
    app_name: str
    features: List[str]
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")
    
    @validator('language')
    def validate_language(cls, v):
        if v not in ['ja', 'en']:
            raise ValueError('language must be either "ja" or "en"')
        return v
```

### 2. レスポンスモデルの定義

```python
# app/models/response_models.py
class ASOTextGenerationResponse(BaseModel):
    keyword_field: str = Field(..., description="キーワードフィールド (100文字)")
    title: str = Field(..., description="タイトル (30文字)")
    subtitle: str = Field(..., description="サブタイトル (30文字)")
    description: str = Field(..., description="概要 (4000文字)")
    whats_new: str = Field(..., description="最新情報 (4000文字)")
    language: str = Field(..., description="生成された言語")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3. 統合エンドポイントの実装

```python
# app/api/v1/aso_endpoints.py
@router.post("/generate-aso-texts", response_model=ASOTextGenerationResponse)
async def generate_aso_texts(
    request: ASOTextGenerationRequest,
    csv_analyzer: CSVAnalyzer = Depends(),
    keyword_selector: KeywordSelector = Depends(),
    keyword_field_generator: KeywordFieldGenerator = Depends(),
    title_generator: TitleGenerator = Depends(),
    subtitle_generator: SubtitleGenerator = Depends(),
    description_generator: DescriptionGenerator = Depends(),
    whats_new_generator: WhatsNewGenerator = Depends()
):
    """
    ASOテキストを一括生成するエンドポイント
    
    - CSVファイルからキーワード分析を実行
    - 主要キーワードを自動選定
    - 指定された言語で全テキスト項目を生成
    """
    try:
        # 1. CSV分析とキーワード選定
        keywords_data = await csv_analyzer.analyze_csv(request.csv_file)
        primary_keyword = keyword_selector.select_primary_keyword(keywords_data)
        
        # 2. 各テキスト項目の生成（言語パラメータを引き渡し）
        keyword_field = await keyword_field_generator.generate(
            keywords_data, primary_keyword, request.language
        )
        title = await title_generator.generate(
            primary_keyword, request.app_name, request.language
        )
        subtitle = await subtitle_generator.generate(
            primary_keyword, request.features, request.language
        )
        description = await description_generator.generate(
            primary_keyword, request.features, request.language
        )
        whats_new = await whats_new_generator.generate(
            request.features, request.language
        )
        
        # 3. レスポンスの構築
        return ASOTextGenerationResponse(
            keyword_field=keyword_field,
            title=title,
            subtitle=subtitle,
            description=description,
            whats_new=whats_new,
            language=request.language
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"テキスト生成中にエラーが発生しました: {str(e)}"
        )
```

### 4. 依存性注入の設定

```python
# app/main.py
from app.services.csv_analyzer import CSVAnalyzer
from app.services.keyword_selector import KeywordSelector
from app.services.keyword_field_generator import KeywordFieldGenerator
from app.services.title_generator import TitleGenerator
from app.services.subtitle_generator import SubtitleGenerator
from app.services.description_generator import DescriptionGenerator
from app.services.whats_new_generator import WhatsNewGenerator

# 依存性注入の設定
def get_csv_analyzer():
    return CSVAnalyzer()

def get_keyword_selector():
    return KeywordSelector()

def get_keyword_field_generator():
    return KeywordFieldGenerator()

def get_title_generator():
    return TitleGenerator()

def get_subtitle_generator():
    return SubtitleGenerator()

def get_description_generator():
    return DescriptionGenerator()

def get_whats_new_generator():
    return WhatsNewGenerator()
```

## 実装手順

1. **リクエスト・レスポンスモデルの作成**
   - `app/models/request_models.py`に`ASOTextGenerationRequest`を追加
   - `app/models/response_models.py`に`ASOTextGenerationResponse`を追加

2. **統合エンドポイントの実装**
   - `app/api/v1/aso_endpoints.py`に統合エンドポイントを追加
   - 依存性注入の設定を追加

3. **既存サービスクラスの確認**
   - 各サービスクラスが`language`パラメータを受け取れることを確認
   - 必要に応じて既存サービスクラスを修正

4. **エラーハンドリングの実装**
   - 適切なエラーレスポンスの定義
   - 例外処理の実装

## テスト項目

### 単体テスト
- [ ] リクエストモデルのバリデーションテスト
- [ ] レスポンスモデルのシリアライゼーションテスト
- [ ] 言語パラメータの検証テスト

### 統合テスト
- [ ] 日本語での全テキスト生成テスト
- [ ] 英語での全テキスト生成テスト
- [ ] 無効な言語パラメータのエラーハンドリングテスト
- [ ] CSVファイルエラーのハンドリングテスト

### パフォーマンステスト
- [ ] 全テキスト生成の実行時間測定
- [ ] メモリ使用量の確認

## 成功基準

- [ ] 統合エンドポイントが正常に動作する
- [ ] 日本語・英語の両方で適切なテキストが生成される
- [ ] エラーハンドリングが適切に機能する
- [ ] レスポンス形式が仕様通りである
- [ ] パフォーマンスが要件を満たしている

## 技術要件

### 必須技術
- FastAPI
- Pydantic
- Python-multipart（ファイルアップロード）
- 既存の全サービスクラス

### 設計原則
- 単一責任の原則
- 依存性注入
- エラーハンドリングの統一
- レスポンス形式の一貫性

## 関連チケット

- **P4-002**: 統一された処理フローの構築
- **P4-003**: レスポンス形式の定義と実装
- **P1-001**: CSVデータモデルとバリデーション
- **P1-002**: キーワードスコアリング
- **P1-003**: 主要キーワードの自動選定
- **P2-001**: キーワードフィールド生成
- **P2-002**: タイトル生成
- **P2-003**: 最新情報生成
- **P3-001**: Geminiサービスクラス実装
- **P3-002**: 多言語プロンプト管理
- **P3-003**: サブタイトル生成
- **P3-004**: 概要生成

## 注意事項

- 言語パラメータの一貫した引き渡しが重要
- 既存サービスクラスの修正が必要な場合は慎重に行う
- エラーハンドリングの統一性を保つ
- パフォーマンスを考慮した実装を行う
