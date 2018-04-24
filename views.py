import urllib2
from flask import redirect, render_template, Blueprint, Response
from flask import request, url_for, send_file

#zz from flask_user import current_user, login_required, roles_accepted
#zz from app import app, db
from app import app
from app.data import logic_main

#zz from app.models import UserProfileForm

from app.data.graphdb_connector import Connector
import json
from app.data.genPdfReport import buildPdf
import time
import shutil

#zz from app.models import User
import string
import random
import os
import collections
from werkzeug.utils import secure_filename
from app.data.get_ocr import get_ocr
import app.data.config as data_config
import app.data.t24_module as t24_module
import app.data.config_module as config_module
from app.data.logic_crawler import NeedCaptcha
import celery_tasks
import app.data.get_pdf as get_pdf
from os import listdir
from os.path import isfile, join
import traceback
from app.data.config import NOT_FOUND
from app.common.public import *
from app.auth import current_user
import app.auth.userAdapter as userAdapter
from PIL import Image
##import imutils

UPLOAD_FOLDER = '/tmp/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mappings = json.loads((open(data_config.local_folder + "mapping.json", "rU")).read())


import logging
logging.basicConfig()
logger = logging.getLogger("Check")
logger.setLevel(logging.DEBUG)

logger_simple = logging.getLogger("Check_Simple")
logger_simple.setLevel(logging.DEBUG)

tmp_folder = "/tmp/"
#ocr_folder = "/root/Developer/OCR_V7/"
ocr_folder = "/install/OCR_V7/"

def escape(s):
    return str("\""+ s.replace("\"","\\\"") + "\"")

def commentsBridger_pdf_target(para, case_names):
    return data_config.target_folder + case_names + "/originalEvidence/" + data_config.create_new_pdf_names(para)

def commentsBridger_pdf_target_bk(para, case_names):
    return data_config.target_folder + case_names + "/originalEvidence/" + data_config.create_new_pdf_names_bk(para)

def getQuestionFields(questionID, caseID):
    logger.info("Get Question Fields: " + str(questionID) + " " + str(caseID))
    logger_simple.info("[Start] Get Question Fields: " + str(questionID) + " " + str(caseID))

    output_list = list()
    fields = []
    for item in mappings:
        if item["description"] == questionID:
            fields = item["fields"]
            break
    with open(os.path.join(data_config.pdf_folder, caseID, "index.json"), "rU") as indexFile:
        fileList = json.loads(indexFile.read())
        for idx, file in enumerate(fileList):
            filename = os.path.join(data_config.pdf_folder, caseID, file + "_entity.json")
            output_list.extend(getFieldValues(fields, filename, idx))

    logger.info("Get Question Fields Result: " + str(output_list))
    logger_simple.info("[Finish] Get Question Fields")
    return output_list


def getFieldValues(s, f, idx):
    logger.info("Get Field Values: " + str(s) + " " + str(f) + " " + str(idx))
    f_0 = open(f, 'r').read()
    fname = os.path.basename(f)
    jf = json.loads(f_0)
    t = jf['documentType']
    jf.pop('documentType')
    output_list = []
    for words in s:
        kw = words.split(' ', 1)[0]
        rest = words.split(' ', 1)[-1]
        if t == kw:
            logger.debug('start parsing the file with word: ' + str(rest))
            for files in jf:
                if rest in files:
                    output_dict = {"name": kw + " " + files, "page": idx, "value": jf[files]}
                    output_list.append(collections.OrderedDict(sorted(output_dict.items())))
        else:
            logger.warning("the files do not cotian field: " + kw)
    logger.info("Get Field Values Result: " + str(output_list))
    return output_list


def randompassword():
    logger.info("Generate Random Password")
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    size = random.randint(8, 12)
    return ''.join(random.choice(chars) for x in range(size))

pages_blueprint = Blueprint('pages', __name__, url_prefix='/')

# The Home page is accessible to anyone
@pages_blueprint.route('')
@login_required
def home_page():
    logger.info("Open Homepage")
    logger_simple.info("[Info] Open Homepage")
    return render_template('pages/home_page.html')


@pages_blueprint.route('case/<caseid>/<bocid>')
@login_required
def case_page(caseid,bocid):
    print bocid
    logger.info("Open Case Page")
    logger_simple.info("[Info] Open Case Page")
    return render_template('pages/case_page.html')


@pages_blueprint.route('check/<caseid>/<bocid>')
@login_required
def check_case_page(caseid, bocid):
    logger.info("Open Case Check Page: " + str(caseid) + " by " + str(bocid))
    logger_simple.info("[Info] Open Case Check Page")
    cnter = Connector(current_user.email)
    if bocid != cnter.getOperator(caseid):
        logger.warning("The different operator " + str(bocid) + " tries to use.")
        return "{'info':'failed'}"

    case = cnter.getCase(caseid)
    customer = case["customer"]
    cur_user = current_user.email
    # full_name = current_user.last_name + ", " + current_user.first_name
    full_name = current_user.email.split('@')[0]

    logger_simple.info("[Info] Start Check")
    celery_tasks.startCheck.delay(caseid, cur_user, full_name, customer, str(bocid))
    logger_simple.info("[Info] Finish Check")

    return "{'result':'successed'}"


@pages_blueprint.route('init_case/<caseid>/<bocid>')
@login_required
def init_case_page(caseid, bocid):
    logger.info("Open Initialize Case Page")
    print caseid
    print bocid
    return render_template('pages/init_case.html')

# The Admin page is accessible to users with the 'admin' role
@pages_blueprint.route('admin')
#zz @roles_accepted('admin')  # Limits access to users with the 'admin' role
def admin_page():
    logger.info("Open Admin Page")
    return render_template('pages/admin_page.html')

@pages_blueprint.route('pdf_evid/<caseid>')
@login_required
def pdf_evid_page(caseid):
    print caseid
    logger.info("Open Initialize Evid Page")
    return render_template('pages/pdf_evid.html')

'''zz start comment
=======

@pages_blueprint.route('pages/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    logger.info("Open User Profile Page")
    # Initialize form
    form = UserProfileForm(request.form, current_user)

    # Process valid POST
    if request.method == 'POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('pages.home_page'))

    # Process GET or invalid POST
    return render_template('pages/user_profile_page.html',
                           form=form)

@pages_blueprint.route("users")
@login_required
@roles_accepted('admin')
def get_userlist():
    logger.info("Get User List")
    users = User.query.all()
    user_list = []
    for user in users:
        user_json = dict()
        user_json["email"] = user.email
        user_json["username"] = user.username
        user_json["active"] = user.active
        user_json["roles"] = [role.name for role in user.roles]
        user_list.append(user_json)
    logger.info("User List: " + str(user_list))
    return json.dumps(user_list)

@pages_blueprint.route("users/delete/<user>")
@login_required
@roles_accepted('admin')
def delete_user(user):
    logger.info("Delete User: " + str(user))
    if request.method == 'GET':
        user = User.query.filter(User.username == user).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            logger.info("Deleted User: " + str(user))
            return Response("{info:'succeed'}")
    logger.info("Failed to Delete User: " + str(user))
    return Response("{error:'succeed'}", 500)


@pages_blueprint.route("users/reset/<username>")
@login_required
@roles_accepted('admin')
def reset_user(username):
    logger.info("Reset User: " + str(username))
    if request.method == 'GET':
        user = User.query.filter(User.username == username).first()
        if user:
            password = randompassword()
            print password
            user.password = app.user_manager.hash_password(password)
            db.session.commit()
            res = {"username": username, "password": password}
            logger.info("Reset User: " + str(username))
            return json.dumps(res)
    logger.info("Failed to Reset User: " + str(username))
    return Response("{error:'succeed'}", 500)
zz end comment '''

@pages_blueprint.route("addpdf/<bocid>", methods=['POST'])
@login_required
def add_file(bocid):
    logger.info("Add File")
    print bocid

    if request.method == 'POST':
        print "Inside addpdf."
        caseID = request.form["newcaseID"]
        file = request.files['file']
        client = request.form["clientID"]
        print caseID
        print file
        print client
        print "started"
        if file :
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print "Will compare filename and case name================="
            print filename[:-4]
            print caseID[:-4]
            if filename[:-4] == caseID[:-4]:
                return "New file name can not equal to case name."
            print "save"
            print filepath
            file.save(filepath)
            print "done"
            if caseID.endswith('.new'):
                caseID = caseID[:-4]
            print "caseID changed to:"
            print caseID
            newcaseID = caseID + ".new"
            celery_tasks.runOCRAddPdf(client, caseID, newcaseID, current_user.email, filepath)
            logger.info("Added File: " + str(filepath))
            return '{"id":"' + str(filename[:-4]) + '"}'
        logger.info("Failed to Add File")

    return '{"info":"failed"}'



@pages_blueprint.route("addsecondarypdf/<bocid>", methods=['POST'])
@login_required
def upload_secondary_file(bocid):
    print bocid
    logger.info("Add File")
    if request.method == 'POST':
        originalcaseID = request.form["caseID"]
        newcaseID = request.form["newcaseID"]
        nextPage = request.form["currentPage"]
        position = request.form["position"]

        cnter = Connector(current_user.email)
        if bocid != cnter.getOperator(originalcaseID):
            logger.warning("The different operator " + str(bocid) + " tries to use.")
            return '{"info":"failed"}'

        print "Will print originalcaseID and newcaseID"
        print originalcaseID
        print newcaseID
        print nextPage
        print "started"

        if position == "Before this page":
            nextPage = int(nextPage)
        else:
            nextPage = int(nextPage)
            nextPage = nextPage + 1


        print "Will print nextPage"
        print nextPage

        print os.path.join(data_config.pdf_folder, newcaseID, "index.json")
        with open(os.path.join(data_config.pdf_folder, newcaseID, "index.json"), "rU") as page_file:
            newpages = json.loads(page_file.read())
            print "newcase Opened"
            print newpages

        print os.path.join(data_config.pdf_folder, originalcaseID, "index.json")
        with open(os.path.join(data_config.pdf_folder, originalcaseID, "index.json"), "rU") as page_file_orig:
            originalpages = json.loads(page_file_orig.read())
            print "originalcase Opened"

        for item in newpages:
            originalpages.insert(nextPage,item)
            nextPage = nextPage +1

        with open(os.path.join(data_config.pdf_folder, originalcaseID, "index.json"), "w") as fn:
            print originalpages
            fn.write(json.dumps(originalpages))
            print "Two cases merged"
        folder = os.path.join(data_config.pdf_folder, newcaseID)
        shutil.rmtree(folder)
    return '{"info":"failed"}'



@pages_blueprint.route("editcase/<bocid>", methods=['POST'])
@login_required
def edit_case(bocid):
    print "Inside editcase function"
    tot_amt=request.form['totalAmount']
    id=request.form['id']
    jno=request.form['jno']
    newType = request.form['newType']
    print "New TyPE==========="
    print newType
    cnter = Connector(current_user.email)
    data={'bocRef':jno,'totalAmount': tot_amt, "transactionType": newType}
    cnter.saveCase(id,data)
    return '{"result":"succeed"}'
@pages_blueprint.route("createcase/<bocid>", methods=['POST'])
@login_required
def upload_file(bocid):
    print "Inside createcase function!!!!!!!!!!!!!!!!"
    print bocid
    logger.info("Upload File")
    if request.method == 'POST':
        client = request.form["client"]
        clientID = request.form["clientID"]
        referenceNo = request.form["referenceNo"]
        bocRef = request.form["bocRef"]
        transactionType = request.form["type"]
        totalAmount = request.form["totalAmount"]
        file = request.files['file']

        caseid = file.filename[:-4]
        print caseid
        cnter = Connector(current_user.email)

        cases = cnter.filterCases(current_user.email, str(bocid))
        print "Will print cases!!!!!!!!!!"
        print cases
        for case in cases:
            if case["referenceNo"] == referenceNo:
                print "Same referenceNo detected!!!!!!!!"
                return "Duplicated referenceNo"

        if cnter.getV(caseid) is not None:
            print "Case is not first time touched"
            logger.warning("The different operator " + str(bocid) + " tries to use.")
            # return '{"info":"failed"}'
            return "PDF file has been edited"

        target_file_path = os.path.join(data_config.pdf_folder, caseid)
        ##Delete .original .record & .retrieve if exist
        originalPath = target_file_path + ".original"
        recordPath = target_file_path + ".record"
        retrievePath = target_file_path + ".retrieve"
        newPath = target_file_path + ".new"
        if os.path.exists(originalPath):
            shutil.rmtree(originalPath)
        if os.path.exists(newPath):
            shutil.rmtree(newPath)
        if os.path.exists(recordPath):
            shutil.rmtree(recordPath)
        if os.path.exists(retrievePath):
            shutil.rmtree(retrievePath)
        if os.path.exists(target_file_path):
            shutil.rmtree(target_file_path)



        logger.info("started")
        if file :
            filename = secure_filename(file.filename)
            print filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            caseid = filename[:-4]
            logger.info("save: " + filepath)
            file.save(filepath)
            logger.info("done: " + filepath)
            cnter = Connector(current_user.email)
            cnter.createCase(current_user.email, bocid, client, caseid, clientID, referenceNo, bocRef, transactionType, totalAmount)
            celery_tasks.runOCR.delay(client, caseid, current_user.email, filepath)
            logger.info("Uploaded File: " + filepath)
            return '{"id":"' + str(filename[:-4]) + '"}'
    logger.info("Failed to Upload File")
    return '{"info":"failed"}'

@pages_blueprint.route("uploadlloyds", methods=['POST'])
@login_required
def upload_lloyds():
    logger.info("Upload ID Configurations")
    print
    if request.method == 'POST':
        bocID = request.form["bocID"]
        lloydsID = request.form["lloydsID"]
        lloydsPassword = request.form["lloydsPassword"]
        bridgerID = request.form["bridgerID"]
        bridgerPassword = request.form["bridgerPassword"]
        dowjonesID = request.form["dowjonesID"]
        dowjonesPassword = request.form["dowjonesPassword"]

        login_folder = 'app/static/login-data'
        boc_user_json = bocID + '.json'
        userInfo = {'lloydsID': lloydsID, 'lloydsPassword': lloydsPassword, 'bridgerID': bridgerID,
                    'bridgerPassword': bridgerPassword, 'dowjonesID': dowjonesID, 'dowjonesPassword': dowjonesPassword}
        #1 Create a folder which will contain JSON files for every user.
        if not os.path.exists(login_folder):
            os.makedirs(login_folder)

        #2 Check whether there is such JSON file that matches bocID.json
        if os.path.isfile(login_folder + '/'+ boc_user_json) and os.access(login_folder + '/'+ boc_user_json, os.R_OK):
            print "File exists and is readable"
        else:
            print "Either file is missing or is not readable"
            os.mknod(login_folder + '/'+ boc_user_json)
            print "Will check whether json exists"
            print os.path.isfile(boc_user_json) and os.access(boc_user_json, os.R_OK)

        #3 Write userInfo into that JSON
        with open(login_folder + '/' + boc_user_json, 'w') as outfile:
            json.dump(userInfo, outfile)
            logger.info("Configuration Information stored.")

    logger.info("Failded to store")
    return '{"info":"failed"}'


@pages_blueprint.route("renderJsonData", methods=['POST'])
@login_required
def renderjsondata():
    logger.info("Render Json file data")
    print
    if request.method == 'POST':
        caseID = request.form["caseid"]
        evidence_name = request.form["eviName"]

        print caseID
        print evidence_name
        abstract_json = data_config.target_folder + caseID + "/bridgerJson/" + evidence_name + "temp.json"
        with open(abstract_json, 'r') as json_file:
            temp_date = json.load(json_file)

    logger.info("Failded to store")
    return json.dumps(temp_date)

@pages_blueprint.route("updateNewJson", methods=['POST'])
@login_required
def updatejsondata():
    logger.info("Update Json file data")
    print
    if request.method == 'POST':
        caseID = request.form["caseid"]
        evidence_name = request.form["eviname"]
        modification = json.loads(request.form["modification"])

        print caseID
        print evidence_name
        temp_json_file = data_config.target_folder + caseID + "/bridgerJson/" + evidence_name + "temp.json"
        target_json_file = data_config.target_folder + caseID + "/bridgerJson/" + evidence_name + ".json"

        ##update to temp json file
        with open(temp_json_file, "r+") as test_file:
            test_data = json.load(test_file)
            for index_temp, item_temp in enumerate(test_data):
                for item in modification:
                    if item["index"] ==(index_temp + 1) and item.has_key("bridgerComments") and len(item["bridgerComments"])!=0:
                        item_temp["bridgerComments"] = item["bridgerComments"]
                        test_file.seek(0)
                        test_file.write(json.dumps(test_data))
                        test_file.truncate()
                    elif item["index"] == (index_temp + 1) and item_temp.has_key("bridgerComments") and ("bridgerComments" not in item):
                        item_temp.pop('bridgerComments', None)
                        test_file.seek(0)
                        test_file.write(json.dumps(test_data))
                        test_file.truncate()

        ##update to real json file
        with open(target_json_file, "r+") as origin_file:
            origin_data = json.load(origin_file)
            for index_temp, item_temp in enumerate(origin_data):
                for item in modification:
                    if item["index"] == (index_temp + 1) and item.has_key("bridgerComments") and len(item["bridgerComments"]) != 0:
                        item_temp["bridgerComments"] = item["bridgerComments"]
                        origin_file.seek(0)
                        origin_file.write(json.dumps(origin_data))
                        origin_file.truncate()
                    elif item["index"] == (index_temp + 1) and item_temp.has_key("bridgerComments") and ("bridgerComments" not in item):
                        item_temp.pop('bridgerComments', None)
                        origin_file.seek(0)
                        origin_file.write(json.dumps(origin_data))
                        origin_file.truncate()



        # ##code working upon here
        # ##Code below are used to insert bridgerComments
        # with open(config.target_folder + case_name + "/bridgerJson/san_felipe.json") as data_file_1:
        #     temp_data = json.load(data_file_1)
        #     for item in temp_data:
        #         with open(name + "_bridge_temp.json", "r+") as orig_file:
        #             orig_data = json.load(orig_file)
        #             for indexO, target_item in enumerate(orig_data):
        #                 if indexO == (item["index"] - 1):
        #                     if item.has_key("bridgerComments") and len(item["bridgerComments"])!=0:
        #                         target_item["bridgerComments"] = item["bridgerComments"]
        #                         orig_file.seek(0)
        #                         orig_file.write(json.dumps(orig_data))
        #                         orig_file.truncate()
        

        millies = int(round(time.time() * 1000))
        print millies
        dynamic_pdf_target = data_config.target_folder + caseID + "/originalEvidence/" + evidence_name.replace(" ", "_").replace("?", "_") + str(millies) + ".pdf"
        try:

            # if os.path.isfile(commentsBridger_pdf_target(evidence_name, caseID)):
            #     print "WIll generate file to _comment_bk.pdf====="
            #     buildPdf(commentsBridger_pdf_target_bk(evidence_name, caseID), target_json_file)
            #     new_url = data_config.target_folder + caseID + "/originalEvidence/" + evidence_name + "_comments_bk.pdf"
            # else:
            #     print "Will generate file to _comment.pdf====="
            #     buildPdf(commentsBridger_pdf_target(evidence_name, caseID), target_json_file)
            #     new_url = data_config.target_folder + caseID + "/originalEvidence/" + evidence_name + "_comments.pdf"
            buildPdf(dynamic_pdf_target, target_json_file)

        except:
            logger.error("Failed to generate PDF for:" + str(evidence_name))
            logger.error(traceback.format_exc())
            return NOT_FOUND
        new_url = dynamic_pdf_target
        # if "_comments_bk.pdf" in new_url and os.path.isfile(commentsBridger_pdf_target(evidence_name, caseID)):
        #     os.remove(commentsBridger_pdf_target(evidence_name, caseID))
        # elif "_comments.pdf" in new_url and os.path.isfile(commentsBridger_pdf_target_bk(evidence_name, caseID)):
        #     os.remove(commentsBridger_pdf_target_bk(evidence_name, caseID))

        print "print new_url===="
        print new_url
        if "./app" in new_url:
            new_url = new_url.replace("./app", "")
        url_data = {"url":new_url, }

    logger.info("Failded to store")
    return json.dumps(url_data)






@pages_blueprint.route("getBocID")
@login_required
def get_BOCID():
    logger.info("Inside getBOCID function")

@pages_blueprint.route("retrieveOriginal/<bocid>", methods=['POST'])
@login_required
def retrieve_pages(bocid):
    print bocid
    logger.info("Inside retrieve function")
    if request.method == 'POST':
        caseID = request.form["caseID"]

        # cnter = Connector(current_user.email)
        # if bocid != cnter.getOperator(caseID):
        #     logger.warning("The different operator " + str(bocid) + " tries to use.")
        #     return '{"info":"failed"}'

        folder = data_config.pdf_folder+caseID+'/'
        ##Empty the current folder
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

        ##copy files to current folder
        src = data_config.pdf_folder + caseID + '.original' + '/'
        dest = data_config.pdf_folder + caseID + '/'
        src_files = os.listdir(src)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, dest)

        print "Successfully retrieve to Original version"
    return '{"info":"failed"}'

@pages_blueprint.route("retrievePrevious/<bocid>", methods=['POST'])
@login_required
def retrieve_previous(bocid):
    logger.info("Inside retrieve previous function")
    print bocid
    if request.method == 'POST':
        caseID = request.form["caseID"]
        currentFolder = data_config.pdf_folder + caseID + '/'
        recordFolder = data_config.pdf_folder + caseID + '.record' + '/'


        # Empty the current folder
        for the_file in os.listdir(currentFolder):
            file_path = os.path.join(currentFolder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    # elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)

        ##copy files to record folder
        src = recordFolder
        dest = currentFolder
        src_files = os.listdir(src)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, dest)

        print "Successfully retrieved to previous version"
    return '{"info":"failed"}'

@pages_blueprint.route("changeToUp", methods=['POST'])
@login_required
def change_type():
    print "Inside changeToUp"
    pageNum = request.form["pageNum"]
    print pageNum
    # caseID = pageNum[:-6]
    pageComb = pageNum.split("_")
    if len(pageComb) ==2:
        caseID = pageComb[0]
    else:
        caseID = ""
        del pageComb[-1]
        print pageComb
        for item in pageComb:
            caseID += item
            caseID +="_"
    print caseID
    if caseID.endswith("_"):
        caseID = caseID[:-1]
    jsonPath = data_config.pdf_folder + caseID + "/" + pageNum + "_entity.json"
    tempPath = data_config.pdf_folder + caseID + "/" + pageNum + "x_entity.json"
    oldjson = ""
    print jsonPath
    with open(jsonPath, "r") as fn:
        oldjson = json.loads(fn.read())
        print oldjson
        print oldjson["documentType"]
        rest = oldjson["documentType"][1:]
        print "rest:"+ rest
        length = len(oldjson["documentType"])
        restLen = length - 1
        firstLet = oldjson["documentType"][:-restLen]
        print firstLet
        firstLet = firstLet.capitalize()
        print "firsdt letter:" + firstLet
        newType = firstLet + rest
        print "newType:" + newType
        oldjson["documentType"] = newType
        print oldjson
        fn.close()

    with open(jsonPath, 'w') as outfile:
        print oldjson
        json.dump(oldjson, outfile)
        outfile.close()

    # os.remove(jsonPath)
    # #
    # # 1 Check whether there is such JSON file that matches bocID.json
    # if os.path.isfile(tempPath) and os.access(tempPath,os.R_OK):
    #     print "File exists and is readable"
    # else:
    #     print "Either file is missing or is not readable"
    #     os.mknod(tempPath)
    #     print "Will check whether json exists"
    #     print os.path.isfile(tempPath) and os.access(tempPath, os.R_OK)
    #
    # # 2 Write data into that JSON
    # with open(tempPath, 'w') as outfile:
    #     print oldjson
    #     json.dump(oldjson, outfile)
    #     outfile.close()
    #
    # os.rename(tempPath,jsonPath)
    #
    # # os.remove(jsonPath)
    # # with open(tempPath, "r") as fn:
    # #     tempJson = json.loads(fn.read())
    # #     print tempJson
    # #
    # if os.path.isfile(jsonPath) and os.access(jsonPath,os.R_OK):
    #     print "File exists and is readable"
    # else:
    #     print "Either file is missing or is not readable"
    #     os.mknod(jsonPath)
    #     print "Will check whether json exists"
    #     print os.path.isfile(jsonPath) and os.access(jsonPath, os.R_OK)
    #
    # with open(jsonPath, 'w') as outfile:
    #     print oldjson
    #     json.dump(oldjson, outfile)
    #     outfile.close()



    # os.rename(jsonPath,(data_config.pdf_folder + caseID + "/" + pageNum + "xx_entity.json"))
    # os.rename((data_config.pdf_folder + caseID + "/" + pageNum + "xx_entity.json"),(data_config.pdf_folder + caseID + "/" + pageNum + "_entity.json"))

    # with open(jsonPath, 'r+') as f:
    #     json_data = json.load(f)
    #     print json_data
    #     print json_data["documentType"]
    #     rest = json_data["documentType"][1:]
    #     print "rest:"+ rest
    #     length = len(json_data["documentType"])
    #     restLen = length - 1
    #     firstLet = json_data["documentType"][:-restLen]
    #     print firstLet
    #     firstLet = firstLet.capitalize()
    #     print "firsdt letter:" + firstLet
    #     newType = firstLet + rest
    #     print "newType:" + newType
    #     json_data["documentType"] = newType
    #     f.seek(0)
    #     f.write(json.dumps(json_data))
    #     f.truncate()
    return "Success"

@pages_blueprint.route("recordPage/<bocid>", methods=['POST'])
@login_required
def record_pages(bocid):
    logger.info("Inside record function")
    print bocid
    if request.method == 'POST':
        caseID = request.form["caseID"]
        folder = data_config.pdf_folder+caseID+'/'

        #create record folder
        recordPath = data_config.pdf_folder+caseID+'.record' +'/'
        if not os.path.exists(recordPath):
            os.makedirs(recordPath)

        for dirpath, dirnames, files in os.walk(recordPath):
            if files:
                print(dirpath, 'has files')

                #Empty the current folder
                for the_file in os.listdir(recordPath):
                    file_path = os.path.join(recordPath, the_file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
                    except Exception as e:
                        print(e)

                ##copy files to record folder
                src = folder
                dest = recordPath
                src_files = os.listdir(src)
                for file_name in src_files:
                    full_file_name = os.path.join(src, file_name)
                    if (os.path.isfile(full_file_name)):
                        shutil.copy(full_file_name, dest)

                print "Successfully Copied"

            if not files:
                print(dirpath, 'is empty')

                ##copy files to record folder
                src = folder
                dest = recordPath
                src_files = os.listdir(src)
                for file_name in src_files:
                   full_file_name = os.path.join(src, file_name)
                   if (os.path.isfile(full_file_name)):
                      shutil.copy(full_file_name, dest)

                print "Successfully Copied"

        print "Pages recorded"
    return '{"info":"failed"}'



@pages_blueprint.route("rotatePage", methods=['POST'])
@login_required
def rotate_page():
    logger.info("Rotate function")
    if request.method == 'POST':
        pageNumber = request.form["page"]
        caseID = request.form["caseid"]
        print type(pageNumber)
        pagePath = data_config.pdf_folder + caseID + "/"+ caseID + "_page" + str(int(pageNumber)+1) + ".png" 

        with open(data_config.pdf_folder + caseID + "/index.json", "rU") as page_file:
            pagesIndex = json.loads(page_file.read())

        print "pagesIndex=============="
        print pagesIndex
        current_page = pagesIndex[int(pageNumber)]

        print "current_page========="
        print current_page

        pagePath = data_config.pdf_folder + caseID + "/"+ current_page + ".png"        

        print "page======"
        print pageNumber
        img = Image.open(pagePath)
        width, height = img.size
        print width
        print height
        if width > height:
            
            new_image = img.resize((width, width))
        else:
            new_image = img.resize((height, height))
        pagePathBK = data_config.pdf_folder + caseID + "/" + caseID + "_page" + str(int(pageNumber) + 1) + "bk.png"
        #new_image.save(pagePathBK)
        new_image.save(pagePath)
        img2 = Image.open(pagePath)
        img3 = img2.rotate(-90)
        img3.save(pagePath)
        ##rotate = imutils.rotate_bound(pagePath, -90)
        ##rotate.save(pagePath)

    return '{"info":"failed"}'





@pages_blueprint.route("evidence/<bocid>", methods=['POST'])
@login_required
def upload_evidence(bocid):
    print bocid
    logger.info("Upload Evidence")
    if request.method == 'POST':
        caseid = request.form["caseid"]

        cnter = Connector(current_user.email)
        if bocid != cnter.getOperator(caseid):
            logger.warning("The different operator " + str(bocid) + " tries to use.")
            return '{"info":"failed"}'

        question = request.form["question"]
        file = request.files['file']
        filepath = ""
        if file :
            filename = secure_filename(file.filename)
            filepath = os.path.join(data_config.pdf_folder, caseid,"originalEvidence")
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            logger.info("save: " + filepath)
            file.save(os.path.join(filepath,filename))
            logger.info("done: " + filepath)
            cnter = Connector(current_user.email)
            urlpath = data_config.data_folder+caseid+"/originalEvidence/"+filename
            # cnter.addEvidence(caseid, question, urlpath)
            logger.info("Uploaded File: " + filename + " to " + filepath)
            return '{"url":"' + urlpath + '"}'
    return '{"info":"failed"}'

@pages_blueprint.route("cases/<bocid>")
@login_required
def get_cases(bocid):
    print bocid
    cnter = Connector(current_user.email)
    # cases = cnter.queryCases(current_user.email)
    cases = cnter.filterCases(current_user.email, str(bocid))
    for case in cases:
        # try:
        jsonPath = os.path.join(data_config.pdf_folder, case["id"], "index.json")
        if os.path.exists(jsonPath):
            with open(os.path.join(data_config.pdf_folder, case["id"], "index.json"), "rU") as page_file:
                pages = json.loads(page_file.read())
                case["pages"] = len(pages)
        # except IOError:
        else:
            case["pages"] = 0

    return json.dumps(cases)


@pages_blueprint.route("casedata/<caseid>/<bocid>")
@login_required
def get_case(caseid,bocid):
    print bocid
    cnter = Connector(current_user.email)
    result = dict()
    case = cnter.getCase(caseid)
    logger.debug("Case: " + str(caseid) + " " + str(case))
    result["customer"] = case["customer"]
    result["transactionType"] = case["transactionType"]
    result["referenceNo"] = case["referenceNo"]
    result["clientID"] = case["clientID"]
    result["bocRef"] = case["bocRef"]
    result["customerName"] = case["customerName"] if "customerName" in case else ""
    result["totalAmount"] = case["totalAmount"] if "totalAmount" in case else ""
    result["remark"] = case["remark"] if "remark" in case else ""
    with open(os.path.join(data_config.pdf_folder, caseid, "index.json"), "rU") as page_file:
        pages = json.loads(page_file.read())
        result["pages"] = pages
    logger.debug("Casedata Result: " + str(result))
    return json.dumps(result)

@pages_blueprint.route("delpage", methods=['POST'])
@login_required
def delete_page():
    if request.method == 'POST':
        caseid = request.form["caseID"]
        print caseid
        page = int(request.form["page"])
        print page

        # print current_user.bocID
        with open(os.path.join(data_config.pdf_folder, caseid, "index.json"), "rU") as page_file:
            pages = json.loads(page_file.read())
            os.remove(os.path.join(data_config.pdf_folder, caseid, pages[page] + ".png"))
            os.remove(os.path.join(data_config.pdf_folder, caseid, pages[page] + "_entity.json"))
            del pages[page]
        with open(os.path.join(data_config.pdf_folder, caseid, "index.json"), "w") as page_file:
            page_file.write(json.dumps(pages))
        return '{"result":"succeed"}'
    return '{"info":"failed"}'

@pages_blueprint.route("delcase/<bocid>", methods=['POST','DELETE'])
@login_required
def delete_case(bocid):
    print bocid
    cnter = Connector(current_user.email)
    cnter.deleteCase(request.form['id'])
    caseid = request.form['id']
    tmp = app.config['UPLOAD_FOLDER']
    path=os.path.join(data_config.pdf_folder, caseid)
    ##Delete .original .record & .retrieve if exist
    originalPath = path + ".original"
    recordPath = path + ".record"
    retrievePath = path + ".retrieve"
    if os.path.exists(originalPath):
        shutil.rmtree(originalPath)
    if os.path.exists(recordPath):
        shutil.rmtree(recordPath)
    if os.path.exists(retrievePath):
        shutil.rmtree(retrievePath)


    path_bkp=path+'.bkp'
    tmp_path=os.path.join(tmp, caseid)
    tmp_path_bkp=os.path.join(tmp, caseid + '.bkp')
    if os.path.exists(path_bkp):
        shutil.rmtree(path_bkp)
        os.rename(path, path_bkp)
    else:
        os.rename(path, path_bkp)
    if os.path.exists(tmp_path_bkp):
        shutil.rmtree(tmp_path_bkp)
        os.rename(tmp_path, tmp_path_bkp)
    else:
        os.rename(tmp_path, tmp_path_bkp)
    return '{"result":"succeed"}'

@pages_blueprint.route("customer/<name>")
@login_required
def search_customer(name):
    result = t24_module.completeWord(name)

    return json.dumps(result)

@pages_blueprint.route("customerid/<cid>")
@login_required
def search_customerid(cid):
    result = t24_module.completeID(cid)

    return json.dumps(result)

# @pages_blueprint.route("customer")
# @login_required
# def search_customer():
#     result = t24_module.getAllWord()
#
#     return json.dumps(result)



@pages_blueprint.route("getConfig")
@login_required
def get_config():
    result = config_module.config_test()
    print "Will print result from config_module"
    print result

    # return json.dumps(result)



@pages_blueprint.route("loadquestion/<caseID>/<question>/<bocid>")
@login_required
def load_question(caseID, question, bocid):
    print bocid
    result = dict()
    cnter = Connector(current_user.email)
    node = cnter.queryQuestion(caseID, question)
    fieldsList = getQuestionFields(question, caseID)
    # print json.dumps(fieldsList)
    if not node:
        result["answered"] = True
        result["comment"] = ""
        result["evidence"] = json.dumps("")
        result["answer"] = "manual"
        result["alert"] = ""
    else:
        result["answered"] = True
        result["comment"] = ""
        result["evidence"] = ""
        result["answer"] = ""
        if "comment" in node:
            result["comment"] = node["comment"]
        if "evidence" in node:
            result["evidence"] = node["evidence"]
        if "answer" in node:
            result["answer"] = node["answer"]
        if "alert" in node:
            result["alert"] = node["alert"]
    result["fields"] = fieldsList
    print result
    return json.dumps(result)


@pages_blueprint.route("casesummary/<caseID>")
@login_required
def load_summary(caseID):
    result = dict()
    cnter = Connector(current_user.email)
    nodes = cnter.queryQuestions(caseID)
    return json.dumps(nodes)


@pages_blueprint.route("exportpdf/<caseID>")
@login_required
def export_pdf(caseID):
    print "Inside exportPdf============================="
    cnter = Connector(current_user.email)
    result = dict()
    case = cnter.getCase(caseID)
    result["type"] = case["transactionType"]
    print "Will print type!!!!!!!!!!!!!!!!!!!!!"
    print result["type"]
    result["TFNumber"] = case["referenceNo"] + " " + case["bocRef"]
    result["customer"] = case["customerName"] if "customerName" in case else ""
    result["amount"] = case["totalAmount"] if "totalAmount" in case else ""
    final_result = ""
    print "amount========="
    print result["amount"]
    if "," not in result["amount"]:
        if "." in result["amount"]:
            amount_array = result["amount"].split(".")
            print len(amount_array)
            print amount_array[0][:1]
            flag = ""
            try:
                int(amount_array[0][:1])
                flag = True
            except:
                flag = False
            print "flag======="
            print flag
            if flag == True:
                print len(amount_array[0])
                # first_num = int(amount_array[0])
                count_three = len(amount_array[0]) / 3
                remain_three = len(amount_array[0]) % 3
                if count_three!=0:
                    if remain_three!=0:
                        first_num_1 = amount_array[0][:remain_three]
                        first_num_rest = amount_array[0][remain_three:]
                        print first_num_1

                        first_num_2 = [first_num_rest[i: i + 3] for i in range(0, len(first_num_rest), 3)]
                        print "first_num======"
                        print first_num_2
                        second_first = ""
                        for item in first_num_2:
                            second_first = second_first + "," + item
                        total_first = first_num_1 + second_first
                        print "total first======"
                        print total_first
                        print "total amount========"
                        print total_first + "." + amount_array[1]
                        final_result = total_first + "." + amount_array[1]
                        print "final_result=============="
                        print final_result
                    else:
                        first_num_2 = [amount_array[0][i: i + 3] for i in range(0, len(amount_array[0]), 3)]
                        print "first_num======"
                        print first_num_2
                        second_first = ""
                        for item in first_num_2:
                            second_first = second_first + "," + item
                        total_first = second_first[1:]
                        print total_first
                        print "total amount======"
                        print total_first + '.' + amount_array[1]
                        final_result = total_first + '.' + amount_array[1]
                        print "final_result=============="
                        print final_result

            else:
                count_three = (len(amount_array[0])-3) / 3
                remain_three = (len(amount_array[0])- 3) % 3
                if count_three!=0:
                    if remain_three!=0:
                        first_num_1 = amount_array[0][:(remain_three + 3)]
                        first_num_rest = amount_array[0][(remain_three+3):]
                        print first_num_1

                        first_num_2 = [first_num_rest[i: i + 3] for i in range(0, len(first_num_rest), 3)]
                        print "first_num======"
                        print first_num_2
                        second_first = ""
                        for item in first_num_2:
                            second_first = second_first + "," + item
                        total_first = first_num_1 + second_first
                        print "total first======"
                        print total_first
                        print "total amount========"
                        print total_first + "." + amount_array[1]
                        final_result = total_first + "." + amount_array[1]
                        print "final_result=============="
                        print final_result
                    else:
                        first_num_2 = [amount_array[0][3:][i: i + 3] for i in range(0, len(amount_array[0]), 3)]
                        print "first_num======"
                        print first_num_2
                        second_first = ""
                        for item in first_num_2:
                            second_first = second_first + "," + item
                        total_first = second_first[1:]
                        print total_first
                        print "total amount======"
                        print amount_array[0][:3] + total_first + '.' + amount_array[1]
                        final_result = amount_array[0][:3] + total_first + '.' + amount_array[1]
                        print "final_result=============="
                        print final_result

        else:
            flag = ""
            try:
                int(result["amount"][:1])
                flag = True
            except:
                flag = False
            print "flag======="
            print flag
            if flag == True:
                print len(result["amount"])
                # first_num = int(amount_array[0])
                count_three = len(result["amount"]) / 3
                remain_three = len(result["amount"]) % 3
                if count_three!=0:
                    if remain_three!=0:
                        first_num_1 = result["amount"][:remain_three]
                        first_num_rest = result["amount"][remain_three:]
                        print first_num_1

                        first_num_2 = [first_num_rest[i: i + 3] for i in range(0, len(first_num_rest), 3)]
                        print "first_num======"
                        print first_num_2
                        second_first = ""
                        for item in first_num_2:
                            second_first = second_first + "," + item
                        total_first = first_num_1 + second_first
                        print "total first======"
                        print total_first
                        final_result = total_first
                        print "final_result=============="
                        print final_result
                    else:
                        first_num_2 = [result["amount"][i: i + 3] for i in range(0, len(result["amount"]), 3)]
                        print "first_num======"
                        print first_num_2
                        second_first = ""
                        for item in first_num_2:
                            second_first = second_first + "," + item
                        total_first = second_first[1:]
                        print total_first
                        final_result = total_first
                        print "final_result=============="
                        print final_result
            else:
                count_three = (len(result["amount"])-3) / 3
                remain_three = (len(result["amount"])-3) % 3
                if count_three!=0:
                    if remain_three!=0:
                        first_num_1 = result["amount"][:(remain_three + 3)]
                        first_num_rest = result["amount"][(remain_three + 3):]
                        print first_num_1

                        first_num_2 = [first_num_rest[i: i + 3] for i in range(0, len(first_num_rest), 3)]
                        print "first_num======"
                        print first_num_2
                        second_first = ""
                        for item in first_num_2:
                            second_first = second_first + "," + item
                        total_first = first_num_1 + second_first
                        print "total first======"
                        print total_first
                        print "total amount========"
                        print total_first
                        final_result = total_first
                        print "final_result=============="
                        print final_result
                    else:
                        first_num_2 = [result["amount"][3:][i: i + 3] for i in range(0, len(result["amount"]), 3)]
                        print "first_num======"
                        print first_num_2
                        second_first = ""
                        for item in first_num_2:
                            second_first = second_first + "," + item
                        total_first = second_first[1:]
                        print total_first
                        print "total amount======"
                        print result["amount"][:3] + total_first
                        final_result = result["amount"][:3] + total_first[:-1]
                        print "final_result=============="
                        print final_result
    else:
        final_result = result["amount"]



    result["amount"] = final_result
    if ",." in result["amount"]:
        print ",.detected========="
        result["amount"] = str(result["amount"]).replace(",.", ".")
        print result["amount"]
    result["remark"] = case["remark"] if "remark" in case else ""
    nodes = cnter.queryQuestions(caseID)
    result["questions"] = list()
    for node in nodes:
        if node["label"] == "question":
            question = dict()
            question["answer"] = node["answer"]
            question["comment"] = node["comment"] if "comment" in node else ""
            question["description"] = node["id"].split("-")[-1]
            result["questions"].append(question)
    pdfPath = "./app/data/template.pdf"
    questionsPosPath = "./app/data/questionsPos.txt"
    infoPosPath = "./app/data/infoPos.txt"
    tempFilePath = "./app/data/tempFiles"
    outPDFPath = "." + tempFilePath + "/" + caseID + ".pdf"
    os.system("rm -f " + outPDFPath)
    print "before buildpdf================"
    print result
    get_pdf.buildPdf(pdfPath, caseID, result, questionsPosPath, tempFilePath, infoPosPath)
    print "after buildpdf================"
    return send_file(outPDFPath, attachment_filename=caseID + '.pdf')


@pages_blueprint.route("stat/<caseID>")
@login_required
def get_stat(caseID):
    print "inside stat"
    cnter = Connector(current_user.email)
    result = {"total":{"bloomberg":0, "dowjones":0, "lloyds":0, "bridgerInsight":0, "alibaba":0},
              "success": {"bloomberg": 0, "dowjones": 0, "lloyds": 0, "bridgerInsight": 0, "alibaba": 0}}
    names = {"total": {"bloomberg": set(), "dowjones": set(), "lloyds": set(), "bridgerInsight": set(), "alibaba": set()},
              "success": {"bloomberg": set(), "dowjones": set(), "lloyds": set(), "bridgerInsight": set(), "alibaba": set()}}
    crawlers = ["bloomberg", "dowjones", "lloyds", "bridgerInsight", "alibaba"]

    for question in cnter.queryQuestions(caseID):
        print "will print question"
        print question
        if question["label"] == "question" and "evidence" in question:
            evidenceFileName = "./app" + question["evidence"]
            with open(evidenceFileName, "r") as evidenceFile:
               evidences = json.load(evidenceFile)
            for evidence in evidences:
                print evidence
                e_type = evidence["type"]
                if not e_type in crawlers:
                  continue
                if (not "url" in evidence and e_type != "lloyds") or not "name" in evidence:
                  continue
                name = evidence["name"]
                names["total"][e_type].add(name)  # Append total evidence
                if not evidence.get("isManual", False):
                    names["success"][e_type].add(name)

    for crawler in crawlers:
        result["total"][crawler] = len(names["total"][crawler])
        result["success"][crawler] = len(names["success"][crawler])

    return json.dumps(result)





@pages_blueprint.route("newEvidence/<caseID>")
@login_required
def get_new_evidence(caseID):
    print "inside get new evidences"
    path = data_config.pdf_folder + caseID + "/newEvidence"
    if not os.path.exists(path):
        result = {"file":[],"eurl":""}
    else:
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
        print onlyfiles
        result = {"file":[],"eurl":""}
        result["file"] = onlyfiles
        filepath = data_config.current_url+ "bocbtvm/cases/" + caseID + "/newEvidence/" + onlyfiles[0]

        print "filepath====="
        print filepath
        result["eurl"] = filepath
        print result

    return json.dumps(result)

@pages_blueprint.route("updateSuccRate/<caseid>", methods=['POST'])
@login_required
def update_sucRat(caseid):
    print "inside updateSuccRate function."
    if request.method == 'POST':
        print "Inside if."
        alibSuc = request.form["countAlib"]
        bridSuc = request.form["countBrid"]
        dowjSuc = request.form["countDowj"]
        lloySuc = request.form["countLloy"]
        bloomSuc = request.form["countBloom"]
        failAlib = request.form["failAlib"]
        failBrid = request.form["failBrid"]
        failDowJ = request.form["failDowJ"]
        failLloy = request.form["failLloy"]
        failBloom = request.form["failBloom"]
        caseInfo = {"succeeded":{"alibaba":alibSuc,"bridgerInsight":bridSuc,"dow jones":dowjSuc,"lloyds":lloySuc,"bloomberg":bloomSuc},"failed":{"alibaba":failAlib,"bridgerInsight":failBrid,"dow jones":failDowJ,"lloyds":failLloy,"bloomberg":failBloom}}
        print caseInfo

        sucRate_folder = 'app/static/succeededRate'
        case_json = caseid + ".json"
        print sucRate_folder
        print case_json


        # 1 Create a folder which will contain JSON files for every user.
        if not os.path.exists(sucRate_folder):
            os.makedirs(sucRate_folder)

        # 2 Check whether there is such JSON file that matches bocID.json
        if os.path.isfile(sucRate_folder + '/' + case_json) and os.access(sucRate_folder + '/' + case_json,
                                                                            os.R_OK):
            print "File exists and is readable"
        else:
            print "Either file is missing or is not readable"
            os.mknod(sucRate_folder + '/' + case_json)
            print "Will check whether json exists"
            print os.path.isfile(case_json) and os.access(case_json, os.R_OK)

        # 3 Write userInfo into that JSON
        with open(sucRate_folder + '/' + case_json, 'w') as outfile:
            json.dump(caseInfo, outfile)
            logger.info("case Info stored.")
        return "case Info stored successfully"


@pages_blueprint.route("loginCheck", methods=['POST'])
@login_required
def loginCheck():
    print "Inside loginCheck function============"
    if request.method == 'POST':
        boc_user_email = current_user.email
        config_result = config_module.userConfig_get(boc_user_email)
        # config_result = config_module.userConfig_getTest()
        print "Will print config_result=============="
        print config_result
        print type(config_result)

        return json.dumps(config_result)


@pages_blueprint.route("logintest/<bocid>", methods=['POST'])
@login_required
def logintest(bocid):
    print "logintest", bocid
    if request.method == 'POST':
        print "Inside logintest function=========================="
        lloydsid = request.form["lloydsInput"]
        lloydspw = request.form["lloydsPassword"]
        bridgeid = request.form["bridgerInput"]
        bridgepw = request.form["bridgerPassword"]
        dowjonesid = request.form["dowjonesInput"]
        dowjonespw = request.form["dowjonesPassword"]
        boc_user_email = current_user.email
        # print "Will print configs=========="
        # print lloydsid
        # print bridgepw
        # print request.form["lloydsInput"]
        # print request.form["bridgerPassword"]


        # ##get server config
        # serverConfig_result = config_module.config_test()
        # print "Will print result from config_module============"
        # print serverConfig_result

        # config_module.userConfig_insertTest()
        # config_module.userConfig_postTest()
        # config_module.userConfig_getTest()

        search_result = config_module.userConfig_get(boc_user_email)
        print "Will print search_result==========="
        print search_result
        if search_result:
            print "Will do post==============="
            config_module.userConfig_post(boc_user_email, lloydsid, lloydspw, bridgeid, bridgepw, dowjonesid, dowjonespw)
            
        else:
            print "Will do insert=============="
            config_module.userConfig_insert(boc_user_email, lloydsid, lloydspw, bridgeid, bridgepw, dowjonesid, dowjonespw)
        ##below can be use
        
        # config_module.userConfig_get(boc_user_email)
        


        url = data_config.crawler_url + "api/logintest/" + lloydsid + "/" + lloydspw + "/" + bridgeid + "/" + bridgepw + "/" + dowjonesid + "/" + dowjonespw
        result = ""
        try:
            req = urllib2.Request(url)
            res = urllib2.urlopen(req)
            result = res.read()
        except urllib2.URLError, e:
            logger.warning("Error while login test: " + str(e))
            if hasattr(e, "code"):
                logger.warning("Code: " + str(e.code))
            if hasattr(e, "reason"):
                logger.warning("Reason: " + str(e.reason))
            res = dict()
            for crawler in ["Google/Bloomberg", "Dow Jones", "Lloyds", "BridgerInsight", "Alibaba"]:
                res[crawler] = "Failed"
                result = json.dumps(res)
        print "Will print result before reture========================!"
        print result
        return result

"""
@app.route("/api/logintest/<lloydsid>/<lloydspw>/<bridgeid>/<bridgepw>/<dowjonesid>/<dowjonespw>/<bocid>")
def logintest(lloydsid, lloydspw, bridgeid, bridgepw, dowjonesid, dowjonespw, bocid):
    print bocid
    url = data_config.crawler_url + "api/logintest/" + lloydsid + "/" + lloydspw + "/" + bridgeid + "/" + bridgepw + "/" + dowjonesid + "/" + dowjonespw
    result = ""
    try:
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        result = res.read()
    except urllib2.URLError, e:
        logger.warning("Error while login test: " + str(e))
        if hasattr(e, "code"):
            logger.warning("Code: " + str(e.code))
        if hasattr(e, "reason"):
            logger.warning("Reason: " + str(e.reason))
        res = dict()
        for crawler in ["Google/Bloomberg", "Dow Jones", "Lloyds", "BridgerInsight", "Alibaba"]:
            res[crawler] = "Failed"
            result = json.dumps(res)
    return result
"""


@pages_blueprint.route("updatecase", methods=['POST'])
@login_required
def update_remark():
    if request.method == 'POST':
        result = dict()
        cnter = Connector(current_user.email)
        caseid = request.form["caseid"]
        result["customer"] = request.form["customer"]
        result["transactionType"] = request.form["transactionType"]
        result["referenceNo"] = request.form["referenceNo"]
        # result["clientID"] = request.form["clientID"]
        result["bocRef"] = request.form["bocRef"]
        result["customerName"] = request.form["customerName"]
        result["totalAmount"] = request.form["totalAmount"]
        result["remark"] = request.form["remark"]
        cnter.saveCase(caseid, result)
        return '{"result":"succeed"}'
    return '{"result":"succeed"}'




@pages_blueprint.route("uploadfolder", methods=['POST'])
@login_required
def update_evi_folder():
    if request.method == 'POST':
        caseid = request.form["caseid"]
        file = request.files['file']
        print caseid
        print file
        flag = 0
        filepath = ""
        if file :
            filename = secure_filename(file.filename)
            print filename
            filepath = data_config.pdf_folder + caseid + "/newEvidence/" +filename
            newEvi_folder = data_config.pdf_folder + caseid + "/newEvidence"
            if not os.path.exists(newEvi_folder):
                os.makedirs(newEvi_folder)
                file.save(filepath)
            else:
                print any(isfile(join(newEvi_folder, i)) for i in listdir(newEvi_folder))
                if any(isfile(join(newEvi_folder, i)) for i in listdir(newEvi_folder)) == True:
                    flag = 1

                else:
                    file.save(filepath)

            print filepath




        return json.dumps({"flag":flag})
    # return '{"result":"succeed"}'



@pages_blueprint.route("delEvipackage", methods=['POST'])
@login_required
def delete_evi_package():
    if request.method == 'POST':
        print "Inside delete evidence package function"
        caseid = request.form["caseid"]
        path = data_config.pdf_folder + caseid + "/newEvidence"
        shutil.rmtree(path)
    return "Successfully removed target directory"


@pages_blueprint.route("downloadOrgEvi", methods=['POST'])
@login_required
def download_org_folder():
    if request.method == 'POST':
        print "Inside download org evidence package function"
        caseid = request.form["caseid"]
        path_before = data_config.pdf_folder + caseid + "/originalEvidence"
        path_after = data_config.pdf_folder + caseid + "/originalEvidences"
        shutil.make_archive(path_after, 'zip', path_before)
        path_after = path_after + ".zip"
        if os.path.exists(path_after):
            print "successfully zip folder"
            # filepath = data_config.current_url + "bocbtvm/cases/" + caseid + "/originalEvidences.zip"
            filepath = "bocbtvm/cases/" + caseid + "/originalEvidences.zip"
            return json.dumps({"ourl":filepath})
        else:
            print "failed to zip folder"
            return json.dumps({"ourl":""})


    return "Successfully removed target directory"



@pages_blueprint.route("getocr/<bocid>", methods=['POST'])
@login_required
def get_OCR(bocid):
    print bocid
    if request.method == 'POST':
        caseid = request.form["caseid"]
        page = request.form["page"]
        filepath = os.path.join(data_config.pdf_folder, caseid, page+".png")
        name = request.form["name"]
        x = float(request.form["x"])
        y = float(request.form["y"])
        w = float(request.form["w"])
        h = float(request.form["h"])
        result = get_ocr(filepath, x, y, w, h)
        filepath = os.path.join(data_config.pdf_folder, caseid, page+"_entity.json")
        newData = dict()
        newData["entityLocation"] = [0,0,0,0]
        newData["rightValues"] = {}
        newData["rightValues"]['value'] = result
        newData["rightValues"]['location'] = [x,y,w,h]
        with open(filepath,"rU") as jsonInput:
            data = json.loads(jsonInput.read())
            data[name] = newData
        with open(filepath, "w") as jsonOutput:
            jsonOutput.write(json.dumps(data))
        return result
    return 'error'

@pages_blueprint.route("changeType", methods=['POST'])
@login_required
def changeType():
    if request.method == 'POST':
        caseid = request.form["caseid"]
        file = request.form["file"]
        modification = json.loads(request.form["modification"])
        filepath = os.path.join(data_config.pdf_folder, caseid, file + "_entity.json")
        with open(filepath, "w") as jsonOutput:
            jsonOutput.write(json.dumps(modification))
        return '{"result":"succeed"}'
    return '{"result":"succeed"}'

@pages_blueprint.route("updateocr/<bocid>", methods=['POST'])
@login_required
def update_OCR(bocid):
    print bocid
    if request.method == 'POST':
        caseid = request.form["caseid"]
        file = request.form["file"]
        modification = json.loads(request.form["modification"])
        ##OCR V6 STRAT###
        # if modification["documentType"]=="Invoice":
            # modification["documentType"] = "invoice"
        # if modification["documentType"]=="BillOfLading":
            # modification["documentType"] = "billOfLading"
        # if modification["documentType"]=="PackingList":
            # modification["documentType"] = "packingList"
        # if modification["documentType"]=="CoverLetter":
            # modification["documentType"] = "coverLetter"
        ##OCR V6 END###
        # print str(modification)
        filepath = os.path.join(data_config.pdf_folder, caseid, file+"_entity.json")
        data = None
        with open(filepath,"rU") as jsonInput:
            data = json.loads(jsonInput.read())

            temp_data = {}
            for key in data:
                if type(data[key])==list:
                    temp_data[key]=[]
                    for i in range(0, len(data[key])):
                        if data[key][i]["fields"].has_key("deleted"):
                            continue
                        else:
                            temp_data[key].append(data[key][i])
                elif type(data[key])==dict:
                    if data[key]["fields"].has_key("deleted"):
                        continue
                    else:
                        temp_data[key]=data[key]
                else:
                    temp_data[key]=data[key]

            data = temp_data
            for key in modification:
                if (modification[key] == ""):
                    del data[key]
                else:

                    if type(modification[key])==list:
                        temp_mod = []
                        for i in range(0, len(modification[key])):
                            if modification[key][i]["fields"].has_key("deleted"):
                                continue
                            else:
                                temp_mod.append(modification[key][i])
                        data[key]=temp_mod
                    elif type(modification[key])==dict:
                        if modification[key]["fields"].has_key("deleted"):
                            continue
                        else:

                            data[key] = modification[key]
                    else:

                        data[key]=modification[key]
        with open(filepath, "w") as jsonOutput:
            jsonOutput.write(json.dumps(data))
        return '{"result":"succeed"}'
    return '{"result":"succeed"}'

@pages_blueprint.route("saveallpages/<bocid>", methods=['POST'])
@login_required
def saveallpages(bocid):
    print bocid
    if request.method == 'POST':
        caseid = request.form["caseid"]
        file = request.form["file"]
        modification = json.loads(request.form["modification"])
        type = modification["documentType"]

        filepath = os.path.join(data_config.pdf_folder, caseid, file+"_entity.json")
        data = None
        with open(filepath,"rU") as jsonInput:
            data = json.loads(jsonInput.read())
            # print "SAVE ALL:" + str(data)
            temp_data = {}
            for key in data:
                # print "length: " + str(len(data[key]))
                if isinstance(data[key],list)==True:
                    temp_data[key]=[]
                    for i in range(0, len(data[key])):
                        if data[key][i]["fields"].has_key("deleted"):
                            continue
                        else:
                            temp_data[key].append(data[key][i])
                elif isinstance(data[key],dict)==True:
                    if data[key]["fields"].has_key("deleted"):
                        continue
                    else:
                        temp_data[key]=data[key]
                else:
                    temp_data[key]=data[key]

            data = temp_data
            # print str(modification)
            for key in modification:
                if (modification[key] == ""):
                    del data[key]
                else:
                    # print str(data[key])
                    if isinstance(modification[key],list)==True:
                        temp_mod = []
                        for i in range(0, len(modification[key])):
                            if modification[key][i]["fields"].has_key("deleted"):
                                continue
                            else:
                                temp_mod.append(modification[key][i])
                        data[key]=temp_mod
                    elif isinstance(modification[key],dict)==True:
                        if modification[key]["fields"].has_key("deleted"):
                            continue
                        else:
                            data[key] = modification[key]
                    else:
                        data[key]=modification[key]

        filepath = data_config.pdf_folder + "/" + caseid
        for root, dirs, files in os.walk(filepath):
            for item in files:
                if "_entity.json" in item:
                    filepath = os.path.join(data_config.pdf_folder, caseid, item)
                    filepath_tmp =  os.path.join(data_config.tmp_folder, caseid, item)
                    data_temp = None
                    flag = 0
                    with open(filepath, "rU") as jsonInput:
                        data_temp = json.loads(jsonInput.read())
                        if data_temp["documentType"] == type:
                            flag = 1
                    if flag == 1:
                        if str(item) == "CM16NY0068_page1_entity.json":
                            print data
                            print filepath
                        with open(filepath, "w") as jsonOutput:
                            jsonOutput.write(json.dumps(data))
                        with open(filepath_tmp, "w") as jsonOutput:
                            jsonOutput.write(json.dumps(data))
        return '{"result":"succeed"}'
    return '{"result":"succeed"}'


@pages_blueprint.route("updatequestion/<bocid>", methods=['POST'])
@login_required
def update_question(bocid):
    print bocid
    print "answer"
    if request.method == 'POST':
        question = request.form["question"]
        caseid = request.form["caseid"]
        values = dict()
        cnter = Connector(current_user.email)
        node = cnter.queryQuestion(caseid, question)
        if not node:
            print "Node doesn't exist!!!"
        else:
            if "alert" in node:
                values["alert"] = node["alert"]


        values["answer"] =  request.form["answer"]
        values["comment"] = request.form["comment"]
        print "Will print comments============"
        print values["comment"]
        values["evidence"] = request.form["evidence"]
        print values
        question = request.form["question"]
        caseid = request.form["caseid"]
        cnter.saveQuestion(caseid, question, values)
        return '{"result":"succeed"}'
    return '{"result":"succeed"}'

@pages_blueprint.route("validate", methods=['POST'])
@login_required
def validate():
    if request.method == 'POST':
        question = request.form["question"]
        paras = json.loads(request.form["para"])
        paras["current user"] = current_user.email
        paras['full name'] = current_user.last_name + ", " + current_user.first_name
        result = getattr(logic_main, question)(paras)
        print str(result)
        return json.dumps(result)
    return '{"result":"none"}'

@pages_blueprint.route("captcha", methods=['POST'])
@login_required
def captcha():
    print "Veiws.py Entered the Captcha Function"
    data = json.loads(request.form.get('data'))
    captcha = data['captcha']
    item = data['item']
    customer = data['customer']
    print "captcha: item: " + item
    print "captcha: data: " + str(captcha)
    print "captcha: customer: " + str(customer)
    res = NeedCaptcha(item, customer, captcha)
    print "Test Result Returned:" + str(res)
    return str(res)

@pages_blueprint.route("bocbtvm/<path:path>")
@login_required
def bocbtvm(path):
    filepath = "bocbtvm/" + path
    return send_file(filepath)


app.register_blueprint(pages_blueprint)


