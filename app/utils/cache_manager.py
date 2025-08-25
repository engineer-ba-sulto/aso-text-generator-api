import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import json

class CacheManager:
    """
    個別エンドポイント用のキャッシュマネージャー
    """
    
    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl_hours = ttl_hours
        self._lock = asyncio.Lock()
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """
        キャッシュキーを生成
        
        Args:
            *args: 位置引数
            **kwargs: キーワード引数
            
        Returns:
            str: キャッシュキー
        """
        # 引数をJSON文字列に変換
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        
        # SHA256ハッシュを生成
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """
        キャッシュから値を取得
        
        Args:
            key: キャッシュキー
            
        Returns:
            Optional[Any]: キャッシュされた値（存在しない場合はNone）
        """
        async with self._lock:
            if key in self.cache:
                cache_entry = self.cache[key]
                
                # TTLチェック
                if datetime.now() < cache_entry['expires_at']:
                    return cache_entry['value']
                else:
                    # 期限切れの場合は削除
                    del self.cache[key]
            
            return None
    
    async def set(self, key: str, value: Any) -> None:
        """
        キャッシュに値を保存
        
        Args:
            key: キャッシュキー
            value: 保存する値
        """
        async with self._lock:
            # キャッシュサイズ制限チェック
            if len(self.cache) >= self.max_size:
                # 最も古いエントリを削除
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k]['created_at']
                )
                del self.cache[oldest_key]
            
            # 新しいエントリを追加
            self.cache[key] = {
                'value': value,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=self.ttl_hours)
            }
    
    async def invalidate_pattern(self, pattern: str) -> None:
        """
        パターンに一致するキャッシュエントリを削除
        
        Args:
            pattern: 削除するパターン
        """
        async with self._lock:
            keys_to_delete = [
                key for key in self.cache.keys()
                if pattern in key
            ]
            for key in keys_to_delete:
                del self.cache[key]
    
    async def clear(self) -> None:
        """キャッシュをクリア"""
        async with self._lock:
            self.cache.clear()
