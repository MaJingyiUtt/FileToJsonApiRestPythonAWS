"""This module is the principle module of this flask application """

import base64
import os
import time

import boto3
import magic
import PyPDF2
from flask import Flask, jsonify, request
from flask.helpers import send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from PIL import Image
from PIL.ExifTags import TAGS

from constants import const

app = Flask(__name__)
ALLOWED_EXTENSIONS = {"txt", "csv", "pdf", "jpg", "png", "gif"}
TMP_FOLDER = "./tmp"
app.config["TMP_FOLDER"] = TMP_FOLDER


@app.route("/static/<path:path>")
def send_static(path):
    """route for swagger"""
    return send_from_directory("static", path)


SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "fil-rouge-jma"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route("/upload", methods=["POST"])
def upload():
    """upload file and return content and metadata"""
    data = {}
    if request.files:
        file = request.files["file"]
        if file.filename != "" and allowed_file(file.filename):
            filepath = os.path.join(app.config["TMP_FOLDER"], file.filename)
            file.save(filepath)
            save_file_to_s3(filepath, file.filename)
            metadata = generate_metadata(filepath)
            filedata = generate_filedata(filepath)
            data = {"metadata": metadata, "filedata": filedata}
            # remove the tmp file created
            if os.path.exists(filepath):
                os.remove(filepath)
        else:
            data = {"error": const.ERROR_MESSAGE_EXTENSION_NOT_ALLOWED}
    else:
        data = {"error": const.ERROR_MESSAGE_NO_FILE}
    return jsonify(data)


def save_file_to_s3(filepath, filename):
    """save file to aws s3 bucket"""
    session = boto3.Session(profile_name="csloginstudent")
    s3bucket = session.client("s3")
    s3bucket.upload_file(filepath, const.S3_BUCKET_NAME, filename)


def generate_metadata(filepath):
    """generate metadata according to file type"""
    metadata = {}
    metadata["mime"] = magic.from_file(filepath, mime=True)
    metadata["size"] = os.stat(filepath).st_size
    metadata["lastmodified"] = time.ctime(os.path.getmtime(filepath))
    metadata["created"] = time.ctime(os.path.getctime(filepath))
    if metadata["mime"].split("/")[0] == "image":
        generate_image_metadata(filepath, metadata)
        generate_rekognition(filepath, metadata)
    if metadata["mime"] == "application/pdf":
        generate_pdf_metadata(filepath, metadata)
    return metadata


def generate_rekognition(filepath, metadata):
    """detect objects in images using aws rekognition"""
    session = boto3.Session(profile_name="csloginstudent")
    rekognition = session.client("rekognition")
    with open(filepath, "rb") as image:
        response = rekognition.detect_labels(
            Image={"Bytes": image.read()},
            MaxLabels=10,
            MinConfidence=80,
        )
    metadata["rekognition"] = {}
    for predict in response["Labels"]:
        conf = str(round(predict["Confidence"], 1)) + "%"
        metadata["rekognition"][predict["Name"]] = conf


def generate_image_metadata(filepath, metadata):
    """generate image metadata using exif"""
    opened_image = Image.open(filepath)
    exifdata = opened_image.getexif()
    # iterating over all EXIF data fields
    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        # decode bytes
        if isinstance(data, bytes):
            data = data.decode()
        metadata[tag] = data


def generate_pdf_metadata(filepath, metadata):
    """get pdf metadata using PyPDF2"""
    pdf_file_obj = open(filepath, "rb")
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
    information = pdf_reader.getDocumentInfo()
    print(information)
    for info in information:
        metadata[info.split("/")[1]] = information[info]
    pdf_file_obj.close()


def generate_filedata(filepath):
    """get file content"""
    filetype = magic.from_file(filepath, mime=True)
    filedata = ""
    if filetype in ("application/csv", "text/plain"):
        file = open(filepath, "r")
        filedata = file.read()
    elif filetype == "application/pdf":
        # creating a pdf file object
        pdf_file_obj = open(filepath, "rb")
        # creating a pdf reader object
        pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
        for page in pdf_reader.pages:
            filedata += page.extractText()
        # closing the pdf file object
        pdf_file_obj.close()
    elif filetype.split("/")[0] == "image":
        # encode image to base64
        image = open(filepath, "rb")
        encoded_string = base64.b64encode(image.read())
        filedata = encoded_string.decode("utf-8")
    return filedata


def allowed_file(filename):
    """check if the file extention is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
