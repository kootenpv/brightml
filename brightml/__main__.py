import sys


def main():
    if "features" in sys.argv[1:]:
        from brightml.brightml import get_features
        import json
        print(json.dumps(get_features(), indent=4))
    else:
        from brightml.brightml import main
        main()
