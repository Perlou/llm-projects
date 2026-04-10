"""
性能测试脚本
"""

import argparse
import asyncio
import time
import statistics
from typing import List

import httpx
from rich.console import Console
from rich.table import Table
from rich.progress import Progress


console = Console()


async def send_request(
    client: httpx.AsyncClient,
    url: str,
    message: str,
) -> dict:
    """发送单个请求"""
    start_time = time.time()

    try:
        response = await client.post(
            f"{url}/v1/chat/completions",
            json={
                "model": "default",
                "messages": [{"role": "user", "content": message}],
                "max_tokens": 100,
                "stream": False,
            },
            timeout=60.0,
        )

        latency = (time.time() - start_time) * 1000
        success = response.status_code == 200

        return {
            "success": success,
            "latency_ms": latency,
            "status_code": response.status_code,
        }

    except Exception as e:
        return {
            "success": False,
            "latency_ms": (time.time() - start_time) * 1000,
            "error": str(e),
        }


async def run_benchmark(
    url: str,
    num_requests: int,
    concurrency: int,
    message: str,
) -> List[dict]:
    """运行压测"""
    results = []
    semaphore = asyncio.Semaphore(concurrency)

    async def limited_request(client, i):
        async with semaphore:
            return await send_request(client, url, message)

    async with httpx.AsyncClient() as client:
        with Progress() as progress:
            task = progress.add_task("发送请求...", total=num_requests)

            tasks = []
            for i in range(num_requests):
                tasks.append(limited_request(client, i))

            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                progress.advance(task)

    return results


def analyze_results(results: List[dict]) -> dict:
    """分析测试结果"""
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    latencies = [r["latency_ms"] for r in successful]

    analysis = {
        "total_requests": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "success_rate": len(successful) / len(results) * 100 if results else 0,
    }

    if latencies:
        analysis.update(
            {
                "avg_latency_ms": statistics.mean(latencies),
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies),
                "p50_latency_ms": statistics.median(latencies),
                "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)]
                if len(latencies) > 1
                else latencies[0],
                "p99_latency_ms": sorted(latencies)[int(len(latencies) * 0.99)]
                if len(latencies) > 1
                else latencies[0],
            }
        )

    return analysis


def main():
    parser = argparse.ArgumentParser(description="API 性能测试")
    parser.add_argument("--url", "-u", default="http://localhost:8000", help="服务 URL")
    parser.add_argument("--requests", "-n", type=int, default=10, help="请求数量")
    parser.add_argument("--concurrency", "-c", type=int, default=5, help="并发数")
    parser.add_argument("--message", "-m", default="Hello", help="测试消息")

    args = parser.parse_args()

    console.print("\n[bold blue]🔧 API 性能测试[/bold blue]\n")
    console.print(f"目标: {args.url}")
    console.print(f"请求数: {args.requests}")
    console.print(f"并发数: {args.concurrency}")
    console.print()

    # 运行测试
    results = asyncio.run(
        run_benchmark(args.url, args.requests, args.concurrency, args.message)
    )

    # 分析结果
    analysis = analyze_results(results)

    # 显示结果
    table = Table(title="测试结果")
    table.add_column("指标", style="cyan")
    table.add_column("值", style="green")

    table.add_row("总请求数", str(analysis["total_requests"]))
    table.add_row("成功", str(analysis["successful"]))
    table.add_row("失败", str(analysis["failed"]))
    table.add_row("成功率", f"{analysis['success_rate']:.1f}%")

    if "avg_latency_ms" in analysis:
        table.add_row("平均延迟", f"{analysis['avg_latency_ms']:.1f} ms")
        table.add_row("最小延迟", f"{analysis['min_latency_ms']:.1f} ms")
        table.add_row("最大延迟", f"{analysis['max_latency_ms']:.1f} ms")
        table.add_row("P50 延迟", f"{analysis['p50_latency_ms']:.1f} ms")
        table.add_row("P95 延迟", f"{analysis['p95_latency_ms']:.1f} ms")
        table.add_row("P99 延迟", f"{analysis['p99_latency_ms']:.1f} ms")

    console.print()
    console.print(table)


if __name__ == "__main__":
    main()
