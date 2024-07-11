from flask import Flask, render_template_string, send_file
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from io import BytesIO


app = Flask(__name__)

AZURE_CONNECTION_STRING = os.getenv('AZURE_STORAGEBLOB_CONNECTIONSTRING')
CONTAINER_NAME = 'cp-images'

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

@app.route('/')
def index():
    # List all blobs in the container
    blobs = container_client.list_blobs()
    image_urls = [blob.name for blob in blobs]
    
    # Render the image URLs in the HTML template
    return render_template_string('''
        <h1>Images</h1>
        <ul>
        {% for url in image_urls %}
            <li><a href="/image/{{ url }}">{{ url }}</a></li>
        {% endfor %}
        </ul>
    ''', image_urls=image_urls)

@app.route('/image/<path:filename>')
def get_image(filename):
    # Get the blob client
    blob_client = container_client.get_blob_client(blob=filename)
    
    # Download the blob as a stream
    stream = BytesIO()
    blob_client.download_blob().readinto(stream)
    stream.seek(0)

    # Send the image file to the browser
    return send_file(stream, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
