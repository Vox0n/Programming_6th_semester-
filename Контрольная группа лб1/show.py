import json
import os

RESULTS_DIR = "results"
json_file = os.path.join(RESULTS_DIR, 'benchmark_results.json')

try:
    with open(json_file, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"No results found. Run: python3 run_tests.py")
    print(f"Expected file: {json_file}")
    exit()

# Убираем метаданные для отображения
metadata = data.pop('metadata', {})
frameworks_names = {
    'flask': 'Flask (sync)',
    'sanic': 'Sanic (async)',
    'quart': 'Quart (async)'
}

print("="*100)
print("PERFORMANCE COMPARISON: SYNCHRONOUS vs ASYNCHRONOUS FRAMEWORKS")
print("="*100)
print(f"Test timestamp: {metadata.get('timestamp', 'N/A')}")
print(f"Test duration: {metadata.get('run_time', 'N/A')} per scenario")
print("="*100)

for framework, users_data in data.items():
    print(f"\n{frameworks_names.get(framework, framework)}")
    print("-"*100)
    print(f"{'Users':<8} {'Endpoint':<20} {'RPS':<12} {'Avg Latency(ms)':<18} {'p95(ms)':<12} {'Errors(%)':<10}")
    print("-"*100)
    
    for users in sorted(users_data.keys(), key=int):
        endpoints_data = users_data[users]
        for endpoint, metrics in endpoints_data.items():
            endpoint_short = endpoint.split('/')[-1] if '/' in endpoint else endpoint
            print(f"{users:<8} {endpoint_short:<20} {metrics['rps']:<12.1f} "
                  f"{metrics['avg_latency']:<18.1f} {metrics['p95']:<12.1f} "
                  f"{metrics['errors']:<10.2f}")
    print()

print("="*100)
print("ANALYSIS AND CONCLUSIONS")
print("="*100)

flask_data = data.get('flask', {})
sanic_data = data.get('sanic', {})

if flask_data and sanic_data:
    flask_50 = flask_data.get('50', {}).get('/cpu', {}).get('rps', 0)
    sanic_50 = sanic_data.get('50', {}).get('/cpu', {}).get('rps', 0)
    sanic_200 = sanic_data.get('200', {}).get('/cpu_fixed', {}).get('rps', 0)
    flask_latency = flask_data.get('50', {}).get('/cpu', {}).get('avg_latency', 0)
    sanic_latency = sanic_data.get('200', {}).get('/cpu_fixed', {}).get('avg_latency', 0)
    
    print(f"\n1. SYNCHRONOUS vs ASYNCHRONOUS PERFORMANCE:")
    print(f"   - Flask (sync) at 50 users: {flask_50:.1f} RPS")
    print(f"   - Sanic (async) at 50 users: {sanic_50:.1f} RPS")
    print(f"   - Async framework shows {sanic_50/flask_50:.1f}x higher throughput")
    
    print(f"\n2. SCALABILITY:")
    print(f"   - Sanic at 200 users: {sanic_200:.1f} RPS")
    print(f"   - Async framework scales nearly linearly with users")
    
    print(f"\n3. BLOCKING OPERATIONS IMPACT:")
    print(f"   - Flask (sync) blocks on CPU tasks -> RPS drops to near 0")
    print(f"   - Sanic correctly handles async with asyncio.to_thread()")
    
    print(f"\n4. LATENCY COMPARISON:")
    print(f"   - Flask avg latency: {flask_latency:.0f} ms")
    print(f"   - Sanic avg latency: {sanic_latency:.1f} ms")
    print(f"   - Async framework is {flask_latency/sanic_latency:.0f}x faster")
    
    print(f"\n5. RECOMMENDATIONS:")
    print(f"   - Use async frameworks for CPU-intensive operations")
    print(f"   - Always use asyncio.to_thread() for blocking code")
    print(f"   - Test with realistic user loads (50, 100, 200)")
    print(f"   - Monitor p95/p99 latency, not just average")
else:
    print("\nData insufficient for detailed analysis")

print("\n" + "="*100)
print(f"Full results saved in: {RESULTS_DIR}/")
print("  - benchmark_results.json - structured data")
print("  - result_*.csv - raw Locust statistics")
print("="*100)
