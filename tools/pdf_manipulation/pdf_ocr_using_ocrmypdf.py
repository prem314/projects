"""
Does not outperform the earlier code
"""



import os
import ocrmypdf
import logging

# --- Optional: Configure logging for ocrmypdf ---
# If you want to see detailed output from ocrmypdf, you can uncomment the following:
# logging.basicConfig(level=logging.INFO)
# ocrmypdf_logger = logging.getLogger('ocrmypdf')
# ocrmypdf_logger.setLevel(logging.INFO)
# If you want less output (e.g., only errors from ocrmypdf):
# ocrmypdf_logger = logging.getLogger('ocrmypdf')
# ocrmypdf_logger.setLevel(logging.ERROR) # Or WARNING

def make_pdf_searchable_ocrmypdf(input_pdf_path, output_pdf_path):
    try:
        print(f"Processing '{os.path.basename(input_pdf_path)}' with OCRmyPDF...")
        
        ocrmypdf.ocr(
            input_pdf_path,
            output_pdf_path,
            deskew=True,         # Straightens pages that are slightly skewed
            rotate_pages=True,   # Tries to auto-rotate pages to the correct orientation
            skip_text=True       # Skips OCRing pages that already have text, remove if you want to force OCR on all pages
            # force_ocr=True    # Uncomment to force OCR on all pages, even if text is present. Overrides skip_text.
            # language='eng'    # Specify language(s), e.g., 'eng+fra' for English and French. Defaults to English if not set.
        )
        
        print(f"OCRmyPDF complete. Searchable PDF saved as '{os.path.basename(output_pdf_path)}'")
        return True
        
    except ocrmypdf.exceptions.PriorOcrFoundError:
        print(f"Skipped '{os.path.basename(input_pdf_path)}' as OCRmyPDF determined it already has an OCR layer (and skip_text=True or default behavior).")
        # If you want to process these files anyway, consider using force_ocr=True
        # Or, you can simply copy the file to the output directory if skipping is acceptable.
        # For this script, we will treat it as a successful skip.
        try:
            if not os.path.exists(output_pdf_path): # Avoid copying if force_ocr was used and it still hit this
                import shutil
                shutil.copy2(input_pdf_path, output_pdf_path)
                print(f"Copied '{os.path.basename(input_pdf_path)}' to output as it likely already has text.")
            return True
        except Exception as copy_e:
            print(f"Could not copy '{os.path.basename(input_pdf_path)}': {copy_e}")
            return False

    except ocrmypdf.exceptions.EncryptedPdfError:
        print(f"Skipped '{os.path.basename(input_pdf_path)}' as it is encrypted. OCRmyPDF cannot process encrypted PDFs without a password.")
        return False
    except ocrmypdf.exceptions.MissingDependencyError as e:
        print(f"OCRmyPDF is missing a dependency for '{os.path.basename(input_pdf_path)}': {e}")
        print("Please ensure all OCRmyPDF dependencies (like Tesseract, Ghostscript, etc.) are correctly installed.")
        return False
    except Exception as e:
        print(f"An error occurred while processing '{os.path.basename(input_pdf_path)}' with OCRmyPDF: {e}")
        return False

if __name__ == "__main__":
    current_directory = os.getcwd()
    output_directory_name = "ocrmypdf_searchable_output"
    output_directory_path = os.path.join(current_directory, output_directory_name)

    if not os.path.exists(output_directory_path):
        os.makedirs(output_directory_path)
        print(f"Created output directory: {output_directory_path}")

    print(f"\nScanning for PDF files in: {current_directory}")
    
    pdf_files_found_count = 0
    successful_conversions_count = 0
    
    for filename in os.listdir(current_directory):
        if filename.lower().endswith(".pdf"):
            input_file_full_path = os.path.join(current_directory, filename)
            
            # Prevent processing files that are already in the designated output directory
            if os.path.abspath(os.path.dirname(input_file_full_path)) == os.path.abspath(output_directory_path):
                continue

            pdf_files_found_count += 1
            
            # Define output file path
            output_filename = f"{os.path.splitext(filename)[0]}_searchable.pdf" # You can adjust the naming
            output_file_full_path = os.path.join(output_directory_path, output_filename)
            
            print(f"\nFound PDF: {filename}")

            # Avoid re-processing if output file already exists (simple check)
            if os.path.exists(output_file_full_path):
                print(f"Output file '{output_filename}' already exists in output directory. Skipping.")
                successful_conversions_count +=1 # Count as success if already processed
                continue

            if make_pdf_searchable_ocrmypdf(input_file_full_path, output_file_full_path):
                successful_conversions_count += 1
    
    if pdf_files_found_count == 0:
        print(f"No PDF files found in '{current_directory}' to process (excluding the output directory itself).")
    else:
        print(f"\n--- Summary ---")
        print(f"Found {pdf_files_found_count} PDF file(s) to process.")
        print(f"Successfully processed/handled {successful_conversions_count} PDF file(s).")
        print(f"Output files are in: '{output_directory_path}'")
