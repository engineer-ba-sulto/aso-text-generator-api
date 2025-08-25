from typing import List

import pandas as pd

from app.models.csv_models import CSVData, KeywordData
from app.utils.exceptions import CSVValidationError


class CSVValidator:
    """CSV ファイル検証クラス"""

    # 標準形式の必須カラム
    STANDARD_REQUIRED_COLUMNS = ["keyword", "ranking", "popularity", "difficulty"]

    # App Store Connect形式のカラムマッピング
    APP_STORE_CONNECT_COLUMNS = {
        "Keyword": "keyword",
        "Ranking": "ranking",
        "Popularity": "popularity",
        "Difficulty": "difficulty",
    }

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def _detect_csv_format(self, df: pd.DataFrame) -> str:
        """CSVファイルの形式を検出"""
        columns = set(df.columns)

        # 標準形式のチェック
        if set(self.STANDARD_REQUIRED_COLUMNS).issubset(columns):
            return "standard"

        # App Store Connect形式のチェック
        if set(self.APP_STORE_CONNECT_COLUMNS.keys()).issubset(columns):
            return "app_store_connect"

        raise CSVValidationError(
            f"サポートされていないCSV形式です。"
            f"標準形式: {self.STANDARD_REQUIRED_COLUMNS} または "
            f"App Store Connect形式: {list(self.APP_STORE_CONNECT_COLUMNS.keys())}"
        )

    def _normalize_dataframe(self, df: pd.DataFrame, format_type: str) -> pd.DataFrame:
        """データフレームを標準形式に正規化"""
        if format_type == "standard":
            return df

        elif format_type == "app_store_connect":
            # カラム名を標準形式に変換
            df_normalized = df.rename(columns=self.APP_STORE_CONNECT_COLUMNS)

            # 必要なカラムのみを選択
            return df_normalized[self.STANDARD_REQUIRED_COLUMNS]

        return df

    def validate_file_structure(self, df: pd.DataFrame) -> bool:
        """CSV ファイルの構造を検証"""
        # 形式を検出
        format_type = self._detect_csv_format(df)

        # データフレームを正規化
        df_normalized = self._normalize_dataframe(df, format_type)

        # 必須カラムの存在チェック
        missing_columns = set(self.STANDARD_REQUIRED_COLUMNS) - set(
            df_normalized.columns
        )
        if missing_columns:
            raise CSVValidationError(f"必須カラムが不足しています: {missing_columns}")

        # データ型チェック（より柔軟に）
        try:
            # keywordカラムを文字列に変換
            df_normalized["keyword"] = df_normalized["keyword"].astype(str)

            # rankingカラムを数値に変換
            df_normalized["ranking"] = pd.to_numeric(
                df_normalized["ranking"], errors="coerce"
            )

            # popularityカラムを数値に変換
            df_normalized["popularity"] = pd.to_numeric(
                df_normalized["popularity"], errors="coerce"
            )

            # difficultyカラムを数値に変換
            df_normalized["difficulty"] = pd.to_numeric(
                df_normalized["difficulty"], errors="coerce"
            )

            # NaN値がある場合はエラー
            if df_normalized["ranking"].isna().any():
                raise CSVValidationError("ranking カラムに無効な数値が含まれています")
            if df_normalized["popularity"].isna().any():
                raise CSVValidationError(
                    "popularity カラムに無効な数値が含まれています"
                )
            if df_normalized["difficulty"].isna().any():
                raise CSVValidationError(
                    "difficulty カラムに無効な数値が含まれています"
                )

        except Exception as e:
            raise CSVValidationError(f"データ型の変換に失敗しました: {str(e)}")

        return True

    def validate_data_ranges(self, df: pd.DataFrame) -> bool:
        """データの値範囲を検証"""
        # 形式を検出して正規化
        format_type = self._detect_csv_format(df)
        df_normalized = self._normalize_dataframe(df, format_type)

        # ランキング範囲チェック（1-1000）
        if (
            not (df_normalized["ranking"] >= 1).all()
            or not (df_normalized["ranking"] <= 1000).all()
        ):
            raise CSVValidationError("ranking は 1-1000 の範囲である必要があります")

        # 人気度範囲チェック（0-100）
        if (
            not (df_normalized["popularity"] >= 0).all()
            or not (df_normalized["popularity"] <= 100).all()
        ):
            raise CSVValidationError("popularity は 0-100 の範囲である必要があります")

        # 難易度範囲チェック（0-100）
        if (
            not (df_normalized["difficulty"] >= 0).all()
            or not (df_normalized["difficulty"] <= 100).all()
        ):
            raise CSVValidationError("difficulty は 0-100 の範囲である必要があります")

        return True

    def load_and_validate_csv(self, file_path: str) -> CSVData:
        """CSV ファイルを読み込み、検証してデータモデルに変換"""
        try:
            df = pd.read_csv(file_path)

            # 構造検証
            self.validate_file_structure(df)

            # 値範囲検証
            self.validate_data_ranges(df)

            # 形式を検出して正規化
            format_type = self._detect_csv_format(df)
            df_normalized = self._normalize_dataframe(df, format_type)

            # データ型を確実に変換
            df_normalized["keyword"] = df_normalized["keyword"].astype(str)
            df_normalized["ranking"] = pd.to_numeric(
                df_normalized["ranking"], errors="coerce"
            ).astype(int)
            df_normalized["popularity"] = pd.to_numeric(
                df_normalized["popularity"], errors="coerce"
            ).astype(float)
            df_normalized["difficulty"] = pd.to_numeric(
                df_normalized["difficulty"], errors="coerce"
            ).astype(float)

            # データモデルに変換
            keywords = []
            for _, row in df_normalized.iterrows():
                keyword_data = KeywordData(
                    keyword=row["keyword"],
                    ranking=int(row["ranking"]),
                    popularity=float(row["popularity"]),
                    difficulty=float(row["difficulty"]),
                )
                keywords.append(keyword_data)

            return CSVData(keywords=keywords)

        except pd.errors.EmptyDataError:
            raise CSVValidationError("CSV ファイルが空です")
        except pd.errors.ParserError:
            raise CSVValidationError("CSV ファイルの形式が不正です")
