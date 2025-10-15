# pip install opencv-python
# pip install pytesseract

import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = \
     "C:/Program Files/Tesseract-OCR/tesseract.exe"
     
image_filename = "i1.jpg"
image = cv2.imread(image_filename)


gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

text = pytesseract.image_to_string(gray_image, lang='tha')
print(text)

cv2.imshow("image", image)
cv2.waitKey(0) 
cv2.destroyAllWindows

