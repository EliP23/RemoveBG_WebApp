import os
import io
import zipfile
from flask import Flask, render_template, request, send_file
from rembg import remove

app = Flask(__name__)


##Route to render the loading page
@app.route('/')
def index():
    return render_template('index.html')


##Route that allows for image processing
@app.route('/process', methods=['POST'])
def process_images():
    ##Use the OS to make a directory called temp images
    temp_dir = 'temp_images'
    os.makedirs(temp_dir, exist_ok=True)

    ##Grab the image files from the "request" recieved to the post
    files = request.files.getlist('images')

    ##Loop through each file in the list
    for file in files:
        ##Read the image data
        img_data = file.read()
        ##Call remove and record the subject as output_data
        output_data = remove(img_data)

        ##Create the output path for the particular file by joining
        ##the path of the current temp directory and the current filename
        output_path = os.path.join(temp_dir, file.filename)


        with open(output_path, 'wb') as image_file:
            image_file.write(output_data)

    ## zip file path
    zip_path = "processed_images.zip"

    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root,file)
                zip_file.write(file_path, file)

    for root, _, files in os.walk(temp_dir):
        for file in files:
            os.remove(os.path.join(root,file))
            
    os.rmdir(temp_dir)

    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)