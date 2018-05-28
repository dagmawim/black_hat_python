def add(num1, num2):
    return num1 + num2

def add_str(num1, num2):
    return str(add(int(num1), int(num2)))
       
answer = add_str("1","1")