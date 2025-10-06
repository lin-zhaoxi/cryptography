# sdes.py - S-DES 算法核心实现

def permute(bit_string, permutation):
    """根据置换表重新排列位字符串"""
    return ''.join([bit_string[i - 1] for i in permutation])


def left_shift(bit_string, shifts=1):
    """循环左移操作"""
    return bit_string[shifts:] + bit_string[:shifts]


def generate_keys(key):
    """生成子密钥 K1 和 K2"""
    # 初始置换 P10
    p10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
    key_p10 = permute(key, p10)

    # 左移后拆分
    left_half = key_p10[:5]
    right_half = key_p10[5:]

    # 生成 K1：左移 1 位 + P8 置换
    left_half_shifted = left_shift(left_half, 1)
    right_half_shifted = left_shift(right_half, 1)
    p8_k1 = [6, 3, 7, 4, 8, 5, 10, 9]
    k1 = permute(left_half_shifted + right_half_shifted, p8_k1)

    # 生成 K2：直接在原始 P10 左右半部基础上左移 2 位 + P8 置换（非累计）
    left_half_shifted_twice = left_shift(left_half, 2)
    right_half_shifted_twice = left_shift(right_half, 2)
    k2 = permute(left_half_shifted_twice + right_half_shifted_twice, p8_k1)

    return k1, k2


def s_box_lookup(bit_segment, s_box):
    """S-Box 查表（4 位输入转 2 位输出）"""
    # 行：第 1、4 位组成的二进制
    row = int(bit_segment[0] + bit_segment[3], 2)
    # 列：第 2、3 位组成的二进制
    col = int(bit_segment[1] + bit_segment[2], 2)
    # 转换为二进制（2 位）
    return f"{s_box[row][col]:02b}"


def f_function(right_half, subkey):
    """轮函数 F：扩展置换 + 异或 + S-Box + P4 置换"""
    # 扩展置换 E/P（4 位 -> 8 位）
    ep = [4, 1, 2, 3, 2, 3, 4, 1]
    expanded = permute(right_half, ep)

    # 与子密钥异或
    xor_result = bin(int(expanded, 2) ^ int(subkey, 2))[2:].zfill(8)

    # S-Box 处理（拆分为两个 4 位段）
    s1_segment = xor_result[:4]
    s2_segment = xor_result[4:]

    # S-Box 定义（按作业规范）
    s1 = [[1, 0, 3, 2], [3, 2, 1, 0], [0, 2, 1, 3], [3, 1, 0, 2]]
    s2 = [[0, 1, 2, 3], [2, 3, 1, 0], [3, 0, 1, 2], [2, 1, 0, 3]]

    s1_output = s_box_lookup(s1_segment, s1)
    s2_output = s_box_lookup(s2_segment, s2)

    # P4 置换
    p4 = [2, 4, 3, 1]
    return permute(s1_output + s2_output, p4)


def encrypt(plaintext, key):
    """S-DES 加密流程"""
    # 初始置换 IP
    ip = [2, 6, 3, 1, 4, 8, 5, 7]
    plaintext_ip = permute(plaintext, ip)

    # 拆分左右半部分
    left = plaintext_ip[:4]
    right = plaintext_ip[4:]

    # 生成子密钥
    k1, k2 = generate_keys(key)

    # 第一轮：F 函数 + 异或 + 交换（SW）
    f_output = f_function(right, k1)
    new_right = bin(int(left, 2) ^ int(f_output, 2))[2:].zfill(4)
    left, right = right, new_right

    # 第二轮：F 函数 + 异或（不交换）
    f_output = f_function(right, k2)
    new_left = bin(int(left, 2) ^ int(f_output, 2))[2:].zfill(4)

    # 最终置换 IP^(-1)
    ip_inv = [4, 1, 3, 5, 7, 2, 8, 6]
    return permute(new_left + right, ip_inv)


def decrypt(ciphertext, key):
    """S-DES 解密流程（与加密对称，子密钥顺序为 K2、K1）"""
    ip = [2, 6, 3, 1, 4, 8, 5, 7]
    ciphertext_ip = permute(ciphertext, ip)

    left = ciphertext_ip[:4]
    right = ciphertext_ip[4:]

    k1, k2 = generate_keys(key)

    # 第一轮用 K2，然后交换（SW）
    f_output = f_function(right, k2)
    new_right = bin(int(left, 2) ^ int(f_output, 2))[2:].zfill(4)
    left, right = right, new_right

    # 第二轮用 K1（不交换）
    f_output = f_function(right, k1)
    new_left = bin(int(left, 2) ^ int(f_output, 2))[2:].zfill(4)

    ip_inv = [4, 1, 3, 5, 7, 2, 8, 6]
    return permute(new_left + right, ip_inv)


def encrypt_text(text, key):
    """ASCII 字符串加密（按字节分组）"""
    ciphertext = ""
    for char in text:
        # 字符转 8 位二进制
        char_bin = f"{ord(char):08b}"
        # 加密后转字符
        cipher_bin = encrypt(char_bin, key)
        ciphertext += chr(int(cipher_bin, 2))
    return ciphertext


def decrypt_text(ciphertext, key):
    """ASCII 字符串解密（按字节分组）"""
    plaintext = ""
    for char in ciphertext:
        char_bin = f"{ord(char):08b}"
        plain_bin = decrypt(char_bin, key)
        plaintext += chr(int(plain_bin, 2))
    return plaintext