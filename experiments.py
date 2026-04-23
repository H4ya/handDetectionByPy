def checkType(x, y, expected_type):
    if not isinstance(x, expected_type) or not isinstance(y, expected_type):
        raise TypeError(f"Expected both {expected_type.__name__}, got {type(x).__name__} and {type(y).__name__}")
    return True

# اختبار
try:
    result = checkType(1, 's', int)
    print(result)
except TypeError as e:
    print(f"Error: {e}")