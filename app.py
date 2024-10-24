from flask import Flask, jsonify, request, abort, send_file
import subprocess
from commits import *
from getters import *
from utils import create_logger, parse_arguments, get_secret, verify_signature
from flask_cors import CORS

logger = create_logger()

app = Flask(__name__)

CORS(app)

@app.route('/webhook', methods=["POST"])
def get_webhook():
    # verification
    signature = request.headers.get('X-Hub-Signature')
    if not signature:
        abort(403, "x-hub-signature-256 header is missing!")
    secret = get_secret()
    # secret = "PrincessConnect!ccserver"
    if not verify_signature(request.data, secret, signature):
        logger.info("Verification failed. MAY BE ATTACK")
        abort(403, "Request signatures didn't match!")

    # sync the files
    logger.info("new push received")
    subprocess.run(["bash", "pull.sh"])
    # return jsonify({})
    data = request.get_json()
    added = data['commits'][0]['added']
    removed = data['commits'][0]['removed']
    modified = data['commits'][0]['modified']

    if len(added) != 0:
        add_content(added, logger)
    if len(modified) != 0:
        modify_content(modified, logger)
    if len(removed) != 0:
        remove_content(removed, logger)
    
    return jsonify({})

@app.route('/get_num_of_articles', methods=["GET"])
def get_num_of_articles():
    return jsonify({'article_counts': article_counts()})

@app.route('/get_num_of_logs', methods=["GET"])
def get_num_of_logs():
    return jsonify({'log_counts': log_counts()})

@app.route('/get_num_of_columns', methods=["GET"])
def get_num_of_columns():
    return jsonify({'column_counts': column_counts()})

@app.route('/get_logs', methods=["GET"])
def get_logs():
    filter = request.args.get("filter")
    if filter is None:
        return logs()
    else:
        return filtered_logs(filter)

@app.route('/get_articles', methods=["GET"])
def get_articles():
    filter = request.args.get("filter")
    if filter is None:
        return articles()
    else:
        return filtered_articles(filter)

@app.route('/get_columns', methods=["GET"])
def get_columns():
    filter = request.args.get("filter")
    if filter is None:
        return columns()
    else:
        return filtered_columns(filter)

@app.route('/get_articles_in_column', methods=["GET"])
def get_articles_in_column():
    column_id = request.args.get("column_id")
    filter = request.args.get("filter")
    if filter is None:
        articles = articles_in_column(column_id)
    else:
        articles = filtered_column_articles(filter, column_id)
    metadata = single_column(column_id)
    return jsonify({
        "metadata": metadata,
        "articles": articles,
    })

@app.route('/get_article', methods=["GET"])
def get_article():
    article_id = request.args.get("article_id")
    return jsonify(single_article(article_id))

@app.route('/get_log', methods=["GET"])
def get_log():
    log_id = request.args.get("log_id")
    return jsonify(single_log(log_id))

@app.route('/images/<path:filepath>', methods=["GET"])
def get_image(filepath):
    full_path = os.path.join(os.getenv("NOTE_REPO_PATH"), filepath)
    return send_file(full_path, mimetype="image/jpeg")
    

if __name__ == '__main__':
    temp_mode, file_list = parse_arguments(logger)
    if temp_mode:
        add_list, modify_list, remove_list = file_list
        add_content(add_list, logger)
        modify_content(modify_list, logger)
        remove_content(remove_list, logger)
    else:
        # pass
        app.run(host='0.0.0.0', port=5000, debug=True)
