import re

def is_valid_username(username):
    # Tên từ 5-15 ký tự, chỉ gồm chữ cái và số
    return bool(re.fullmatch(r'[a-zA-Z0-9]{5,15}', username))

def is_strong_password(password):
    # Mật khẩu dài 8–32, chứa ít nhất 1 chữ, 1 số, 1 ký tự đặc biệt
    if len(password) < 8 or len(password) > 32:
        return False
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[\W_]', password):  # \W là ký tự đặc biệt, _ tính là đặc biệt luôn
        return False
    return True
