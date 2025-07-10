import os
import fitz
import pandas as pd
import base64
from openai import OpenAI
from prompts import VISION_IMAGE_PROMPT
import csv
import mimetypes

import dotenv
dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_directory_files(directory_path):
    parsed_files = []

    for root, _, files in os.walk(directory_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1].lower()

            try:
                if ext == '.pdf':
                    text = parse_pdf(file_path)
                elif ext == '.txt':
                    text = parse_txt(file_path)
                elif ext == '.xlsx':
                    text = parse_excel(file_path)
                elif ext == '.csv':
                    text = parse_csv(file_path)
                elif ext == '.png':
                    text = parse_image_with_vision(file_path)
                else:
                    continue

                parsed_files.append({
                    'file_name': filename,
                    'content': text
                })

            except Exception as e:
                parsed_files.append({
                    'file_name': filename,
                    'content': f"[Error reading file: {str(e)}]"
                })

    return parsed_files


def parse_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()


def parse_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()



def parse_excel(file_path):
    excel_data = pd.read_excel(file_path, sheet_name=None, header=None)
    results = []

    for sheet_name, df in excel_data.items():
        rows = df.values.tolist()

        start_idx = None
        for i, row in enumerate(rows):
            non_empty_count = sum(1 for cell in row if str(cell).strip() and str(cell).lower() != 'nan')
            if non_empty_count >= 4:
                start_idx = i
                break

        if start_idx is None:
            continue

        table_rows = rows[start_idx:]

        cleaned_rows = []
        for i, row in enumerate(table_rows):
            str_row = [str(cell).strip() if pd.notna(cell) else '' for cell in row]
            while str_row and str_row[-1] == '':
                str_row.pop()
            if any(str_row):
                row_number = f"Row {i+1}"
                cleaned_rows.append(f"{row_number}," + ','.join(str_row))

        if cleaned_rows:
            results.append(f"Sheet: {sheet_name}\n" + '\n'.join(cleaned_rows))

    return '\n\n'.join(results).strip() if results else "[No valid table found in Excel]"



def parse_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = list(csv.reader(f))

    table_start_index = None
    for i, row in enumerate(lines):
        non_empty_count = sum(1 for cell in row if cell.strip())
        if non_empty_count >= 4:
            table_start_index = i
            break

    if table_start_index is None:
        return "[No valid table found]"

    clean_rows = []
    for row in lines[table_start_index:]:
        while row and row[-1].strip() == '':
            row.pop()
        if any(cell.strip() for cell in row):
            clean_rows.append(','.join(cell.strip() for cell in row))

    numbered_rows = [f"Row {i+1}," + row for i, row in enumerate(clean_rows)]
    return '\n'.join(numbered_rows)




def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_mime_type(image_path):
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        raise ValueError(f"Unsupported image type for file: {image_path}")
    return mime_type

def parse_image_with_vision(image_path):
    base64_image = encode_image(image_path)
    mime_type = get_mime_type(image_path)

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": VISION_IMAGE_PROMPT },
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime_type};base64,{base64_image}",
                    },
                ],
            }
        ],
    )

    return response.output_text.strip()
