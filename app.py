import os
from azure.storage.blob import BlobServiceClient
from flask import Flask, request, redirect, render_template

app = Flask(__name__)

# Retrieve connection string
# Add your AZURE_STORAGE_CONNECTION_STRING 
connect_str = os.getenv('AZURE_STORAGEBLOB_CONNECTIONSTRING')
if not connect_str:
	raise ValueError("Please set the AZURE_STORAGE_CONNECTION_STRING environment variable")

container_name = 'cp-images'
blob_service_client = BlobServiceClient.from_connection_string(conn_str=connect_str)

try:
	container_client = blob_service_client.get_container_client(container=container_name)
	container_client.get_container_properties()
except Exception as e:
	print(e)
	print("Creating container...")
	container_client = blob_service_client.create_container(container_name)

@app.route("/")
def view_media():
	blob_items = container_client.list_blobs()
	images = []
	videos = []

	for blob in blob_items:
		blob_client = container_client.get_blob_client(blob=blob.name)
		if blob.name.endswith(('.png', '.jpeg', '.jpg', '.gif')):
			images.append(blob_client.url)
		elif blob.name.endswith(('.mp4', '.webm', '.ogg')):
			videos.append(blob_client.url)
			
	return render_template('index.html', images=images, videos=videos)


@app.route("/upload-media", methods=["POST"])
def upload_media():
	for file in request.files.getlist("media"):
		try:
			container_client.upload_blob(file.filename, file)
		except Exception as e:
			print(e)
			print("Ignoring duplicate filenames")
	return redirect('/')

if __name__ == "__main__":
	app.run(debug=True)
