"""
This code needs both pytesseract and tesseract to be installed on the computer. pytesseract is just a way for python to communicate with the utility called tesseract, which sits outside python. Both can be installed using conda.
"""



try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from pdf2image import convert_from_path
import os # Added for directory operations

def ocr_pdf(pdf_path):
    """
    Performs OCR on a PDF file and returns the extracted text.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from all pages of the PDF.
              Returns an error message string if Tesseract is not installed/found or another error occurs.
    """
    try:
        # Convert PDF to a list of PIL images
        # You might need to specify poppler_path for Windows if not in PATH
        # e.g., images = convert_from_path(pdf_path, poppler_path=r"C:\path\to\poppler-xxx\bin")
        images = convert_from_path(pdf_path)
        
        all_text = ""
        
        print(f"Processing {len(images)} page(s) from '{os.path.basename(pdf_path)}'...")
        
        for i, image in enumerate(images):
            print(f"  - Performing OCR on page {i+1}...")
            # You can specify language e.g., lang='eng' for English
            text = pytesseract.image_to_string(image)
            all_text += f"--- Page {i+1} ---\n{text}\n\n"
            
        print(f"OCR complete for '{os.path.basename(pdf_path)}'.")
        return all_text
        
    except pytesseract.TesseractNotFoundError:
        error_message = (
            f"Tesseract is not installed or not in your PATH. OCR failed for '{os.path.basename(pdf_path)}'.\n"
            "Please install Tesseract OCR: https://github.com/tesseract-ocr/tesseract#installing-tesseract\n"
            "And make sure the Tesseract installation directory is in your system's PATH."
        )
        print(error_message)
        return error_message # Return the error message to be handled by the caller
    except Exception as e:
        error_message = f"An error occurred while processing '{os.path.basename(pdf_path)}': {e}"
        print(error_message)
        return error_message # Return the error message

# --- Main Execution ---
if __name__ == "__main__":
    # Optional: Configure Tesseract path if not in system PATH
    # For Windows, it might be like this:
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    # For Linux/macOS, it's usually found automatically if installed via package managers.

    current_directory = os.getcwd()
    print(f"Scanning for PDF files in: {current_directory}")
    
    pdf_files_found = False
    
    for filename in os.listdir(current_directory):
        if filename.lower().endswith(".pdf"):
            pdf_files_found = True
            pdf_file_path = os.path.join(current_directory, filename)
            print(f"\nFound PDF: {filename}")
            
            extracted_text = ocr_pdf(pdf_file_path)
            
            # Check if OCR returned an error message or actual text
            if "Tesseract is not installed" in extracted_text or \
               "An error occurred while processing" in extracted_text or \
               "pdftoppm not found" in extracted_text: # Common pdf2image error if Poppler is missing
                print(f"Skipping text file generation for '{filename}' due to OCR error.")
            else:
                # Create a name for the output text file
                base_filename = os.path.splitext(filename)[0]
                output_txt_filename = f"{base_filename}_extracted_text.txt"
                output_txt_path = os.path.join(current_directory, output_txt_filename)
                
                try:
                    with open(output_txt_path, "w", encoding="utf-8") as f:
                        f.write(extracted_text)
                    print(f"Extracted text saved to: {output_txt_filename}")
                except Exception as e:
                    print(f"Could not write to file {output_txt_filename}. Error: {e}")
    
    if not pdf_files_found:
        print("No PDF files found in the current directory.")
