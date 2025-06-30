# PDF Table of Contents (TOC) Utility

This code helps you to embed TOC in any PDF using AI. AI reads the pdf, gives a well structured, python readable info about the TOC, which can then be embedded in the PDF. 

## How to use this code to generate TOC on any pdf using LLM:

Step 1: Paste the pdf and following prompt in any competent LLM like gemini 2.5 pro:


<pre>
Convert the following outline of the PDF (with page number details) into a well structured form that I will tell you about. Give the output in codeblock so that I can copy it easily to a .txt file with the structure. I need it in a well structured form because then I will use a python code to embed the outline into the corresponding .pdf of the book. Here is the details of the outline copied directly from the pdf. The copied text is not in good form and comes with errors. recognize these errors and fix them.

<content details>

I want it in the following format. Indentation to specify the subsection heirarchy and Page <page number> to specify the page number details.

Contents - Page 6
List of symbols - Page 12
1 First and second quantization - Page 18
    1.1 First quantization, single-particle systems - Page 19
    1.2 First quantization, many-particle systems - Page 21
        1.2.1 Permutation symmetry and indistinguishability - Page 22
        1.2.2 The single-particle states as basis states - Page 23
        1.2.3 Operators in first quantization - Page 24
    1.3 Second quantization, basic concepts - Page 26


Think carefully. Take your time. And do a good job. I have full faith in you.
</pre>

Step 2: Paste the TOC output given by LLM into toc.txt

Step 3: run the code toc_append.py

Step 4: A new pdf with TOC will hopefully be generated.




## Details

This utility consists of two Python scripts designed to work with the table of contents (TOC) of PDF files:

1. **toc_fetch.py**: Extracts the TOC from a given PDF file and saves it to a text file (`toc.txt`).
2. **toc_append.py**: Reads a TOC from a text file (`toc.txt`) and appends it as bookmarks to a given PDF file, saving a new PDF with bookmarks.

## Requirements

- Python 3.6 or higher
- PyMuPDF (`fitz`) library

Use conda env pdf, which has the required environments

## toc_fetch.py

### Purpose

Extracts the TOC from a specified PDF file and saves the TOC information to `toc.txt` in the current working directory. The TOC is saved in a simple format where each line represents an entry in the TOC with a format of "Title - Page X", and indentation (4 spaces per level) to indicate hierarchy.


## toc_append.py

### Purpose

Reads the TOC information from `toc.txt` and uses it to create bookmarks in a new copy of the specified PDF file. The new file will be saved with "toc_" prefixed to the original filename.

You can also correct for the zero error in the page numbering in the script.


## Usage

Run both the script and follow the instructions to enter the name of the PDF file:


## Notes

- Ensure that `toc.txt` exists in the working directory when running `toc_append.py`.
- The scripts assume the PDF file is accessible in the current working directory or a path is provided.


## Generating toc.txt using AI: The AI prompt

  - Copy the content of the contents from the pdf of a pdf and then give the following prompt to a good AI like o1-mini
  

