import os
import io
import zipfile
from flask import Flask, render_template, request, send_file
from rembg import remove
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def process_single_image(file, temp_dir):
    # Read the image data
    img_data = file.read()
    # Call remove and record the subject as output_data
    output_data = remove(img_data)

    # Create the output path for the particular file by joining
    # the path of the current temp directory and the current filename
    output_path = os.path.join(temp_dir, file.filename)

    with open(output_path, 'wb') as image_file:
        image_file.write(output_data)

@app.route('/process', methods=['POST'])
def process_images():
    # Use the OS to make a directory called temp images
    temp_dir = 'temp_images'
    os.makedirs(temp_dir, exist_ok=True)

    # Grab the image files from the "request" received to the post
    files = request.files.getlist('images')

    # Create a ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        # Submit each file to be processed in parallel
        futures = [executor.submit(process_single_image, file, temp_dir) for file in files]
        
        # Wait for all threads to complete
        for future in futures:
            future.result()

    # Zip file path
    zip_path = "processed_images.zip"

    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, file)

    # Clean up the temporary directory
    for root, _, files in os.walk(temp_dir):
        for file in files:
            os.remove(os.path.join(root, file))
    os.rmdir(temp_dir)

    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
