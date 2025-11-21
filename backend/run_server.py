from app import app
import sys

print("Starting server...")
sys.stdout.flush()

if __name__ == "__main__":
    try:
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
