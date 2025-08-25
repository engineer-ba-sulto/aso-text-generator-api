### チケット: P3-001 Gemini サービスクラスの実装

#### 背景 / 目的

- **背景**: 既存の`gemini_generator.py`は基本的なクラス構造のみで、実際の Gemini API 連携機能が未実装
- **目的**: Google Gemini API を活用したテキスト生成サービスクラスを完全実装し、多言語対応とエラーハンドリングを備えた堅牢なシステムを構築する

#### スコープ（このチケットでやること）

1. **Gemini API 連携の実装**

   - `google-genai`ライブラリを使用した API 連携
   - API キー管理と環境変数からの読み込み
   - モデル選択（Gemini Pro）の実装

2. **多言語対応メソッドの実装**

   - `generate_subtitle()`: サブタイトル生成（30 文字制限）
   - `generate_description()`: 概要生成（4000 文字制限）
   - 各メソッドが`language`パラメータを受け取る設計

3. **エラーハンドリングとリトライ機能**

   - API 呼び出しエラーの適切な処理
   - レート制限への対応
   - 自動リトライ機能（最大 3 回）
   - タイムアウト設定（30 秒）

4. **テキスト最適化機能**
   - 文字数制限の自動調整
   - 品質チェック機能
   - 不適切なコンテンツのフィルタリング

#### やらないこと（Out of Scope）

- プロンプトテンプレートの定義（P3-002 で対応）
- サブタイトル・概要生成の具体的なロジック（P3-003, P3-004 で対応）
- API エンドポイントの統合（ステップ 4 で対応）

#### 受入条件（Acceptance Criteria）

- Gemini API が正常に連携し、テキスト生成が動作すること
- 日本語・英語の両方で適切に API 呼び出しができること
- エラーハンドリングが適切に動作し、適切なエラーメッセージが返されること
- レート制限時に自動リトライが機能すること
- 文字数制限が正しく適用されること
- 単体テストが実装され、カバレッジが 90%以上であること
- 環境変数からの API キー読み込みが正常に動作すること

#### 技術仕様

**クラス構造:**

```python
class GeminiGenerator:
    def __init__(self, api_key: str = None)
    def generate_subtitle(self, prompt: str, language: str = "ja") -> str
    def generate_description(self, prompt: str, language: str = "ja") -> str
    def _call_gemini_api(self, prompt: str, max_tokens: int = 1000) -> str
    def _retry_with_backoff(self, func, max_retries: int = 3) -> Any
    def _validate_text_length(self, text: str, max_length: int) -> str
```

**設定項目:**

- API キー: 環境変数`GOOGLE_API_KEY`から読み込み
- モデル: `gemini-pro`
- タイムアウト: 30 秒
- 最大リトライ回数: 3 回
- バックオフ間隔: 1 秒、2 秒、4 秒

#### 影響/変更ファイル

- 変更:
  - `app/services/gemini_generator.py` (完全実装)
  - `app/config.py` (Gemini API 設定の追加)
- 追加:
  - `tests/test_gemini_generator.py` (単体テスト)
  - `.env.example` (Gemini API キー設定例)

#### 依存関係 / ブロッカー

- **依存**: `google-genai`ライブラリのインストール
- **ブロッカー**: Google AI (Gemini) API キーの取得
- **後続**: P3-002（多言語プロンプト管理）は本チケットの完了に依存

#### 実装手順

1. **環境設定**

   - `requirements.txt`に`google-genai`を追加
   - `.env`ファイルに Gemini API キー設定を追加
   - `app/config.py`に Gemini 設定を追加

2. **Gemini API 連携実装**

   - `google-genai`ライブラリを使用した API 呼び出し
   - モデル初期化と設定
   - 基本的なテキスト生成機能

3. **多言語対応メソッド実装**

   - `generate_subtitle()`メソッドの実装
   - `generate_description()`メソッドの実装
   - 言語パラメータの処理

4. **エラーハンドリング実装**

   - API 呼び出しエラーの処理
   - リトライ機能の実装
   - タイムアウト処理

5. **テキスト最適化機能実装**

   - 文字数制限の適用
   - 品質チェック機能
   - フィルタリング機能

6. **テスト実装**
   - 単体テストの作成
   - モックを使用した API 呼び出しテスト
   - エラーケースのテスト

#### 参考資料

- [Google GenAI Python SDK](https://ai.google.dev/tutorials/python_quickstart)
- [Gemini API リファレンス](https://ai.google.dev/api/gemini-api)
- [Gemini Pro モデル仕様](https://ai.google.dev/models/gemini)

#### リスク / 留意点

- **API キー管理**: セキュアな API キー管理の実装
- **レート制限**: Gemini API の利用制限への適切な対応
- **コスト管理**: API 呼び出しコストの監視と制御
- **品質保証**: 生成テキストの品質と一貫性の確保
- **エラー処理**: API 障害時の適切なフォールバック

#### 見積り

- **4 時間**
  - 環境設定: 30 分
  - Gemini API 連携実装: 1.5 時間
  - 多言語対応メソッド実装: 1 時間
  - エラーハンドリング実装: 45 分
  - テスト実装: 45 分

#### 完了定義

- [ ] Gemini API 連携が正常に動作する
- [ ] 多言語対応メソッドが実装されている
- [ ] エラーハンドリングが適切に動作する
- [ ] 単体テストが実装され、カバレッジが 90%以上である
- [ ] ドキュメントが更新されている
