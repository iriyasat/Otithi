from app import create_app
import sys

app = create_app()

if __name__ == '__main__':
    port = 5001 if len(sys.argv) > 1 and sys.argv[1] == '--port' else 5000
    print(f"Starting Othiti on port {port}...")
    print(f"Visit: http://localhost:{port}")
    app.run(debug=True, port=port, host='0.0.0.0') 