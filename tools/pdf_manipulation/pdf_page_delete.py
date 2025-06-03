import PyPDF2

def remove_pages(input_pdf, output_pdf, m, n):
    """
    Remove pages m to n (inclusive, 1-indexed) from input_pdf and save to output_pdf.
    """
    # Open the input PDF in binary read mode
    with open(input_pdf, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        pdf_writer = PyPDF2.PdfWriter()

        total_pages = len(pdf_reader.pages)
        # Convert 1-indexed pages to 0-indexed pages
        start_remove = m - 1
        end_remove = n - 1

        # Iterate through all pages and add those outside the removal range
        for i in range(total_pages):
            if not (start_remove <= i <= end_remove):
                pdf_writer.add_page(pdf_reader.pages[i])

        # Write the output PDF
        with open(output_pdf, "wb") as out_file:
            pdf_writer.write(out_file)

if __name__ == "__main__":
    input_pdf = "input.pdf"
    output_pdf = "output.pdf"
    
    # Get page numbers (as 1-indexed) from the user
    m = int(input("Enter the start page number to remove (1-indexed): "))
    n = int(input("Enter the end page number to remove (1-indexed): "))
    
    remove_pages(input_pdf, output_pdf, m, n)
    print(f"Pages {m} to {n} have been removed. Output saved as {output_pdf}.")

