from tasks import add


def main():
    result = add.delay(4, 4)
    print(f"Submitted task: {result.id}")
    print(f"Task result: {result.get(timeout=10)}")


if __name__ == "__main__":
    main()
