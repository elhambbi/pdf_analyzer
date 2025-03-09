import fitz
import json
import os

# some functions to extract text from a pdf file using Fitz

def extract_pdf_page_blocks(pdf_path: str) -> None:           
    """ 
    Extracts text from a PDF file page by page and saves it in a JSON file.
    Each page is stored as a list of blocks (paragraphs).
    """
    pages = []
    try:
        print(f"Extracting page blocks for: {pdf_path}")
        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc): 
            page_blocks = []       
            blocks = page.get_text('blocks') 
            for el in blocks:  # el is a tuple of 6 elements. the 4th one is the transcribed text (blocks)
                block = el[4].replace("\t", " ").replace("\n", " ").strip()
                #block = el[4]
                if block.strip():
                    page_blocks.append(block)
            pages.append(page_blocks)
    except Exception as e:
        raise Exception(f"Error extracting page blocks from {pdf_path}: {e}")

    print(f"{len(pages)} total pages transcibed")
    pdf_dir = os.path.dirname(pdf_path)
    pdf_name = os.path.basename(pdf_path).split(".")[0]
    output_path = os.path.join(pdf_dir, f"{pdf_name}_page_blocks.json")
    with open(output_path, "w", encoding='utf-8') as file:
        json.dump(pages, file, ensure_ascii= False, indent= 4)
    print(f"Saved {output_path}")


def extract_pdf_blocks(pdf_path: str) -> None:           
    """ Saves all blocks of text in a pdf file in a single list in a json file"""
    all_blocks = []
    try:
        print(f"Extracting blocks for: {pdf_path}")
        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc):      
            blocks = page.get_text('blocks') 
            for el in blocks:  
                block = el[4].replace("\t", " ").replace("\n", " ").strip()
                #block = el[4]
                if block.strip():
                    all_blocks.append(block)
    except Exception as e:
        raise Exception(f"Error extracting blocks from {pdf_path}: {e}")

    pdf_dir = os.path.dirname(pdf_path)
    pdf_name = os.path.basename(pdf_path).split(".")[0]
    output_path = os.path.join(pdf_dir, f"{pdf_name}_blocks.json")
    with open(output_path, "w", encoding='utf-8') as file:
        json.dump(all_blocks, file, ensure_ascii= False, indent= 4)
    print(f"Saved {output_path}")

    
def extract_pdf_page_lines(pdf_path: str) -> None:
    """ 
    Extracts text from a PDF file page by page and saves it in a JSON file.
    Each page is stored as a list of lines.
    """
    pages = []
    try:
        print(f"Extracting page lines for: {pdf_path}")
        doc = fitz.open(pdf_path)
        for page in doc:
            page_lines = []
            page_dict = page.get_text("dict")  # extract text as dictionary
            for el in page_dict['blocks']:
                if el['type'] == 0:      # 0 text, 1 img
                    for line in el['lines']:   # spans contains other info such as font, size, bbox - might be useful
                        fixed_line = ''.join(span['text'] for span in line['spans'])
                        if fixed_line.strip():  
                            page_lines.append(fixed_line.strip())
            pages.append(page_lines)
    except Exception as e:
        raise Exception(f"Error extracting page lines from {pdf_path}: {e}")

    print(f"{len(pages)} total pages transcibed")
    pdf_dir = os.path.dirname(pdf_path)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join(pdf_dir, f"{pdf_name}_page_lines.json")
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(pages, file, ensure_ascii=False, indent=4)
    print(f"Saved {output_path}")


def extract_pdf_lines(pdf_path: str) -> None:           
    """ Saves all lines of text in a pdf file as they are in a single list in a json file"""
    all_lines = []
    try:
        print(f"Extracting lines for: {pdf_path}")
        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc):
            page_dict = page.get_text("dict") 
            for el in page_dict['blocks']:      # blocks , lines, spans
                if el['type'] == 0:             # type is 0 for text, 1 for image
                    for line in el['lines']:     
                        fixed_line = ''.join(span['text'] for span in line['spans'])
                        if fixed_line.strip():
                            all_lines.append(fixed_line.strip())  
    except Exception as e:
        raise Exception(f"Error extracting lines from {pdf_path}: {e}")
    
    pdf_dir = os.path.dirname(pdf_path)
    pdf_name = os.path.basename(pdf_path).split(".")[0]
    output_path = os.path.join(pdf_dir, f"{pdf_name}_lines.json")
    with open(output_path, "w", encoding='utf-8') as file:
        json.dump(all_lines, file, ensure_ascii= False, indent= 4)
    print(f"Saved {output_path}")