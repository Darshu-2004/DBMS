from flask import Flask, jsonify
from flask_cors import CORS

test_app = Flask(__name__)
CORS(test_app)

@test_app.route('/test')
def test():
    return jsonify({"message": "Server is working!"})

if __name__ == '__main__':
    print("Starting test server on port 5001...")
    test_app.run(debug=False, host='0.0.0.0', port=5001, use_reloader=False)
