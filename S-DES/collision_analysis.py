# collision_analysis.py - S-DES 碰撞分析
# 分析密钥碰撞和密文碰撞情况

import sdes
import itertools
from collections import defaultdict
import time

def analyze_key_collisions():
    """
    分析密钥碰撞：对于同一个明密文对，是否存在多个密钥
    """
    print("=== 密钥碰撞分析 ===")
    print("测试：对于同一个明密文对，是否存在多个密钥？")
    print()
    
    # 测试用例
    test_cases = [
        ("10101010", "00110011"),  # 8位明文
        ("11110000", "00001111"),  # 另一个8位明文
        ("00000000", "11111111"),  # 全0明文
        ("11111111", "00000000"),  # 全1明文
    ]
    
    collision_found = False
    
    for plaintext, ciphertext in test_cases:
        print(f"测试明密文对: {plaintext} -> {ciphertext}")
        
        # 暴力破解找到所有匹配的密钥
        matched_keys = []
        for i in range(2 ** 10):  # 遍历所有1024个密钥
            key = f"{i:010b}"
            encrypted = sdes.encrypt(plaintext, key)
            if encrypted == ciphertext:
                matched_keys.append(key)
        
        print(f"  找到匹配密钥数量: {len(matched_keys)}")
        
        if len(matched_keys) > 1:
            collision_found = True
            print(f"  ⚠️  发现密钥碰撞！匹配的密钥:")
            for i, key in enumerate(matched_keys, 1):
                print(f"    {i}. {key}")
        elif len(matched_keys) == 1:
            print(f"  ✅ 唯一密钥: {matched_keys[0]}")
        else:
            print(f"  ❌ 未找到匹配密钥")
        print()
    
    return collision_found

def analyze_ciphertext_collisions():
    """
    分析密文碰撞：对于同一个明文，不同密钥是否可能产生相同密文
    """
    print("=== 密文碰撞分析 ===")
    print("测试：对于同一个明文，不同密钥是否可能产生相同密文？")
    print()
    
    # 测试明文
    test_plaintexts = [
        "10101010",
        "11110000", 
        "00000000",
        "11111111",
        "01010101",
        "11001100"
    ]
    
    collision_found = False
    
    for plaintext in test_plaintexts:
        print(f"测试明文: {plaintext}")
        
        # 记录每个密文对应的密钥
        ciphertext_to_keys = defaultdict(list)
        
        # 遍历所有密钥
        for i in range(2 ** 10):
            key = f"{i:010b}"
            ciphertext = sdes.encrypt(plaintext, key)
            ciphertext_to_keys[ciphertext].append(key)
        
        # 检查是否有密文碰撞
        collisions = {ct: keys for ct, keys in ciphertext_to_keys.items() if len(keys) > 1}
        
        if collisions:
            collision_found = True
            print(f"  ⚠️  发现密文碰撞！")
            for ciphertext, keys in collisions.items():
                print(f"    密文 {ciphertext} 对应 {len(keys)} 个密钥:")
                for i, key in enumerate(keys, 1):
                    print(f"      {i}. {key}")
        else:
            print(f"  ✅ 无密文碰撞，每个密文对应唯一密钥")
        print()
    
    return collision_found

def analyze_key_space_distribution():
    """
    分析密钥空间分布：统计不同密钥产生的密文分布
    """
    print("=== 密钥空间分布分析 ===")
    print("分析密钥空间到密文空间的映射分布")
    print()
    
    plaintext = "10101010"  # 固定明文
    ciphertext_count = defaultdict(int)
    key_to_ciphertext = {}
    
    # 统计所有密钥的密文
    for i in range(2 ** 10):
        key = f"{i:010b}"
        ciphertext = sdes.encrypt(plaintext, key)
        ciphertext_count[ciphertext] += 1
        key_to_ciphertext[key] = ciphertext
    
    print(f"明文: {plaintext}")
    print(f"密钥空间大小: 1024")
    print(f"密文空间大小: {len(ciphertext_count)}")
    print(f"密文空间利用率: {len(ciphertext_count)/256*100:.2f}%")
    print()
    
    # 统计密文分布
    distribution = defaultdict(int)
    for count in ciphertext_count.values():
        distribution[count] += 1
    
    print("密文分布统计:")
    print("密文出现次数 -> 有多少个这样的密文")
    for count in sorted(distribution.keys()):
        print(f"  {count} 次 -> {distribution[count]} 个密文")
    print()
    
    return len(ciphertext_count), distribution

def analyze_s_des_properties():
    """
    分析S-DES算法的基本性质
    """
    print("=== S-DES 算法性质分析 ===")
    print()
    
    # 1. 密钥空间大小
    print("1. 密钥空间:")
    print(f"   - 密钥长度: 10位")
    print(f"   - 密钥空间大小: 2^10 = 1024")
    print()
    
    # 2. 明文/密文空间大小
    print("2. 明文/密文空间:")
    print(f"   - 明文长度: 8位")
    print(f"   - 明文空间大小: 2^8 = 256")
    print(f"   - 密文长度: 8位")
    print(f"   - 密文空间大小: 2^8 = 256")
    print()
    
    # 3. 理论分析
    print("3. 理论分析:")
    print(f"   - 密钥空间 > 密文空间 (1024 > 256)")
    print(f"   - 理论上存在密钥碰撞的可能性")
    print(f"   - 理论上存在密文碰撞的可能性")
    print()
    
    # 4. 实际测试
    print("4. 实际测试结果:")
    key_collision = analyze_key_collisions()
    cipher_collision = analyze_ciphertext_collisions()
    unique_ciphers, distribution = analyze_key_space_distribution()
    
    print("5. 结论:")
    if key_collision:
        print("   ✅ 存在密钥碰撞：同一个明密文对可能对应多个密钥")
    else:
        print("   ❌ 未发现密钥碰撞")
    
    if cipher_collision:
        print("   ✅ 存在密文碰撞：同一个明文用不同密钥可能产生相同密文")
    else:
        print("   ❌ 未发现密文碰撞")
    
    print(f"   📊 密文空间利用率: {unique_ciphers}/256 = {unique_ciphers/256*100:.2f}%")
    
    if unique_ciphers < 256:
        print("   ⚠️  密文空间未完全利用，存在多个密钥映射到同一密文")
    else:
        print("   ✅ 密文空间完全利用")

def main():
    """主函数"""
    print("S-DES 碰撞分析工具")
    print("=" * 50)
    print()
    
    start_time = time.time()
    analyze_s_des_properties()
    end_time = time.time()
    
    print(f"\n分析完成，耗时: {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    main()
