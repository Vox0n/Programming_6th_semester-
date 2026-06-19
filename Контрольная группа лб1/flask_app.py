from flask import Flask, jsonify
import time

app = Flask(__name__)

def cpu_intensive_task():
    total = 0
    for i in range(5_000_000):  # уменьшено с 15 до 5 млн
        total += i
    return total

@app.route('/cpu')
def cpu():
    start = time.time()
    result = cpu_intensive_task()
    elapsed = time.time() - start
    return jsonify({
        "result": result,
        "execution_time": elapsed,
        "mode": "blocking"
    })

@app.route('/cpu_fixed')
def cpu_fixed():
    return jsonify({
        "error": "sync framework cannot do non-blocking CPU task"
    }), 501

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=False, processes=1)
EOF

cat > sanic_app.py << 'EOF'
from sanic import Sanic, json
import asyncio
import time

app = Sanic("Benchmark")

def cpu_intensive_task():
    total = 0
    for i in range(5_000_000):
        total += i
    return total

@app.route('/cpu')
async def cpu(request):
    start = time.time()
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
    result = await asyncio.to_thread(cpu_intensive_task)
    elapsed = time.time() - start
    return json({
        "result": result,
        "execution_time": elapsed,
        "mode": "non-blocking"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=1, access_log=False)
EOF

cat > quart_app.py << 'EOF'
from quart import Quart, jsonify
import asyncio
import time

app = Quart(__name__)

def cpu_intensive_task():
    total = 0
    for i in range(5_000_000):
        total += i
    return total

@app.route('/cpu')
async def cpu():
    start = time.time()
    result = cpu_intensive_task()
    elapsed = time.time() - start
    return jsonify({
        "result": result,
        "execution_time": elapsed,
        "mode": "blocking"
    })

@app.route('/cpu_fixed')
async def cpu_fixed():
    start = time.time()
    result = await asyncio.to_thread(cpu_intensive_task)
    elapsed = time.time() - start
    return jsonify({
        "result": result,
        "execution_time": elapsed,
        "mode": "non-blocking"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, workers=1)
