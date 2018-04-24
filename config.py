import json
import re
from datetime import date

# # current_url = "http://systemgboc4.sl.cloud9.ibm.com:8809/"
# current_url = "http://22.232.213.31:8808/"
# # crawler_url = "http://systemgboc4.sl.cloud9.ibm.com:5022/"
crawler_url = "http://21.232.215.27:80/"
# crawler_url = "http://21.232.215.28:80/"
# current_url = "http://22.232.213.31:8808/"
current_url = "http://22.232.212.148:8808/"
# crawler_url = "http://systemgboc4.sl.cloud9.ibm.com:5022/"
# crawler_url = "http://21.232.215.28:80/"

crawler_lloyds_url = crawler_url + "api/lloyds/"
crawler_dowjones_url = crawler_url + "api/dowjones/"
crawler_alibaba_url = crawler_url + "api/alibaba/"
crawler_alibaba_url2 = crawler_url + "api/alibaba/v2/"
crawler_alibaba_url_multiple = crawler_url + "api/alibaba/multiple/"
crawler_alibaba_pdf = crawler_url + "static/Alibaba/pdf_file_prev/"
crawler_alibaba_captcha = crawler_url + 'alibaba/captcha/'
crawler_bridger_url = crawler_url + "api/bridgerinsight/"
crawler_google_url = crawler_url + "api/google/"

#zz add
connection_folder = "/data/bocbtvm/users/"

pdf_folder = "/data/bocbtvm/cases/"
tmp_folder = "/tmp/"
#ocr_folder = "/root/Developer/OCR_V7/"
ocr_folder = "/install/OCR_V7/"
data_folder = "/bocbtvm/cases/"
data_folder_1 = "bocbtvm/cases/"
answer_folder = "./app/data/answers/"

local_folder = "./app/bocbtvm/"
target_folder = "./app/bocbtvm/cases/"
local_lloyds_folder = local_folder + "lloyds/"
local_dowjones_folder = local_folder + "dowjones/"
local_google_folder = local_folder + "google/"
local_alibaba_folder = local_folder + "alibaba/"
local_bridge_folder = local_folder + "bridgerInsight/"
local_excel_folder = local_folder + "excel/"

web_data_folder = "bocbtvm/"
web_lloyds_folder = web_data_folder + "lloyds/"
web_dowjones_folder = web_data_folder + "dowjones/"
web_google_folder = web_data_folder + "google/"
web_alibaba_folder = web_data_folder + "alibaba/"
web_bridge_folder = web_data_folder + "bridgerInsight/"
web_excel_folder = web_data_folder + "excel/"


### Create PDF file name from element
def create_pdf_name(name):
    return name.replace(" ", "_").replace("?", "_") + ".pdf"

# def create_pdf_name_1(name):
#     return name.replace(" ", "_").replace("?", "_") + ".pdf"

def create_new_pdf_names(name):
    return name.replace(" ", "_").replace("?", "_") + "_comments.pdf"

def create_new_pdf_names_bk(name):
    return name.replace(" ", "_").replace("?", "_") + "_comments_bk.pdf"


def create_json_name(name):
    return name.replace(" ", "_").replace("?", "_") + ".json"

def create_temp_json_name(name):
    return name.replace(" ", "_").replace("?", "_") + "temp.json"

### Common English words file
english_words_file = "./app/data/common-english-words.txt"

### Crawler Account
def account_file(operator):
  return "app/static/login-data/" + operator + ".json"
# account_file = "app/static/data-temp/ConfigurationInfo.json"

def get_account_name(mail_addr):
  return mail_addr.split("@")[0]

### Entity JSON File
entity_json_suffix = "_entity.json"
def entity_json_path(caseid, page):
  return os.path.join(pdf_folder, caseid, str(page) + entity_json_suffix)


def get_dowjones_account(operator):
  f = open(account_file(operator), 'r')
  account = json.load(f)
  username = str(account["dowjonesID"]).strip()
  password = str(account["dowjonesPassword"]).strip()
  f.close()
  return username, password

def get_lloyds_account(operator):
  f = open(account_file(operator), 'r')
  account = json.load(f)
  username = str(account["lloydsID"]).strip()
  password = str(account["lloydsPassword"]).strip()
  f.close()
  return username, password

def get_bridger_account(operator):
  f = open(account_file(operator), 'r')
  account = json.load(f)
  username = str(account["bridgerID"]).strip()
  password = str(account["bridgerPassword"]).strip()
  f.close()
  return username, password


## Directory path for PDF in the crawler server (MUST BE THE SAME AS CRAWLER!)
google_pdf_folder = "static/GooglePDF/pdf_file_prev/"
dowjones_pdf_folder = "static/dow_jones/pdf_file_prev/"
lloyds_pdf_folder = "static/lloyds/pdf_file_prev/"
bridger_pdf_folder = "static/bridgerinsight/pdf_file/"

## Returned failure messages from crawler
NOT_FOUND = "NOTHING IS FOUND!"
SERVER_ERROR = "SERVER ERROR OCCURRED!"

#### File System Operations
import os
import shutil

def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def rmdir(path):
    shutil.rmtree(path)


def cp(src, dst):
    shutil.copy2(src, dst)


def mv(src, dst):
    shutil.move(src, dst)


def rm(file):
    os.remove(file)


def filename_format(keyword):
    """
    Convert a raw keyword to filename-friendly format
    Example: "  &&''alibaba,LTD_ __" -> "alibaba_ltd"
    :param keyword:
    :return:
    """
    tmp = re.sub('[^0-9a-zA-Z]', '_', keyword).strip('_')
    return re.sub('_+', '_', tmp).lower()


def crawler_format(keyword):
    """
    Convert a raw keyword to crawler-friendly format (space-separated)
    Example: "  &&''alibaba,LTD_ __" -> "alibaba ltd"
    :param keyword:
    :return:
    """
    tmp = re.sub('[^0-9a-zA-Z]', '_', keyword).strip('_')
    return re.sub('_+', ' ', tmp).lower()


def date_format(date_str):
    """
    Convert a date string to filename-friendly format
    :param date_str:
    :return:
    """
    return date_str.replace("/", "_")


def get_today():
    return date.today().strftime("%d/%m/%Y")


class Fields:
    COMPLIANCE_MANAGER = 'compliance'

    ALIBABA_CRAWLER = "alibaba_crawler"
    GOOGLE_CRAWLER = "google_crawler"
    DOWJONES_CRAWLER = "dowjones_crawler"
    BRIDGER_CRAWLER = "bridger_crawler"
    LLOYDS_CRAWLER = "lloyds_crawler"

    ALIBABA = "alibaba"
    INVOICE_BUYER = "invoice buyer"
    INVOICE_SELLER = "invoice seller"
    INVOICE_DESCRIPTION = "invoice description"
    INVOICE_INFO = "invoice info"
    LADING_SHIPPER = "lading shipper"
    LADING_NOTIFY_PARTY = "lading notify party"
    LADING_CONSIGNEE = "lading consignee"
    INVOICE_COUNTRY = "invoice country"
    LADING_COUNTRY = "lading country"
    LADING_MASTER = "lading master"
    MASTER = "master"

    VESSEL = "vessel"
    BL_TRANSSHIPMENT_VESSEL = "bl transshipment vessel"

    SHIPMENT_DATE = "shipment date"
    BL_TRANSSHIPMENT_DATE = "Transshipment date"

    APPLICATION_SHIPMENT_DATE = "shipment date in application"
    APPLICATION_DATE = "application date"
    LADING_PORT_LOADING = "lading port of loading"
    LADING_PORT_DISCHARGE = "lading port of discharge"
    INVOICE_ORIGIN = "invoice origin"
    CERTIFICATE_ORIGIN = "certificate origin"
    INVOICE_UNIT_PRICE = "invoice unit price"
    INVOICE_MIN_PRICE = "invoice min price"
    INVOICE_MAX_PRICE = "invoice max price"
    LADING_UNIT_PRICE = "lading unit price"
    INVOICE_GROSS_WEIGHT = "invoice gross weight"
    INVOICE_QUANTITY = "invoice quantity"
    LADING_GROSS_WEIGHT = "lading gross weight"
    LADING_QUANTITY = "lading quantity"
    LADING_DESCRIPTION = "lading description"
    INVOICE_AMOUNT = "invoice amount"
    LADING_NET_WEIGHT = "lading net weight"
    INVOICE_NET_WEIGHT = "invoice net weight"
    INVOICE_COMMODITY = "invoice commodity"
    MANUFACTURER = "manufacturer"
    THIRD_PARTY = "third party"
    INVOICE_NUMBER = "invoice number"
    TRANSSHIPMENT_COUNTRY = "transshipment country"
    LC_PD_COUNTRY = "lc pd country"
    LC_APPLICANT = "lc applicant"
    LC_BENEFICIARY = "lc beneficiary"
    LC_END_USER = "lc end user"
    LC_ADVISING_BANK = "lc advising bank"
    LC_PL_COUNTRY = "lc pl country"
    CL_CORRESPONDENT_BANK = "cl correspondent bank"
    BL_TRANSSHIPMENT_COUNTRY = "bl transshipment country"
    BL_PL_COUNTRY = "bl pl country"
    BL_PD_COUNTRY = "bl pd country"
    TRUCK_PL_COUNTRY = "truck pl country"
    TRUCK_PD_COUNTRY = "truck pd country"

    ###Added 10/16
    INVOICE_THIRD_PARTY = "invoice third party"
    BL_THIRD_PARTY = "bl third party"
    PL_THIRD_PARTY = "pl third party"
    APPLICATION_THIRD_PARTY = "application third party"
    CL_THIRD_PARTY = "cl third party"
    CERTIFICATE_THIRD_PARTY = "certificate third party"
    LC_THIRD_PARTY = "lc third party"
    INSURANCE_THIRD_PARTY = "insurance third party"
    AIRWAY_THIRD_PARTY = "airway third party"
    TRUCK_THIRD_PARTY = "truck third party"
    DRAFT_THIRD_PARTY = "draft third party"
    APPLICAITON_BUYER = "application buyer"
    APPLICATION_SELLER = "application seller"
    APPLICATION_TRANSFER_BANK = "application transfer bank"
    APPLICATION_SECOND_BENEFICIARY = "application second beneficiary"
    APPLICATION_ASSIGNEE = "application assignee"
    APPLICATION_ASSIGNEE_BANK = "application assignee bank"
    INSURANCE_COMPANY = "insurance company"
    AIRWAY_SHIPPER = "airway shipper"
    AIRWAY_RECEIVER = "airway receiver"
    AIRWAY_DEPARTURE_COUNTRY = 'airway departure country'
    AIRWAY_ARRIVAL_COUNTRY = 'airway arrival country'
    TRUCK_PL_COUNTRY = "truck p/l country"
    TRUCK_PD_COUNTRY = "truck p/d country"
    TRUCK_COMPANY_NAME = "truck company name"
    TRUCK_SHIPPER = "truck shipper"
    TRUCK_RECEIVER = "truck receiver"

    LC_TRANSSHIPMENT_COUNTRY = "lc transshipment country"
    BANKS = "additional banks"
    TOTAL_VESSEL = "total vessel"
    TOTAL_DATE = "total date"
    BANK_OF_CHINA = "bank of china"
    PL_GROSS_WEIGHT = "pl gross weight"
    PL_NET_WEIGHT = "pl net weight"
    DOCUMENT_TYPES = "document types"


    TYPE_IMPORT_ISSUANCE = '0'
    TYPE_IMPORT_DRAWING = '8'
    TYPE_LC_EXPORT = '1'
    TYPE_INWARD_COLLECTION = '2'
    TYPE_OUTWARD_COLLECTION = '3'
    TYPE_RISK = '4'
    TYPE_FORFAITING = '5'
    TYPE_FACTORING = '6'
    TYPE_SHORT_TERM = '7'
    T24_EXCLUDE_DICT = {TYPE_RISK: True, TYPE_FORFAITING: True, TYPE_FACTORING: True, TYPE_SHORT_TERM: True}

    _vessels = [VESSEL, SHIPMENT_DATE]
    _companies = [INVOICE_BUYER, INVOICE_SELLER, LADING_SHIPPER, LADING_NOTIFY_PARTY, LADING_CONSIGNEE, THIRD_PARTY]
    _areas = [INVOICE_COUNTRY, LADING_COUNTRY, LADING_PORT_LOADING, LADING_PORT_DISCHARGE, INVOICE_ORIGIN,
              CERTIFICATE_ORIGIN]

    @staticmethod
    def related_vessel(name):
        return name in Fields._vessels

    @staticmethod
    def related_company(name):
        return name in Fields._companies

    @staticmethod
    def related_area(name):
        return name in Fields._areas


class Config:
    username = ""
    caseid = ""

    @staticmethod
    def set(username, caseid):
        Config.username = username
        Config.caseid = caseid

    @staticmethod
    def get_username():
        return Config.username

    @staticmethod
    def get_caseid():
        return Config.caseid

    @staticmethod
    def data_dir():
        return data_folder + Config.caseid


if __name__ == "__main__":
    import urllib2
    import sys
    import os

    print "Check Crawler Server Connection"
    try:
        urllib2.urlopen(crawler_url)
    except urllib2.URLError as e:
        print "Cannot Connect Crawler Server!"
        print e
        sys.exit(1)

    print "Check Directory Locations"
    if not os.path.isdir(pdf_folder):
        print "Warning: PDF folder does not exist."
        os.makedirs(pdf_folder)
    if not os.path.isdir(tmp_folder):
        print "Warning: Temporary folder does not exist."
        os.makedirs(tmp_folder)
