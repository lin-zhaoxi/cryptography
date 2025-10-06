from flask import Flask, request, jsonify, send_from_directory
import os
import sdes
import brute_force

app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')


@app.route('/api/encrypt', methods=['POST'])
def api_encrypt():
    data = request.get_json(force=True)
    mode = data.get('mode', 'binary')
    key = data.get('key', '')
    text = data.get('text', '')

    if not key or len(key) != 10 or any(c not in '01' for c in key):
        return jsonify({'error': '密钥必须是10位二进制'}), 400

    try:
        if mode == 'binary':
            bits = ''.join(text.split())
            if not bits or len(bits) % 8 != 0 or any(c not in '01' for c in bits):
                return jsonify({'error': '二进制输入需为8的倍数，且仅含0/1'}), 400
            out_blocks = []
            for i in range(0, len(bits), 8):
                out_blocks.append(sdes.encrypt(bits[i:i+8], key))
            return jsonify({'result': ' '.join(out_blocks)})
        else:
            # ascii
            cipher = sdes.encrypt_text(text, key)
            return jsonify({'result': cipher})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/decrypt', methods=['POST'])
def api_decrypt():
    data = request.get_json(force=True)
    mode = data.get('mode', 'binary')
    key = data.get('key', '')
    text = data.get('text', '')

    if not key or len(key) != 10 or any(c not in '01' for c in key):
        return jsonify({'error': '密钥必须是10位二进制'}), 400

    try:
        if mode == 'binary':
            bits = ''.join(text.split())
            if not bits or len(bits) % 8 != 0 or any(c not in '01' for c in bits):
                return jsonify({'error': '二进制输入需为8的倍数，且仅含0/1'}), 400
            out_blocks = []
            for i in range(0, len(bits), 8):
                out_blocks.append(sdes.decrypt(bits[i:i+8], key))
            return jsonify({'result': ' '.join(out_blocks)})
        else:
            plain = sdes.decrypt_text(text, key)
            return jsonify({'result': plain})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/brute', methods=['POST'])
def api_bruteforce():
    data = request.get_json(force=True)
    pairs_raw = data.get('pairs', '')  # multiline: "PT CT" per line
    threads = int(data.get('threads', 1))

    pairs = []
    for line in pairs_raw.split('\n'):
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            return jsonify({'error': f"格式错误: '{line}' 应为: PT CT"}), 400
        pt, ct = parts
        if len(pt) != 8 or len(ct) != 8 or any(c not in '01' for c in pt+ct):
            return jsonify({'error': f"位串错误: '{line}'，PT/CT需为8位二进制"}), 400
        pairs.append((pt, ct))

    if not pairs:
        return jsonify({'error': '至少提供一行明密文对'}), 400

    keys, elapsed = brute_force.brute_force_multi(pairs, threads=max(1, threads))
    # 验证
    verify = []
    for k in keys:
        ok = all(sdes.encrypt(pt, k) == ct for pt, ct in pairs)
        verify.append({'key': k, 'ok': ok})

    return jsonify({'keys': keys, 'verify': verify, 'elapsed': elapsed, 'count': len(keys)})


@app.route('/static/<path:path>')
def static_proxy(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 