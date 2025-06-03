import os
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf_from_jpgs(output_pdf_name="output.pdf"):
    """
    Converts all .jpg files in the current working directory to a single PDF,
    with images added in alphabetical order of their filenames.
    """
    current_dir = os.getcwd()
    jpg_files = sorted([f for f in os.listdir(current_dir) if f.lower().endswith(".jpg")])

    if not jpg_files:
        print("No .jpg files found in the current directory.")
        return

    c = canvas.Canvas(output_pdf_name, pagesize=letter)
    width, height = letter  # Standard letter page size

    print(f"Creating PDF: {output_pdf_name}")
    print("Processing files:")

    for jpg_file in jpg_files:
        try:
            img_path = os.path.join(current_dir, jpg_file)
            print(f" - Adding {jpg_file}")
            img = Image.open(img_path)
            img_width, img_height = img.size

            # Calculate scaling to fit the image on the page while maintaining aspect ratio
            aspect = img_height / float(img_width)
            new_width = width
            new_height = new_width * aspect

            if new_height > height:
                new_height = height
                new_width = new_height / aspect

            # Center the image on the page
            x_offset = (width - new_width) / 2
            y_offset = (height - new_height) / 2

            c.drawImage(img_path, x_offset, y_offset, width=new_width, height=new_height)
            c.showPage() # Create a new page for the next image
            img.close()
        except Exception as e:
            print(f"Error processing {jpg_file}: {e}")

    c.save()
    print(f"\nPDF '{output_pdf_name}' created successfully with {len(jpg_files)} images.")

if __name__ == "__main__":
    create_pdf_from_jpgs()
    # You can specify a different output name if you like:
    # create_pdf_from_jpgs("my_album.pdf")
