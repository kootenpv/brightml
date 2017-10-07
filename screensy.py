import sys


def get_old_value():
    try:
        with open("/home/pascal/egoroot/screensy/screensy_value") as f:
            return int(f.read())
    except Exception as e:
        print(e)
        return 100


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("requires args op=+ or op=- and <number>")
        sys.exit(1)

    op, value = sys.argv[1], sys.argv[2]
    value = int(value)
    old_value = get_old_value()
    if op == "+":
        value = old_value + value
    elif op == "-":
        value = old_value - value
    else:
        sys.exit(1)
    if value < 0:
        value = 0
    if value > 500:
        value = 500
    with open("/home/pascal/egoroot/screensy/screensy_value", "w") as f:
        f.write(str(value))
