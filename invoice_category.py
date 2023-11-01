import cv2
import pytesseract
import re
import json


class ReceiptDetailsRecognition:
    def __init__(self, **kwargs):
        self.image_param = kwargs['image_name']

    def main(self):

        # Read a dataset
        self.ocr_analysis()

    def ocr_analysis(self):

        # get the path/directory
        f_dir = "dataset/images"
        img = cv2.imread(f_dir + f"/{self.image_param}")

        # Set the tesseract in the screen
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        # Add custom options
        custom_config = r'--oem 3 --psm 6'

        # Use pytesseract to OCR the image
        extracted_text = pytesseract.image_to_string(img, config=custom_config)
        receipt_ocr = self.feature_selection(extracted_text)

        receipt_json = json.dumps(receipt_ocr)
        with open("receipt.json", "w")as outfile:
            outfile.write(receipt_json)

    def feature_selection(self, extracted_txt):
        receipt_ocr = {}
        splits = extracted_txt.splitlines()

        # get items including date, tax, and total
        tax = ""
        total = ""
        date = []

        for line in splits:

            # Find date format ####################
            if not date:
                d1 = re.findall(r'[\d]{1,2}/[\d]{1,2}/[\d]{2,4}', line)
                d2 = re.findall(r'[\d]{1,2}-[\d]{1,2}-[\d]{2,4}', line)
                d3 = re.findall(r'[\d]{1,2}.[\d]{1,2}.[\d]{2,4}', line)
                if d3:
                    try:
                        if "." in d3[0]:
                            d3_num = d3[0].split('.')
                            if len(d3_num) == 3:
                                if not ((1 <= int(d3_num[0]) <= 12 and 1 <= int(d3_num[1]) <= 30)
                                        and 2000 <= int(d3_num[2])) < 2030:
                                    d3 = []
                            else:
                                d3 = []
                        else:
                            d3 = []
                    except ValueError:
                        d3 = []

                d4 = re.findall(r"(\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec) \d{2,4})", line)
                d5 = re.findall(r"(\d{1,2}(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec)\d{2,4})", line)
                d6 = re.findall(r"(\d{1,2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec)-\d{2,4})", line)
                d7 = re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec) [\d]{1,2}, [\d]{2,4}', line)

                date = max(d1, d2, d3, d4, d5, d6, d7)
                if not date == []:
                    receipt_ocr['date'] = date[0]

            # Find tax word #######################
            # Tax-feature1- tax match
            if re.search(r'Tax', line):
                tax = line
            elif re.search(r'tax', line):
                tax = line
            elif re.search(r'TAX', line):
                tax = line

            # Find total word #####################
            if re.search(r'TOTAL', line):
                total = line
            elif re.search(r'Total', line):
                total = line
            elif re.search(r'total', line):
                total = line
            elif re.search(r'SUMME', line):
                total = line
            elif re.search(r'Tota', line):
                total = line
            elif re.search(r'CASH', line):
                total = line

        # Store the results in the dict
        tax_value = self.extract_num_from_str(tax)
        if not tax_value == []:
            receipt_ocr['tax'] = tax_value[-1]
        else:
            for line in splits:
                # Tax-feature2- GST
                # if re.search(r'CGST', line):
                #     total_tax = line
                #     receipt_ocr['tax'] = min(self.extract_num_from_str(total_tax))
                # elif re.search(r'SGST', line):
                #     total_tax = line
                #     receipt_ocr['tax'] = min(self.extract_num_from_str(total_tax))
                # elif re.search(r'GST', line):
                #     total_tax = line
                #     receipt_ocr['tax'] = min(self.extract_num_from_str(total_tax))
                if re.search(r'CGST', line):
                    try:
                        total_tax = line
                        receipt_ocr['tax'] = min(self.extract_num_from_str(total_tax))
                    except ValueError:
                        if re.search(r'SGST', line):
                            try:
                                total_tax = line
                                receipt_ocr['tax'] = min(self.extract_num_from_str(total_tax))
                            except ValueError:
                                if re.search(r'GST', line):
                                    try:
                                        total_tax = line
                                        receipt_ocr['tax'] = min(self.extract_num_from_str(total_tax))
                                    except ValueError:
                                        receipt_ocr['tax'] = []

        total_value = self.extract_num_from_str(total)
        if not total_value == []:
            receipt_ocr['total'] = total_value[-1]
        else:
            for line in splits:
                # Total-feature2- GST
                if re.search(r'CGST', line):
                    total_tax = line
                    receipt_ocr['total'] = max(self.extract_num_from_str(total_tax))
                elif re.search(r'SGST', line):
                    total_tax = line
                    receipt_ocr['total'] = max(self.extract_num_from_str(total_tax))

        receipt_json = json.dumps(receipt_ocr)
        print(receipt_json)
        return receipt_ocr

    def class_detection(self):
        pass

    @staticmethod
    def extract_num_from_str(s):
        new_string = "".join((ch if ch in "0123456789.," else " ") for ch in s)

        try:
            num_list = [float(i.replace(",", "").replace("$", "")) if len(i.split(",")[-1]) == 3 else
                        float(i.replace(",", ".")) for i in new_string.split()]
        except ValueError:
            num_list = []

        return num_list


image = '49.jpg'
receipt_details_recognition = ReceiptDetailsRecognition(image_name=image)
receipt_details_recognition.main()
