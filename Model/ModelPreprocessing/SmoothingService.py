import io
import os
import requests
import textwrap
import re
from fpdf import FPDF
from transformers import AutoTokenizer
from bidi.algorithm import get_display
import arabic_reshaper
from arabic_reshaper import ArabicReshaper, config_for_true_type_font, ENABLE_ALL_LIGATURES
import time
import random
import sys
from groq import Groq


def prompt(text):
    return (
        "رجاءً أعد صياغة النص التالي بلغة عربية فصيحة وسهلة وسلسة، مع الحفاظ على الموضوع الأساسي والمحتوى العام."
        "لكن يُسمح لك بالإبداع في اختيار الكلمات، تركيب الجمل، وتسلسل العبارات.\n"
        "اجعل النص أكثر ترابطًا بين الفقرات، بحيث يكون الانتقال من فقرة إلى أخرى منطقيًا وسلسًا.\n"
        "أعطِ النص روحًا جديدة وجاذبية لغوية مميزة، ولكن دون أن تخرج عن الفكرة الأصلية أو تغيّر الحقائق أو تضيف معلومات غير موجودة.\n\n"

        "التعليمات:\n"
        "- اجعل النص أكثر وضوحًا وسلاسة في القراءة، وأفضل في الربط بين الجمل والفقرات.\n"
        "- كل فقرة يجب أن تحتوي على جمل مرتبطة بنفس السياق أو الموقف، وإذا تغير الموضوع، ابدأ فقرة جديدة.\n"
        "- احرص على أن تكون نهاية الفقرة مهيئة لما يليها لزيادة الانسجام.\n"
        "- افصل بين كل فقرتين بسطرين فارغين (\\n\\n) وليس فقط سطر واحد.\n"
        "- لا تدمج مواضيع مختلفة في نفس الفقرة.\n"
        "- يمكنك دمج الجمل أو تفكيكها بما يخدم سلاسة القراءة.\n"
        "- لا تلتزم بنفس الترتيب الحرفي للجمل، لكن احرص على تسلسل منطقي للأفكار.\n"
        "- لا تقم بتكرار المحتوى أو توسيعه بشكل زائد.\n"
        "- إذا وُجدت جمل ركيكة أو مملة أو مكررة، فأعد صياغتها بأسلوب مشوق، أو احذفها إن لم تكن مؤثرة.\n"
        "- انتبه جيدًا للتفاصيل الدقيقة مثل الأرقام، التواريخ، الأماكن، والأسماء. صحّح أي خطأ دون تغيير الهوية.\n"
        "- تجنّب إضافة أو حذف معلومات غير موجودة، لكن يمكن حذف التكرار أو إعادة صياغته بطريقة أفضل.\n"
        "- حافظ على تسلسل الأحداث والمنطق الداخلي للنص كما هو.\n\n"

        "ابدأ فورًا بالنص المعاد صياغته:\n\n"
        "النص:\n\n"
        f"{text}\n\n"
        "النص المُعاد صِياغتُه :"
    )


class SmoothingService:
    def __init__(self):
        # === API Keys and Client Setup ===
        self.key = "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"
        self.current_key = self.key
        self.client = Groq(api_key=self.current_key)
        self.key_switched = False
        self.FONT_PATH = "Fonts/Sahel_Regular.ttf"
        self.OUTPUT_PDF_PATH = "smoothed_output.pdf"
        self.MAX_TOKENS_PER_CHUNK = 700

    def save_to_pdf(self, text):
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("Sahel", "", self.FONT_PATH, uni=True)
        pdf.set_font("Sahel", size=12)

        for paragraph in text.split("\n\n"):
            lines = textwrap.wrap(paragraph.strip(), width=90)
            for line in lines:
                reshaped = arabic_reshaper.reshape(line)
                bidi_line = get_display(reshaped)
                pdf.multi_cell(0, 10, bidi_line, align='R')
            pdf.ln(5)

        # Get PDF content as a string, encode it, and write to BytesIO
        pdf_bytes = io.BytesIO()
        pdf_output = pdf.output(dest='S').encode('latin1')
        pdf_bytes.write(pdf_output)
        pdf_bytes.seek(0)
        # pdf_output.output(output_path)
        return pdf_bytes.read()

    def run_prompt(self, prompt, max_retries=5):
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="meta-llama/llama-4-scout-17b-16e-instruct"
                )
                return response.choices[0].message.content.strip()

            except Exception as e:
                match = re.search(r"Please try again in (\d+)m(\d+(\.\d+)?)s", str(e))
                if match:
                    minutes = int(match.group(1))
                    seconds = float(match.group(2))
                    wait_time = minutes * 60 + seconds
                    print(f" Rate limit exceeded. Wait time: {wait_time:.2f} seconds.")
                    time.sleep(wait_time)

                # Handle other errors with backoff
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"️ Error: {e}. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)

        return "Error: Max retries exceeded."

    def process_text_file(self, chunks):
        smoothed_chunks = []

        for i, chunk in enumerate(chunks):
            print(f"Smoothing part {i + 1} of {len(chunks)} ...")
            smoothed = self.run_prompt(prompt(chunk))
            smoothed_chunks.append(smoothed)

        final_text = "\n\n".join(smoothed_chunks)
        return self.save_to_pdf(final_text)
