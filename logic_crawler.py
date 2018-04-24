# Functions will be used in logic.py
import os
import urllib2, urllib
from bridger_insight_parser import bridger_insight_parser
from genPdfReport import buildPdf
import config
import shutil
import concept_sim
import json
from datetime import datetime
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (Flowable, Paragraph, SimpleDocTemplate, Spacer)
import traceback
'''
modified on 10/18  --chenxi:
1) modify the local link if contains Non-ASCII code

'''
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
"""

import logging
logging.basicConfig()
logger = logging.getLogger("Check")
logger.setLevel(logging.DEBUG)

from config import NOT_FOUND

import signal
import time
 
def test_request(arg=None):
    """Your http request."""
    time.sleep(2)
    return arg
 
class Timeout():
    """Timeout class using ALARM signal."""
    class Timeout(Exception):
        pass
 
    def __init__(self, sec):
        self.sec = sec
 
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)
 
    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm
 
    def raise_timeout(self, *args):
        raise Timeout.Timeout()

def url_check(url):
    try:
        urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        logger.error(e.code)
        raise e
    except urllib2.URLError, e:
        logger.error(e.args)
        raise e


class MCLine_copy(Flowable):
   """Line flowable --- draws a line in a flowable"""
   def __init__(self,width):
      Flowable.__init__(self)
      self.width = width

   def __repr__(self):
      return "Line(w=%s)" % self.width

   def draw(self):
      self.canv.line(0, 0, self.width,0)

def dowjones_url(username, password, item):
    try:
        print "type of item=========="
        print type(item)
        print str(item)
        return config.crawler_dowjones_url + urllib.quote(username) + '/' + urllib.quote(password) + '/' + urllib.quote_plus(str(item))
    except:
        return "unicode detected!!!!!!"

def lloyds_url(username, password, keyword, date):
    return config.crawler_lloyds_url + str(username) + '/' + str(password) + '/' + keyword +'/' + date.replace('/', '-')

def lloyds_batch_url(username, password, keyword, date, num):
    return config.crawler_lloyds_url + str(username) + '/' + str(password) + '/' + keyword + '/' + date.replace('/', '-') + '/' + num

def alibaba_url(item, down, up, unit, customer):
    return config.crawler_alibaba_url + str(item) + '/' + str(down) + '/' + str(up) + '/' + str(unit) + '/' + str(customer)

def alibaba_pdf_remote(item):
    return config.crawler_alibaba_pdf + item.replace(' ', '_') + '.pdf'


def bridger_url(username, password, para):
    try:
        return config.crawler_bridger_url + urllib.quote(username) + '/' + urllib.quote(password) + '/' + urllib.quote_plus(str(para))
    except:
        return "unicode detected!!!!!!"


def bridger_pdf_local(para):
    return config.local_bridge_folder + config.date_format(config.get_today()) + "/" + config.create_pdf_name(para)


def bridger_pdf_target(para, case_names):
    return config.target_folder + case_names + "/originalEvidence/" + config.create_pdf_name(para)

def commentsBridger_pdf_target(para, case_names):
    return config.target_folder + case_names + "/originalEvidence/" + config.create_new_pdf_names(para)


def bridger_json_target(para, case_names):
    return config.target_folder + case_names + "/bridgerJson/" + config.create_json_name(para)

def bridger_temp_json_target(para, case_names):
    return config.target_folder + case_names + "/bridgerJson/" + config.create_temp_json_name(para)


def bridger_pdf_web(para):
    return config.web_bridge_folder + config.date_format(config.get_today()) + "/" + config.create_pdf_name(para)


def dowjones_login_test(operator):
    logger.info("Dowjones login test")
    username, password = config.get_dowjones_account(operator)

def lloyds_login_test(operator):
    logger.info("Lloyds login test")
    username, password = config.get_lloyds_account(operator)

def bridger_login_test(operator):
    logger.info("BridgerInsight login test")
    username, password = config.get_bridger_account(operator)


def dowjones_crawling(item, operator, case_name):
    """
    :param item: Company name
    :return: List of PDF URL
    """
    # item = urllib.quote(item.encode('utf8'), ':/')
    logger.info("Dowjones item: " + str(item))

    username, password = config.get_dowjones_account(operator)
    # Mark
    item = item.replace('/', '_')
    craw_str = dowjones_url(username, password, item)
    if craw_str!="unicode detected!!!!!!":
        print craw_str
        logger.debug(craw_str)

        name_item = config.filename_format(item)
    ################
        # stored_file = config.local_dowjones_folder + config.date_format(config.get_today()) + "/" + name_item + ".pdf"
        # if os.path.exists(stored_file):
            # logger.debug("Downloaded PDF File Already Exists!")
            # entry_file = config.current_url + config.web_dowjones_folder + config.date_format(config.get_today()) + "/" + name_item + ".pdf"
            # return [entry_file]
    ##########
        stored_file = config.local_dowjones_folder + config.date_format(config.get_today()) + "/" + name_item + "_Dowjones_summary.pdf"
        result = []
    #    if os.path.exists(stored_file):
    #        logger.debug("Downloaded PDF File Already Exists!")
    #        entry_file = config.current_url + config.web_dowjones_folder + config.date_format(config.get_today()) + "/" + name_item + "_Dowjones_summary.pdf"
    #
    #        pdf_local_path = config.local_dowjones_folder + config.date_format(config.get_today()) + "/"
    #
    #        entry_path = config.current_url + config.web_dowjones_folder + config.date_format(config.get_today()) + "/" 
    #
    #        result.append(entry_file)
    #        
    #        pdf_file = os.listdir(pdf_local_path)
    #        for file in pdf_file:
    #            if name_item + "_companyDetail_" in file and file.startswith(name_item):
    #                result.append(entry_path+file)
    #        return result


        crawler = None
        try:
            req = urllib2.Request(craw_str)
            res = urllib2.urlopen(req)
            crawler = res.read()
        except urllib2.URLError, e:
            logger.error("Error while crawling: " + str(e))
            if hasattr(e, "code"):
                logger.error("Code: " + str(e.code))
            if hasattr(e, "reason"):
                logger.error("Reason: " + str(e.reason))
            return NOT_FOUND

        if not crawler or crawler == NOT_FOUND:
            logger.warning(NOT_FOUND)
            return NOT_FOUND
        print "DowJones Result", crawler
        
        crawler = json.loads(crawler)
        if str(crawler['urls'][0]) == '':
            logger.warning(NOT_FOUND)
            return NOT_FOUND  
        result = []
        # if "found" in crawler and crawler["found"]:
        logger.debug("Dow Jones Crawling Result: " + str(crawler))
        for craw_item in crawler['urls']:
            name = craw_item['link']
            name = name.split('/')
            name = name[len(name) - 1]
            crawler_path = config.crawler_url + config.dowjones_pdf_folder + name
            local_dir = config.local_dowjones_folder + config.date_format(config.get_today())
            config.mkdirs(local_dir)
            # local = local_dir + "/" + name_item + ".pdf"
            local = local_dir + "/" + name
            target_folder = config.target_folder + case_name + "/originalEvidence"
            print "target_folder========"
            print target_folder
            if not os.path.exists(target_folder):
                print "target_folder doesnt exist!!"
                os.makedirs(target_folder)
            target = target_folder + "/" + name

            logger.info("remote path: " + crawler_path)
            logger.info("local path: " + local)

            crawler_path = urllib.quote(crawler_path.encode('utf8'), ':/')
            urllib.urlretrieve(crawler_path, local)

            # urllib.urlretrieve(crawler_path, target)
            if (os.path.isfile(local)):
                print "File exists and will start copy DOWJONES"
                shutil.copy(local, target)

            ret_path = config.current_url + config.web_dowjones_folder + config.date_format(config.get_today()) + "/" + name
            # ret_path = config.current_url + config.web_dowjones_folder + config.date_format(config.get_today()) + "/" + name_item + ".pdf"
            logger.info("Return Path" + ret_path)
            temp = ret_path
            result.append({'origin': craw_item['origin'], 'link': temp})
        # if not crawler["found"]:
        #             break
        # else:
        #     logger.warning(NOT_FOUND)
        #     return NOT_FOUND

        logger.info("Dowjones Result: " + str(result))
        return result
    else:
        return NOT_FOUND


def lloyds_crawling_batch(vessels, dates, operator, case_name):
    logger.info("Lloyds Logic: " + str(vessels) + " " + str(dates))
    crawler = urllib.quote_plus(json.dumps(vessels))
    date = urllib.quote(json.dumps(dates))
    num = len(vessels)

    username, password = config.get_lloyds_account(operator)
    url = lloyds_batch_url(username, password, crawler, date, str(num))
    logger.info("Lloyds URL: " + url)

    try:
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        crawler = res.read()
        logger.debug("Lloyds Crawler: " + str(crawler))
    except urllib2.URLError, e:
        logger.error("Error while crawling: " + str(e))
        if hasattr(e, "code"):
            logger.error("Code: " + str(e.code))
        if hasattr(e, "reason"):
            logger.error("Reason: " + str(e.reason))
        return [NOT_FOUND] * num, set()

    logger.debug("Lloyds crawling get: " + str(crawler))

    results = json.loads(crawler)
    store_path = config.local_lloyds_folder
    config.mkdirs(store_path)

    ret = list()
    owners = set()
    for result in results:
        if result == NOT_FOUND:
            ret.append(NOT_FOUND)
            continue

        for item in result:
            if type(item) != dict:
                continue
            if not item.has_key('overview_pdf'):
                continue
            if not item['overview_pdf']:
                continue
            temp = item['overview_pdf'].split("/")
            temp_len = len(temp)
            pdffile = temp[temp_len - 1]
            local = config.local_lloyds_folder + pdffile

            target_folder = config.target_folder + case_name + "/originalEvidence"
            print "target_folder========"
            print target_folder
            if not os.path.exists(target_folder):
                print "target_folder doesnt exist!!"
                os.makedirs(target_folder)
            target = target_folder + "/" + pdffile

            full_url = config.crawler_url + config.lloyds_pdf_folder + pdffile
            url_check(full_url)
            urllib.urlretrieve(full_url, local)
            if (os.path.isfile(local)):
                print "File exists and will start copy lloyds_crawling_batch OVERVIEW"
                shutil.copy(local, target)
            item['overview_file'] = config.web_lloyds_folder + pdffile

            if not item.has_key('movement_pdf'):
                continue
            if not item['movement_pdf']:
                continue
            temp = item['movement_pdf'].split("/")
            temp_len = len(temp)
            pdffile = temp[temp_len - 1]
            local = config.local_lloyds_folder + pdffile
            target_folder = config.target_folder + case_name + "/originalEvidence"
            print "target_folder========"
            print target_folder
            if not os.path.exists(target_folder):
                print "target_folder doesnt exist!!"
                os.makedirs(target_folder)
            target = target_folder + "/" + pdffile
            full_url = config.crawler_url + config.lloyds_pdf_folder + pdffile
            url_check(full_url)
            urllib.urlretrieve(full_url, local)
            if (os.path.isfile(local)):
                print "File exists and will start copy lloyds_crawling_batch MOVEMENT"
                shutil.copy(local, target)
            item['movement_file'] = config.web_lloyds_folder + pdffile

            if not item.has_key('ownership_pdf'):
                continue
            if not item['ownership_pdf']:
                continue
            temp = item['ownership_pdf'].split("/")
            temp_len = len(temp)
            pdffile = temp[temp_len - 1]
            local = config.local_lloyds_folder + pdffile
            target_folder = config.target_folder + case_name + "/originalEvidence"
            print "target_folder========"
            print target_folder
            if not os.path.exists(target_folder):
                print "target_folder doesnt exist!!"
                os.makedirs(target_folder)
            target = target_folder + "/" + pdffile
            full_url = config.crawler_url + config.lloyds_pdf_folder + pdffile
            print "before url check:" + full_url
            url_check(full_url)
            print "before url retrieve:" + full_url
            urllib.urlretrieve(full_url, local)
            # urllib.urlretrieve(full_url, target)
            if (os.path.isfile(local)):
                print "File exists and will start copy lloyds_crawling_batch OWNERSHIP"
                shutil.copy(local, target)
            item['ownership_file'] = config.web_lloyds_folder + pdffile

            if not item.has_key('movement_csv'):
                continue
            if not item['movement_csv']:
                continue
            temp = item['movement_csv'].split("/")
            temp_len = len(temp)
            pdffile = temp[temp_len - 1]
            local = config.local_lloyds_folder + pdffile
            target_folder = config.target_folder + case_name + "/originalEvidence"
            print "target_folder========"
            print target_folder
            if not os.path.exists(target_folder):
                print "target_folder doesnt exist!!"
                os.makedirs(target_folder)
            target = target_folder + "/" + pdffile
            full_url = config.crawler_url + config.lloyds_pdf_folder + pdffile
            print "before url check:" + full_url
            url_check(full_url)
            print "before url retrieve:" + full_url
            urllib.urlretrieve(full_url, local)
            # urllib.urlretrieve(full_url, target)
            if (os.path.isfile(local)):
                print "File exists and will start copy lloyds_crawling_batch OWNERSHIP"
                shutil.copy(local, target)
            item['movement_csv'] = config.web_lloyds_folder + pdffile
            
            owners.update(item['owners']) # Add owner names
        logger.info("Lloyds Result: " + str(result))
        ret.append(result)


    return ret, owners


def lloyds_crawling(vessel, date, operator):
    """
    Extract vessel information from Lloyds website
    :param vessel: Vessel Name
    :param date: Shipment Date
    :return: Data structure contains exported PDF file path or NOT_FOUND
    """
    logger.info("Lloyds Logic: " + str(vessel) + " " + str(date))
    crawler = urllib.quote_plus(vessel)
    if date:
        date = date.replace('/', '_')
    else:
        date = "Empty"

    username, password = config.get_lloyds_account(operator)
    url = lloyds_url(username, password, crawler, date)
    logger.info("Lloyds URL: " + url)

    try:
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        crawler = res.read()
        logger.debug("Lloyds Crawler: " + str(crawler))
    except urllib2.URLError, e:
        logger.error("Error while crawling: " + str(e))
        if hasattr(e, "code"):
            logger.error("Code: " + str(e.code))
        if hasattr(e, "reason"):
            logger.error("Reason: " + str(e.reason))
        return NOT_FOUND

    logger.debug("Lloyds crawling get: " + str(crawler))

    if str(crawler) == NOT_FOUND:
        logger.warning(NOT_FOUND)
        return NOT_FOUND

    result = json.loads(crawler)
    store_path = config.local_lloyds_folder
    #test if the floder exists or not
    config.mkdirs(store_path)

    for item in result:
        if type(item) != dict:
            continue
        if not item.has_key('overview_pdf'):
            continue
        if not item['overview_pdf']:
            continue
        temp = item['overview_pdf'].split("/")
        temp_len = len(temp)
        pdffile = temp[temp_len - 1]
        local = config.local_lloyds_folder + pdffile
        full_url = config.crawler_url + config.lloyds_pdf_folder + pdffile
        target_folder = config.target_folder + case_name + "/originalEvidence"
        print "target_folder========"
        print target_folder
        if not os.path.exists(target_folder):
            print "target_folder doesnt exist!!"
            os.makedirs(target_folder)
        target = target_folder + "/" + pdffile
        url_check(full_url)
        urllib.urlretrieve(full_url, local)
        if (os.path.isfile(local)):
            print "File exists and will start copy lloyds_crawling OVERVIEW"
            shutil.copy(local, target)
        item['overview_file'] = config.web_lloyds_folder + pdffile

        if not item.has_key('movement_pdf'):
            continue
        if not item['movement_pdf']:
            continue
        temp = item['movement_pdf'].split("/")
        temp_len = len(temp)
        pdffile = temp[temp_len - 1]
        local = config.local_lloyds_folder + pdffile
        full_url = config.crawler_url + config.lloyds_pdf_folder + pdffile
        url_check(full_url)
        target_folder = config.target_folder + case_name + "/originalEvidence"
        print "target_folder========"
        print target_folder
        if not os.path.exists(target_folder):
            print "target_folder doesnt exist!!"
            os.makedirs(target_folder)
        target = target_folder + "/" + pdffile
        urllib.urlretrieve(full_url, local)
        if (os.path.isfile(local)):
            print "File exists and will start copy lloyds_crawling MOVEMENT"
            shutil.copy(local, target)
        item['movement_file'] = config.web_lloyds_folder + pdffile

        if not item.has_key('ownership_pdf'):
            continue
        if not item['ownership_pdf']:
            continue
        temp = item['ownership_pdf'].split("/")
        temp_len = len(temp)
        pdffile = temp[temp_len - 1]
        local = config.local_lloyds_folder + pdffile
        full_url = config.crawler_url + config.lloyds_pdf_folder + pdffile
        url_check(full_url)
        urllib.urlretrieve(full_url, local)
        target_folder = config.target_folder + case_name + "/originalEvidence"
        print "target_folder========"
        print target_folder
        if not os.path.exists(target_folder):
            print "target_folder doesnt exist!!"
            os.makedirs(target_folder)
        target = target_folder + "/" + pdffile
        if (os.path.isfile(local)):
            print "File exists and will start copy lloyds_crawling OWENERSHIP"
            shutil.copy(local, target)
        item['movement_file'] = config.web_lloyds_folder + pdffile
        item['ownership_file'] = config.web_lloyds_folder + pdffile

    logger.info("Lloyds Result: " + str(result))
    return result


def google_helper(crawler_url, craw_pdf, item, case_name):
    """
    :param crawler_url: REST API address for crawler
    :param craw_pdf: PDF file name in crawler
    :param item: Google search query keywords
    :return: Full PDF file address in crawler
    """
    logger.info("Google Helper: " + crawler_url + " " + craw_pdf + " " + str(item))
    crawler = None

    try:
        with Timeout(120):
            req = urllib2.Request(crawler_url)
            res = urllib2.urlopen(req)
            crawler = res.read()
    except urllib2.URLError, e:
        logger.error("Error while crawling: " + str(e))
        if hasattr(e, "code"):
            logger.error("Code: " + str(e.code))
        if hasattr(e, "reason"):
            logger.error("Reason: " + str(e.reason))
        return NOT_FOUND

    if crawler is None or crawler == NOT_FOUND:
        logger.warning("No crawler results: " + str(crawler_url))
        return NOT_FOUND

    logger.debug("Google Crawler Result: " + str(crawler))

    store_path = config.local_google_folder
    res_folder = os.path.exists(store_path)
    if not res_folder:
        os.system('mkdir ' + store_path)
    out_pdf = item.replace(' ', '_') + '.pdf'
    local = config.local_google_folder + config.date_format(config.get_today()) + "/"
    config.mkdirs(local)
    local = local + out_pdf
    target_folder = config.target_folder + case_name + "/originalEvidence"
    print "target_folder========"
    print target_folder
    if not os.path.exists(target_folder):
        print "target_folder doesnt exist!!"
        os.makedirs(target_folder)
    target = target_folder + "/" + out_pdf

    full_url = config.crawler_url + config.google_pdf_folder + craw_pdf
    logger.info("Crawling: " + full_url + " " + local)
    logger.info("Crawling:================ " + full_url + " " + target)
    urllib.urlretrieve(full_url, local)
    # urllib.urlretrieve(full_url, target)
    if (os.path.isfile(local)):
        print "File exists and will start copy GOOOOOGLE/BLOOMBERG"
        shutil.copy(local, target)
    return full_url


def bridger_crawling(para, full_name, operator, case_name):
    """
    :param para: Company name
    :param full_name: Full name of current user
    :return: Evidence if found, otherwise NOT_FOUND
    """
    logger.info("BridgerInsight Helper: " + str(para) + " " + str(full_name))
    keyword = para
    # MARK
    para = para.replace('/', '_')

    username, password = config.get_bridger_account(operator)
    
    evidence = dict()
    url = bridger_url(username, password, para)
    if url!="unicode detected!!!!!!":

        crawler = None
        try:
            req = urllib2.Request(url)
            res = urllib2.urlopen(req)
            crawler = res.read()
        except urllib2.URLError, e:
            logger.error("Error while crawling: " + str(e))
            if hasattr(e, "code"):
                logger.error("Code: " + str(e.code))
            if hasattr(e, "reason"):
                logger.error("Reason: " + str(e.reason))
            return NOT_FOUND

        if crawler == NOT_FOUND:
            logger.warning(NOT_FOUND)
            return NOT_FOUND

        # logger.info("BridgerInsight Result: " + str(crawler))
        config.mkdirs(config.local_bridge_folder + config.date_format(config.get_today()))
        name_orig = para.replace('/','_')
        para = (case_name + '_' + para).replace('/', '_')
        item=json.loads(crawler)
        if item['Records'] is None or item["Records"]["ResultRecord"][0]["Watchlist"]["Matches"] is None:
            bridger_no_result(operator, name_orig, bridger_pdf_local(para))
            evidence["type"] = "bridgerInsight"
            evidence["url"] = config.current_url + bridger_pdf_web(para)
            evidence["missing"] = False
            evidence["name"] = keyword
            logger.info("Evidence: " + str(evidence))
            return evidence
        
        item['full name'] = operator
        crawler = json.dumps(item)
       
        name = para.replace(" ", "_")
        fileObject = open(name + "_bridge.json", 'w')
        fileObject.write(str(crawler))
        fileObject.close()
        exists = bridger_insight_parser(name + "_bridge.json", name + "_bridge_temp.json")
        if not exists:
            return NOT_FOUND

        print "pdf target======"
        print bridger_pdf_local(name)

        try:
            buildPdf(bridger_pdf_local(name), name + "_bridge_temp.json")
            # buildPdf(bridger_pdf_target(name, case_name), name + "_bridge_temp.json")
            if (os.path.isfile(bridger_pdf_local(name))):
                print "File exists and will start copy BRIDGERINSIGHT!!!!"
                shutil.copy(bridger_pdf_local(name), bridger_pdf_target(name, case_name))
        except:
            logger.error("Failed to generate PDF for:" + str(name))
            logger.error(traceback.format_exc())
            return NOT_FOUND

        abstract_data = []
        hit_flag = False
        with open(name + "_bridge.json") as data_file:
            ab_data = json.load(data_file)
            for temp_item in ab_data['Records']['ResultRecord']:
                wl = temp_item['Watchlist']['Matches']['WLMatch']
                for index, wl_item in enumerate(wl):
                    if wl_item['EntityDetails'] is None and wl_item["CountryDetails"] is not None:
                        entry = {}
                        entry['EntityScore'] = wl_item['BestCountryScore']
                        if int(entry['EntityScore']) == 100:
                            hit_flag = True
                        entry['FileName'] = wl_item['File']['Name'][:-4]
                        entry['Entity Name'] = wl_item['EntityName']
                        entry["index"] = index + 1
                        abstract_data.append(entry)
                    elif wl_item["EntityDetails"] is not None and wl_item["CountryDetails"] is None:
                        entry = {}
                        entry['EntityScore'] = wl_item['EntityScore']
                        if int(entry['EntityScore']) == 100:
                            hit_flag = True
                        entry['FileName'] = wl_item['File']['Name'][:-4]
                        entry['Entity Name'] = wl_item['EntityName']
                        entry["index"] = index + 1
                        abstract_data.append(entry)


        target_json_folder = config.target_folder + case_name + "/bridgerJson"
        # 1 Create a folder which will contain JSON files for every user.
        if not os.path.exists(target_json_folder):
            os.makedirs(target_json_folder)

        # 2 Check whether there is such JSON file that matches bocID.json
        if os.path.isfile(bridger_temp_json_target(name, case_name)) and os.access(bridger_temp_json_target(name, case_name),
                                                                          os.R_OK):
            print "File exists and is readable"
        else:
            print "Either file is missing or is not readable"
            os.mknod(bridger_temp_json_target(name, case_name))
            print "Will check whether json exists"
            print os.path.isfile(bridger_temp_json_target(name, case_name)) and os.access(bridger_temp_json_target(name, case_name), os.R_OK)

        # 3 Write userInfo into that JSON

        with open(bridger_temp_json_target(name, case_name), "w") as fileObject_1:
            json.dump(abstract_data, fileObject_1, indent=4, ensure_ascii=False)


        if (os.path.isfile(name + "_bridge_temp.json")):
            print "Will COPY original Bridger data."
            shutil.copy((name + "_bridge_temp.json"), bridger_json_target(name, case_name))

        # os.system("rm " + name + "_bridge.json " + name + "_bridge_temp.json")
        os.remove(name + "_bridge.json")
        os.remove(name + "_bridge_temp.json")
        evidence["type"] = "bridgerInsight"
        evidence["url"] = config.current_url + bridger_pdf_web(name)
        evidence["missing"] = False
        evidence["name"] = keyword
        evidence["isHit"] = hit_flag
        logger.info("Evidence: " + str(evidence))
        return evidence
    else:
        return NOT_FOUND


def match_desc(desc1, desc2):
    logger.info("Match Desc: " + str(desc1) + " " + str(desc2))
    f = open(config.english_words_file)
    common_words = f.read().strip().split(',')
    f.close()
    concept_names = desc1
    sim = concept_sim.word_similarity_max(concept_sim.check_tag(concept_names.strip(), common_words, 0),
                                  concept_sim.check_tag(desc2.strip(), common_words, 0))
    f.close()
    logger.info("Match Desc Result: " + str(sim))
    return sim


def fantastic_t24():
    logger.info("Fantastic T24")
    result = [{
             'Letter_of_credit':'customer',
             'Application_number':'TF110310817408',
             'Ship_fm_country': 'US',
             'Ship_to_country': 'CN',
             'Country_origin': 'FR',
             'Document_amount': 361820.10,
             'Transaction_date': '20110110',
             'Invoice_num': '1017607 107198',
             'Amendment_number': 'NO1',
             'Amendment_date': '2011011',
             'Amendment_del': 'delete',
             'Good_description': 'WASTE PAPER'}]
    logger.info("Fantastic T24: " + str(result))
    return result

def captchaOrNot(item, price, customer, unit):
    logger.info("Captcha or not: " + str(item) + " " + str(price) + " " + str(customer) + " " + str(unit))
    if not item:
        logger.warning("No item found")
        return False
    up_limit = float(price * 1.1)
    down_limit = float(price * 0.9)
    temp = item
    item = urllib.quote_plus(item)
    unit = urllib.quote_plus(unit)
    craw_str = alibaba_url(item, down_limit, up_limit, unit, customer)
    logger.debug("Crawling query: " + craw_str)
    item = temp
    path = None
    try:
        req = urllib2.Request(craw_str)
        res = urllib2.urlopen(req)
        path = res.read()
        logger.debug("JSON path: " + str(path))
    except urllib2.URLError, e:
        logger.error("URL Error: " + str(e))
        if hasattr(e, "code"):
            logger.error("Code: " + str(e.code))
        if hasattr(e, "reason"):
            logger.error("Reason: " + str(e.reason))
    if path is None or path == NOT_FOUND:
        logger.warning("No path found")
        return '11'

    if not os.path.exists(config.local_folder):
        os.system('mkdir ' + config.local_folder)
    logger.info("File path: " + path)
    return path
def NoCaptcha(item, price):
    logger.info("No Captcha: " + str(item) + " " + str(price))
    local_folder = config.local_alibaba_folder
    if not os.path.exists(local_folder):
        os.system('mkdir ' + local_folder)

    pdffile = item.replace(' ', '_') + '_' + str(price) + '.pdf'
    local_name = local_folder + pdffile
    remote_name = alibaba_pdf_remote(item)
    logger.debug("local name: " + local_name)
    logger.debug("remote name: " + remote_name)
    urllib.urlretrieve(remote_name, local_name)

    resultLink = config.web_alibaba_folder + pdffile
    logger.info("No Captcha Result Path: " + resultLink)
    return resultLink

def storeCaptcha(item, customer):
    logger.info("Stop Captcha: " + str(item) + " " + str(customer))
    tag = datetime.now().microsecond
    item_tag = item.replace(" ", "_")
    remote_name = alibaba_pdf_remote(item)
    pngfile = customer + '_' + str(item_tag) + '_' + str(tag) + '_temp.png'
    local_name = config.local_folder + pngfile
    logger.debug('remote name: ' + remote_name)
    logger.debug('local name: ' + local_name)
    urllib.urlretrieve(remote_name, local_name)
    res_name = config.web_data_folder + pngfile
    logger.info("Stop Captcha Result Path: " + res_name)
    return res_name

def NeedCaptcha(item, customer, temp_name):
    logger.info("Need Captcha: " + str(item) + " " + str(customer) + " " + str(temp_name))
    craw_str = config.crawler_alibaba_captcha + str(temp_name) + '/' + item.replace(' ', '_') + '/' + str(customer)
    logger.debug("Crawling URL: " + craw_str)
    res = ''
    try:
        req = urllib2.Request(craw_str)
        res = urllib2.urlopen(req)
        res = res.read()
    except urllib2.URLError, e:
        logger.error("URL Error: " + str(e))
        if hasattr(e, "code"):
            logger.error("Code: " + str(e.code))
        if hasattr(e, "reason"):
            logger.error("Reason: " + str(e.reason))
    if res is None:
        logger.warning("NOTHING IS SEARCHED!")
        return "NOTHING IS SEARCHED!"
    local_folder = config.local_alibaba_folder
    if not os.path.exists(local_folder):
        os.system('mkdir ' + local_folder)
    local_name = local_folder + item.replace(' ', '_') + '.pdf'
    remote_name = alibaba_pdf_remote(item)
    logger.debug('remote name: ' + remote_name)
    logger.debug('local name: ' + local_name)
    urllib.urlretrieve(remote_name, local_name)
    resultLink = config.web_alibaba_folder + item.replace(' ', '_') + '.pdf'
    os.system('rm ' + config.local_folder + '*png')
    logger.info("Need Captcha Result Path: " + resultLink)
    return resultLink


def bridger_no_result(full_name, para, pdfName):

    logger.info("Bridge No Result: " + full_name + " " + str(para) + " " + pdfName)
    darkstyle = ParagraphStyle(
        name='dark',
        fontSize=12,
        fontName='Helvetica-Bold',
        leading=16,
    )
    boldstyle = ParagraphStyle(
        name='bold',
        fontSize=12,
        fontName='Helvetica-Bold',
    )

    doc = SimpleDocTemplate(pdfName,pagesize=letter,
                        rightMargin=72,leftMargin=72,
                        topMargin=72,bottomMargin=18)
    now = datetime.now()
    search_date = str(now.month) + "/" + str(now.day) + "/" + str(now.year)
    search_time = str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
    logger.debug("Date: " + search_date)
    logger.debug("Time: " + search_time)

    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    Story=[]

    logo = "title.png"
    im = Image(logo, 4*inch, 0.5*inch)
    im.hAlign = 'LEFT'
    Story.append(im)


    ptext = '<font size=12>%s</font>' % ('Bank of China, USA')
    Story.append(Paragraph(ptext, style=boldstyle))
    Story.append(Spacer(1, 5))

    line = MCLine_copy(455)
    Story.append(line)

    ptext = '<font size=12>%s: %s</font>' % ('Name', para.replace("?", "/").replace("_", "/").replace('&','&amp;'))
    Story.append(Paragraph(ptext, style=boldstyle))
    Story.append(Spacer(1, 2))
    # ptext = '<font size=12>%s: </font>' % ('SSN')
    # Story.append(Paragraph(ptext, style=boldstyle))
    # Story.append(Spacer(1, 2))

    ptext = '<font size=12>%s: </font>' % ('EIN')
    Story.append(Paragraph(ptext, style=boldstyle))
    Story.append(Spacer(1, 2))
    ptext = '<font size=12>%s: </font>' % ('Address')
    Story.append(Paragraph(ptext, style=boldstyle))
    Story.append(Spacer(1, 2))
    ptext = '<font size=12>%s: </font>' % ('Phone')
    Story.append(Paragraph(ptext, style=boldstyle))
    Story.append(Spacer(1, 2))
    ptext = '<font size=12>%s: </font>' % ('Account ID')
    Story.append(Paragraph(ptext, style=boldstyle))
    Story.append(Spacer(1, 2))
    # ptext = '<font size=12>%s: </font>' % ('Result ID')
    # Story.append(Paragraph(ptext, style=boldstyle))
    # Story.append(Spacer(1, 2))
    ptext = '<font size=12>%s: %s</font>' % ('Origin', 'Real-Time')
    Story.append(Paragraph(ptext, style=boldstyle))
    Story.append(Spacer(1, 2))
    ptext = '<font size=12>%s: %s</font>' % ('Search Date', search_date)
    Story.append(Paragraph(ptext, style=boldstyle))
    Story.append(Spacer(1, 2))
    ptext = '<font size=12>%s: %s</font>' % ('Search Time', search_time)
    Story.append(Paragraph(ptext, style=boldstyle))
    Story.append(Spacer(1, 2))
    # ptext = '<font size=12>%s: </font>' % ('Division')
    # Story.append(Paragraph(ptext, style=boldstyle))
    # Story.append(Spacer(1, 2))
    # ptext = '<font size=12>%s: %s</font>' % ('Assigned To', "US1-TSD-"+ full_name)
    # Story.append(Paragraph(ptext, style=boldstyle))
    # Story.append(Spacer(1, 2))
    # ptext = '<font size=12>%s: %s</font>' % ('Record Status', 'None')
    # Story.append(Paragraph(ptext, style=boldstyle))
    # Story.append(Spacer(1, 2))
    # ptext = '<font size=12>%s: </font>' % ('Updated By')
    # Story.append(Paragraph(ptext, style=boldstyle))
    # Story.append(Spacer(1, 2))
    # ptext = '<font size=12>%s: %s</font>' % ('Alert State', 'Open')
    # Story.append(Paragraph(ptext, style=boldstyle))
    # Story.append(Spacer(1, 2))
    # ptext = '<font size=12>%s: </font>' % ('Updated By')
    # Story.append(Paragraph(ptext, style=boldstyle))
    # Story.append(Spacer(1, 2))
    ptext = '<font size=12>%s: %s</font>' % ('Searched By', "US1-TSD-" + full_name)
    Story.append(Spacer(1, 2))
    Story.append(Paragraph(ptext, style=boldstyle))
    Story.append(Spacer(1, 5))

    line = MCLine_copy(455)
    Story.append(line)
    ptext = '<font size=12>%s</font>' % ("Watchlist Match Information")
    Story.append(Paragraph(ptext, style=boldstyle))
    Story.append(Spacer(1, 3))
    ptext = '<font size=12>%s</font>' % ("No Matches Found")
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 10))

    ptext = '<font size=12>%s</font>' % ("Input Information")
    Story.append(Paragraph(ptext, style=boldstyle))
    Story.append(Spacer(1, 3))
    ptext = '<font size=12>Entity Type&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Business</font>'
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 3))
    ptext = '<font size=12>%s</font>' % ("Predefined Search&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BOC STANDARD")
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 3))

    doc.build(Story)
