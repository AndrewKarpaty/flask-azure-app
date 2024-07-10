import logging
from flask import Flask, request, send_file, jsonify
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
from io import BytesIO

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Azure Blob Storage configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
CONTAINER_NAME = 'cp-images'

blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

@app.route('/images/<image_id>.<image_format>', methods=['GET'])
def get_image(image_id, image_format):
    try:
        blob_name = f'{image_id}.{image_format}'
        blob_client = container_client.get_blob_client(blob_name)
        download_stream = blob_client.download_blob()
        mimetype = f'image/{image_format}'
        return send_file(BytesIO(download_stream.readall()), mimetype=mimetype)
    except Exception as e:
        app.logger.error(f"Error retrieving image: {e}")
        return jsonify({"error": str(e)}), 404

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        file = request.files['file']
        blob_client = container_client.get_blob_client(file.filename)
        blob_client.upload_blob(file)
        return jsonify({"message": "Image uploaded successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error uploading image: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/list', methods=['GET'])
def list_images():
    try:
        blob_list = container_client.list_blobs()
        blobs = [{"name": blob.name} for blob in blob_list]
        return jsonify(blobs)
    except Exception as e:
        app.logger.error(f"Error listing images: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
