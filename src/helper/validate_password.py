import re

def validate_password(password):
    # Kiểm tra độ dài tối thiểu là 8 kí tự
    if len(password) < 8:
        return False

    # Kiểm tra chữ hoa, chữ thường và kí tự đặc biệt
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False

    # Kiểm tra không có khoảng trắng
    if ' ' in password:
        return False

    return True