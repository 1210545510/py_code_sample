# ssh root@systemgboc1.sl.cloud9.ibm.com
# systemg4all
import json
import re
import os
import sys
import time
import subprocess
import ast
import codecs
import shutil
from datetime import datetime
from config import Fields
sys.path.insert(1, '/root/Developer/systemg-tools-1.5.0/python/python2.7')
from py_gShell import _py_gshell as gShell
import config
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import logging
logging.basicConfig()
logger = logging.getLogger("Check")
logger.setLevel(logging.DEBUG)

mapping = '/mapping.json'
graph = gShell()
# listGraph = json.loads(graph.list_all())
# if "test" not in listGraph["stores"]:
    # graph.create_graph("test", "directed")
#graph.create_graph("test", "directed")
# graph.set_current_graph("test")
# graph.set_current_graph("admin@example.com_prev")
# graph.set_current_graph("admin@example.com_prev")

# Returns text safe string for insertion into database
def wrap(input):
    if '"' in input:
        return input
    else:
        return "\"" + input + "\""

# Returns text safe string for a list
def ltos(input):
    return "\"" + str(input) + "\""

# Returns a list object of a list stored in graphDB
def stol(input):
    return ast.literal_eval(input)

def escape(s):
    return str("\""+ s.replace("\"","\\\"") + "\"")


############# BASIC GRAPH OPPERATIONS #############
class Connector():
    _instance = None # Singleton

    def __init__(self, name=None):
        if name is not None:
            self.username = name
            self.switch_user(name)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def switch_user(self, name):
        logger.debug("User name: " + name)
        username = str(name)
        exists = False
        listGraph = json.loads(graph.list_all())
        for store in listGraph["stores"]:
            if str(store["name"]) == name:
                exists = True
                # logger.debug("Graph " + name + " exists")
                break
        if not exists:
            logger.debug("Create Graph: " + name)
            graph.create_graph(username, "directed")
            graph.add_vertex(username, "user")
            graph.set_current_graph(username)
            self.inital_customer()
            self.inital_category()
            self.initial_b16country()
            self.initial_b20country()
            self.initial_b21country()
        graph.set_current_graph(username)

    # Create new graph store object
    def create(self,name,type):
        response = graph.create_graph(graph_name=name, graph_type=type)
        logger.debug("Create Graph: Name = " + str(name) + ", Type = " + str(type))
        return response

    # Delete graph store, input graph name
    def purge(self,input):
        input = wrap(input)
        logger.debug("Delete Graph: Name = " + str(input))
        return graph.delete_graph(input)

    # Returns Dictionary of Node Properties
    def getV(self, nodeID):
        result = json.loads(graph.find_vertex(vertex_id=str(nodeID)))
        if "nodes" in result:
            logger.info("Get Vertex: " + str(nodeID) + " " + str(result["nodes"][0]))
            return result["nodes"][0]
        else:
            logger.warning("Get Vertex: Not found")
            return None

    # Returns a single property value from a Node
    @staticmethod
    def getVProp(nodeID, propKey):
        node = dict(json.loads(graph.find_vertex(vertex_id=str(nodeID)))['nodes'][0])
        logger.debug("Get Vertex Property: ID = " + str(nodeID) + ", Key = " + str(propKey) + ", Value = " + str(node[propKey]))
        return node[propKey]

    # Returns an operator of case
    def getOperator(self, caseID):
        return self.getVProp(caseID, "operator")

    # Returns nodeIDs satisfying the node label filter type
    def filterV(self, input):
        nodes = json.loads(graph.filter_vertices(label = input))['nodes']
        l = []
        for i in nodes:
            l.append(i['id'])
        logger.debug("Filter Vertex: " + str(l))
        return l

    # Returns edge properties as a dictionary from GraphDB
    def getE(self, source, sink):
        return json.loads(graph.find_edge(src=str(source), targ=str(sink)))['edges']

    # Update the key-value pair of a vertex property
    def updateV(self, nodeID, propVal):
        logger.debug("Update Vertex: ID = " + str(nodeID) + ", Values = " + str(propVal))
        graph.add_vertex(vertex_id = str(nodeID), prop=propVal)

    # Returns edge properties, provide key-value entry as a dictionary ~ writes over previous value
    def updateE(self, srcID, targID, payload):
        logger.debug("Update Edge: Source ID = " + str(srcID) + ", Target ID = " + str(targID) + ", Values = " + str(payload))
        graph.update_edge(src=srcID,targ=targID, prop=payload)

    ############## 35 questions logic functions########
    # question a1: Has customer folder been created?
    def checkNodeExist(self, input):
        result = json.loads(graph.filter_vertices(label="customer", prop="name", condition='"name"==input'))['node']
        if len(result):
            logger.debug("Node Exists: " + str(input) + " " + str(result))
            return True
        else:
            logger.debug("Node Does Not Exist: " + str(input))
            return False

    # question b6: Has the invoice number covering this shipment not been used for previous shipments?

    def inoviceNumberExist(self, seller, invoice_num):
        result = json.loads(graph.filter_vertices(label="invoice", prop={"seller", "invoice_num"},
                                                      condition='"seller"==seller, "invoice_num"==invoice_num'))['node']
        if len(result):
            logger.debug("Invoice Number Exists: " + str(seller) + " " + str(invoice_num) + " " + str(result))
            return True
        else:
            logger.debug("Invoice Number Does Not Exist: " + str(seller) + " " + str(invoice_num))
            return False

    # question b7: "Is the shipped quantity and quality of the goods consistent with the invoice?
    # def quan_qual_check():

    ############# OCR RELATED OPPERATIONS #############
    def saveCase(self, caseID, values):
        # self.switch_user()
        print "Inside saveCase function"
        print "Values============="
        print values
        for key in values:
            values[key] = escape(values[key])
        graph.update_vertex(vertex_id= str(caseID), prop=values)

    def saveQuestion(self, caseID, question, values):
        """
        Store the result of question
        :param caseID:
        :param question:
        :param values:
        :return:
        """
        # self.switch_user()
        evidence = values["evidence"]
        filepath = os.path.join(config.pdf_folder, caseID,"evidence",question+".json")
        fileurl = os.path.join(config.data_folder, caseID,"evidence",question+".json")
        print(question)
        print(evidence)
        with codecs.open(filepath,"w") as output:
            output.write(evidence.encode('utf-8'))
        edgeNeeded = False
        questionID = str(caseID + "-" + question)
        if not self.getV(questionID):
            edgeNeeded = True
            graph.add_vertex(questionID, "question", prop={"answer": escape(values['answer']), "comment": escape(values["comment"]), "evidence": escape(fileurl)})
        else:
            graph.update_vertex(vertex_id=str(questionID), prop={"answer": escape(values['answer']), "comment": escape(values["comment"]), "evidence": escape(fileurl)})
        if "alert" in values and values['alert']:
            graph.update_vertex(vertex_id=str(questionID), prop={"alert": escape(values["alert"])})
        else:
            graph.delete_vprop(vertex_id=str(questionID), prop=["alert"])

        if "comment" in values and values['comment']:
            graph.update_vertex(vertex_id=str(questionID), prop={"comment": escape(values["comment"])})
        else:
            graph.delete_vprop(vertex_id=str(questionID), prop=["comment"])

        if edgeNeeded:
            graph.add_edge(src=str(caseID),targ=questionID,edgelabel="has_question")
            graph.add_edge(src=questionID,targ=str(caseID),edgelabel="has_question")

    def queryQuestion(self, caseID, question):
        # self.switch_user()
        return self.getV(caseID + "-" + question)

    def queryQuestions(self, caseID):
        # self.switch_user()
        result = graph.find_neighbors(vertex_id=str(caseID))
        result = json.loads(result)
        return result["nodes"]

    # Reads mapping.json file to map valid entities to appropriate questions (for UI)
    def mapQuestions(self, path):
        # self.switch_user()
        file = open(path)
        json_data = json.loads(file.read())
        for i in json_data:
            question = wrap(i['description'])
            # print question
            l = []
            q_prop = dict()
            if len(i['fields']) > 0:
                for n in i['fields']:
                    l.append(n)
                    field = wrap(' '.join(n.split(' ')[1:]))
                    graph.add_vertex(vertex_id=str(field), label='entity')
                    graph.add_edge(src=str(question), targ=str(field), edgelabel='get_field')
            q_prop['fields'] = ltos(l)
            # Stores the fields list in the question vertex as a property ~ used to return valid question fields
            graph.add_vertex(vertex_id=str(question), label='question', prop=q_prop)

    ############# MAIN BATCH ROUTINE ON STARTUP #############

    # Create Database > Load Question Mappings > Load Sample Document
    def reload(self):
        self.purge('test')
        self.create('test','undirected')
        self.mapQuestions(mapping)
        # self.OCR('BOC','Case1','/home/systemg/Samples/Sample_2.pdf')

    ############# WEB UI UTILITES #############

    # Pretty print JSON Payload
    def printJSON(input):
        logger.info("Print JSON: " + str(input))
        print json.dumps(input,indent=4,sort_keys=True)

    # Copies upload from temp directory, renames clientID_userID_timestamp.pdf, calls OCR module
    def moveUpload(self, tempPath, clientID, userID, caseID):
        timestamp = int(time.time())
        filePath = ''
        fileID = clientID + '_' + userID + '_' + str(timestamp) + '.pdf'
        filePath = filePath + fileID
        cp_file = 'sudo cp ' + tempPath + ' ' + filePath
        os.system(cp_file)
        rm_file = 'sudo rm ' + tempPath
        os.system(rm_file)
        self.OCR(clientID, caseID, filePath)

    def getCase(self, caseID):
        node = self.getV(caseID)
        if "customer" in node:
            logger.debug("Case: " + str(caseID) + " " + str(node["customer"]))
            logger.debug("Node: " + str(node))
            return node
        else:
            nodes = graph.find_neighbors(vertex_id=str(caseID))
            nodes = json.loads(nodes)
            for n in nodes["nodes"]:
                if n["label"] == "client":
                    customer = n['id']
                    logger.debug("Case: " + str(customer))
                    graph.update_vertex(vertex_id=str(caseID), prop={'customer': str(customer)})
                    return self.getV(caseID)
            logger.debug("Case Not Found: " + str(caseID))
            return None

    # Create a new case (contains multiple PDFS)
    def createCase(self, userID, operator, client, caseID, clientID, referenceNo, bocRef, transactionType, totalAmount):
        logger.info("Create case: " + str(caseID) + " " + str(userID) + " " + str(operator) + " " + str(totalAmount))
        graph.add_vertex(str(clientID), 'client', prop={"clientName": str(client)})
        graph.add_vertex(str(caseID), 'case', prop={'customer': str(clientID),
                                        'status': "initialized",
                                        'lastModified': '"' + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + '"',
                                        'referenceNo': str(referenceNo),
                                        'bocRef': str(bocRef),
                                        'clientID': str(clientID),
                                        'transactionType': str(transactionType),
                                        # 'operator': str(userID),
                                        'customerName': escape(client),
                                        "totalAmount": escape(totalAmount),
                                        "operator": str(operator)})  ## Add operator
        graph.add_vertex(str(userID), 'user')
        graph.add_edge(str(clientID), str(caseID))
        graph.add_edge(str(caseID), str(userID))
        graph.add_edge(str(userID), str(caseID))

    def deleteCase(self, caseID):
        graph.delete_vertex(str(caseID))

#########INITIAL OF THE SYSTEM, UPLOAD LIST FUNCTIONS###############################

    def inital_customer(self):
        customerID = open('app/data/graph_lists/a1_CustomerID.txt')
        customerName = open('app/data/graph_lists/a1_CustomerName.txt')
        ID_line = customerID.readline()
        Name_line = customerName.readline()
        while ID_line and Name_line:
            Name_line = Name_line.replace(' ', '_')
            graph.add_vertex(vertex_id=str(ID_line), label='Customer', prop={'name': str(Name_line)})
            # result = json.loads(graph.find_vertex(vertex_id=str(ID_line)))
            # logger.debug("Result of JSON loading: " + str(result))
            ID_line = customerID.readline()
            Name_line = customerName.readline()
        customerID.close()
        customerName.close()

    def get_custmomer(self):
        dd = graph.print_all()
        # logger.debug("Contents of graph: " + str(dd))
        result = json.loads(graph.filter_vertices(label='Customer'))['nodes']
        return_val = {}
        for item in result:
            temp = item['name']
            temp = temp.replace('_', ' ')
            return_val[item['id']] = temp
        return return_val

    def inital_category(self):
        category = open('app/data/graph_lists/b15_Category.txt')
        category_desc = open('app/data/graph_lists/b15_CategoryDescription.txt')
        cate_Line = category.readline()
        cate_des_Line = category_desc.readline()
        while cate_Line and cate_des_Line:
            cate_Line = cate_Line.replace(' ', '_')
            cate_des_Line = cate_des_Line.replace(' ', '_')
            graph.add_vertex(vertex_id=str(cate_Line), label='b15', prop={'description': str(cate_des_Line)})
            cate_Line = category.readline()
            cate_des_Line = category_desc.readline()
        category.close()
        category_desc.close()

    def get_category(self):
        result = json.loads(graph.filter_vertices(label='b15'))['nodes']
        return_val = {}
        for item in result:
            if "description" in item:
                temp = item['description']
                temp = temp.replace('_', ' ')
                temp2 = item['id']
                temp2 = temp2.replace('_', ' ')
                return_val[temp2] = temp
        return return_val

    def initial_b16country(self):
        short = open('app/data/graph_lists/b16CountryShort.txt')
        full = open('app/data/graph_lists/b16Country.txt')
        short_line = short.readline()
        full_line = full.readline()
        while short_line and full_line:
            full_line = full_line.split()
            full_line = '_'.join(full_line)
            for i in range(0, len(full_line)):
                if full_line[i] == '_':
                    full_line = full_line[i+1:len(full_line)]
                    break
            graph.add_vertex(vertex_id=str(short_line), label='b16', prop={'description': str(full_line)})
            short_line = short.readline()
            full_line = full.readline()
        short.close()
        full.close()

    def get_b16country(self):
        result = json.loads(graph.filter_vertices(label='b16'))['nodes']
        return_val = {}
        for item in result:
            temp = item['description']
            return_val[item['id']]=temp
        return return_val

    def initial_b20country(self):
        short = open('app/data/graph_lists/b20_CountryShort.txt')
        full = open('app/data/graph_lists/b20_Country.txt')
        short_line = short.readline()
        full_line = full.readline()
        while short_line and full_line:
            full_line = full_line.replace(' ', '_')
            graph.add_vertex(vertex_id=str(short_line), label='b20', prop={'description': str(full_line)})
            short_line = short.readline()
            full_line = full.readline()
        short.close()
        full.close()

    def get_b20country(self):
        result = json.loads(graph.filter_vertices(label='b20'))['nodes']
        return_val = {}
        for item in result:
            temp = item['description']
            return_val[item['id']] = temp
        return return_val

    def initial_b21country(self):
        short = open('app/data/graph_lists/b21_CountryShort.txt')
        full = open('app/data/graph_lists/b21_Country.txt')
        short_line = short.readline()
        full_line = full.readline()
        while short_line and full_line:
        # print full_line
            full_line = full_line.replace(' ', '_')
            graph.add_vertex(vertex_id=str(short_line), label='b21', prop={'description': str(full_line)})
            result = json.loads(graph.find_vertex(vertex_id=str(short_line)))
            #print result
            short_line = short.readline()
            full_line = full.readline()
                # break
        short.close()
        full.close()

    def get_b21country(self):
        result = json.loads(graph.filter_vertices(label='b21'))['nodes']
        return_val = {}
        for item in result:
            temp = item['description']
            return_val[item['id']] = temp
        return return_val

    # Query cases that an individual has access to
    def queryCases(self, userID):
        # self.switch_user()
        neighbors = json.loads(graph.find_neighbors(str(userID)))
        logger.debug("Neighbors of " + str(userID) + ": " + str(neighbors))
        cases = list()
        if 'nodes' in neighbors:
            for i in neighbors['nodes']:
                if i['label'] == 'case':
                    cases.append(i)
        return cases

    # Filter cases by operator
    def filterCases(self, userID, operator):
        neighbors = json.loads(graph.find_neighbors(str(userID)))
        logger.debug("Neighbors of " + str(userID) + ": " + str(neighbors))
        cases = list()
        if 'nodes' in neighbors:
            for i in neighbors['nodes']:
                if i['label'] == 'case' and "operator" in i and i["operator"] == operator or operator == Fields.COMPLIANCE_MANAGER:
                    cases.append(i)
        print cases
        return cases


    # Get the status of a case
    def getStatus(caseID):
        return dict(json.loads(graph.find_vertex(caseID))['nodes'][0])['status']

    # Set the access level of a user
    def getAccess(caseID):
        return dict(json.loads(graph.find_vertex(caseID))['nodes'][0])['access']

    # Get files associated with a case (multiple files attached to case ~ to come)
    def getFiles(caseID):
        neighbors = dict(json.loads(graph.find_neighbors(caseID)))['nodes']
        return neighbors['nodes']

    # Set the status of a case
    def setStatus(caseID, userID, status):
        status = wrap(status)
        graph.update_vertex(vertex_id=caseID, prop={'status' : status})

    # Set the access level of a user
    def setAccess(userID, level):
        graph.update_vertex(vertex_id=userID, prop={'access' : wrap(level)})

    # Set document mapping - manual from UI update
    def mapDocument(userID, caseID, fileID, questionID, entryID, NW, SE):
        coordinates = {'NW' : NW, 'SE' : SE}
        graph.update_edge(src=caseID, targ=questionID, eid=fileID, prop=coordinates)
        return 1

    # Get PNG file names associated with a PDF
    def getPNGs(fileID):
        return json.loads(graph.find_vertex(vertex_id=str(fileID)))['nodes'][0]['pngs']

    # Get documents associated with a case
    def getDocs(caseID):
        pages = dict()
        for key in json.loads(graph.find_neighbors(caseID))['edges']:
            if key['label'] == 'get_file':
                doc =  str(key['target'])
            if key['label'] == 'get_page':
                pages[doc] = str(key['target'])
        return pages

    # Get entities associated with file entityID
    def getEntities(entityID):
        pages = []
        for key in json.loads(graph.find_neighbors(entityID))['edges']:
            if key['target'] != entityID:
                pages.append(key)
        return pages

    ############# OCR SPECIFIC FUNCTIONS AND OPERATIONS #############

    # Run OCR package on copied PDF file provided
    def OCR(self, clientID, caseID, path):
        """
        Run OCR package on copied PDF file provided
        :param clientID:
        :param caseID:
        :param path:
        :return:
        """
        logging.basicConfig()
        logger_ocr = logging.getLogger("OCR")
        logger_ocr.info("Inside OCR in connector.")

        # graph.update_vertex(str(caseID), prop={"status":"processing"})
        fileID = path.split('/')[(len(path.split('/')))-1].split('.pdf')[:-1]
        fileID = fileID[0].replace(' ', '_')
        filePath = config.tmp_folder + fileID
        config.mkdirs(filePath + "/temp")
        logger_ocr.info(filePath)

        inputPDF = filePath + "/" + fileID + ".pdf"
        logger_ocr.info("Prepare PDF file: " + inputPDF)
        cp_file = 'cp ' + path + ' ' + inputPDF
        os.system(cp_file)
        rm_file = 'rm ' + path
        os.system(rm_file)

        logger_ocr.info("Start OCR: " + inputPDF)
        run_ocr = config.ocr_folder + 'run_ocr.sh ' + inputPDF
        logger_ocr.debug("OCR Script: " + run_ocr)
        os.system("sh " + run_ocr)
        logger_ocr.info("Stop OCR: " + inputPDF)

        cp_file = 'cp ' + filePath + "/* " + config.pdf_folder + caseID + '/'
        os.system(cp_file)


        # #create retrieve folder
        # retrievePath = config.pdf_folder+caseID+'.retrieve' +'/'
        # config.mkdirs(retrievePath)
        # config.mkdirs(config.pdf_folder + caseID)
        #
        #
        # ##copy files to retrieve folder
        # src = config.pdf_folder+caseID+'/'
        # dest = config.pdf_folder+caseID+'.retrieve' +'/'
        # src_files = os.listdir(src)
        # for file_name in src_files:
        #     full_file_name = os.path.join(src, file_name)
        #     if os.path.isfile(full_file_name):
        #         shutil.copy(full_file_name, dest)


        ##Producing index.json
        files = list()
        for name in os.listdir(config.pdf_folder + caseID + '/'):
            if os.path.isfile(os.path.join(config.pdf_folder + caseID + '/', name)) and ".png" in name:
                logger.debug("PNG File: " + str(name))
                files.append(name[0:name.index(".png")])
        files.sort(key=lambda item: (re.findall("(.*)page(\d+)", item)))
        page_num = len(files)
        general_name = fileID + "_page"
        index = 1
        temp_files = []
        for item in files:
            temp_item = general_name+str(index)
            index = index+1
            temp_files.append(temp_item)
        files = temp_files

        with open(config.pdf_folder + caseID + '/index.json',"w") as output:
            output.write(json.dumps(files))

        filepath = os.path.join(config.pdf_folder, fileID,"evidence")
        config.mkdirs(filepath)


        #######Copy all the file to caseID.original folder
        #Copy file in folder to folder.original/
        folder = config.pdf_folder + caseID + '/'

        # create record folder
        recordPath = config.pdf_folder + caseID + '.original' + '/'
        if not os.path.exists(recordPath):
            os.makedirs(recordPath)

        for dirpath, dirnames, files in os.walk(recordPath):
            if files:
                print(dirpath, 'has files')

                # Empty the current folder
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
        print "New case created and caseID.oeiginal created"

    def OCRAddPdf(self, clientID, caseID, newcaseID, path):
        """
        Run OCR package on copied PDF file provided
        :param clientID:
        :param caseID:
        :param newcaseID:
        :param path:
        :return:
        """
        logging.basicConfig()
        logger_ocr = logging.getLogger("OCR")
        # self.switch_user()
        print "Inside OCRAddPdf in connector."

        # graph.update_vertex(str(caseID), prop={"status":"processing"})
        fileID = path.split('/')[(len(path.split('/'))) - 1].split('.pdf')[:-1]
        fileID = fileID[0].replace(' ', '_')
        filePath = config.tmp_folder + fileID
        mkfolder = "mkdir " + filePath
        os.system(mkfolder)
        mkfolder = "mkdir " + filePath + "/temp"
        os.system(mkfolder)
        file = filePath + "/" + fileID + ".pdf"
        logger_ocr.info("Prepare PDF file: " + file)
        cp_file = 'cp ' + path + ' ' + file
        os.system(cp_file)
        rm_file = 'rm ' + path
        os.system(rm_file)

        print mkfolder
        print file

        logger_ocr.info("Start OCR: " + file)
        run_ocr = config.ocr_folder + 'run_ocr.sh ' + file
        logger_ocr.debug("OCR Script: " + run_ocr)
        os.system("sh " + run_ocr)
        logger_ocr.info("Stop OCR: " + file)
        mkfolder = "mkdir " + config.pdf_folder + newcaseID


        print mkfolder

        os.system(mkfolder)
        cp_file = 'cp ' + filePath + "/* " + config.pdf_folder + newcaseID + '/'
        os.system(cp_file)

        ########################COPY FILES FROM NEWCASEID FORLDER TO ORIGINAL CASE FOLDER###########################
        src = config.pdf_folder+newcaseID+'/'
        dest = config.pdf_folder+caseID+'/'
        src_files = os.listdir(src)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if(os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, dest)

        print os.listdir(dest)

        files = list()
        for name in os.listdir(config.pdf_folder + newcaseID + '/'):
            if os.path.isfile(os.path.join(config.pdf_folder + newcaseID + '/', name)) and ".png" in name:
                logger.debug("PNG File: " + str(name))
                files.append(name[0:name.index(".png")])
        files.sort(key=lambda item: ((re.findall("(.*)page(\d+)", item))))
        page_num = len(files)
        general_name = fileID + "_page"
        index = 1
        temp_files = []
        for item in files:
            temp_item = general_name + str(index)
            index = index + 1
            temp_files.append(temp_item)
        files = temp_files

        print files
        print config.pdf_folder
        print newcaseID

        with open(config.pdf_folder + newcaseID + '/index.json', "w") as output:
            output.write(json.dumps(files))

        filepath = os.path.join(config.pdf_folder, fileID, "evidence")
        if not os.path.exists(filepath):
            os.makedirs(filepath)

    # Inserts nodes for entities extracted from PDF file
    def injestDocuments(caseID, fileID, itemID):
        """
        Inserts nodes for entities extracted from PDF file to graph database
        :param fileID: UNUSED
        :param itemID: JSON file path
        :return:
        """
        try:
            with open(itemID) as json_data:
                page = itemID.split('.json')[0].split('/')[-1]
                # extract page type from top of json file (encoded as: lading, dowjones, letter)
                docType = dict()
                docType['pageType'] = wrap('invoice')
                graph.add_vertex(vertex_id=page, label='page', prop=docType)
                graph.add_edge(src=str(caseID), targ=str(page), edgelabel='get_page')
                d = json.load(json_data)
                logger.debug("JSON Data: " + str(d))
                for key in d:
                    logger.debug("JSON Key: " + str(key))
                    graph.add_vertex(vertex_id=str(key), label='entity')
                    locations = dict()
                    for g in d[key]:
                        logger.debug("JSON Value: " + str(g))
                        if g == 'bottomValues' or g == 'rightValues':
                            locations[str(g)] = "\"" + str(d[key][g]['location']) + "\""
                            logger.debug("Location: " + str(locations[str(g)]))
                            logger.debug("Location: " + str(locations[g]))
                            h = 1
                            for x in d[key][g]:
                                if x == 'value':
                                    value = wrap(d[key][g][x])
                                    logger.debug("Value: " + str(value))
                                    h = 0
                            if h == 1:
                                value = wrap(d[key][g])
                                logger.debug("Value: " + str(value))
                        elif g == 'entityLocation':
                            locations['entityLocation'] = wrap(d[key]['entityLocation'])
                            logger.debug("Entity Location: " + str(locations['entityLocation']))
                    logger.debug("Value: " + str(value))
                    locations['value'] = str(value)
                    graph.add_edge(src=str(page), targ=str(key), edgelabel=str(key), prop=locations)
        except EnvironmentError:
            logger.warning("Falied to read JSON files")




if __name__ == '__main__':
    cntr = Connector("test")
    cntr.inital_customer()
    cntr.inital_category()
    cntr.initial_b16country()
    cntr.initial_b20country()
    cntr.initial_b21country()
