import asyncio
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
import psutil
import gc

class ResourceManager:
    """
    リソース使用量を監視・管理するマネージャー
    """
    
    def __init__(self):
        self.memory_threshold = 0.8  # 80%のメモリ使用率で警告
        self.cpu_threshold = 0.9     # 90%のCPU使用率で警告
    
    def get_memory_usage(self) -> float:
        """
        現在のメモリ使用率を取得
        
        Returns:
            float: メモリ使用率（0.0-1.0）
        """
        return psutil.virtual_memory().percent / 100.0
    
    def get_cpu_usage(self) -> float:
        """
        現在のCPU使用率を取得
        
        Returns:
            float: CPU使用率（0.0-1.0）
        """
        return psutil.cpu_percent(interval=0.1) / 100.0
    
    def check_resource_limits(self) -> Dict[str, Any]:
        """
        リソース制限をチェック
        
        Returns:
            Dict[str, Any]: リソース使用状況
        """
        memory_usage = self.get_memory_usage()
        cpu_usage = self.get_cpu_usage()
        
        return {
            'memory_usage': memory_usage,
            'cpu_usage': cpu_usage,
            'memory_warning': memory_usage > self.memory_threshold,
            'cpu_warning': cpu_usage > self.cpu_threshold,
            'overloaded': memory_usage > self.memory_threshold or cpu_usage > self.cpu_threshold
        }
    
    async def optimize_memory(self) -> None:
        """
        メモリ使用量を最適化
        """
        # ガベージコレクションを実行
        gc.collect()
        
        # 少し待機してメモリ解放を待つ
        await asyncio.sleep(0.1)
    
    @asynccontextmanager
    async def resource_monitor(self):
        """
        リソース監視のコンテキストマネージャー
        """
        try:
            yield
        finally:
            # 処理完了後にメモリ最適化を実行
            await self.optimize_memory()
