import streamlit as st
import cv2
from pylibdmtx import pylibdmtx
import numpy as np

def decode_barcode(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    decoded_objects = pylibdmtx.decode(thresh)
    return decoded_objects

st.title("2D Matrix Barcode Scanner")

# Use the camera to capture an image
camera_image = st.camera_input("Capture an image of the barcode")

if camera_image:
    # Read the image from the uploaded file
    file_bytes = np.asarray(bytearray(camera_image.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)

    # Decode the barcode
    decoded_objects = decode_barcode(image)

    if decoded_objects:
        for obj in decoded_objects:
            st.write("Barcode Format:", obj.data.decode('utf-8'))  # Decoded data
            st.write("Bounding box coordinates:", obj.rect)  # Location of the barcode
    else:
        st.write("No barcode detected. Please try again.")