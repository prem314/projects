import fitz
import os

def read_toc_from_file(toc_file_name, offset=0):
    """
    Reads the TOC from a text file, expecting a 4-space indentation to represent levels.
    Returns a list of tuples (level, title, page_number).
    
    Args:
        toc_file_name (str): Path to the TOC text file.
        offset (int): Number of pages to offset the page numbers.
        
    Returns:
        list of tuples: Each tuple contains (level, title, page_number).
    """
    toc = []
    with open(toc_file_name, 'r', encoding='utf-8') as file:
        for line in file:
            # Ignore empty lines
            if not line.strip():
                continue

            # Count leading spaces and divide by 4 to determine level
            leading_spaces = len(line) - len(line.lstrip(' '))
            level = (leading_spaces // 4) + 1

            # Split the line into title and page number
            parts = line.strip().rsplit(" - Page ", 1)
            if len(parts) == 2:
                title = parts[0].strip()
                page_str = parts[1].strip()

                try:
                    page = int(page_str) + offset
                    toc.append((level, title, page))
                except ValueError:
                    print(f"Warning: Invalid page number '{page_str}' in line: '{line.strip()}'")
            else:
                print(f"Warning: Line format incorrect, skipping line: '{line.strip()}'")
    return toc

def create_bookmarks_from_toc(pdf_file_path, toc_file_name="toc.txt", offset=0):
    """
    Creates a new PDF with bookmarks added based on the TOC provided in a text file.
    
    Args:
        pdf_file_path (str): Path or name of the original PDF file.
        toc_file_name (str): Path to the TOC text file. Default is 'toc.txt'.
        offset (int): Number of pages to offset the page numbers.
    """
    if not pdf_file_path:
        print("Error: PDF file name is required.")
        return

    original_pdf = pdf_file_path
    if not original_pdf.lower().endswith(".pdf"):
        original_pdf = f"{original_pdf}.pdf"

    base_path = os.path.splitext(original_pdf)[0]
    new_pdf = f"{base_path}_with_toc.pdf"
    
    try:
        doc = fitz.open(original_pdf)
    except Exception as e:
        print(f"Error: Could not open PDF file '{original_pdf}'. {e}")
        return
    
    # Read the TOC from the provided toc.txt file with the specified offset
    bookmarks = read_toc_from_file(toc_file_name, offset)
    
    # Validate page numbers against the PDF's page count
    max_page = doc.page_count
    valid_bookmarks = []
    for level, title, page in bookmarks:
        if 1 <= page <= max_page:
            # fitz uses zero-based page indices
            valid_bookmarks.append((level, title, page - 1))
        else:
            print(f"Warning: Page number {page} for '{title}' is out of range. Skipping this bookmark.")
    
    if not valid_bookmarks:
        print("No valid bookmarks to add. Exiting.")
        doc.close()
        return
    
    # Apply the TOC (bookmarks) to the document
    doc.set_toc(valid_bookmarks)
    
    # Save the modified document
    try:
        doc.save(new_pdf)
        print(f"Bookmarks added from '{toc_file_name}' with an offset of {offset} pages.")
        print(f"New PDF saved as '{new_pdf}'.")
    except Exception as e:
        print(f"Error: Could not save new PDF file '{new_pdf}'. {e}")
    finally:
        doc.close()

if __name__ == "__main__":
    import sys

    print("=== PDF TOC Bookmark Adder ===")
    
    if len(sys.argv) < 2:
        print("Usage: python toc_append.py file.pdf")
        sys.exit(1)

    pdf_file_path = sys.argv[1].strip()
    if not pdf_file_path:
        print("Error: PDF file name is required.")
        sys.exit(1)
    
    
    # Prompt for the TOC file name
    toc_file_name = input("Enter the name of the TOC file (default 'toc.txt'): ").strip()
    if not toc_file_name:
        toc_file_name = "toc.txt"
    
    # Prompt for the page number offset
    offset_input = input("Enter the page number offset (e.g., 0 if no offset, 5 if first TOC page starts at page 6): ").strip()
    try:
        offset = int(offset_input) + 1 if offset_input else 1 # I artificially put offset of +1 because for some reason, the code has a default ofset of -1.
    except ValueError:
        print("Invalid input for offset. Using offset = 0.")
        offset = 1
    
    # Create bookmarks from the TOC
    create_bookmarks_from_toc(pdf_file_path, toc_file_name, offset)
