# Thai Text Extraction using OpenCV and Pytesseract

This project demonstrates how to extract **Thai text** from an image using **OpenCV** for image processing and **Pytesseract** for Optical Character Recognition (OCR).

---

## 🧩 Prerequisites

Install the required dependencies using pip:

```bash
pip install opencv-python
pip install pytesseract
```

Also, install **Tesseract OCR** from [Tesseract's official GitHub](https://github.com/tesseract-ocr/tesseract) and note its installation path.

---

## ⚙️ Configuration

Set up the Tesseract executable path according to your system:

```python
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"
```

---

## 🧠 Code Example

```python
import cv2
import pytesseract

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

# Load image
image_filename = "i1.jpg"
image = cv2.imread(image_filename)

# Convert to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Extract text (Thai language)
text = pytesseract.image_to_string(gray_image, lang='tha')
print(text)

# Display image
cv2.imshow("image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

---

## 📤 Output

* The extracted **Thai text** will be printed in the terminal.
* The processed image will appear in a new window.

---

## 🧾 Notes

* Make sure the **Thai language pack** is installed in your Tesseract setup.
* You can check installed languages using:

  ```bash
  tesseract --list-langs
  ```

  If `tha` is missing, install it via Tesseract language data files.

---

## 🧰 Example Use Case

This setup can be used for:

* Extracting Thai text from scanned documents.
* Preprocessing text with OpenCV filters before OCR.
* Automating Thai document digitization workflows.

---

**Author:** [Saksham Upreti](mailto:sakshamupreti101@gmail.com)


