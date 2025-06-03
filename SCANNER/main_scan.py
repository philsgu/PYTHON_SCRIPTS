import cv2
from pylibdmtx import pylibdmtx

image_path = 'SCANNER/havirax_2d_matrix.png'
image = cv2.imread(image_path)
#convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#apply thresholding for better detection
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

decoded_objects = pylibdmtx.decode(thresh)  # Or use `gray` if thresholding isn't needed
for obj in decoded_objects:
    print("Barcode Format:", obj.data)  # Decoded data
    print("Bounding box coordinates:", obj.rect)  # Location of the barcode
