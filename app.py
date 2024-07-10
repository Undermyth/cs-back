from flask import Flask, jsonify, request
import subprocess
from commits import *

app = Flask(__name__)

@app.route('/webhook', methods=["POST"])
def get_webhook():
    # sync the files
    subprocess.run(["bash", "pull.sh"])
    data = request.get_json()
    commit = data['commits']
    added = data['commits'][0]['added']
    removed = data['commits'][0]['removed']
    modified = data['commits'][0]['modified']

    if len(added) != 0:
        add_content(added)
    if len(modified) != 0:
        modify_content(modified)
    if len(removed) != 0:
        remove_content(removed)
    
    return jsonify({})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
