# Streamlit Barcode Scanner

This project is a Streamlit web application that allows users to scan 2D matrix barcodes using their device's camera. The application captures images and processes them to detect and decode barcodes.

## Project Structure

```
streamlit_barcode_scanner
├── app.py
├── requirements.txt
└── README.md
```

## Installation

To run this application, you need to have Python installed on your machine. Follow the steps below to set up the project:

1. Clone the repository or download the project files.
2. Navigate to the project directory.
3. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To start the Streamlit application, run the following command in your terminal:

```
streamlit run app.py
```

This will launch the application in your default web browser.

## Usage

Once the application is running, you can use the camera interface to scan 2D matrix barcodes. The decoded data will be displayed on the screen along with the bounding box coordinates of the detected barcode.

## Dependencies

The project requires the following Python packages:

- Streamlit
- OpenCV
- pylibdmtx

Make sure to install these packages using the `requirements.txt` file provided in the project.