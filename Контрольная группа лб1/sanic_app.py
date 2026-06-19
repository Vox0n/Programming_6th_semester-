from sanic import Sanic, json
import asyncio
import time

app = Sanic("Benchmark")

def cpu_intensive_task():
    total = 0
    for i in range(15_000_000):
        total += i
    return total

@app.route('/cpu')
async def cpu(request):
    start = time.time()
    # BLOCKING - bad for async
    result = cpu_intensive_task()
    elapsed = time.time() - start
    return json({
        "result": result,
        "execution_time": elapsed,
        "mode": "blocking"
    })

@app.route('/cpu_fixed')
async def cpu_fixed(request):
    start = time.time()
    # NON-BLOCKING - good
    result = await asyncio.to_thread(cpu_intensive_task)
    elapsed = time.time() - start
    return json({
        "result": result,
        "execution_time": elapsed,
        "mode": "non-blocking"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=1, access_log=False)