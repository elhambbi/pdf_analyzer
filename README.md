## Text and image extraction for PDF files

The code includes several useful functions for extracting text and images from PDFs in a structured format using the Fitz library. 

Extracting both text and images from a PDF file is useful for an OCR project because it allows you to apply OCR only to the images while preserving the extracted text from the PDF. Since the position of each image within the text is known, the recognized text from images can be seamlessly embedded into the extracted PDF text.

This approach ensures high accuracy in text extraction by avoiding the need to run OCR on the entire PDF when only a few images require processing.
