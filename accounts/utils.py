from io import BytesIO
import requests
from pdfminer.high_level import extract_text
import spacy
import re
import phonenumbers
import os
import pandas as pd
from .constant import PROVINCES, PROVINCES_1, PROVINCES_2

def extract_text_from_pdf(pdf_path):
    response = requests.get(pdf_path)
    pdf_bytes = BytesIO(response.content)
    text = extract_text(pdf_bytes)
    return text

def extract_phone_number(text) -> list:
    phone_numbers = []
    for match in phonenumbers.PhoneNumberMatcher(text, "VN"):
        phone_numbers.append(re.sub(r'\D', '', phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)))
    return phone_numbers

def extract_location(text):
    # List of location names in Vietnamese
    locations = PROVINCES
    # Find all matches of the location names in the text
    matches = [loc for loc in locations if re.search(loc, text, re.IGNORECASE)]
    
    if matches:
        if matches[0] in PROVINCES_2:
            index = PROVINCES_2.index(matches[0])
            return PROVINCES_1[index]
        return matches[0]
    else:
        return None

nlp = spacy.load("en_core_web_sm")
def extract_skills(nlp_text):
    data = pd.read_csv(os.path.join(os.path.dirname(__file__), 'skills.csv'))
    SKILLS = list(data.columns.values)
    doc = nlp(nlp_text)
    skills = []
    for token in doc:
        if token.text.lower() in SKILLS:
            skills.append(token.text)
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        for skill in SKILLS:
            if skill in chunk_text:
                skills.append(skill)
    lowered_list = [item.lower() for item in skills]
    unique_list = list(set(lowered_list))
    return ", ".join(unique_list)


PROVINCES_1 = ['An Giang', 'Bà Rịa-Vũng Tàu', 'Bắc Giang', 'Bắc Kạn', 'Bạc Liêu', 'Bắc Ninh', 'Bến Tre', 'Bình Định', 'Bình Dương', 'Bình Phước', 'Bình Thuận', 'Cà Mau', 'Cần Thơ', 'Cao Bằng', 'Đà Nẵng', 'Đắk Lắk', 'Đắk Nông', 'Điện Biên', 'Đồng Nai', 'Đồng Tháp', 'Gia Lai', 'Hà Giang', 'Hà Nam', 'Hà Nội', 'Hà Tĩnh', 'Hải Dương', 'Hải Phòng', 'Hậu Giang', 'Hòa Bình', 'Hưng Yên', 'Khánh Hòa', 'Kiên Giang', 'Kon Tum', 'Lai Châu', 'Lâm Đồng', 'Lạng Sơn', 'Lào Cai', 'Long An', 'Nam Định', 'Nghệ An', 'Ninh Bình', 'Ninh Thuận', 'Phú Thọ', 'Phú Yên', 'Quảng Bình', 'Quảng Nam', 'Quảng Ngãi', 'Quảng Ninh', 'Quảng Trị', 'Sóc Trăng', 'Sơn La', 'Tây Ninh', 'Thái Bình', 'Thái Nguyên', 'Thanh Hóa', 'Thừa Thiên-Huế', "Thừa Thiên Huế", 'Tiền Giang', 'TP Hồ Chí Minh', 'Trà Vinh', 'Tuyên Quang', 'Vĩnh Long', 'Vĩnh Phúc', 'Yên Bái']
PROVINCES_2 = [
    "An Giang",
    "Ba Ria - Vung Tau",
    "Bac Giang",
    "Bac Kan",
    "Bac Lieu",
    "Bac Ninh",
    "Ben Tre",
    "Binh Dinh",
    "Binh Duong",
    "Binh Phuoc",
    "Binh Thuan",
    "Ca Mau",
    "Can Tho",
    "Cao Bang",
    "Da Nang",
    "Dak Lak",
    "Dak Nong",
    "Dien Bien",
    "Dong Nai",
    "Dong Thap",
    "Gia Lai",
    "Ha Giang",
    "Ha Nam",
    "Ha Noi",
    "Ha Tay",
    "Ha Tinh",
    "Hai Duong",
    "Hai Phong",
    "Hau Giang",
    "Hoa Binh",
    "Ho Chi Minh",
    "Huyen Lang Son",
    "Hung Yen",
    "Khanh Hoa",
    "Kien Giang",
    "Kon Tum",
    "Lai Chau",
    "Lam Dong",
    "Lang Son",
    "Lao Cai",
    "Long An",
    "Nam Dinh",
    "Nghe An",
    "Ninh Binh",
    "Ninh Thuan",
    "Phu Tho",
    "Phu Yen",
    "Quang Binh",
    "Quang Nam",
    "Quang Ngai",
    "Quang Ninh",
    "Quang Tri",
    "Soc Trang",
    "Son La",
    "Tay Ninh",
    "Thai Binh",
    "Thai Nguyen",
    "Thanh Hoa",
    "Thua Thien - Hue",
    "Thua Thien Hue",
    "Tien Giang",
    "Tra Vinh",
    "Tuyen Quang",
    "Vinh Long",
    "Vinh Phuc",
    "Yen Bai"
]
PROVINCES = PROVINCES_1 + PROVINCES_2