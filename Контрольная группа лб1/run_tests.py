import subprocess
import time
import os
import json
import csv
from datetime import datetime

# Создаем папку для результатов
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

FRAMEWORKS = {
    'flask': {
        'start': 'gunicorn --workers=1 --bind 127.0.0.1:5000 flask_app:app',
        'port': 5000,
        'name': 'Flask'
    },
    'sanic': {
        'start': 'sanic sanic_app:app --host=127.0.0.1 --port=8000 --workers=1 --access-log=False',
        'port': 8000,
        'name': 'Sanic'
    },
    'quart': {
        'start': 'hypercorn quart_app:app --bind 127.0.0.1:8001 --workers=1',
        'port': 8001,
        'name': 'Quart'
    }
}

USERS = [50, 100, 200]
RUN_TIME = '20s'

processes = []

def start_server(framework):
    print(f"[START] {FRAMEWORKS[framework]['name']}")
    proc = subprocess.Popen(FRAMEWORKS[framework]['start'], shell=True, 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    processes.append(proc)
    time.sleep(3)
    return proc

def stop_all_servers():
    for proc in processes:
        proc.terminate()
        time.sleep(1)
        if proc.poll() is None:
            proc.kill()
    processes.clear()

def run_test(framework, port, users):
    output = os.path.join(RESULTS_DIR, f"result_{framework}_{users}")
    
    cmd = f'python3 -m locust -f locustfile.py --host=http://127.0.0.1:{port} --headless -u {users} -r {users//2} --run-time {RUN_TIME} --csv={output}'
    
    print(f"  [TEST] {users} users")
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    stats_file = f"{output}_stats.csv"
    results = {}
    
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'cpu' in row.get('Name', row.get('Type', '')):
                    rps = float(row.get('Requests/s', 0)) if row.get('Requests/s', '') else 0
                    avg_latency = float(row.get('Average Response Time', 0)) if row.get('Average Response Time', '') else 0
                    p95 = float(row.get('95%', 0)) if row.get('95%', '') else 0
                    errors = float(row.get('Failure Rate', 0)) if row.get('Failure Rate', '') else 0
                    
                    results[row['Name']] = {
                        'rps': rps,
                        'avg_latency': avg_latency,
                        'p95': p95,
                        'errors': errors
                    }
    
    return results

def main():
    print("="*60)
    print("BENCHMARK START")
    print(f"Results will be saved to: {RESULTS_DIR}/")
    print("="*60)
    
    all_results = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'run_time': RUN_TIME,
            'users': USERS,
            'frameworks': list(FRAMEWORKS.keys())
        }
    }
    
    for framework in FRAMEWORKS:
        print(f"\n--- {FRAMEWORKS[framework]['name']} ---")
        start_server(framework)
        
        framework_results = {}
        for users in USERS:
            results = run_test(framework, FRAMEWORKS[framework]['port'], users)
            if results:
                framework_results[str(users)] = results
            time.sleep(2)
        
        all_results[framework] = framework_results
        stop_all_servers()
        time.sleep(3)
    
    # Сохраняем JSON
    json_file = os.path.join(RESULTS_DIR, 'benchmark_results.json')
    with open(json_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Выводим таблицу
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    
    for framework, users_data in all_results.items():
        if framework == 'metadata':
            continue
        print(f"\n{FRAMEWORKS[framework]['name'].upper()}")
        print("-"*70)
        
        for users, endpoints in users_data.items():
            print(f"\n  {users} users:")
            print(f"  {'Endpoint':<15} {'RPS':<10} {'Avg(ms)':<12} {'p95(ms)':<12} {'Errors(%)':<10}")
            print(f"  {'-'*60}")
            
            for endpoint, metrics in endpoints.items():
                print(f"  {endpoint:<15} {metrics['rps']:<10.1f} {metrics['avg_latency']:<12.1f} "
                      f"{metrics['p95']:<12.1f} {metrics['errors']:<10.2f}")
    
    print("\n" + "="*60)
    print("BENCHMARK COMPLETE")
    print(f"Results saved to: {RESULTS_DIR}/")
    print(f"  - JSON: {json_file}")
    print(f"  - CSV files: {RESULTS_DIR}/result_*.csv")
    print("="*60)

if __name__ == '__main__':
    main()
