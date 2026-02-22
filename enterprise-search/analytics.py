"""
搜索分析模块
记录和分析搜索行为
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter


@dataclass
class SearchLog:
    """搜索日志"""

    query: str
    timestamp: datetime
    result_count: int
    latency_ms: float
    expanded_terms: List[str] = field(default_factory=list)


class SearchAnalytics:
    """搜索分析器"""

    def __init__(self):
        self.logs: List[SearchLog] = []
        self.query_counter: Counter = Counter()

    def log_search(
        self,
        query: str,
        result_count: int,
        latency_ms: float,
        expanded_terms: List[str] = None,
    ):
        """记录搜索"""
        log = SearchLog(
            query=query,
            timestamp=datetime.now(),
            result_count=result_count,
            latency_ms=latency_ms,
            expanded_terms=expanded_terms or [],
        )
        self.logs.append(log)
        self.query_counter[query] += 1

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.logs:
            return {
                "total_searches": 0,
                "avg_latency_ms": 0,
                "avg_results": 0,
            }

        return {
            "total_searches": len(self.logs),
            "avg_latency_ms": sum(log.latency_ms for log in self.logs) / len(self.logs),
            "avg_results": sum(log.result_count for log in self.logs) / len(self.logs),
            "unique_queries": len(self.query_counter),
        }

    def get_top_queries(self, n: int = 10) -> List[tuple]:
        """获取热门查询"""
        return self.query_counter.most_common(n)

    def get_recent_searches(self, n: int = 10) -> List[SearchLog]:
        """获取最近搜索"""
        return self.logs[-n:][::-1]

    def get_zero_result_queries(self) -> List[str]:
        """获取无结果的查询"""
        return [log.query for log in self.logs if log.result_count == 0]

    def get_slow_queries(self, threshold_ms: float = 2000) -> List[SearchLog]:
        """获取慢查询"""
        return [log for log in self.logs if log.latency_ms > threshold_ms]

    def format_stats(self) -> str:
        """格式化统计信息"""
        stats = self.get_stats()
        return f"""
📊 搜索统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总搜索次数: {stats["total_searches"]}
唯一查询数: {stats.get("unique_queries", 0)}
平均延迟: {stats["avg_latency_ms"]:.1f}ms
平均结果数: {stats["avg_results"]:.1f}
"""
