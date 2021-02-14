"""This module is the principle module of this flask application """

from flask import Flask, jsonify, request
from PIL import Image
from PIL.ExifTags import TAGS
from constants import const
import magic
import os


app = Flask(__name__)
ALLOWED_EXTENSIONS = {"txt", "csv", "pdf", "jpg", "png", "gif"}
TMP_FOLDER = "./tmp"
app.config["TMP_FOLDER"] = TMP_FOLDER


@app.route("/upload", methods=["POST"])
def upload_file():
    if request.files:
        file = request.files["file"]
        if file.filename != "" and allowed_file(file.filename):
            filepath = os.path.join(app.config["TMP_FOLDER"], file.filename)
            file.save(filepath)
            metadata = generate_metadata(filepath)
            filedata = generate_filedata(filepath)
            data = {"metadata": metadata, "filedata": filedata}
            return jsonify(data)
        else:
            return const.ERROR_MESSAGE_EXTENSION_NOT_ALLOWED
    else:
        return const.ERROR_MESSAGE_NO_FILE


def generate_metadata(filepath):
    metadata = {}
    metadata["mime"] = magic.from_file(filepath, mime=True)
    metadata["size"] = os.stat(filepath).st_size
    return metadata


def generate_filedata(filepath):
    filedata = "aaabbbccc"
    return filedata


def allowed_file(filename):
    """check if the file extention is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
