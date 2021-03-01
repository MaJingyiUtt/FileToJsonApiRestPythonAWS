"""This module is the principle module of this flask application """

import base64
import os

import magic
import PyPDF2
from flask import Flask, jsonify, request
from PIL import Image
from PIL.ExifTags import TAGS

from constants import const

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
            # remove the tmp file created
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify(data)
        else:
            return const.ERROR_MESSAGE_EXTENSION_NOT_ALLOWED
    else:
        return const.ERROR_MESSAGE_NO_FILE


def generate_metadata(filepath):
    metadata = {}
    metadata["mime"] = magic.from_file(filepath, mime=True)
    metadata["size"] = os.stat(filepath).st_size
    if metadata["mime"].split("/")[0] == "image":
        generate_image_metadata(filepath, metadata)
    if metadata["mime"] == "application/pdf":
        generate_pdf_metadata(filepath, metadata)
    return metadata


def generate_image_metadata(filepath, metadata):
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
    # creating a pdf file object
    pdfFileObj = open(filepath, "rb")
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    information = pdfReader.getDocumentInfo()
    print(information)
    for info in information:
        metadata[info.split("/")[1]] = information[info]
    pdfFileObj.close()


def generate_filedata(filepath):
    type = magic.from_file(filepath, mime=True)
    filedata = ""
    if type == "application/csv" or type == "text/plain":
        f = open(filepath, "r")
        filedata = f.read()
    elif type == "application/pdf":
        # creating a pdf file object
        pdfFileObj = open(filepath, "rb")
        # creating a pdf reader object
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        for page in pdfReader.pages:
            filedata += page.extractText()
        # closing the pdf file object
        pdfFileObj.close()
    elif type.split("/")[0] == "image":
        # encode image to base64
        image = open(filepath, "rb")
        encoded_string = base64.b64encode(image.read())
        filedata = encoded_string.decode("utf-8")
    return filedata


def allowed_file(filename):
    """check if the file extention is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
