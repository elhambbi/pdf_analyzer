from pdf2image import convert_from_path
import fitz
import os
import json

def convert_pdf_to_images(pdf_path: str, output_folder: str) -> None:
    """Converts and saves all pages of a pdf as images"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    pdf_name = os.path.basename(pdf_path).split(".")[0]
    images = convert_from_path(pdf_path)
    for i, image in enumerate(images):
        image.save(f"{output_folder}/{pdf_name}_page_{i+1}.jpg", "JPEG")
    print(f"All pages of {pdf_name} saved as images.")


def extract_pdf_pages_text(pdf_path: str, output_folder: str, by_blocks= False) -> None:
    """ 
    Extracts text from a PDF file page by page and saves it in a JSON file.
    Each page is stored as a list of lines or blocks depending on by_blocks arg.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    pages = []
    doc = fitz.open(pdf_path)
    if by_blocks:
        try:
            print(f"Extracting page blocks for: {pdf_path}")
            for page_num, page in enumerate(doc): 
                page_blocks = []       
                blocks = page.get_text('blocks') 
                for el in blocks:  # el is a tuple of 6 elements. the 4th one is the text (blocks)
                    block = el[4].replace("\t", " ").replace("\n", " ").strip()
                    if block.strip():
                        page_blocks.append(block)
                pages.append(page_blocks)
        except Exception as e:
            raise Exception(f"Error extracting page blocks from {pdf_path}: {e}")
    else:
        try:
            print(f"Extracting page lines for: {pdf_path}")
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
    
    doc.close()
    print(f"{len(pages)} total pages transcibed")
    pdf_name = os.path.basename(pdf_path).split(".")[0]
    suffix = "by_blocks" if by_blocks else "by_lines"
    output_path = os.path.join(output_folder, f"{pdf_name}_pages_{suffix}.json")
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(pages, file, ensure_ascii=False, indent=4)
    print(f"Saved {output_path}")


def extract_pdf_text(pdf_path: str, output_folder: str, by_blocks= False) -> None:           
    """Extrcats and saves all text from a pdf file in a single list of lines or blocks depending on by_blocks arg, in a JSON file"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    doc = fitz.open(pdf_path)
    all_text = []
    if by_blocks:
        try:
            print(f"Extracting blocks for: {pdf_path}")
            for page_num, page in enumerate(doc):      
                blocks = page.get_text('blocks') 
                for el in blocks:  
                    block = el[4].replace("\t", " ").replace("\n", " ").strip()
                    if block.strip():
                        all_text.append(block)
        except Exception as e:
            raise Exception(f"Error extracting blocks from {pdf_path}: {e}")
    else:
        try:
            print(f"Extracting lines for: {pdf_path}")
            for page_num, page in enumerate(doc):
                page_dict = page.get_text("dict") 
                for el in page_dict['blocks']:      # blocks , lines, spans
                    if el['type'] == 0:             # type is 0 for text, 1 for image
                        for line in el['lines']:     
                            fixed_line = ''.join(span['text'] for span in line['spans'])
                            if fixed_line.strip():
                                all_text.append(fixed_line.strip())  
        except Exception as e:
            raise Exception(f"Error extracting lines from {pdf_path}: {e}")
    
    doc.close()
    pdf_name = os.path.basename(pdf_path).split(".")[0]
    suffix = "by_blocks" if by_blocks else "by_lines"
    output_path = os.path.join(output_folder, f"{pdf_name}_text_{suffix}.json")
    with open(output_path, "w", encoding='utf-8') as file:
        json.dump(all_text, file, ensure_ascii= False, indent= 4)
    print(f"Saved {output_path}")


def extract_pdf_pages_images(pdf_path: str, output_folder: str, by_blocks = False):
    """Extracts and saves images and their position wrt the text (lines or blocks of text depending on by_blocks arg) for each page in a pdf file"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    doc = fitz.open(pdf_path)
    image_data = {}
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_data[page_num + 1] = []  # Initialize list for this page
        extracted_xrefs = set()
        text_lines = page.get_text("dict")["blocks"]  # Get detailed text lines information
        text_blocks = page.get_text("blocks")  # gets the blocks (paragraphs) of text

        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            if xref in extracted_xrefs:
                continue
            extracted_xrefs.add(xref)

            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            image_filename = os.path.join(
                output_folder,
                f"{os.path.basename(pdf_path).split('.')[0]}_page{page_num + 1}_img{img_index + 1}.{image_ext}",
            )
            with open(image_filename, "wb") as img_file:
                img_file.write(image_bytes)
            print(f"Saved: {image_filename}")

            image_bbox = fitz.Rect(page.get_image_bbox(img))

            preceding_text = ""
            following_text = ""
            block_number = -1
            found_following_text = False

            if by_blocks:
                for block_num, block in enumerate(text_blocks):
                    text_bbox = fitz.Rect(block[:4])
                    text = block[4].replace("\t", " ").replace("\n", " ").strip()
                    if text.strip():
                        if text_bbox.intersects(image_bbox):
                            block_number = block_num
                        if text_bbox.y1 <= image_bbox.y0:  # text block is above the image
                            preceding_text = text
                        elif text_bbox.y0 >= image_bbox.y1: # text block is below the image
                            following_text = text
                            found_following_text = True
                            break  # Stop after the first following text block        
            else:
                for block_num, block in enumerate(text_lines):
                    if block["type"] != 0:  # Skip non-text blocks (like images)
                        continue
                    for line in block["lines"]:
                        line_bbox = fitz.Rect(line["bbox"])
                        line_text = " ".join([span["text"] for span in line["spans"]])
                        if line_text.strip():
                            if line_bbox.intersects(image_bbox):
                                block_number = block_num
                            if line_bbox.y1 <= image_bbox.y0: # Line is above the image
                                preceding_text = line_text 
                            elif line_bbox.y0 >= image_bbox.y1:  # Line is below the image
                                following_text = line_text
                                found_following_text = True
                                break  # Stop after the first following line
                    if found_following_text:
                        break 

            image_data[page_num + 1].append({
                'filename': image_filename,
                'bbox': (image_bbox.x0, image_bbox.y0, image_bbox.x1, image_bbox.y1),
                'preceding_text': preceding_text,
                'following_text': following_text,
                'block_number': block_number
            })

    doc.close()
    try:
        suffix = "by_blocks" if by_blocks else "by_lines"
        json_filename = os.path.join(output_folder,
                f"{os.path.basename(pdf_path).split('.')[0]}_image_data_{suffix}.json"
                )
        with open(json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(image_data, json_file, indent=4) 
        print(f"Image data saved to: {json_filename}")
    except Exception as e:
        print(f"Error saving JSON: {e}")

    return image_data


def extract_unique_images_from_pdf(pdf_path, output_folder):
    """Extracts and saves all unique images in a pdf files."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    doc = fitz.open(pdf_path)
    extracted_xrefs = set() 
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        for img_index, img in enumerate(page.get_images(full=True)):  # full=False returns only the xref
            xref = img[0]  
            if xref in extracted_xrefs:
                continue
            extracted_xrefs.add(xref)
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            image_filename = os.path.join(output_folder,
                                           f"{pdf_path.split('/')[-1].split('.')[0]}_page{page_num + 1}_img{img_index + 1}.{image_ext}"
                                           )
            with open(image_filename, "wb") as img_file:
                img_file.write(image_bytes)
            print(f"Saved: {image_filename}")
    doc.close()
