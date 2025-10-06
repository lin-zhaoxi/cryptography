# brute_force.py - S-DES 暴力破解功能

import sdes
import time
import threading
from typing import List, Tuple


def brute_force(plaintext, ciphertext):
    """
    暴力破解 S-DES 密钥（单个明密文对，单线程）
    遍历所有可能的 10 位密钥，找到匹配的密钥
    """
    matched_keys = []
    start_time = time.time()

    # 遍历所有 2^10 = 1024 个可能的密钥
    for i in range(2 ** 10):
        key = f"{i:010b}"  # 转换为 10 位二进制字符串
        encrypted = sdes.encrypt(plaintext, key)
        if encrypted == ciphertext:
            matched_keys.append(key)

    end_time = time.time()
    elapsed_time = end_time - start_time

    return matched_keys, elapsed_time


def _search_range(start_key: int, end_key: int, pairs: List[Tuple[str, str]], out_list: list):
    """在线程中搜索指定范围内的密钥，所有明密文对均匹配才记录。"""
    for i in range(start_key, end_key):
        key = f"{i:010b}"
        ok = True
        for pt, ct in pairs:
            if sdes.encrypt(pt, key) != ct:
                ok = False
                break
        if ok:
            out_list.append(key)


def brute_force_multi(pairs: List[Tuple[str, str]], threads: int = 1):
    """
    多明密文对 + 可选多线程的暴力破解。
    - pairs: [(plaintext8, ciphertext8), ...]
    - threads: 线程数，>=1
    返回: (matched_keys, elapsed_time)
    """
    if not pairs:
        return [], 0.0

    total_keys = 2 ** 10
    threads = max(1, int(threads))
    step = (total_keys + threads - 1) // threads

    matched_keys_shared = []
    matched_keys_lock = threading.Lock()

    def worker(start, end):
        local = []
        _search_range(start, end, pairs, local)
        if local:
            with matched_keys_lock:
                matched_keys_shared.extend(local)

    start_time = time.time()
    ts = []
    for t in range(threads):
        start = t * step
        end = min((t + 1) * step, total_keys)
        if start >= end:
            continue
        th = threading.Thread(target=worker, args=(start, end), daemon=True)
        ts.append(th)
        th.start()

    for th in ts:
        th.join()

    elapsed_time = time.time() - start_time
    return sorted(set(matched_keys_shared)), elapsed_time


def test_brute_force():
    """测试暴力破解功能（单对）"""
    # 示例明文、密钥和密文
    plaintext = "10101010"
    key = "1100110011"
    ciphertext = sdes.encrypt(plaintext, key)

    print(f"明文: {plaintext}")
    print(f"密文: {ciphertext}")
    print(f"原始密钥: {key}\n")

    print("开始暴力破解(单对/单线程)...")
    matched_keys, elapsed_time = brute_force(plaintext, ciphertext)

    print(f"完成，耗时: {elapsed_time:.4f} 秒; 匹配数量: {len(matched_keys)}")
    if matched_keys:
        print("匹配的密钥:")
        for k in matched_keys:
            print(f"- {k}")
        print("\n验证:")
        for k in matched_keys:
            decrypted = sdes.decrypt(ciphertext, k)
            print(f"{k} -> {decrypted} ({'成功' if decrypted == plaintext else '失败'})")


def test_brute_force_multi():
    """测试多对 + 多线程暴力破解功能"""
    pt1, key = "10101010", "1100110011"
    ct1 = sdes.encrypt(pt1, key)
    pt2 = "11110000"
    ct2 = sdes.encrypt(pt2, key)
    pairs = [(pt1, ct1), (pt2, ct2)]
    print("开始暴力破解(多对/多线程=4)...")
    matched_keys, elapsed = brute_force_multi(pairs, threads=4)
    print(f"完成，耗时: {elapsed:.4f} 秒; 匹配数量: {len(matched_keys)}")
    for k in matched_keys:
        ok = all(sdes.encrypt(pt, k) == ct for pt, ct in pairs)
        print(f"- {k} 验证: {'成功' if ok else '失败'}")


if __name__ == "__main__":
    test_brute_force()
    print()
    test_brute_force_multi()