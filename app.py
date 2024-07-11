import os
from flask import Flask, request, redirect, render_template_string, send_file
from azure.storage.blob import BlobServiceClient
import io

app = Flask(__name__)

connect_str = os.getenv('AZURE_STORAGEBLOB_CONNECTIONSTRING')  # Retrieve the connection string from the environment variable
container_name = "cp-images"  # Container name in which images will be stored in the storage account

blob_service_client = BlobServiceClient.from_connection_string(connect_str)  # Create a blob service client to interact with the storage account

try:
    container_client = blob_service_client.get_container_client(container_name)  # Get container client to interact with the container in which images will be stored
    container_client.get_container_properties()  # Get properties of the container to force exception to be thrown if container does not exist
except Exception as e:
    container_client = blob_service_client.create_container(container_name)  # Create a container in the storage account if it does not exist


@app.route("/")
def home():
    return render_template_string("""
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/">Photos App</a>
            </div>
        </nav>
        <div class="container">
            <div class="card" style="margin: 1em 0; padding: 1em 0 0 0; align-items: center;">
                <h3>Upload new File</h3>
                <div class="form-group">
                    <form method="post" action="/upload-photos" enctype="multipart/form-data">
                        <div style="display: flex;">
                            <input type="file" accept=".png, .jpeg, .jpg, .gif" name="photos" multiple class="form-control" style="margin-right: 1em;">
                            <input type="submit" class="btn btn-primary">
                        </div>
                    </form>
                </div>
            </div>
            <div style="text-align: center;">
                <a href="/view-photos" class="btn btn-success">View Photos</a>
            </div>
        </div>
    </body>
    """)


@app.route("/view-photos")
def view_photos():
    blob_items = container_client.list_blobs()  # List all the blobs in the container

    img_html = "<div style='display: flex; justify-content: space-between; flex-wrap: wrap;'>"

    for blob in blob_items:
        blob_client = container_client.get_blob_client(blob.name)  # Get blob client to interact with the blob
        # Download blob content
        download_stream = blob_client.download_blob()
        blob_data = download_stream.readall()
        img_html += f"<img src='data:image/jpeg;base64,{blob_data.encode('base64')}' width='auto' height='200' style='margin: 0.5em 0;'/>"  # Display the image

    img_html += "</div>"

    return render_template_string("""
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/">Photos App</a>
            </div>
        </nav>
        <div class="container">
            <div style="margin: 1em 0; padding: 1em 0; align-items: center;">
                <h3>Uploaded Photos</h3>
                <a href="/" class="btn btn-primary">Upload More Photos</a>
            </div>
            {{ img_html|safe }}
        </div>
    </body>
    """, img_html=img_html)


@app.route("/upload-photos", methods=["POST"])
def upload_photos():
    filenames = ""

    for file in request.files.getlist("photos"):
        try:
            container_client.upload_blob(file.filename, file)  # Upload the file to the container using the filename as the blob name
            filenames += file.filename + "<br /> "
        except Exception as e:
            print(e)
            print("Ignoring duplicate filenames")  # Ignore duplicate filenames

    return redirect('/view-photos')


if __name__ == "__main__":
    app.run(debug=True)
