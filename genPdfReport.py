# -*- coding: utf-8 -*-
'''
modification on 2017/10/06:
1. fix http link problem on comments column
2. fix address table too large to fit page 

modification on 2017/10/10
1. add function <chop_line> to chop long text

modification on 2017/10/11
1. add bidi.algorithm to solve Arabic language dispaly issue
'''


import json
from datetime import datetime, timedelta
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import legal
# from reportlab.lib.pagesizes import A4
from reportlab.platypus import Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.platypus import (Flowable, Paragraph, SimpleDocTemplate, Spacer)
from reportlab.lib.colors import (
    black,
    purple,
    white,
    yellow,
    red
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import re
from bidi.algorithm import get_display

import sys
stdout = sys.stdout  
stdin = sys.stdin  
stderr = sys.stderr  
reload(sys)
sys.setdefaultencoding("utf-8")
sys.stdout = stdout  
sys.stdin = stdin  
sys.stderr = stderr

import logging
logging.basicConfig() 
logger = logging.getLogger("Check")
logger.setLevel(logging.DEBUG)

def chop_Line(all_line, max_number):
    all_line = all_line.decode("utf-8", "ignore")
    maxline= max_number
#     all_line = all_line.replace('/', '/ ')
    tmp_text_list = all_line.split(' ')
    #tmp_text_list = [text_line for text_line in tmp_text_list if len(text_line)>20]
    
    all_line_list = []
    
    for line in tmp_text_list:
    
#         if len(line)<maxline \
#             or ('http' in line and type(line) == str) \
#             or ('www.' in line and type(line) == str) \
#             or ('.com' in line and type(line) == str) \
#             or ('.org' in line and type(line) == str) \
#             or ('.net' in line and type(line) == str):
        if len(line)<maxline \
            or ('http' in line and line.index('http') < 23) \
            or ('www.' in line and line.index('www') < 23) \
            or ('.com' in line and line.index('.com') < 46) \
            or ('.org' in line and line.index('.org') < 46) \
            or ('.net' in line and line.index('.net') < 46) : 
            
            all_line_list.append(line)
       
        elif '\r\n\r\n' in line:  
                
            lines = line.split('\r\n\r\n')
            split_word = 0
            strline = ""
            while split_word < len(lines):
                
                line1 = lines[split_word]
#                 website_string = ''
#                 if 'https' in line1:
#                     print 'found http here '
#                     print line1
#                     pattern = re.compile('[\s("](https://.+?)["\s)]')
#                     for i in re.findall(pattern, line1):
#                         website_string = i
#                         line1.replace(i, '###')
#                     print line1
#                 elif 'http' in line1:
#                     pattern = re.compile('[\s("](http://.+?)["\s)]')
#                     for i in re.findall(pattern, line1):
#                         website_string = i
#                         line1.replace(i, '###')
 
                if len(line1)<maxline:
                    strline += line1
                else:
                    cant = len(line1) / maxline
                    cant += 1
                    index = maxline
                    for i in range(1,cant):
                        index = maxline * i                
                        strline += "%s " %(line1[(index-maxline):index])
                    strline += "%s " %(line1[index:])
                    
                strline += '\r\n\r\n'
                split_word += 1 
#                 strline = strline.replace('###', website_string).replace('# ##', website_string).replace('## #', website_string)
            logger.debug('strline orig: ' + strline)
            logger.debug('strline -4: ' + strline[:-4])
            all_line_list.append(strline[:-4]) 
  

        elif '\r\n' in line:       
            lines = line.split('\r\n')
            split_word = 0
            strline = ""
            while split_word < len(lines):
                line1 = lines[split_word]

                if len(line1)<maxline:
                    strline += line1
                else:
                    cant = len(line1) / maxline
                    cant += 1
                    index = maxline
                    for i in range(1,cant):
                        index = maxline * i
                        strline += "%s " %(line1[(index-maxline):index])
                    strline += "%s " %(line1[index:])
                strline += '\r\n'
                split_word += 1 
            if 'http' in line: print line.index('http')
            logger.debug('strline orig: ' + strline)
            logger.debug('strline -2: ' + strline[:-2])
            all_line_list.append(strline[:-2]) 
                    
        else:
            index = maxline
            strline = ''
            if len(line)<maxline:
                strline += line
            else:
                cant = len(line) / maxline
                cant += 1
                index = maxline
                for i in range(1,cant):
                    index = maxline * i
                    strline += "%s " %(line[(index-maxline):index])
                strline += "%s " %(line[index:])
            logger.debug('strline orig: ' + strline)
          
            all_line_list.append(strline)
    return_line = ' '.join(all_line_list)    
    return return_line


def line_assem(line):
    print "Will print each line before assem==========="
    print line
    print "=========================================="
    maxline = 44
    strline = ""
    if len(line)<maxline:
        strline += line
    else:
        cant = len(line) / maxline
        cant += 1

        index = maxline
        for i in range(1,cant):
            index = maxline * i
            strline += "%s " %(line[(index-maxline):index])
        strline += "%s " %(line[index:])
    return strline


def link_parser(text):
    
    href_format = '''<a href="%s">%s</a>'''#(href, href_transformation)
    search_text = ' '+text+' '
    pattern = re.compile('[\s("](http://.+?)["\s)]')

    for i in re.findall(pattern, search_text):
        #if len(i)>69:
        display_text = i.replace('/','/ ')
        print 'iamworking'
        print display_text
        display_text = chop_Line(display_text, 46)
        href_link = href_format%(i,display_text)
        text = text.replace(i, href_link)

    pattern = re.compile('[\s("](https://.+?)["\s)]')

    for i in re.findall(pattern, search_text):
        #if len(i)>69:
        
        display_text = i.replace('/','/ ')
        display_text = chop_Line(display_text, 46)
        href_content = i.replace('&amp;', '&')
        href_link = href_format%(href_content,display_text)
        text = text.replace(i, href_link)

    return text

# def link_parser(text):
#     href_format = '''<a href="%s">%s</a>'''#(href, href_transformation)
#     search_text = ' '+text+' '
#     pattern = re.compile("[\s(](http.+?)[\s)]")

#     for i in re.findall(pattern, search_text):
#         #if len(i)>69:
#         display_text = i.replace('/','/ ')
        
#         display_text = display_text.split('/')
#         strline = ''
#         for j in display_text:
#             j = chop_Line(j)
#             strline += j
#             strline += '/'
#         strline = strline[:-1]
#         href_link = href_format%(i,strline)
#         text = text.replace(i, href_link)

#     return text


def myFirstPage(canvas, doc):  
    canvas.saveState()  
    canvas.setFont('Times-Roman',10) 
    canvas.drawString(560, 15, "Page 1")  
    canvas.restoreState() 

def myLaterPages(canvas, doc):  
    canvas.saveState()  
    canvas.setFont('Times-Roman',10) 
    canvas.drawString(560, 15, "Page %d"%(doc.page))  
    canvas.restoreState() 

class MCLine(Flowable):
   """Line flowable --- draws a line in a flowable"""
   def __init__(self,width):
      Flowable.__init__(self)
      self.width = width

   def __repr__(self):
      return "Line(w=%s)" % self.width

   def draw(self):
      self.canv.line(0, 0, self.width,0)

def format(string, width):
    # return [string[x:x+width] for x in range(0, len(string), width)]
    return [string[x:x+width] for x in range(0, len(string), width)]
# Split a long text to smaller texts with fixed chars
def split_text(ptext):
    CHARS_LIMIT = 2000
    # CHARS_LIMIT = 2000
    return [ptext[i:i + CHARS_LIMIT] for i in range(0, len(ptext), CHARS_LIMIT)]


def buildPdf(pdfName, jsonPath):
    
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    pdfmetrics.registerFont(TTFont('CODE2000', 'CODE2000.TTF'))
    
    darkstyle = ParagraphStyle(
        name='dark',
        fontSize=12,
        fontName='CODE2000', # ''Helvetica-Bold',
        leading=16,
    )
    boldstyle = ParagraphStyle(
        name='bold',
        fontSize=7,
        fontName='CODE2000', # ''Helvetica-Bold',
    )
    lightstyle = ParagraphStyle(
        name='light',
        fontSize=9,
        fontName='CODE2000', # ''Helvetica-Bold',
        textColor= red,
    )
    # LEGAL = (8.5 * inch, 200 * inch)
    # doc = SimpleDocTemplate(pdfName,pagesize=A4,
    #                     rightMargin=36,leftMargin=36,
    #                     topMargin=72,bottomMargin=18,
    #                         initialFontName='CODE2000')

    doc = SimpleDocTemplate(pdfName,pagesize=legal,
                        rightMargin=0,leftMargin=0,
                        topMargin=72,bottomMargin=18,
                            initialFontName='CODE2000')

    with open(jsonPath, "r+") as fileObject:
        fileObject = fileObject.read()
        fileObject = fileObject.replace('&','&amp;')
        fileObject = get_display(fileObject)
        data = json.loads(fileObject)
        """
        json_data = open(jsonPath).read()
        data = json.loads(json_data)
        """
        keys = ['Source Date', 'Entity Type', 'Gender', 'Title', 'Number', 'Entity Date', 'Record Information'
            , 'Match Information', 'Reason', 'Comments', 'IDs', 'IDss', 'CurrentAddress', 'Address', 'Phone Number', 'Alternate Country', 'Country', 'Cities', 'Ports', 'Nationality Term']

        styles=getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        styles["Normal"].fontName = 'CODE2000'
        
        Story=[]

        logo = "title.png"
        im = Image(logo, 4*inch, 0.5*inch)
        im.hAlign = 'LEFT'
        Story.append(im)
        for item in data:
            if item.has_key("Result Date"): 
                result_time = item["Result Date"].split(".")[0]
                result_time = datetime.strptime(result_time, "%Y-%m-%d %H:%M:%S")
                result_time = result_time + timedelta(hours=-5)
                result_time = result_time.strftime("%m/%d/%Y %H:%M:%S")
                search_date = result_time.split(" ")[0]
                search_time = result_time.split(" ")[1]
            else:
                now = datetime.now()
                search_date = str(now.month) + "/" + str(now.day) + "/" + str(now.year)
                search_time = str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
                item["Result Date"] = str(now.year) + "/" + str(now.month) + "/" + str(now.day) + " " + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
            # fileObject.seek(0)
            # fileObject.write(json.dumps(data))
            # fileObject.truncate()

        ptext = '<font size=12>%s</font>' % ('Bank of China, USA')
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 5))

        line = MCLine(455)
        Story.append(line)

        data_name = data[0]
       
        ptext = '<font size=12>%s: %s</font>' % ('Name', data_name['Record Information'].replace("_", " "))
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 2))
        ptext = '<font size=12>%s: </font>' % ('SSN')
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 2))
        ptext = '<font size=12>%s: </font>' % ('Phone')
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 2))
        ptext = '<font size=12>%s: </font>' % ('Account ID')
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 2))
        ptext = '<font size=12>%s: </font>' % ('Address')
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 2))
        ptext = '<font size=12>%s: %s</font>' % ('Result ID', data_name['Result ID'])
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 2))
        ptext = '<font size=12>%s: %s</font>' % ('Origin','Real-Time')
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 2))
        ptext = '<font size=12>%s: %s</font>' % ('Search Date', search_date)
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 2))
        ptext = '<font size=12>%s: %s</font>' % ('Search Time', search_time)
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 2))
        ptext = '<font size=12>%s: </font>' % ('Division')
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 2))
        ptext = '<font size=12>%s: %s</font>' % ('Assigned To', "US1-TSD-" + data[0]["Full Name"])
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 2))
        ptext = '<font size=12>%s: %s</font>' % ('Record Status', 'None')
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 2))
        ptext = '<font size=12>%s: </font>' % ('Updated By')
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 2))
        ptext = '<font size=12>%s: %s</font>' % ('Alert State', 'Open')
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 2))
        ptext = '<font size=12>%s: </font>' % ('Updated By')
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 2))
        ptext = '<font size=12>%s: %s</font>' % ('Searched By', "US1-TSD-" + data[0]["Full Name"])
        Story.append(Paragraph(ptext, style=boldstyle))
        Story.append(Spacer(1, 3))

        line = MCLine(455)
        Story.append(line)
        Story.append(Spacer(1, 3))
        npages = 0

        for index, item in enumerate(data):
            if item.has_key('Match Information'):
                ptext1 = '<font size=12>%s</font>' % chop_Line(item['Entity Name'],23)
                ptext2 = '<font size=12>%s</font>' % (item['EntityScore'])
                # ptext2 = '<font size=12>%s</font>' % (item['TEST'])  

                ptext3 = '<font size=12>%s</font>' % (item['FileName'][:-4])
                ptext4 = '<font size=12>%s</font>' % ("Index:" + str(index + 1))
                tbl_data = [[Paragraph(ptext1, style=darkstyle),
                             Paragraph(ptext2, style=darkstyle), 
                             Paragraph(ptext3, style=darkstyle),
                             Paragraph(ptext4, style=darkstyle)]]
                tbl = Table(tbl_data)
                tbl.setStyle(TableStyle([("BACKGROUND", (0,0),(3,0), colors.grey)]))
                Story.append(tbl)
                Story.append(Spacer(1, 3))
            for key in keys:
                if item.has_key(key):
                    key = str(key).decode('latin-1').encode("utf-8")
                    ptext1 = '<font size=12>%s:</font>' % (key)
               
                    if not key in ["IDs", "IDss", "Address", "Phone Number", 'Alternate Country', 'Country', 'Cities', 'Ports', 'Nationality Term']:
                        item[key] = str(item[key]).decode("utf-8").replace(u"\u2018", "'").replace(u"\u2019", "'").encode("utf-8")
                        
                    if key == "IDs":
                       
                        id_str = ""
                        for ID in item[key]:
                            # IDtype = ID["IDtype"]
                            # name = ID["name"]
                            otherId = ID['otherId']
                            issuer = ID['issuer']
                            label = ID['label']
                            id_type = ID['id_type']
                            expire_date = ID["expire_date"]
                            issue_date = ID["issue_date"]
                            id_comments = ID["comments"]
    # error code 
                            #id_comments = ID["test"]

                            if str(id_type) != 'None':
                                otherId = link_parser(otherId)
                                id_str += id_type + ":   "+ otherId + '<br/>'
                            else:
                            # if otherId is not None:
                                otherId = link_parser(otherId)
                                id_str += "Other ID:&nbsp;" + otherId + "<br/>"
                            if issuer is not None:
                                id_str += "&nbsp;Issuer:&nbsp;" + issuer + "<br/>"
                            if id_comments is not None:
                                id_str += 'Comments:    ' +  id_comments.replace('|', '<br/>') + '<br/>'
                            if label is not None:
                                id_str += "&nbsp;Label:&nbsp;" + label + "<br/>"
                            if str(issue_date) is not "":
                                id_str += "&nbsp;Issue Date:&nbsp;" + issue_date + "<br/>"
                            if str(expire_date) is not "":
                                id_str += "&nbsp;Expired Date:&nbsp;" + expire_date + "<br/>"
                        #id_str = link_parser(id_str)
                        output = id_str

                    elif key == "Phone Number":
                        phone_str = ''
                        for phone in item[key]:
                            phone_str += phone['type'] + ':&nbsp;' + phone['phone'] + "<br/>"
                            if phone["comments"] is not None:
                                phone_str += "&nbsp;&nbsp;&nbsp;&nbsp;Comments" + ':&nbsp;' + phone["comments"] + "<br/>"
                        output = phone_str

    #                 elif key == "AKAs":
                      
    #                     aka_str = ""
    #                     if len(item[key])!=0:
                            
    #                         for aka in item[key]:
    #                             aka_type = aka["AKAtype"]

    #                             name = chop_Line(aka["name"])

    #                             aka_title = aka["title"]
    #                             category = aka['category']
    #                             print "aka_title========="
    #                             print aka_title
                                
    #                             if str(category) != "None":
    #                                 aka_str += aka_type + '(' + category + '):&nbsp;' + name + "<br/>"
    #                             else:
    #                             #     aka_str += aka_type + ":   " + name + "<br/>"
    #                                 aka_str += aka_type + ":&nbsp;" + name + "<br/>"
    #                                 if str(aka_title) is not "":
    #                                     aka_str += "Title" + ":&nbsp;" + aka_title + "<br/>"
    #                             # =========== 
    #                             aka_comments = str(aka['aka_comments']).strip()
    #                             if len(str(aka_comments).strip()) != 0:
    #                                 aka_str += 'Comments:    ' +  aka_comments.replace('|', '<br/>') + '<br/>'
    # #                     aka_str = get_display(aka_str)            
    #                     output = aka_str + '<br/>'

                    elif key == "IDss":
                      
                        idss_str = ""
                        for id in item[key]:
                            idss_id = id["ID"]
                            idss_str += idss_id + "<br/>"
                            idss_label = id["Label"]
                            idss_str += idss_label + "<br/>"
                        output = idss_str

                    # elif key == "CurrentAddress":
                    #     output = "<br/>".join(item[key])
                    elif key == "Address":
                        address_list = item[key]
                        add_output_list = []
                        
                        for address_data in address_list:
                            address_str = ""
                            address_str +="Address"
                            if str(address_data["type"]) == 'Current':
                                address_str +="(" + address_data["type"] + "):" + "&nbsp;&nbsp;&nbsp;&nbsp;"
                            if str(address_data["type"]) == "Unknown":
                                address_str +=":" + "&nbsp;&nbsp;"
                            if len(address_data["street1"])!=0:
                                address_str += address_data["street1"] + "<br/>"
                            if len(address_data["street2"])!=0:
                                address_str += address_data["street2"] + "<br/>"
                            if len(address_data["city"])!=0:
                                address_str += address_data["city"] + "  "
                            # address_str += address_data["city"] + "<br/>"
                            if len(address_data["state"])!=0:
                                address_str += address_data["state"] + "  "
                            if len(address_data["zipcode"])!=0:
                                address_str +=address_data["zipcode"]
                            if len(address_data["city"])==0 and len(address_data["state"])==0 and len(address_data["zipcode"])==0:
                                address_str += address_data["country"]  + "<br/><br/>"
                            else:
                                address_str += "<br/>" +address_data["country"]  + "<br/><br/>"
                            add_comments = str(address_data['add_comments']).strip()
                            if len(add_comments)!=0:
                                
                                address_str += "Notes:" +"&nbsp;&nbsp;&nbsp;&nbsp;"+ address_data["add_comments"] + "<br/><br/>"
                            add_output_list.append(address_str)

                        output = add_output_list
                        #output = address_str

                    elif key == "Alternate Country":
                        alter_str = ""
                        for alter in item[key]:
                            alterLabel = "Country Name:"
                            alter_str +=alterLabel + "     "
                            alterVal = alter
                            alter_str +=alterVal + "<br/><br/>"
                        output = alter_str

                    elif key == "Country":
                        count_str = ""
                        for count in item[key]:
                            countLabel = "Country Code:"
                            count_str +=countLabel + "     "
                            alterVal = count
                            count_str +=alterVal + "<br/><br/>"
                        output = count_str

                    elif key == "Cities":
                        citi_str = ""
                        for citi in item[key]:
                            citiLabel = "City Name:"
                            citi_str +=citiLabel + "     "
                            citiVal = citi
                            citi_str +=citiVal + "<br/><br/>"
                        output = citi_str

                    elif key == "Ports":
                        port_str = ""
                        for port in item[key]:
                            portLabel = "Port Name:"
                            port_str +=portLabel + "     "
                            portVal = port
                            port_str +=portVal + "<br/><br/>"
                        output = port_str

                    elif key == "Nationality Term":
                        nation_str = ""
                        for nation in item[key]:
                            nationLabel = "Country Term:"
                            nation_str +=nationLabel + "     "
                            nationVal = nation
                            nation_str +=nationVal + "<br/><br/>"
                        output = nation_str

                    elif key == "Comments":    
                        comments_final = ""
                        key_comment = str(item[key])
                        index_num1 = 0
                        index_num2 = 0
                        
                        
                        if False:
                        #if "http" in key_comment.lower():
                            #print 'findhttp'
                            #print key_comment
                            index_list = [m.start() for m in re.finditer('http', key_comment.lower())]
                            max_index = index_list[0]
                            pre_outputs = format(key_comment[max_index:], 40)
                            res = key_comment[:max_index].replace("|", "<br/>")

                            for pre_output in pre_outputs:
                                res += pre_output + '<br/>'

                            res1 = res.decode('utf-8').encode("utf-8")
                            res2 = res1.replace("\n", "<br/>")
                            res3 = res2.replace("|", "<br/>")
                            output = res3.replace("<a", "").replace("/a>", "")
                        else:
                              
                            key_comment = chop_Line(key_comment, 46)
                            key_comment = link_parser(key_comment)

    #                         href_format = '''<a href="%s">%s</a>'''#(href, href_transformation)
    #                         key_comment = key_comment.replace("<a", "").replace("/a>", "")
    #                         search_text = ' '+key_comment+' '
    #                         pattern = re.compile("[\s(](http.+?)[\s)]")
                            
    #                         for i in re.findall(pattern, search_text):
    #                             #if len(i)>69:
    #                             display_text = i.replace('/','/ ')
    #                             href_link = href_format%(i,display_text)
    #                             key_comment = key_comment.replace(i, href_link)

    #                             print 'href link:'
    #                             print href_link
                            array_key = format(key_comment, 70)
                            for i in range (0, len(array_key)):
                                comments_final = comments_final + str(array_key[i])
                                """
                                if i != len(array_key):
                                    comments_final = comments_final + "<br/>"
                                """
                            comments_final = comments_final.decode('utf-8').encode("utf-8") # .decode('latin-1').encode("utf-8")                        
                            output = comments_final.replace("\n", "<br/>").replace("|", "<br/>")
                            # output = output.replace('カーイダ', '<br/>カーイダ').replace('されているISIL', '<br/>されているISIL').replace('・イスラミ','<br/>・イスラミ').replace('及びシ', '<br/>及びシ').replace('（国際刑事', '<br/>（国際刑事').replace('・リンク：', '<br/>・リンク：')
             
                        logger.debug("==============================================================================")
                        logger.debug("comments_final: " + str(comments_final))
                        logger.debug("dealed comments: " + str(output))
                        logger.debug("==============================================================================")
                    else:
                        output = item[key]

                    #texts = split_text(output)
                    #if type(output)==str:texts = [output]
                    if type(output)==list: texts = output
                    else: texts = split_text(output)
                    
                    for ptext2 in texts:
                        styleSheet = getSampleStyleSheet()
                      
                        ptext3 = str(ptext2).decode("utf-8", "ignore").replace(u"\u2018", "''").replace(u"\u2019", "'").encode("utf-8")
                        ptext4 = '<font size=12>%s</font>' % (ptext3)
                        
                        if ptext3 != "None" and str(ptext3.strip())!="<br/>":
                             tbl_data = [[Paragraph(ptext1, style=boldstyle), Paragraph(ptext4.decode("utf-8", "ignore"), styles["Normal"])]]
                             # tbl_data = [[Paragraph(ptext1, style=boldstyle), Paragraph(ptext4.decode("utf-8", "ignore"), styleSheet["BodyText"])]]
                             tbl = Table(tbl_data)
                             tbl.setStyle(TableStyle([('VALIGN', (0, 0), (1, 0), 'TOP')]))
                             Story.append(tbl)
                             Story.append(Spacer(1, 2))
                             if key == "Comments" and len(texts) > 1:
                                Story.append(PageBreak())

            if (item.has_key('AKAs') and len(item["AKAs"]) != 0):
                ptext = '<font size=12>%s:</font>' % "AKAs"
                Story.append(Paragraph(ptext, style=boldstyle))
                Story.append(Spacer(1, 2))
                for aka in item['AKAs']:
                    aka_type = aka["AKAtype"]
                    name = chop_Line(aka["name"], 46)
                    aka_title = aka["title"]
                    category = aka['category']
                    aka_comments = str(aka['aka_comments']).strip()
                    if str(category) != "None":
                        aka_type = aka_type + '(' + category + ')'
                    
                    ptext1 = '<font size=12>%s:</font>' % (aka_type)
                    texts = split_text(name)
                    for ptext3 in texts:
                        if ptext3 !="":
                            ptext2 = '<font size=12>%s</font>' % (ptext3)
                            tbl_data = [[Paragraph(ptext1, style=boldstyle), Paragraph(ptext2.decode("utf-8", "ignore"), styles["Normal"])]]
                            tbl = Table(tbl_data)
                            tbl.setStyle(TableStyle([('VALIGN', (0, 0), (1, 0), 'TOP')]))
                            Story.append(tbl)
                            Story.append(Spacer(1, 1.5))
                    
                    if str(aka_title) is not "":
                        ptext1 = '<font size=12>%s:</font>' % ('Title')
                        texts = split_text(aka_title)
                        for ptext3 in texts:
                            if ptext3 !="":
                                ptext2 = '<font size=12>%s</font>' % (ptext3)
                                tbl_data = [[Paragraph(ptext1, style=boldstyle), Paragraph(ptext2.decode("utf-8", "ignore"), styles["Normal"])]]
                                tbl = Table(tbl_data)
                                tbl.setStyle(TableStyle([('VALIGN', (0, 0), (1, 0), 'TOP')]))
                                Story.append(tbl)
                                Story.append(Spacer(1, 1.5))
                        
                    if len(str(aka_comments).strip()) != 0:
    #                     aka_type = "Comments"
                        ptext1 = '<font size=12>%s:</font>' % ('Comments')
                        
                        texts = split_text(aka_comments)
                        for ptext3 in texts:
                            if ptext3 !="":
                                ptext2 = '<font size=12>%s</font>' % (ptext3)
                                tbl_data = [[Paragraph(ptext1, style=boldstyle), Paragraph(ptext2.decode("utf-8", "ignore"), styles["Normal"])]]
                                tbl = Table(tbl_data)
                                tbl.setStyle(TableStyle([('VALIGN', (0, 0), (1, 0), 'TOP')]))
                                Story.append(tbl)
                                Story.append(Spacer(1, 2))

            if (item.has_key('Additional Info') and item["Additional Info"] is not None):
                ptext = '<font size=12>%s:</font>' % "Additional Infomation"
                Story.append(Paragraph(ptext, style=boldstyle))
                Story.append(Spacer(1, 2))
                if item.has_key('Additional Info'):
                    for add_item in item['Additional Info']:
                     
                        array_key = format(str(add_item['value']), 70)
                        add_comment = ""

                        for i in range(0, len(array_key)):
                            add_comment = add_comment + str(array_key[i])
                       
                        ptext1 = '<font size=12>%s:</font>' % (add_item['type'])

                        texts = split_text(add_comment)
                        for ptext3 in texts:
                       
                            if ptext3 !="":
                                ptext2 = '<font size=12>%s</font>' % (ptext3)
                                tbl_data = [[Paragraph(ptext1, style=boldstyle), Paragraph(ptext2.decode("utf-8", "ignore"), styles["Normal"])]]
                                tbl = Table(tbl_data)
                                tbl.setStyle(TableStyle([('VALIGN', (0, 0), (1, 0), 'TOP')]))
                                Story.append(tbl)
                                Story.append(Spacer(1, 2))

                        if len(str(add_item['comments']).strip()) != 0:
                            ptext1 = '<font size=12>%s:</font>' % ('&nbsp;Comments:')

                            texts = split_text(add_item['comments'])
                            for ptext3 in texts:
                           
                                if ptext3 !="":
                                    ptext2 = '<font size=12>%s</font>' % (ptext3)
                                    tbl_data = [[Paragraph(ptext1, style=boldstyle), Paragraph(ptext2.decode("utf-8", "ignore"), styles["Normal"])]]
                                    tbl = Table(tbl_data)
                                    tbl.setStyle(TableStyle([('VALIGN', (0, 0), (1, 0), 'TOP')]))
                                    Story.append(tbl)
                                    Story.append(Spacer(1, 2))
           

                Story.append(Spacer(1, 12))

            if (item.has_key('bridgerComments') and len(item["bridgerComments"])!=0):
                comments_ptext = '<font size=12>%s:</font>' % "Operator's Comments"
           
                comment_key = format(str(item["bridgerComments"]), 40)
               

                if type(comment_key)==list: texts_comments = comment_key
                else: texts_comments = split_text(comment_key)

                for final_index, final_ptext in enumerate(texts_comments):
                   
                    final_ptext_1 = '<font size=12>%s</font>' % (final_ptext)
                  
                    if final_index == 0:                
                        tbl_data_1 = [[Paragraph(comments_ptext, style=lightstyle), Paragraph(final_ptext_1, style=lightstyle)]]
                        tbl_1 = Table(tbl_data_1)
                        tbl_1.setStyle(TableStyle([('VALIGN', (0, 0), (1, 0), 'TOP')]))
                        Story.append(tbl_1)
                        Story.append(Spacer(1, 2))
                    else:
                        tbl_data_1 = [[Paragraph("", style=lightstyle), Paragraph(final_ptext_1, style=lightstyle)]]
                        tbl_1 = Table(tbl_data_1)
                        tbl_1.setStyle(TableStyle([('VALIGN', (0, 0), (1, 0), 'TOP')]))
                        Story.append(tbl_1)
                        Story.append(Spacer(1, 2))

               

        Story.append(PageBreak())
        npages += 1
        logger.debug("Preparing Page: " + str(npages))

        #doc.build(Story)
        doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)

if __name__ == '__main__':
    jsonPath = "WORLDWIDE EXPORT SERVICES.json"
    pdfPath = "WORLDWIDE EXPORT SERVICES.pdf"
    buildPdf(pdfPath, jsonPath)

    print 'ok'
