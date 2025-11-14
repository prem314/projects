"""
There is an another solution using ocrmypdf, but the results are similar.

This code destroys the embedded data like the outline.

OCRmypdf version also fails sometimes.
"""


try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfWriter, PdfReader # Changed from PdfFileMerger to PdfWriter/Reader for PyPDF2 v3.0+
import io # For handling bytes streams
import os

def make_pdf_searchable(input_pdf_path, output_pdf_path):
    """
    Performs OCR on a PDF file and saves a new PDF with an embedded text layer.

    Args:
        input_pdf_path (str): The path to the input PDF file.
        output_pdf_path (str): The path where the searchable PDF will be saved.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        print(f"Processing '{os.path.basename(input_pdf_path)}' to make it searchable...")
        
        # Convert PDF to a list of PIL images
        # You might need to specify poppler_path for Windows if not in PATH
        # e.g., images = convert_from_path(input_pdf_path, poppler_path=r"C:\path\to\poppler-xxx\bin")
        images = convert_from_path(input_pdf_path
#    ,dpi=150,           # Lower the resolution from the default
#    fmt='jpeg'         # Use JPEG format instead of the default (often PPM)
)

        
        pdf_writer = PdfWriter()
        
        for i, image in enumerate(images):
            print(f"  - OCRing and creating searchable PDF layer for page {i+1}/{len(images)}...")
            # Use Pytesseract to do OCR and get PDF output (as bytes)
            # Tesseract will create a PDF with the image and an invisible text layer
            page_pdf_bytes = pytesseract.image_to_pdf_or_hocr(image, extension='pdf', lang='eng') # Specify language if needed
            
            # Create a PdfReader object from the bytes
            page_pdf_reader = PdfReader(io.BytesIO(page_pdf_bytes))
            
            # Add the (single) page from the reader to the writer
            pdf_writer.add_page(page_pdf_reader.pages[0])

        # Write the merged PDF to the output file
        with open(output_pdf_path, "wb") as f_out:
            pdf_writer.write(f_out)
            
        print(f"Searchable PDF saved as '{os.path.basename(output_pdf_path)}'")
        return True
        
    except pytesseract.TesseractNotFoundError:
        print(
            f"Tesseract is not installed or not in your PATH. OCR failed for '{os.path.basename(input_pdf_path)}'.\n"
            "Please ensure Tesseract OCR engine is installed and accessible."
        )
        return False
    except Exception as e:
        print(f"An error occurred while processing '{os.path.basename(input_pdf_path)}': {e}")
        # Common errors could be pdf2image failing if Poppler is not found on Windows
        if "pdftoppm" in str(e).lower() or "poppler" in str(e).lower():
             print("This might be an issue with Poppler. Ensure Poppler binaries are in your PATH or specify poppler_path in convert_from_path.")
        return False

# --- Main Execution ---
if __name__ == "__main__":
    # Optional: Configure Tesseract path if not in system PATH
    # For Windows, it might be like this:
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    current_directory = os.getcwd()
    output_directory = os.path.join(current_directory, "searchable_pdfs")

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created output directory: {output_directory}")

    print(f"\nScanning for PDF files in: {current_directory}")
    
    pdf_files_found = 0
    successful_conversions = 0
    
    for filename in os.listdir(current_directory):
        if filename.lower().endswith(".pdf"):
            # Avoid processing PDFs that are already in the output directory or seem to be already processed
            if "_searchable.pdf" in filename.lower() or os.path.dirname(os.path.join(current_directory, filename)) == output_directory :
                print(f"Skipping already processed or output file: {filename}")
                continue

            pdf_files_found += 1
            input_pdf_file_path = os.path.join(current_directory, filename)
            
            base_filename = os.path.splitext(filename)[0]
            output_pdf_filename = f"{base_filename}_searchable.pdf"
            output_pdf_file_path = os.path.join(output_directory, output_pdf_filename)
            
            print(f"\nFound PDF: {filename}")
            if make_pdf_searchable(input_pdf_file_path, output_pdf_file_path):
                successful_conversions +=1
    
    if pdf_files_found == 0:
        print("No PDF files found in the current directory to process.")
    else:
        print(f"\n--- Summary ---")
        print(f"Processed {pdf_files_found} PDF file(s).")
        print(f"Successfully created {successful_conversions} searchable PDF(s) in '{output_directory}'.")
