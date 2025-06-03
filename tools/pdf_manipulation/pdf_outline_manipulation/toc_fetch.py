import fitz  # PyMuPDF

def extract_toc_to_file(pdf_file_name):
    # Open the PDF file
    
    pdf_file_name = pdf_file_name + '.pdf'
    
    doc = fitz.open(pdf_file_name)
    
    # Extract the table of contents
    toc = doc.get_toc()
    
    # Open a text file to write the TOC
    with open("toc.txt", "w") as toc_file:
        for item in toc:
            level, title, page = item
            toc_file.write(f"{' ' * (4 * (level - 1))}{title} - Page {page}\n")
    
    print("Table of contents extracted to toc.txt.")

if __name__ == "__main__":
    pdf_file_name = input("Enter the name of the PDF file: ")
    extract_toc_to_file(pdf_file_name)

