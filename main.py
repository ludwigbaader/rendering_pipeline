from src.server import app

def main():
    print("Hello from rendering-pipeline!")
    app.run(host='0.0.0.0', port=8000)


if __name__ == "__main__":
    main()
