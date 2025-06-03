import os
import glob
from pdf2image import convert_from_path

# Find the first PDF file in the current working directory
pdf_files = glob.glob("*.pdf")
if not pdf_files:
    print("No PDF files found in the working directory.")
    exit()

pdf_file = pdf_files[0]
print(f"Using PDF file: {pdf_file}")

# Create a folder called "pages" if it doesn't exist
output_dir = "pages"
os.makedirs(output_dir, exist_ok=True)

# Convert PDF pages to images
pages = convert_from_path(pdf_file)

# Save each page as a JPEG image named with the page number
for i, page in enumerate(pages, start=1):
    image_path = os.path.join(output_dir, f"{i}.jpg")
    page.save(image_path, "JPEG")
    print(f"Saved page {i} as {image_path}")

