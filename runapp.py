# -*- coding: utf-8 -*-
# Owner - ADC


# Importing required libraries to run the application 
# Most important library required would be Flask as it builds the web framework for the application
# 1. render template is used to host the HTML files
# 2. session is used to get data from the HTML pages
# 3. request is used to get data from HTML forms
from flask import Flask,render_template, request,session

# pyodbc is used for making ODBC connections to the Database. This is very important package as it helps getting data from the database where alerts and transactions are stored
import pyodbc

# pandas and numpy are used for numerical and data analysis purposes
import pandas as pd
import numpy as np

# Calendar, OS and time are tertiary packages that are used for specific purposes within the code.
import calendar
import os 

import datetime
mth = datetime.datetime.now().strftime("%m")


np.set_printoptions(suppress=True)

# Application is named app. It is provided a secret_key which is used for login purposes.
# The application is configured to add the application root directory

app = Flask(__name__)
app.secret_key = os.urandom(15);  
app.config['APPLICATION_ROOT'] = '/'

# ODBC connection is made as shown below. This needs Driver name, Server name, Database UserID and Password.
# if Windows authentication is provided, then TRUSTED_CONNECTION = True must be written in place of UID and PWD
# It is important to have MultipleActiveResultSets as it enables multiple connections to the database. 2 connections are made in this case
#cxn = pyodbc.connect (r'DRIVER={SQL Server Native Client 10.0}; SERVER=9AMHSADCSQL103\BOC; DATABASE = Pbsa; UID=TsdAdmin; PWD=A$123456; MultipleActiveResultSets=True',timeout=0)
#cxn1 = pyodbc.connect (r'DRIVER={SQL Server Native Client 10.0}; SERVER=9AMHSADCSQL103\BOC; DATABASE = Pbsa; UID=TsdAdmin; PWD=A$123456; MultipleActiveResultSets=True',timeout=0)
#cxn2 = pyodbc.connect (r'DRIVER={SQL Server Native Client 10.0}; SERVER=9AMHSADCSQL103\BOC; DATABASE = Pbsa; UID=TsdAdmin; PWD=A$123456; MultipleActiveResultSets=True',timeout=0)
#cxn3 = pyodbc.connect (r'DRIVER={SQL Server Native Client 10.0}; SERVER=9AMHSADCSQL103\BOC; DATABASE = Pbsa; UID=TsdAdmin; PWD=A$123456; MultipleActiveResultSets=True',timeout=0)
cxn = pyodbc.connect (r'DRIVER={SQL Server Native Client 10.0}; SERVER=9AMHSADCSQL1T7\BOC; DATABASE = Pbsa; UID=TsdAdmin; PWD=A$123456; MultipleActiveResultSets=True',timeout=0)
cxn1 = pyodbc.connect (r'DRIVER={SQL Server Native Client 10.0}; SERVER=9AMHSADCSQL1T7\BOC; DATABASE = Pbsa; UID=TsdAdmin; PWD=A$123456; MultipleActiveResultSets=True',timeout=0)
cxn2 = pyodbc.connect (r'DRIVER={SQL Server Native Client 10.0}; SERVER=9AMHSADCSQL1T7\BOC; DATABASE = Pbsa; UID=TsdAdmin; PWD=A$123456; MultipleActiveResultSets=True',timeout=0)
cxn3 = pyodbc.connect (r'DRIVER={SQL Server Native Client 10.0}; SERVER=9AMHSADCSQL1T7\BOC; DATABASE = Pbsa; UID=TsdAdmin; PWD=A$123456; MultipleActiveResultSets=True',timeout=0)

# Isocode for all countries are read from the file "wikipedia-iso-country-codes.csv" using pandas:read_csv. 
isocode = pd.read_csv("C:\wamp\www\TSDReporting\static\data\wikipedia-iso-country-codes.csv")

# A dictionary is created with all scenarios and their short names which is used in different functions
dict_tables = {"Carousel" : "Carousel Transactions (TSD)", "NewGeo":"Trading in New Geographies (TSD)", 
               "NewGoods" : "Trading New Goods (TSD)", "Vessel" : "Discrepancies in Vessel or Shipment Information (TSD)", 
               "MultiInvoice" : "Multiple Invoicing (TSD)", "HRG" : "High Risk Jurisdiction (TSD)", 
               "DocDis" : "Pattern of Document Discrepancies (TSD)", "ExcWithdrawal" : "Pattern of Excessive Withdrawal (BKD)",
               "Foreign": "Foreign Debit Card Transactions (BKD)" }

# A dictionary with all months and their numeric representation 
month_dict = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 
              10:'Oct', 11:'Nov', 12:'Dec'}
scenario_months = month_dict[int(mth)]			  
# Create global variables: message, logged_in and login_type
global message
message = ""

global logged_in 
logged_in=False

global login_type
login_type = "USER"

#--------------------------------- Other Functions ------------------------------------------------------------#
# These functions are used inside different app.route functions and thus are placed separately
# This function just returns the month name of the corresponding numberical representation
def getMonth(x):
    return month_dict[x]

# This function is used to calculate the 6 month dates given the transaction data
def get_dates(datafr, mths):
    # This is done by calculating the latest month and the current year. Then using this to calculate the last date of the month
    maxmonth = np.max(datafr['TRANS_DATE']).month
    curryear = np.max(datafr['TRANS_DATE']).year
    lastday = calendar.monthrange(curryear, maxmonth)[1]
    lastdate = pd.to_datetime(curryear*10000+maxmonth*100+lastday, format="%Y%m%d")
    
    # six months is subtracted and the first date is calculated
    minmonth = (lastdate - pd.DateOffset(months=mths)).month
    
    if mths == 6:
        if maxmonth >=7:
            minyear = curryear
        else:
                minyear = curryear-1
    else:
        minyear = curryear - 1
    minday = 1
    firstdate =  pd.to_datetime(minyear*10000+minmonth*100+minday, format="%Y%m%d")
    
    return firstdate, lastdate

#--------------------------------- Retrieving data from SQL Tables ------------------------------------------#
# This function gets all alerts from the ConsolidatedAlerts table
def db_allalerts():
    df2=pd.read_sql_query("select * from pbsa.dbo.CONSOLIDATEDALERTS",cxn)   
    return df2

# This function gets all alerts from the DebitCard_AlertArchive table
def db_allalertsbkd():
    df3 = pd.read_sql_query("Select * from pbsa.dbo.DebitCard_AlertArchive", cxn)
    df3['FromAccountNumber'] = '0'+ df3['FromAccountNumber'].astype(str)
    
    return df3

# This function gets all transactions from the DebitCard_TranArchive table
def db_alltransbkd():
    df4 = pd.read_sql_query("Select * from pbsa.dbo.DebitCard_TranArchive", cxn)
    df4['FromAccountNumber'] = '0'+ df4['FromAccountNumber'].astype(str)
    df4['TransactionAmount'] = df4['TransactionAmount'].round(2)
    return df4

# This function gets all transactions from the HistoricalTransactions table
def db_alltrans():
    df4 = pd.read_sql_query("Select * from pbsa.dbo.HISTORICALTRANSACTIONS", cxn)
    return df4

# This function returns alerts corresponidng to the scenario short name provided as a parameter
def db_getAlerts(vals):
    if vals == "Carousel":
        df=pd.read_sql_query("select * from pbsa.dbo.CarouselAlertCustomers",cxn)   
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "NewGeo":
        df=pd.read_sql_query("select * from pbsa.dbo.TradeInNewGeoAlertCustomers",cxn)   
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "NewGoods":
        df=pd.read_sql_query("select * from pbsa.dbo.TradeInNWHRDUAlertCustomers",cxn)   
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "Vessel":
        df=pd.read_sql_query("select * from pbsa.dbo.VSSLSHMTDSPYALERTCUSTOMERS order by GROUP_NO",cxn)   
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "MultiInvoice":
        df=pd.read_sql_query("select * from pbsa.dbo.MULTINVALERTCUSTOMERS",cxn)
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "HRG":
        df=pd.read_sql_query("select * from pbsa.dbo.TradeInHRGeoAlertCustomers",cxn)   
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "DocDis":
        df=pd.read_sql_query("select * from pbsa.dbo.DocDspyAlertCustomers",cxn)   
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "ExcWithdrawal":
        df = pd.read_sql_query("select * from pbsa.dbo.ExcessiveWithdrawals_Alert", cxn)
        df['FromAccountNumber'] = '0'+ df['FromAccountNumber'].astype(str)
        df['MaxThreeDayAvg'] = df['MaxThreeDayAvg'].round(2)
        df['Difference'] = (df['Difference']*100).astype(str)+ '%'
        return df
    elif vals == "Foreign":
        df = pd.read_sql_query("SELECT * FROM ForeignDebit_Alert", cxn)
        df['FromAccountNumber'] = '0'+ df['FromAccountNumber'].astype(str)
        
        return df 
    
        
        
# This finctions returns transactions corresponding to the scenario short name provided as a paramter along with the focal entity for which the transactions are displayed        
def db_getTransactions(focent, vals):
        
    if vals == "Carousel":
        df=pd.read_sql_query("select * from pbsa.dbo.CarouselAlertTransactions where FOCALENTITY = '" + str(focent)+"' ORDER BY TRANS_DATE", cxn)   
        return df
    elif vals == "NewGeo":
        df=pd.read_sql_query("select * from pbsa.dbo.TradeInNewGeoAlertTransactions where FOCALENTITY = '" + str(focent)+"' ORDER BY TRANS_DATE", cxn)   
        return df
    elif vals == "NewGoods":
        df=pd.read_sql_query("select * from pbsa.dbo.TradeInNWHRDUAlertTransactions where FOCALENTITY = '" + str(focent)+"' ORDER BY TRANS_DATE", cxn)   
        return df
    elif vals == "Vessel":
        df=pd.read_sql_query("select * from pbsa.dbo.DISCPNCYSHPMNTTRANSACTIONS where FOCALENTITY = '" + str(focent)+"' ORDER BY TRANS_DATE", cxn)  
        return df
    elif vals == "MultiInvoice":
        df=pd.read_sql_query("select * from pbsa.dbo.MULTINVALERTCUSTTRANS where FOCALENTITY = '" + str(focent)+"' ORDER BY TRANS_DATE", cxn)  
        return df
    elif vals == "HRG":
        df=pd.read_sql_query("select * from pbsa.dbo.TradeInHRGeoAlertTransactions where FOCALENTITY = '" + str(focent)+"' ORDER BY TRANS_DATE", cxn)  
        return df
    elif vals == "DocDis":
        df=pd.read_sql_query("select * from pbsa.dbo.DocDspyAlertTransaction where FOCALENTITY = '" + str(focent)+"' ORDER BY TRANS_DATE", cxn)
        return df
    elif vals == "ExcWithdrawal":
        df = pd.read_sql_query("select * from pbsa.dbo.ExcessiveWithdrawals_AlertedTxn where FromAccountNumber = '" + str(focent)+ "'", cxn)
        df['FromAccountNumber'] = '0'+ df['FromAccountNumber'].astype(str)
        df['TransactionAmount'] = df['TransactionAmount'].round(2)
        return df
    elif vals == "Foreign":
        df = pd.read_sql_query("SELECT * FROM pbsa.dbo.ForeignDebit_AlertedTxn where FromAccountNumber = '" + str(focent)+ "'", cxn)
        df['FromAccountNumber'] = '0'+ df['FromAccountNumber'].astype(str)
        df['TransactionAmount'] = df['TransactionAmount'].round(2)
        return df


# This function returns historical transactions corresponding to the focal entity and the scenario short name to plot graphs or display historical transactions
def db_geodata(focent, vals):
    if vals == "NewGeo":
        #df=pd.read_sql_query("select * from pbsa.dbo.TradeInNewGeoMapData3 where FOCALENTITY = '" + str(focent)+"'",cxn)
        df=pd.read_sql_query("select * from pbsa.dbo.TradeInNewGeoMapData where FOCALENTITY = '" + str(focent)+"'",cxn)
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "HRG":
        df=pd.read_sql_query("select * from pbsa.dbo.TRADEINHIGHRISKGEOMAPDATA where FOCALENTITY = '" + str(focent)+"'",cxn)
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "Carousel":
        df = pd.read_sql_query("select *, case when LC_TYPE like 'I%' or LC_TYPE like 'SO%' or LC_TYPE like 'CI%' then 'Import' else 'Export' end as ImpExp from pbsa.dbo.CAROUSELMAPDATA where FOCALENTITY = '" + str(focent) + "'", cxn)
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "NewGoods":
        df=pd.read_sql_query("select * from pbsa.dbo.TradeInNewGoodsMapData where FOCALENTITY = '" + str(focent)+"'", cxn)   
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        #df=pd.read_sql_query(("select * from pbsa.dbo.TradeInNewGoodsMapData where FOCALENTITY = '%s'"), params = [str(focent)] , cxn)   
        return df
    elif vals == "DocDis":
        df=pd.read_sql_query("select * from pbsa.dbo.DOCDISCREPANCYMAPDATA where FOCALENTITY = '" + str(focent)+"'", cxn)
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "MultiInvoice":
        df=pd.read_sql_query("select * from pbsa.dbo.MULTINVOICEMAPDATA where FOCALENTITY = '" + str(focent)+"'", cxn)
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "ExcWithdrawal":
        df = pd.read_sql_query("Select * from pbsa.dbo.ExcessiveWithdrawals_Alert1YearTxn where FromAccountNumber = '" + str(focent)+ "'", cxn1)
        df['FromAccountNumber'] = '0'+ df['FromAccountNumber'].astype(str)
        df['TransactionAmount'] = df['TransactionAmount'].round(2)
        return df
    elif vals == "Foreign":
        df = pd.read_sql_query("SELECT * FROM pbsa.dbo.ForeignDebit_Alert1YearTxn where FromAccountNumber = '" + str(focent)+ "'", cxn1)
        df['FromAccountNumber'] = '0'+ df['FromAccountNumber'].astype(str)
        df['TransactionAmount'] = df['TransactionAmount'].round(2)
        return df


# This is similar to the above function but with a different ODBC connection
def db_linedata(focent, vals):
    if vals == "NewGeo":
        #df=pd.read_sql_query("select * from pbsa.dbo.TradeInNewGeoMapData3 where FOCALENTITY = '" + str(focent)+"'",cxn)
        df=pd.read_sql_query("select * from pbsa.dbo.TradeInNewGeoMapData where FOCALENTITY = '" + str(focent)+"'",cxn1)
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "HRG":
        df=pd.read_sql_query("select * from pbsa.dbo.TRADEINHIGHRISKGEOMAPDATA where FOCALENTITY = '" + str(focent)+"'",cxn1)
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "NewGoods":
        df=pd.read_sql_query("select * from pbsa.dbo.TradeInNewGoodsMapData where FOCALENTITY = '" + str(focent)+"'", cxn1)  
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "DocDis":
        df=pd.read_sql_query("select * from pbsa.dbo.DOCDISCREPANCYMAPDATA where FOCALENTITY = '" + str(focent)+"'", cxn1)
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "MultiInvoice":
        df=pd.read_sql_query("select * from pbsa.dbo.MULTINVOICEMAPDATA where FOCALENTITY = '" + str(focent)+"'", cxn1)
        df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
        return df
    elif vals == "ExcWithdrawal":
        df = pd.read_sql_query("Select * from pbsa.dbo.ExcessiveWithdrawals_Alert1YearTxn where FromAccountNumber = '" + str(focent)+ "'", cxn2)
        df['FromAccountNumber'] = '0'+ df['FromAccountNumber'].astype(str)
        df['TransactionAmount'] = df['TransactionAmount'].round(2)
        return df
    elif vals == "Foreign":
        df = pd.read_sql_query("SELECT * FROM pbsa.dbo.ForeignDebit_Alert1YearTxn where FromAccountNumber = '" + str(focent)+ "'", cxn2)
        df['FromAccountNumber'] = '0'+ df['FromAccountNumber'].astype(str)
        df['TransactionAmount'] = df['TransactionAmount'].round(2)
        return df

def db_getCardData(focent, vals):
    if vals == "ExcWithdrawal":    
        df = pd.read_sql_query("select FromAccountNumber, CustomerID, CustomerName, Relationship, CustomerResidence, MaxThreeDayAvg, HistAvg, Difference, MaxSingleDayWD, TransactionCount from pbsa.dbo.ExcessiveWithdrawals_Alert where FromAccountNumber = '" + str(focent) +"'", cxn3)
        df['FromAccountNumber'] = '0'+ df['FromAccountNumber'].astype(str)
        df['MaxThreeDayAvg'] = df['MaxThreeDayAvg'].round(2)
        df['Difference'] = (df['Difference']*100).astype(str)+ '%'
        return df
    elif vals == "Foreign":
        df = pd.read_sql_query("select * from pbsa.dbo.ForeignDebit_Alert where FromAccountNumber = '" + str(focent) +"'", cxn3)    
        df['FromAccountNumber'] = '0'+ df['FromAccountNumber'].astype(str)
        
# This function is called only for Vessel Shipment alert view because the user has the option to view alerts based on the discrepancy or shipment
def db_getvesselalerts(vals, disc):
    if disc == "orig":
       df=pd.read_sql_query("select * from pbsa.dbo.VSSLSHMTDSPYALERTCUSTOMERS where SHIPMENT_DISCREPANCY= 'COUNTRY_ORIG' Order by GROUP_NO",cxn)   
       df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
       return df 
    elif disc == "shipto":
       df=pd.read_sql_query("select * from pbsa.dbo.VSSLSHMTDSPYALERTCUSTOMERS where SHIPMENT_DISCREPANCY= 'SHIP_TO_COUNTRY' Order by GROUP_NO ",cxn)    
       df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
       return df
    elif disc == "shipfrom":
       df=pd.read_sql_query("select * from pbsa.dbo.VSSLSHMTDSPYALERTCUSTOMERS where SHIPMENT_DISCREPANCY= 'SHIP_FM_COUNTRY' Order by GROUP_NO",cxn)    
       df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
       return df
    elif disc == "voyager":
       df=pd.read_sql_query("select * from pbsa.dbo.VSSLSHMTDSPYALERTCUSTOMERS where SHIPMENT_DISCREPANCY= 'VOYAGE_NUMBER' Order by GROUP_NO ",cxn)    
       df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
       return df
    elif disc == "all":
       df=pd.read_sql_query("select * from pbsa.dbo.VSSLSHMTDSPYALERTCUSTOMERS Order by GROUP_NO ",cxn)    
       df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
       return df

# This function reutrn trnsactions only for vessel & shipment discrepancy scenario based on the discrepancy and the group number.
# This group number will have all focal entities that belong to the same set of alerted transactions
def db_getvesseltrans(group, disc):
    
     df=pd.read_sql_query("select * from pbsa.dbo.DISCPNCYSHPMNTTRANSACTIONS where GROUP_NO = '"+ group +"' and SHIPMENT_DISCREPANCY = '" + disc + "'", cxn)  
     df['FOCALENTITY'] = df['FOCALENTITY'].replace({' ': '_'}, regex = True)
     return df
# Although this function is called map there is no actual map being drawn. This functions maps the transctions based on the focal entity
def db_vesselmap( focent):
     df1=pd.read_sql_query("select * from pbsa.dbo.SHIPPINGDISCREPANCYGEOMAPDATA where FOCALENTITY = '"+ str(focent) +"'", cxn)  
     df2 = pd.read_sql_query("select distinct SHIPMENT_DISCREPANCY from  pbsa.dbo.VSSLSHMTDSPYALERTCUSTOMERS where FOCALENTITY = '"+ str(focent) +"'", cxn)
     df1['FOCALENTITY'] = df1['FOCALENTITY'].replace({' ': '_'}, regex = True)
     
     return df1, df2


#-------------------------------------------------Login Function-------------------------------------------------------------- #
# app.route("/").  route() decorator tells Flask what URL should trigger the function written below "/" by typing "localhost/" # 
# or "22.232.1.172/" will call this function which renders an html page using the render_template function                     #
# ---------------------------------------------------------------------------------------------------------------------------- #
# This function is used for web authentication. This requires access to the UserAuthentication table in PBSA database
@app.route("/login", methods=['POST'])
def login():
    Post_UserID=request.form['nameuser']
    Post_Password=request.form['word']
	# Get user and password from the html form and check the table
    df=pd.read_sql_query("EXEC [PBSA].[DBO].[BOC_UserAuthentication] @IDUser = '"+Post_UserID+"', @pPass='"+Post_Password+"'", cxn) 
	# if table contains the user and the right password is input, then put session['logged_in'] = True  else send an invalid password error
	# and call the home function which renders the home page
    if(df.iat[0,0]=='SUCCESS'):
        session['logged_in']=True
        global  logged_in        
        logged_in=True
        df_2=pd.read_sql_query("Select LoginType from [PBSA].[DBO].[TACTICALUSER] where USERID='"+Post_UserID.upper()+"' and  PasswordHash=HASHBYTES('SHA1','"+Post_Password+"'+CAST(Salt AS NVARCHAR(36)))",cxn)
        session['login_type']=df_2.iat[0,0]
        global login_type
        login_type =  session['login_type']
        message=""
    else:
        
        global message
        message=df.iat[0,0]
    return home()

# Once user clicks on Logout tab in the front end, the logged_in key is set to False and the home function is called
@app.route("/Logout", methods=['Get'])
def logout():
    session['logged_in']=False
    global logged_in
    logged_in=False
    global message
    message=""
    global login_type
    login_type = "USER"
    return home()

# Only the admin is given access to add new users and passwords 
@app.route("/ModifyUsers")
def AddDelUsers():
    global login_type
    loginType=str(login_type)
    # Check if user is Admin
    # render template testresult.html else call the home function
    if(loginType.upper()=="ADMIN"):
        print "Enter"
        df_3=pd.read_sql_query("Select UserID,LoginType,FirstName,LastName from [PBSA].[DBO].[TACTICALUSER]",cxn)
        return render_template('testresult.html', userList=df_3, cols = list(df_3.columns), userID=df_3['UserID'])
    else:
        return home()
        
# The function is called to delete users
@app.route("/DeleteUser")
def DeleteUser():
    # get arguments from the page and delete using odbc connection to the database
    # once this is done, load the "modify users" page 
    delUserArgs=request.args
    userID=delUserArgs.get('UserID')
    cursor=cxn.cursor()
    cursor.execute("Delete from [PBSA].[DBO].[TACTICALUSER] where userID='"+userID+"'")
    cursor.commit()
    return AddDelUsers()    

# The function is called to add users
@app.route("/AddUser", methods=['POST'])
def AddUsers():
  # Get user information from the web page and input it in the table
  # load the "modify users" page
  userID=request.form['userID']
  loginType=request.form['loginType']
  password=request.form['password']
  firstName=request.form['firstName']
  lastName=request.form['lastName']
  df=pd.read_sql_query("EXEC [PBSA].[DBO].[BOC_AddUser] @UserID = '"+userID+"', @pLogintType='"+loginType+"',@pPassword='"+password+"',@pFirstName='"+firstName+"',@pLastName='"+lastName+"'", cxn) 
  cxn.commit()
  df_3=pd.read_sql_query("Select UserID,LoginType,FirstName,LastName from [PBSA].[DBO].[TACTICALUSER]",cxn)
  return AddDelUsers()  

# --------------------------------------------------------------- Different pages are loaded once the user logs in ---------------------------------------------- #

# -------------------------------------------------------------------- Home Page -------------------------------------------------------------------------------- #
# This is the Home page. Once the user logs in he/she can render the home page, either by suffixing '/' or '/Home' to the Web URL (22.232.1.172 or localhost)
# The homepage is rendered only when the user has logged in else the intro page is loaded where the users needs to enter their credentials

# There are two routes with the same functional operation. Check function "start" and "home".
# The reason behind two functions is that when the user logs in the first time, the '/' page is loaded, 
# but when the user click on the "Home" tab in the front end, the route "/Home" function is loaded

@app.route("/")
def home():
	# if the user has not logged in render intro.html else render home.html
    if not session.get('logged_in'):
       return render_template('intro.html',error=message)
    else:
        var=login_type.upper()
        dat = db_allalerts()
        dat['No. of Alerts'] = 1
        dat_gr = dat[['ALERT_MONTH', 'SCENARIO', 'No. of Alerts']].groupby(by = ['ALERT_MONTH', 'SCENARIO']).count()
        dat_gr.reset_index(level=1, inplace=True)
        dat_gr[dat_gr.index.name] = dat_gr.index
        dat_gr.index = np.arange(1, len(dat_gr)+1)
        dat_gr.columns = ['Scenario', 'No. of Alerts', 'AlertDate']
        dat_gr['Department'] = 'TSD'
        dat1 = db_allalertsbkd()
        dat1['No. of Alerts'] = 1
        dat_gr1 = dat1[['AlertMonth', 'Scenario', 'No. of Alerts']].groupby(by = ['AlertMonth', 'Scenario']).count()
        dat_gr1.reset_index(level=1, inplace=True)
        dat_gr1[dat_gr1.index.name] = dat_gr1.index
        dat_gr1.index = np.arange(1, len(dat_gr1)+1)
        dat_gr1.columns = ['Scenario', 'No. of Alerts', 'AlertDate']
        dat_gr1['Department'] = 'BKD'
        dat_final = dat_gr.append(dat_gr1)
        dat_final['AlertDate'] = dat_final['AlertDate'].apply(lambda x: pd.to_datetime(str(x)))
        
        dat_final['Year'] = pd.DatetimeIndex(dat_final['AlertDate']).year
        month_list = list(pd.DatetimeIndex(dat_final['AlertDate']).month)
        
        months = [month_dict[x] for x in month_list]
        dat_final['Month'] = months
        dats =  dat_final.sort_values(by = ['AlertDate','No. of Alerts'], ascending = [False, False])
        return render_template('home.html',loginType=var, 
                               Alerts = dats[['Department', 'Scenario', 'Month', 'Year', 'No. of Alerts', 'AlertDate']].to_html(classes = 'trans', index = False))

@app.route("/Home")
def start():
        if not logged_in:
            return render_template('intro.html',error=message)
        else:
            var=login_type.upper()
            dat = db_allalerts()
            dat['No. of Alerts'] = 1
            dat_gr = dat[['ALERT_MONTH', 'SCENARIO', 'No. of Alerts']].groupby(by = ['ALERT_MONTH', 'SCENARIO']).count()
            dat_gr.reset_index(level=1, inplace=True)
            dat_gr[dat_gr.index.name] = dat_gr.index
            dat_gr.index = np.arange(1, len(dat_gr)+1)
            dat_gr.columns = ['Scenario', 'No. of Alerts', 'AlertDate']
            dat_gr['Department'] = 'TSD'
            dat1 = db_allalertsbkd()
            dat1['No. of Alerts'] = 1
            dat_gr1 = dat1[['AlertMonth', 'Scenario', 'No. of Alerts']].groupby(by = ['AlertMonth', 'Scenario']).count()
            dat_gr1.reset_index(level=1, inplace=True)
            dat_gr1[dat_gr1.index.name] = dat_gr1.index
            dat_gr1.index = np.arange(1, len(dat_gr1)+1)
            dat_gr1.columns = ['Scenario', 'No. of Alerts', 'AlertDate']
            dat_gr1['Department'] = 'BKD'
            dat_final = dat_gr.append(dat_gr1)
            
            dat_final['AlertDate'] = dat_final['AlertDate'].apply(lambda x: pd.to_datetime(str(x)))
            
            dat_final['Year'] = pd.DatetimeIndex(dat_final['AlertDate']).year
            month_list = list(pd.DatetimeIndex(dat_final['AlertDate']).month)
        
            months = [month_dict[x] for x in month_list]
            dat_final['Month'] = months

            dats = dat_final.sort_values(by = ['AlertDate','No. of Alerts'], ascending = [False, False])
            
            return render_template('home.html', loginType=var, Alerts = dats[['Department','Scenario', 'Month', 'Year', 'No. of Alerts', 'AlertDate']].to_html(classes = 'trans', index = False))

# This route is used by bar_home.js to load a bar chart in the main home.html page 
@app.route("/BarHome")
def home_bar2():
	# if the user has not logged in render intro.html else render home.html
    if not session.get('logged_in'):
       return render_template('intro.html',error=message)
    else:
        scenario_short = {'CAROUSEL_ALERTS':'CAROUSEL', 'DISCREPANCY_IN_SHIPPING_INFORMATION':'VESSEL_DISC.',
                          'DOCUMENTARY_DISCREPANCIES':'DOC_DISC.', 'MULTIPLE_INVOICING':'MULTI_INVOICE', 
                          'TRADE_IN_HIGH_RISK_GEO':'HIGH_RISK_GEO', 'TRADE_IN_NEW_GEO':'NEW_GEO',
                          'TRADE_IN_NEW_GOODS':'NEW_GOODS', 'Foreign_Debit_Card':'FOREIGN_DEBIT',
                          'Pattern_of_Excessive_Withdrawals':'EXC._WITHDRAWAL'}
        dat = db_allalerts()
        dat['Alerts'] = 1
        dat_gr = dat[['ALERT_MONTH', 'SCENARIO', 'Alerts']].groupby(by = ['ALERT_MONTH', 'SCENARIO']).count()
        dat_gr.reset_index(level=1, inplace=True)
        dat_gr[dat_gr.index.name] = dat_gr.index
        dat_gr.index = np.arange(1, len(dat_gr)+1)
        dat_gr.columns = ['Scenario', 'Alerts', 'AlertDate']
        dat_gr['Department'] = 'TSD'
        dat1 = db_allalertsbkd()
        dat1['Alerts'] = 1
        dat_gr1 = dat1[['AlertMonth', 'Scenario', 'Alerts']].groupby(by = ['AlertMonth', 'Scenario']).count()
        dat_gr1.reset_index(level=1, inplace=True)
        dat_gr1[dat_gr1.index.name] = dat_gr1.index
        dat_gr1.index = np.arange(1, len(dat_gr1)+1)
        dat_gr1.columns = ['Scenario', 'Alerts', 'AlertDate']
        dat_gr1['Department'] = 'BKD'
        dat_final = dat_gr.append(dat_gr1)
        dat_final['AlertDate'] = dat_final['AlertDate'].apply(lambda x: pd.to_datetime(str(x)))
        
        dat_final['Year'] = pd.DatetimeIndex(dat_final['AlertDate']).year
        month_list = list(pd.DatetimeIndex(dat_final['AlertDate']).month)
        
        months = [month_dict[x] for x in month_list]
        dat_final['Month'] = months
        dats =  dat_final.sort_values(by = ['AlertDate','Alerts'], ascending = [False, False])
        dats['Scenario'] = dats['Scenario'].replace({' ': '_'}, regex = True)
        vals = dats['AlertDate'].iloc[0]
        bar_data = dats.loc[dats['AlertDate']==vals]
        scen = [scenario_short[i] for i in bar_data['Scenario']]
        bar_data['Scenario'] = scen
        bars = bar_data.to_string(header=True, index=False, index_names=False).split('\n')
        
        bardata = [','.join(ele.split()) for ele in bars]
        
        ld= '\n'.join(bardata)
        return ld


# ------------------------------------------------------------------------------------------------------------------------------ #
# Every function from here on will check whether the user has logged in and only then will access to different pages be provided #
# It is very important to adhere to this procedure so that unauthorized access is not provided                                   #
# ------------------------------------------------------------------------------------------------------------------------------ #

# -------------------------------------------------------------- Get TSD Alerts ------------------------------------------------ #
# This function gets all alerts in a consolidated view and renders allalerts.html
# It calls db_allalerts() to get the data from the database and converts it into HTML format
# "classes" parameter in to_html helps in styling the table on the front end
@app.route("/GetAlerts")
def allalerts():
    if not logged_in:
      return render_template('intro.html',error=message)
    else:
        alerts = db_allalerts()
        alert_html = alerts.to_html(classes = 'trans', index = False)
        return render_template('allalerts.html', allalerts = alert_html) 

# -------------------------------------------------------------- Get BKD Alerts ------------------------------------------------ #
# This function gets all BKD alerts in a consolidated view and renders allalertsbkd.html page
@app.route("/GetAlertsBKD")
def allalertsbkd():
    if not logged_in:
      return render_template('intro.html',error=message)
    else:
        alerts = db_allalertsbkd()
        alert_html = alerts.to_html(classes = 'trans', index = False)
        return render_template('allalertsbkd.html', allalerts = alert_html) 

# -------------------------------------------------------- Get BKD Transactions ------------------------------------------------ #
# This function gets all BKD transactions in a consolidated view and renders alltransbkd.html
@app.route("/GetTransactionsBKD")
def alltransbkd():
    if not logged_in:
      return render_template('intro.html',error=message)
    else:
        alerts = db_alltransbkd()
        alert_html = alerts.to_html(classes = 'trans', index = False)
        return render_template('alltransbkd.html', allalerts = alert_html) 

# -------------------------------------------------------- Get TSD Transactions ------------------------------------------------ #
# This function gets all TSD transactions in a consolidated view and renders alltrans.html
@app.route("/GetTransactions")
def alltrans():
    if not logged_in:
      return render_template('intro.html',error=message)
    else:
        alerts = db_alltrans()
        alert_html = alerts.to_html(classes = 'trans', index = False)
        return render_template('alltrans.html', allalerts = alert_html) 

        
# -------------------------------------------------------- Scenario Description ------------------------------------------------ #
# This function just renders a simple scenario description page.
# The page contains description of all TSD and BKD Scenarios 
@app.route("/Description")
def descs():
    if not logged_in:
      return render_template('intro.html',error=message)
    else:
        return render_template('desc.html')

# ----------------------------------------- Display Alerts of Corresponding Scenario ------------------------------------------- #
# This function renders a webpage which displays alerts corresponding to the scenario short name
@app.route("/Alerts")
def alerts():
    if not logged_in:
      return render_template('intro.html',error=message)
    else:
        # Get the name of the scenario from the arguments stored in table_ids
        table_ids = request.args
        vals = table_ids.get('Name')
        pd.set_option('display.max_colwidth', -1)
        # Apart from vessel scenario, call the db_getAlerts function with the scenario name as an argument
        if  vals != 'Vessel':
            dat = db_getAlerts(vals)    
          
            # Add  2 additional columns with the values shown below
            view_trans = ['View Alerted Transactions']*len(dat)
            view_info = ['View Supporting Information']*len(dat)
            
            dat['Transactions'] = view_trans
            dat['Information'] = view_info
        
        # Call the GetVesselAlerts function just for Vessel scenario and render a separate template 'vessel_alerts.html' 
        # Provide alert data, column list,  focal entity, name of dicrepancy, group numbers separately, scenario short name and scenario full name
        # These arguments are used in the front end
        if vals == 'Vessel':
            dat = db_getvesselalerts('Vessel', 'all') 
            view_trans = ['View Alerted Transactions']*len(dat)
            view_info = ['View Supporting Information']*len(dat)
        
            dat['Transactions'] = view_trans
            dat['Information'] = view_info
            return render_template('vessel_alerts.html', datlist = dat, cols = list(dat.columns), focEnt = dat['FOCALENTITY'], disc_name = dat['SHIPMENT_DISCREPANCY'],
                               groupNo = dat['GROUP_NO'], tablename=vals, alert=dict_tables[vals], scenMonth = scenario_months)
        # Or simply render template.html and provide arguments like the actual alert data, column list, focal entity, scenario short name and full name
        # Those arguments are used in the front end
        elif vals == "ExcWithdrawal" or vals == "Foreign":
            return render_template('template.html', datlist= dat, cols = list(dat.columns), focEnt = dat['FromAccountNumber'], tablename=vals, alert=dict_tables[vals],
                                   scenMonth = scenario_months)
        else:
            return render_template('template.html', datlist= dat, cols = list(dat.columns), focEnt = dat['FOCALENTITY'], tablename=vals, alert=dict_tables[vals])

# The first time, the user requests to view Vessel Alerts, the Above function will be called.
# From then on, the vesselalerts function is called 
# The code is similar to above and the same arguments are provided
@app.route("/VesselAlerts")
def vesselalerts():
    if not logged_in:
      return render_template('intro.html',error=message)
    else:
        table_ids = request.args
        vals = table_ids.get('Name')
        disc = table_ids.get('Value')
        pd.set_option('display.max_colwidth', -1)
        
        dat = db_getvesselalerts(vals, disc)   
        view_trans = ['View Alerted Transactions']*len(dat)
        view_info = ['View Supporting Information']*len(dat)
        
        dat['Transactions'] = view_trans
        dat['Information'] = view_info
        dat.sort_values(by = ['SHIPMENT_DISCREPANCY', 'GROUP_NO'], inplace = True)
        return render_template('vessel_alerts.html', datlist = dat, cols = list(dat.columns), focEnt = dat['FOCALENTITY'], disc_name = dat['SHIPMENT_DISCREPANCY'],
                               groupNo = dat['GROUP_NO'],   tablename=vals, alert=dict_tables[vals])

# ----------------------------------------------------- Display Alerted Transactions of Corresponding Scenario ------------------------------------------------ #
# This function is called only when the users want to view the "alerted transactions"
# The db_getTransactions function takes the focal entity and the scenario short name and retuns the corresponding alerted transactions 
@app.route("/Transactions")
def getTrans():
 if not logged_in:
   return render_template('intro.html',error=message)
 else:
    # ids contain data sent back from the html page
    ids = request.args
    focalentity = ids.get('FocEnt')
    vals = ids.get('AlertTable')
    
    pd.set_option('display.max_colwidth', -1)
    trans = db_getTransactions(focalentity, vals)
  
    # Convert to HTML format and render the transactions.html page
    # Along with the transactions data, the full name of the scenario is also passed
    trans_html = trans.to_html(classes = 'trans', index = False)
    return render_template('transactions.html', translist = trans_html, namealert = dict_tables[vals])

# This function is used only by Vessel & shipment discrepancies if Alerted transactions of this scenario were to be viewed
# It calls the db_getvesseltrans function with arguments Group number and discrepancies
@app.route("/VesselTransactions")
def getvesselTrans():
 if not logged_in:
   return render_template('intro.html',error=message)
 else:
    ids = request.args
    group = ids.get('Group')
    disc = ids.get('Disc')
    pd.set_option('display.max_colwidth', -1)
    trans = db_getvesseltrans(group, disc)
    trans_html = trans.to_html(classes = 'trans', index = False)
    return render_template('transactions.html', translist = trans_html, namealert = dict_tables['Vessel']) 
    
    
# -------------------------------------------------------- View Historical Transactions ------------------------------------------------ #
# This function is called by the New grographies, New Goods, High Risk Jurisdiction, Documentary discrepancies
# and multiple invoice alert display pages.
# When the user clicks on the "View Supporting Information" link on the alerts table, it directs them to different pages based on the scenario and calls the "/Display" route function
@app.route("/Display")
def getGeo():
 if not logged_in:
   return render_template('intro.html',error=message)
 else:
    geo_ids = request.args
    focalentity = geo_ids.get('FocEnt')
    vals = geo_ids.get('AlertTable')
    
    # For new geographies scenario, get data from db_geodata function    
    if vals == "NewGeo":
        dat = db_geodata(focalentity, vals)
        dat['DOCUMENT_AMOUNT'] = dat['DOCUMENT_AMOUNT'].astype(float)
        
        # Only select columns required by the scenario and group by the columns shown below and add the values in columns
        fin_data = dat[["SHIP_FM_COUNTRY", "SHIP_TO_COUNTRY", "COUNTRY_ORIG", "DOCUMENT_AMOUNT", 
        "NEWORIGCOUNTRY", "NEWSHIPTOCOUNTRY", "NEWSHIPFMCOUNTRY"]].groupby(["SHIP_FM_COUNTRY", "SHIP_TO_COUNTRY", "COUNTRY_ORIG"]).sum()
        
        # Change the New Ship from, Ship to and orignatior country as flags rather than sum of transactions
        fin_data["NEWSHIPFMCOUNTRY"].loc[fin_data.NEWSHIPFMCOUNTRY >0] = 1
        fin_data["NEWSHIPTOCOUNTRY"].loc[fin_data.NEWSHIPTOCOUNTRY >0] = 1
        fin_data["NEWORIGCOUNTRY"].loc[fin_data.NEWORIGCOUNTRY >0] = 1
        
        # Group by functions results in creating indexes of columns that were used for grouping
        # This it is required to change the index from the above columns to simple innumeration
        fin_data.reset_index(level=2, inplace=True)
        fin_data.reset_index(level=1, inplace=True)
        fin_data[fin_data.index.name] = fin_data.index
        fin_data.index = np.arange(len(fin_data))
        
        # Merge the ISO code that was read at the start with the data
        fin_data = fin_data.merge(isocode[['ISO2', 'ISO3']], how = 'left', left_on = "COUNTRY_ORIG", right_on = 'ISO2', suffixes=['', 'ORIG'])
        fin_data = fin_data.merge(isocode[['ISO2', 'ISO3']], how = 'left', left_on = "SHIP_FM_COUNTRY", right_on = 'ISO2', suffixes=['', 'SHIP_FM'])
        fin_data = fin_data.merge(isocode[['ISO2', 'ISO3']], how = 'left', left_on = "SHIP_TO_COUNTRY", right_on = 'ISO2', suffixes=['', 'SHIP_TO'])  
        fin_data['FocalEntity'] = str(focalentity)
        
        # Create temporary variables and store all ship to, ship from and originator countries as comma separated strings
        temp1 = list(np.unique(fin_data["SHIP_TO_COUNTRY"]))
        shipto = ', '.join(temp1)
        if shipto == '':
            shipto = '-'

        temp2 = list(np.unique(fin_data["SHIP_FM_COUNTRY"]))
        shipfm = ', '.join(temp2)
        if shipfm == '':
            shipfm = '-'

        temp3 = list(np.unique(fin_data["COUNTRY_ORIG"]))
        countorig = ', '.join(temp3)     
        if countorig == '':
            countorig = '-'

        # Do the same for new ship from, new ship to and new originating countries
        temp4 = list(np.unique(fin_data["SHIP_TO_COUNTRY"].loc[fin_data.NEWSHIPTOCOUNTRY >0]))
        newshipto = ', '.join(temp4)
        if newshipto == '':
            newshipto = '-'

        temp5 = list(np.unique(fin_data["SHIP_FM_COUNTRY"].loc[fin_data.NEWSHIPFMCOUNTRY >0]))
        newshipfm = '\n'.join(temp5)
        if newshipfm == '':
            newshipfm = '-'

        temp6 = list(np.unique(fin_data["COUNTRY_ORIG"].loc[fin_data.NEWORIGCOUNTRY >0]))
        newcountorig = '\n'.join(temp6)      
        if newcountorig == '':
            newcountorig = '-'
        
        # Render the display template and send arguments like focal entity, ship from, ship to, originating countries along with the new counterparts
        # convert the historical transatcions dataframe to html format and send that as an argument also
        return render_template('display.html', fe = str(focalentity), 
                               noFmCnt = shipfm, noToCnt = shipto, noOrCnt = countorig,
                               noNewFmCnt = newshipfm, noNewToCnt = newshipto, noNewOrCnt = newcountorig,
                               hist_trans = dat.to_html(classes='trans1', index = False)
                               )                               
        
    # For new goods scenario, get data from db_geodata function
    elif vals == "NewGoods":
        dat = db_geodata(focalentity, vals)
        dat['DOCUMENT_AMOUNT'] = dat['DOCUMENT_AMOUNT'].astype(float)
        dat['GOODSTYPE'] = dat['GOODSTYPE'].fillna(value = 'Other')
        dat['GOODSTYPE'] = dat['GOODSTYPE'].replace({' ': '_'}, regex = True)
        # Create a variable allgoods that contains all the goods that were traded by the focal entity
        allgoods = '\n '.join(list(np.unique(dat['GOODSTYPE'])))        
        
        # Do the same thing for new goods, high risk goods and dual use goods
        if len(np.unique(dat['GOODSTYPE'].loc[dat['NEWGOODS']==1])) == 0:   
            newgoods = 'NONE'
        else:
            newgoods = '\n '.join(list(np.unique(dat['GOODSTYPE'].loc[dat['NEWGOODS']==1])))
        
        if len(np.unique(dat['GOODSTYPE'].loc[dat['HRGOODS']==1])) == 0:   
            hrgoods = 'NONE'
        else:
            hrgoods = '\n '.join(list(np.unique(dat['GOODSTYPE'].loc[dat['HRGOODS']==1])))
        
        if len(np.unique(dat['GOODSTYPE'].loc[dat['DUGOODS']==1])) == 0:   
            dugoods = 'NONE'
        else:
            dugoods = '\n '.join(list(np.unique(dat['GOODSTYPE'].loc[dat['DUGOODS']==1])))
        
        # create a data frame such that each column represents a single goods type and contains the rows contain the actual values calculated from the above variables
        ag = pd.DataFrame(np.unique(dat['GOODSTYPE']), columns = ['All Goods Type'])
        ng = pd.DataFrame(np.unique(dat['GOODSTYPE'].loc[dat['NEWGOODS']==1]), columns = ['New Goods Type'])
        hrg = pd.DataFrame(np.unique(dat['GOODSTYPE'].loc[dat['HRGOODS']==1]), columns = ['High Risk Goods Type'])
        dug = pd.DataFrame(np.unique(dat['GOODSTYPE'].loc[dat['DUGOODS']==1]), columns = ['Potential Dual Use Goods Type'])
        
        d1 = ag.merge(ng, how = "outer", left_index = True, right_index = True)
        d2 = d1.merge(hrg, how = "outer", left_index = True, right_index = True)
        d3 = d2.merge(dug, how = "outer", left_index = True, right_index = True)
        
        d3.fillna("-", inplace = True)
        
        # Convert this data to html and along with the actual historical transactions data send to newgoods.html
        d3_html = d3.to_html(classes = 'trans', index = False)
        return render_template('newgoods.html',  fe = str(focalentity), hist_trans = dat.to_html(classes='trans1', index = False), d3_info = d3_html,
                               newgoods = newgoods, hrgoods = hrgoods, dugoods = dugoods, allgoods = allgoods )       
       
   
    # For high risk geographies scenario, perform similar calculations like the new geographies scenario but change the columns appropriately
    elif vals == "HRG":
        dat = db_geodata(focalentity, vals)
        dat['DOCUMENT_AMOUNT'] = dat['DOCUMENT_AMOUNT'].astype(float)
        fin_data = dat[["SHIP_FM_COUNTRY", "SHIP_TO_COUNTRY", "COUNTRY_ORIG", "DOCUMENT_AMOUNT", "HIGHRISKORIGCOUNTRY", "HIGHRISKSHIPTOCOUNTRY", "HIGHRISKSHIPFMCOUNTRY"]].groupby(["SHIP_FM_COUNTRY", "SHIP_TO_COUNTRY", "COUNTRY_ORIG"]).sum()
    
        fin_data["HIGHRISKSHIPFMCOUNTRY"].loc[fin_data.HIGHRISKSHIPFMCOUNTRY >0] = 1
        fin_data["HIGHRISKSHIPTOCOUNTRY"].loc[fin_data.HIGHRISKSHIPTOCOUNTRY >0] = 1
        fin_data["HIGHRISKORIGCOUNTRY"].loc[fin_data.HIGHRISKORIGCOUNTRY >0] = 1
        
        fin_data.reset_index(level=2, inplace=True)
        fin_data.reset_index(level=1, inplace=True)
        fin_data[fin_data.index.name] = fin_data.index
        fin_data.index = np.arange(len(fin_data))
        
        fin_data = fin_data.merge(isocode[['ISO2', 'ISO3']], how = 'left', left_on = "COUNTRY_ORIG", right_on = 'ISO2', suffixes=['', 'ORIG'])
        fin_data = fin_data.merge(isocode[['ISO2', 'ISO3']], how = 'left', left_on = "SHIP_FM_COUNTRY", right_on = 'ISO2', suffixes=['', 'SHIP_FM'])
        fin_data = fin_data.merge(isocode[['ISO2', 'ISO3']], how = 'left', left_on = "SHIP_TO_COUNTRY", right_on = 'ISO2', suffixes=['', 'SHIP_TO'])  
        fin_data['FocalEntity'] = str(focalentity)

        temp1 = list(np.unique(fin_data["SHIP_TO_COUNTRY"]))
        shipto = ', '.join(temp1)
        if shipto == '':
            shipto = '-'

        temp2 = list(np.unique(fin_data["SHIP_FM_COUNTRY"]))
        shipfm = ', '.join(temp2)
        if shipfm == '':
            shipfm = '-'

        temp3 = list(np.unique(fin_data["COUNTRY_ORIG"]))
        countorig = ', '.join(temp3)     
        if countorig == '':
            countorig = '-'

        
        temp4 = list(np.unique(fin_data["SHIP_TO_COUNTRY"].loc[fin_data.HIGHRISKSHIPTOCOUNTRY >0]))
        hrshipto = ', '.join(temp4)
        if hrshipto == '':
            hrshipto = '-'

        temp5 = list(np.unique(fin_data["SHIP_FM_COUNTRY"].loc[fin_data.HIGHRISKSHIPFMCOUNTRY >0]))
        hrshipfm = '\n'.join(temp5)
        if hrshipfm == '':
            hrshipfm = '-'

        temp6 = list(np.unique(fin_data["COUNTRY_ORIG"].loc[fin_data.HIGHRISKORIGCOUNTRY >0]))
        hrcountorig = '\n'.join(temp6)      
        if hrcountorig == '':
            hrcountorig = '-'


        return render_template('highriskgeo.html', fe = str(focalentity), noFmCnt = shipfm, 
                               noToCnt = shipto, noOrCnt = countorig,
                               noNewFmCnt = hrshipfm, noNewToCnt = hrshipto,
                               noNewOrigCnt = hrcountorig,
                               hist_trans = dat.to_html(classes='trans1', index = False)
                               )
    # For document discrepancy scenario, get historical transactions data from db_geodata function
    elif vals == "DocDis":
        dat = db_geodata(focalentity, vals)
        dat['DOCUMENT_AMOUNT'] = dat['DOCUMENT_AMOUNT'].astype(float)
        # Count the number of transactions for DiscrepancyFlag = 1 and 0
        # store it as a dataframe in final_data1
        cnt = dat[['DOCUMENT_AMOUNT', 'DISCREPANCYFLAG']].groupby(by = "DISCREPANCYFLAG").count()
        
        cnt['Value'] = "No. of Transactions"
        cnt[cnt.index.name] = cnt.index
        cnt.index = np.arange(len(cnt))
        final_data1 = cnt.pivot(index = 'Value', columns = 'DISCREPANCYFLAG', values = 'DOCUMENT_AMOUNT')
        final_data1.columns = ['No Discrepancy', 'Discrepancy']
        del final_data1.columns.name
        
        final_data1[final_data1.index.name] = final_data1.index
        final_data1.index = np.arange(len(final_data1))  
        
        # Calculate the sum amount for DiscrepancyFlag = 1 and 0
        amt = dat[['DOCUMENT_AMOUNT', 'DISCREPANCYFLAG']].groupby(by = "DISCREPANCYFLAG").sum()
    
        amt['Value'] = "Total Document Amount ($)"
       
        amt[amt.index.name] = amt.index
        amt.index = np.arange(len(amt))
        final_data2 = amt.pivot(index = 'Value', columns = 'DISCREPANCYFLAG', values = 'DOCUMENT_AMOUNT')
        final_data2.columns = ['No Discrepancy', 'Discrepancy']
        del final_data2.columns.name
        
        final_data2[final_data2.index.name] = final_data2.index
        final_data2.index = np.arange(len(final_data2))  
        # Append the two dataframes
        findata = final_data1.append(final_data2)
        
        findata.columns = ['No Discrepancy in Doc.', 'Discrepancy', '']
        findata['Customer'] = str(focalentity)
        # Calculate percentage of discrepancy vs non-discrepancy
        findata['% Discrepancy'] = (findata['Discrepancy'] / (findata['No Discrepancy in Doc.']+findata['Discrepancy'])).round(3)*100.00
        
                
        findata['% Discrepancy'] = findata['% Discrepancy'].astype(str)
        findata['% Discrepancy'] = findata['% Discrepancy']+ '%'

        

        # Calculate total for count and amount 
        findata['Total'] = findata['No Discrepancy in Doc.']+ findata['Discrepancy']        
        # Convert columns into string
        for c in findata.columns:
            findata[c] = findata[c].astype(str)
        
        
        # Create a final data frame with relevant columns and convert to html table format and render docdisc.html
        fin_html = findata[['','Total', 'No Discrepancy in Doc.', 'Discrepancy', '% Discrepancy', 'Customer']] .to_html(classes = 'trans', index = False)
        
        return render_template("docdisc.html", fe = str(focalentity), hist_trans = dat.to_html(classes = "trans1", index = False), disc_info = fin_html)
       
    # Perform similar calculations as Documentary discrepancies, except change the columns and tables appropriately   
    elif vals == "MultiInvoice":
        dat = db_geodata(focalentity, vals)
        
        dat['DOCUMENT_AMOUNT'] = dat['DOCUMENT_AMOUNT'].astype(float)
        cnt = dat[['DOCUMENT_AMOUNT', 'ALERTEDTRANSACTION']].groupby(by = "ALERTEDTRANSACTION").count()
        
        cnt['Value'] = "No. of Transactions"
        cnt[cnt.index.name] = cnt.index
        cnt.index = np.arange(len(cnt))
        final_data1 = cnt.pivot(index = 'Value', columns = 'ALERTEDTRANSACTION', values = 'DOCUMENT_AMOUNT')
        final_data1.columns = ['No Multiple Invoice', 'Multiple Invoice']
        del final_data1.columns.name
        
        final_data1[final_data1.index.name] = final_data1.index
        final_data1.index = np.arange(len(final_data1))  
        
        amt = dat[['DOCUMENT_AMOUNT', 'ALERTEDTRANSACTION']].groupby(by = "ALERTEDTRANSACTION").sum()
    
        amt['Value'] = "Total Document Amount ($)"
       
        amt[amt.index.name] = amt.index
        amt.index = np.arange(len(amt))
        final_data2 = amt.pivot(index = 'Value', columns = 'ALERTEDTRANSACTION', values = 'DOCUMENT_AMOUNT')
        final_data2.columns = ['No Multiple Invoice', 'Multiple Invoice']
        del final_data2.columns.name
        
        final_data2[final_data2.index.name] = final_data2.index
        final_data2.index = np.arange(len(final_data2))  
        
        
        
        
        findata = final_data1.append(final_data2)
        
        findata.columns = ['No Multiple Invoice', 'Multiple Invoice', '']
        findata['Customer'] = str(focalentity)
        findata['% With Multiple Invoices'] = (findata['Multiple Invoice'] / (findata['No Multiple Invoice']+findata['Multiple Invoice'])).round(3)*100.00
        
                
        findata['% With Multiple Invoices'] = findata['% With Multiple Invoices'].astype(str)
        findata['% With Multiple Invoices'] = findata['% With Multiple Invoices']+ '%'

        

        
        findata['Total'] = findata['No Multiple Invoice']+ findata['Multiple Invoice']        
        
        for c in findata.columns:
            findata[c] = findata[c].astype(str)
        
        
        
        fin_html = findata[['','Total','Multiple Invoice', '% With Multiple Invoices', 'Customer']] .to_html(classes = 'trans', index = False)
        return render_template("multinvoice.html", fe = str(focalentity), hist_trans = dat.to_html(classes = "trans1", index = False), invoice_info = fin_html)
    
    # Perform similar calculations as Documentary discrepancies, except change the columns and tables appropriately 
    elif vals == "Carousel":
        dat = db_geodata(focalentity, vals)
        dat['DOCUMENT_AMOUNT'] = dat['DOCUMENT_AMOUNT'].astype(float)
        if len(np.unique(dat['GOODSTYPE'].loc[(dat['CAROUSELTRANSACTIONS']==1) & (dat['ImpExp'] == 'Import')])) == 0:   
            importgoods = 'NONE'
        else:
            importgoods = '\n '.join(list(np.unique(dat['GOODSTYPE'].loc[(dat['CAROUSELTRANSACTIONS']==1) & (dat['ImpExp'] == 'Import')])))
        
        if len(np.unique(dat['GOODSTYPE'].loc[(dat['CAROUSELTRANSACTIONS']==1) & (dat['ImpExp'] == 'Export')])) == 0:   
            exportgoods = 'NONE'
        else:
            exportgoods = '\n '.join(list(np.unique(dat['GOODSTYPE'].loc[(dat['CAROUSELTRANSACTIONS']==1) & (dat['ImpExp'] == 'Export')])))
        
        car_sum = dat[['DOCUMENT_AMOUNT', 'ImpExp']].loc[dat['CAROUSELTRANSACTIONS'] == 1].groupby(by = 'ImpExp').sum()
        car_sum.columns = ['Total Sum']        
        car_count = dat[['DOCUMENT_AMOUNT', 'ImpExp']].loc[dat['CAROUSELTRANSACTIONS'] == 1].groupby(by = 'ImpExp').count()
        car_count.columns = ['# Transactions']
        car = car_sum.merge(car_count, left_index = True, right_index = True)
        car[car.index.name] = car.index
        car.index = np.arange(len(car)) 
        car['Customer Number'] = focalentity
        car['Goods'] = ''
        car['Goods'].loc[dat['ImpExp'] == 'Export'] = exportgoods
        car['Goods'].loc[dat['ImpExp'] == 'Import'] = importgoods
        car.columns = ['Total Transaction Amount', '# Transactions', 'Import/Export', 'Customer Number','Goods']
        carousel = car[['Customer Number', 'Total Transaction Amount', '# Transactions', 'Import/Export', 'Goods']].to_html(classes = "trans", index = False)
        return render_template("carousel.html", fe = str(focalentity), hist_trans = dat.to_html(classes = "trans1", index = False), carousel_info = carousel)
    
    # Excessive withdrawal transactions, supporting information and the graphs are displayed in excwithdrawal.html page
    elif vals == "ExcWithdrawal":
        dat = db_geodata(focalentity, vals)     
        dat1 = db_getCardData(focalentity, vals)
        return render_template("excwithdrawal.html", fe = str(focalentity), hist_trans = dat.to_html(classes = "trans1", index = False), 
                               withdrawal_info = dat1.to_html(classes = "trans", index = False) )
    
    # Foreign Debit card transactions, supporting information and the graphs are displayed in foreigndebit.html page
    elif vals == "Foreign":
        dat = db_geodata(focalentity, vals)
        fin_data = dat[["TerminalCountry", "TransactionAmount", "AlertedTxn"]].groupby(["TerminalCountry"]).sum()
    
        fin_data["AlertedTxn"].loc[fin_data.AlertedTxn >0] = 1
       
        
        fin_data[fin_data.index.name] = fin_data.index
        fin_data.index = np.arange(len(fin_data))
        isocode['Country'] = isocode['Country'].str.upper()
        fin_data['TerminalCountry'] = fin_data['TerminalCountry'].str.strip()
        fin_data = fin_data.merge(isocode[['ISO2', 'ISO3', 'Country']], how = 'left', left_on = "TerminalCountry", right_on = 'Country')
        
        fin_data['FocalEntity'] = str(focalentity)

        temp1 = list(np.unique(fin_data["TerminalCountry"]))
        termCnt = ', '.join(temp1)
        if termCnt == '':
            termCnt = '-'

        temp4 = list(np.unique(fin_data["TerminalCountry"].loc[fin_data.AlertedTxn >0]))
        fortermCnt = ', '.join(temp4)
        if fortermCnt == '':
            fortermCnt = '-'

        customerNumber = str(dat['CustomerID'].iloc[0])
        customerName = str(dat['CustomerName'].iloc[0])
        return render_template('foreigndebit.html', fe = str(focalentity), cuName = customerName, cuNo = customerNumber,
                               noTermCnt = termCnt, noForTermCnt = fortermCnt,
                               hist_trans = dat.to_html(classes='trans1', index = False)
                               )
        
        
# This renders vessel_info.html with alerted transactions based on the focal entity and other discrepancy information
@app.route("/VesselDisplay")
def vesselinfo():
 if not logged_in:
   return render_template('intro.html',error=message)
 else:
    vessel_id = request.args
    focalentity = vessel_id.get('FocEnt')
    dat, shpmt =  db_vesselmap(focalentity)
    dat['DOCUMENT_AMOUNT'] = dat['DOCUMENT_AMOUNT'].astype(float)
    
    discpr = shpmt.to_string(header = False, index = False, index_names = False).split('\n')
    discp_list = ', '.join(discpr)
    
    
    dat_display = pd.DataFrame([[focalentity, dat['DOCUMENT_AMOUNT'].sum(), dat['DOCUMENT_AMOUNT'].count(), discp_list ]], 
                                 columns = ['Focal Entity', 'Total Transaction Amount', '# Transactions',  'All Shipment Discrepancies'])




    fin_html = dat_display.to_html(classes = 'trans', index = False)
    
    return render_template("vessel_info.html", fe = str(focalentity), hist_trans = dat.to_html(classes = "trans1", index = False), discrepancy_info = fin_html)
#---------------------------------------------------  New Geography ---------------------------------------------------------------------- #
# This function is called by a JavaScript file "gdata.js" to plot map with countries the focal entity has transacted with
@app.route("/Displays")
def geomap():
 if not logged_in:
   return render_template('intro.html',error=message)
 else:
    geo_ids = request.args
    focalentity = geo_ids.get('FocEnt')
    vals = geo_ids.get('AlertTable')
    
    # Get historical transactions data 
    dat = db_geodata(focalentity, vals)
    dat['DOCUMENT_AMOUNT'] = dat['DOCUMENT_AMOUNT'].astype(float)
    #time.sleep(3)
    # Apply group by function with relevant columns
    fin_data = dat[["SHIP_FM_COUNTRY", "SHIP_TO_COUNTRY", "COUNTRY_ORIG", "DOCUMENT_AMOUNT", "NEWORIGCOUNTRY", "NEWSHIPTOCOUNTRY", "NEWSHIPFMCOUNTRY"]].groupby(["SHIP_FM_COUNTRY", "SHIP_TO_COUNTRY", "COUNTRY_ORIG"]).sum()
    # Change numbers to flags for ease of mapping
    fin_data["NEWSHIPFMCOUNTRY"].loc[fin_data.NEWSHIPFMCOUNTRY >0] = 1
    fin_data["NEWSHIPTOCOUNTRY"].loc[fin_data.NEWSHIPTOCOUNTRY >0] = 1
    fin_data["NEWORIGCOUNTRY"].loc[fin_data.NEWORIGCOUNTRY >0] = 1

    
    fin_data.reset_index(level=2, inplace=True)
    fin_data.reset_index(level=1, inplace=True)
    fin_data[fin_data.index.name] = fin_data.index
    fin_data.index = np.arange(len(fin_data))
    # Merge with ISO data loaded at the beginning
    fin_data = fin_data.merge(isocode[['ISO2', 'ISO3']], how = 'left', left_on = "COUNTRY_ORIG", right_on = 'ISO2', suffixes=['', 'ORIG'])
    fin_data = fin_data.merge(isocode[['ISO2', 'ISO3']], how = 'left', left_on = "SHIP_FM_COUNTRY", right_on = 'ISO2', suffixes=['', 'SHIP_FM'])
    fin_data = fin_data.merge(isocode[['ISO2', 'ISO3']], how = 'left', left_on = "SHIP_TO_COUNTRY", right_on = 'ISO2', suffixes=['', 'SHIP_TO'])  
    fin_data['FocalEntity'] = str(focalentity)
    fin_data = fin_data.replace(' ', '')
    # This is an important step.
    # Every javascript file requires data to be in CSV format or | delimited format. Since, it is not good practice to store the data in CSV format and then read it separately by the 
    # javascript file, the conversion into csv or | delimited format is performed here and directly sent to the javascript file
    gdata = fin_data.to_string(header=True, index=False, index_names=False).split('\n')
    
    # First conver the data to string as above then split by ','.
    # This requires that the data does not contain any string or spaces in between 
    # This will cause mapping error of the data to the right columns
    geodata = [','.join(ele.split()) for ele in gdata]
    # Finally separate each row by \n and return this raw file. WHenever this URL or function is called, raw data is returned
    gd = '\n'.join(geodata)
    return  gd


# Same as above but for a line chart.
# This url/function is called by the "line_chart.js"
@app.route("/Displays2")
def linechart():
 if not logged_in:
   return render_template('intro.html',error=message)
 else:
    l_ids = request.args
    focalentity = l_ids.get('FocEnt')
    vals = l_ids.get('AlertTable')
    
    
    ldat = db_linedata(focalentity, vals)
    ldat['DOCUMENT_AMOUNT'] = ldat['DOCUMENT_AMOUNT'].astype(float)
    #time.sleep(1)
    
    ldat['TRANS_DATE'] = ldat['TRANS_DATE'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
    ldat.sort_values(by=['TRANS_DATE'], ascending=True, inplace=True)

    fd, ld = get_dates(ldat,6)
    dat_dates = pd.date_range(start = fd, end = ld)
    ldat = pd.DataFrame(dat_dates, columns = ['Dates']).merge(ldat, how='left', left_on = 'Dates', right_on = 'TRANS_DATE')
    ldat['DOCUMENT_AMOUNT'].fillna(value = 0, inplace = True)
   
    
    ldata = ldat.to_string(header=True, index=False, index_names=False).split('\n')
    
    linedata = ['|'.join(ele.split()) for ele in ldata]
    
    ld= '\n'.join(linedata)
    return  ld
    
        
#-------------------------------------------------------- New Goods ----------------------------------------------------------------------------------- #

# This function is called by a JavaScript file "multi_bar.js" to plot bar graphs of different goods traded by the focal entity using historical and current data
@app.route("/Goods")
def goods():   
 if not logged_in:
   return render_template('intro.html',error=message)
 else:
    # Get relevant historical transactions data 
    goods_ids = request.args
    focalentity = goods_ids.get('FocEnt')
    vals = goods_ids.get('AlertTable')
   
    # Convert transaction date to date format from integer
    dat = db_geodata(focalentity, vals)
    dat['DOCUMENT_AMOUNT'] = dat['DOCUMENT_AMOUNT'].astype(float)
    dat['GOODSTYPE'] = dat['GOODSTYPE'].fillna(value = 'Other')
    dat['GOODSTYPE'] = dat['GOODSTYPE'].replace({' ':'_'}, regex = True)
    dat['TRANS_DATE'] = dat['TRANS_DATE'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
    dat.sort_values(by=['TRANS_DATE'], ascending=True, inplace=True)
    dat['Month'] = dat['TRANS_DATE'].apply(lambda x: 100*x.month+10000*x.year)
    dat['DOCUMENT_AMOUNT'] = dat['DOCUMENT_AMOUNT'].astype(float)
    
    
    # Calculating Sum
    fin_data = dat.groupby(by = ['Month', 'GOODSTYPE'], sort = False).sum()
    fin_data.reset_index(level=1, inplace=True)
    fin_data[fin_data.index.name] = fin_data.index
    fin_data.index = np.arange(len(fin_data))
    fin_data1 = fin_data[['GOODSTYPE', 'Month', 'DOCUMENT_AMOUNT']]   
    fin_data2 = fin_data1.pivot(index = 'Month', columns = 'GOODSTYPE', values = 'DOCUMENT_AMOUNT')
    fin_data2.fillna(value = 0.05, inplace = True)
    
    del fin_data2.columns.name
    
    fin_data2[fin_data2.index.name] = fin_data2.index
    fin_data2.index = np.arange(len(fin_data2))
    fin_data2['Month'] = ((fin_data2['Month']%10000)/100).astype(int)
    fin_data2['Month'] = map(getMonth, fin_data2['Month'])    
    
    
    
    
  
    gdata = fin_data2.to_string(header=True, index=False, index_names=False).split('\n')
    
    geodata = ['|'.join(ele.split()) for ele in gdata]
    
    gd = '\n'.join(geodata)
    return  gd
    
# This function is called by a JavaScript file "newgoods_linechart.js" to plot historical data
# This is similar to new geography linechart
@app.route("/Goods2")
def goodslinechart():
 if not logged_in:
   return render_template('intro.html',error=message)
 else:
    l_ids = request.args
    focalentity = l_ids.get('FocEnt')
    vals = l_ids.get('AlertTable')
    
    ldat = db_linedata(focalentity, vals)
    ldat['DOCUMENT_AMOUNT'] = ldat['DOCUMENT_AMOUNT'].astype(float)
    ldat['GOODSTYPE'] = ldat['GOODSTYPE'].fillna(value = 'Other')
    ldat['GOODSTYPE'] = ldat['GOODSTYPE'].replace({' ':'_'}, regex = True)
    
    ldat['TRANS_DATE'] = ldat['TRANS_DATE'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
    ldat.sort_values(by=['TRANS_DATE'], ascending=True, inplace=True)

    fd, ld = get_dates(ldat, 6)
    dat_dates = pd.date_range(start = fd, end = ld)
    ldat = pd.DataFrame(dat_dates, columns = ['Dates']).merge(ldat, how='left', left_on = 'Dates', right_on = 'TRANS_DATE')
    ldat['DOCUMENT_AMOUNT'].fillna(value = 0, inplace = True)
   
    
    ldata = ldat.to_string(header=True, index=False, index_names=False).split('\n')
    
    linedata = ['|'.join(ele.split()) for ele in ldata]
    
    ld= '\n'.join(linedata)
    return  ld

#----------------------------------------------------------------------------- High Risk Geographies ------------------------------------------------------------ #
# This is similar to New Geographies with the Javascript file highriskgeo.js to plot the map data
@app.route("/Highrisk")
def highriskgeo():
 if not logged_in:
   return render_template('intro.html',error=message)
 else:
    geo_ids = request.args
    focalentity = geo_ids.get('FocEnt')
    vals = geo_ids.get('AlertTable')
    dat = db_geodata(focalentity, vals)
    dat['DOCUMENT_AMOUNT'] = dat['DOCUMENT_AMOUNT'].astype(float)
    fin_data = dat[["SHIP_FM_COUNTRY", "SHIP_TO_COUNTRY", "COUNTRY_ORIG", "DOCUMENT_AMOUNT", "HIGHRISKORIGCOUNTRY", "HIGHRISKSHIPTOCOUNTRY", "HIGHRISKSHIPFMCOUNTRY"]].groupby(["SHIP_FM_COUNTRY", "SHIP_TO_COUNTRY", "COUNTRY_ORIG"]).sum()
    
    fin_data["HIGHRISKSHIPFMCOUNTRY"].loc[fin_data.HIGHRISKSHIPFMCOUNTRY >0] = 1
    fin_data["HIGHRISKSHIPTOCOUNTRY"].loc[fin_data.HIGHRISKSHIPTOCOUNTRY >0] = 1
    fin_data["HIGHRISKORIGCOUNTRY"].loc[fin_data.HIGHRISKORIGCOUNTRY >0] = 1

    
    fin_data.reset_index(level=2, inplace=True)
    fin_data.reset_index(level=1, inplace=True)
    fin_data[fin_data.index.name] = fin_data.index
    fin_data.index = np.arange(len(fin_data))
    
    fin_data = fin_data.merge(isocode[['ISO2', 'ISO3']], how = 'left', left_on = "COUNTRY_ORIG", right_on = 'ISO2', suffixes=['', 'ORIG'])
    fin_data = fin_data.merge(isocode[['ISO2', 'ISO3']], how = 'left', left_on = "SHIP_FM_COUNTRY", right_on = 'ISO2', suffixes=['', 'SHIP_FM'])
    fin_data = fin_data.merge(isocode[['ISO2', 'ISO3']], how = 'left', left_on = "SHIP_TO_COUNTRY", right_on = 'ISO2', suffixes=['', 'SHIP_TO'])  
    fin_data['FocalEntity'] = str(focalentity)
    fin_data = fin_data.replace(' ', '')
    gdata = fin_data.to_string(header=True, index=False, index_names=False).split('\n')
    
    geodata = [','.join(ele.split()) for ele in gdata]
    
    gd = '\n'.join(geodata)
    return  gd


# This calls the hrg_linechart.js file to plot the historical data
@app.route("/Highrisk2")
def hrlinechart():
 if not logged_in:
   return render_template('intro.html',error=message)
 else:
    l_ids = request.args
    focalentity = l_ids.get('FocEnt')
    vals = l_ids.get('AlertTable')
    
    ldat = db_linedata(focalentity, vals)
    ldat['DOCUMENT_AMOUNT'] = ldat['DOCUMENT_AMOUNT'].astype(float)
    
    ldat['TRANS_DATE'] = ldat['TRANS_DATE'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
    ldat.sort_values(by=['TRANS_DATE'], ascending=True, inplace=True)

    fd, ld = get_dates(ldat, 6)
    dat_dates = pd.date_range(start = fd, end = ld)
    ldat = pd.DataFrame(dat_dates, columns = ['Dates']).merge(ldat, how='left', left_on = 'Dates', right_on = 'TRANS_DATE')
    ldat['DOCUMENT_AMOUNT'].fillna(value = 0, inplace = True)
   
    
    ldata = ldat.to_string(header=True, index=False, index_names=False).split('\n')
    
    linedata = ['|'.join(ele.split()) for ele in ldata]
    ld= '\n'.join(linedata)
    return  ld

# -------------------------------------------------------- Document Discrepancy ------------------------------------------------------------------ #
# This plots the historical data by calling docdis_linechart.js which is similar to other linecharts
@app.route("/DocDis3")
def docdiscline():
 if not logged_in:
   return render_template('intro.html',error=message)
 else:
    geo_ids = request.args
    focalentity = geo_ids.get('FocEnt')
    vals = geo_ids.get('AlertTable')
    
    
    ldat = db_geodata(focalentity, vals)
    ldat['DOCUMENT_AMOUNT'] = ldat['DOCUMENT_AMOUNT'].astype(float)
    
    ldat['TRANS_DATE'] = ldat['TRANS_DATE'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
    ldat.sort_values(by=['TRANS_DATE'], ascending=True, inplace=True)

    fd, ld = get_dates(ldat, 6)
    dat_dates = pd.date_range(start = fd, end = ld)
    ldat = pd.DataFrame(dat_dates, columns = ['Dates']).merge(ldat, how='left', left_on = 'Dates', right_on = 'TRANS_DATE')
    ldat['DOCUMENT_AMOUNT'].fillna(value = 0, inplace = True)
   
    
    ldata = ldat[['DOCUMENT_AMOUNT', 'TRANS_DATE', 'Dates', 'DISCREPANCYFLAG']].to_string(header=True, index=False, index_names=False).split('\n')
    
    linedata = [','.join(ele.split()) for ele in ldata]
    
    ld= '\n'.join(linedata)
    return  ld

# ------------------------------------------------------------ Multiple Invoice ------------------------------------------------------------------- #
# This plots historical data by calling multi_invoice_linechart.js
@app.route("/MultiInvoice")
def multiInvoiceline():
 if not logged_in:
   return render_template('intro.html',error=message)
 else:
    geo_ids = request.args
    focalentity = geo_ids.get('FocEnt')
    vals = geo_ids.get('AlertTable')
    
    
    ldat = db_geodata(focalentity, vals)
    ldat['DOCUMENT_AMOUNT'] = ldat['DOCUMENT_AMOUNT'].astype(float)
    
    ldat['TRANS_DATE'] = ldat['TRANS_DATE'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
    ldat.sort_values(by=['TRANS_DATE'], ascending=True, inplace=True)

    fd, ld = get_dates(ldat, 6)
    dat_dates = pd.date_range(start = fd, end = ld)
    ldat = pd.DataFrame(dat_dates, columns = ['Dates']).merge(ldat, how='left', left_on = 'Dates', right_on = 'TRANS_DATE')
    ldat['DOCUMENT_AMOUNT'].fillna(value = 0, inplace = True)
    ldat['TRANS_DATE']=ldat['Dates']
    
    ldata = ldat[['DOCUMENT_AMOUNT', 'TRANS_DATE', 'ALERTEDTRANSACTION', 'Dates']].to_string(header=True, index=False, index_names=False).split('\n')
    
    linedata = [','.join(ele.split()) for ele in ldata]
    
    ld= '\n'.join(linedata)
    return  ld


#------------------------------------------------------- Vessel & Shipment Discrepancy------------------------------------------------------------ #
# This plots historical data by calling vessel_linechart.js    
@app.route("/VesselChart")
def vesselchart():
 if not logged_in:
   return render_template('intro.html',error=message)
 else:
    vessel_id = request.args
    focalentity = vessel_id.get('FocEnt')
    
    dat1, shpmt =  db_vesselmap(focalentity)
    dat1['DOCUMENT_AMOUNT'] = dat1['DOCUMENT_AMOUNT'].astype(float)
    dat1['TRANS_DATE'] = dat1['TRANS_DATE'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
    dat1.sort_values(by=['TRANS_DATE'], ascending=True, inplace=True)
    fd, ld = get_dates(dat1, 6)
    dat_dates = pd.date_range(start = fd, end = ld)
    dat1 = pd.DataFrame(dat_dates, columns = ['Dates']).merge(dat1, how='left', left_on = 'Dates', right_on = 'TRANS_DATE')
    dat1['DOCUMENT_AMOUNT'].fillna(value = 0, inplace = True)
    dat1['TRANS_DATE']=dat1['Dates']
    
    dat1 = dat1[['DOCUMENT_AMOUNT', 'TRANS_DATE', 'Dates']].to_string(header=True, index=False, index_names=False).split('\n')
    
    linedata = [','.join(ele.split()) for ele in dat1]
    
    ld= '\n'.join(linedata)
    return  ld
    
# --------------------------------------------------------------------- Carousel ----------------------------------------------------------------------- #
# This plots historical data by calling carousel_linechart.js    
@app.route("/CarouselLine")
def carouselline():
 if not logged_in:
   return render_template('intro.html',error=message)
 else:
    geo_ids = request.args
    focalentity = geo_ids.get('FocEnt')
    vals = geo_ids.get('AlertTable')
    
    
    ldat = db_geodata(focalentity, vals)
    ldat['DOCUMENT_AMOUNT'] = ldat['DOCUMENT_AMOUNT'].astype(float)
    
    ldat['TRANS_DATE'] = ldat['TRANS_DATE'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
    ldat.sort_values(by=['TRANS_DATE'], ascending=True, inplace=True)

    fd, ld = get_dates(ldat, 6)
    dat_dates = pd.date_range(start = fd, end = ld)
    ldat = pd.DataFrame(dat_dates, columns = ['Dates']).merge(ldat, how='left', left_on = 'Dates', right_on = 'TRANS_DATE')
    ldat['DOCUMENT_AMOUNT'].fillna(value = 0, inplace = True)
   
    
    ldata = ldat[['DOCUMENT_AMOUNT', 'TRANS_DATE', 'Dates', 'ImpExp']].to_string(header=True, index=False, index_names=False).split('\n')
    
    linedata = [','.join(ele.split()) for ele in ldata]
    
    ld= '\n'.join(linedata)
    return  ld
  
#--------------------------------------------------- Debit Card Scenarios ------------------------------------------------------------------------------ #
# The Debit Card scenarios are similar to the TSD scenarios above

# ---------------------------------------------------------- Excessive Withdrawals ------------------------------------------------------------------- #
# This plots the historical data by calling withdrawal_linechart.js
@app.route("/WithdrawalLine")
def excWithdrawal():
    if not logged_in:
        return render_template('intro.html',error=message)
    else:
        geo_ids = request.args
        focalentity = geo_ids.get('FocEnt')
        vals = geo_ids.get('AlertTable')
        
        
        ldat = db_geodata(focalentity, vals)
        ldat['FromAccountNumber'] = ldat['FromAccountNumber'].astype(int)
        print ldat['TransactionDate']
        
        ldat['TRANS_DATE'] = ldat['TransactionDate'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
        
        ldat.sort_values(by=['TRANS_DATE'], ascending=True, inplace=True)
        
        fd, ld = get_dates(ldat, 11)
        dat_dates = pd.date_range(start = fd, end = ld)
        ldat = pd.DataFrame(dat_dates, columns = ['Dates']).merge(ldat, how='left', left_on = 'Dates', right_on = 'TRANS_DATE')
        ldat['TransactionAmount'].fillna(value = 0, inplace = True)
       
        
        ldata = ldat[['TransactionAmount', 'TRANS_DATE', 'Dates','AlertedTxn']].to_string(header=True, index=False, index_names=False).split('\n')
        
        linedata = [','.join(ele.split()) for ele in ldata]
        
        ld= '\n'.join(linedata)
        return  ld

# ---------------------------------------------------------- Foreign Debit Transactions ------------------------------------------------------------------- #
# This plots the map chart by calling foreign_geo.js
@app.route("/ForeignGeo")
def foreignGeo():
    if not logged_in:
        return render_template('intro.html',error=message)
    else:
        geo_ids = request.args
        focalentity = geo_ids.get('FocEnt')
        vals = geo_ids.get('AlertTable')
        
        dat = db_geodata(focalentity, vals)
        fin_data = dat[["TerminalCountry", "TransactionAmount", "AlertedTxn"]].groupby(["TerminalCountry"]).sum()
        fin_data["AlertedTxn"].loc[fin_data.AlertedTxn >0] = 1
        fin_data[fin_data.index.name] = fin_data.index
        fin_data.index = np.arange(len(fin_data))
        isocode['Country'] = isocode['Country'].str.upper()
        fin_data['TerminalCountry'] = fin_data['TerminalCountry'].str.strip()
        fin_data = fin_data.merge(isocode[['ISO2', 'ISO3', 'Country']], how = 'left', left_on = "TerminalCountry", right_on = 'Country')
        
        fin_data['FocalEntity'] = str(focalentity)
        fin_data['AlertedTxn'].loc[fin_data["TerminalCountry"] == "UNITED STATES"] = 0
        fin_data['AlertedTxn'].loc[fin_data["TerminalCountry"] != "UNITED STATES"] = 1
        gdata = fin_data[["ISO3", "AlertedTxn"]].to_string(header=True, index=False, index_names=False).split('\n')
        
        geodata = [','.join(ele.split()) for ele in gdata]
        
        gd = '\n'.join(geodata)
        return  gd
        
# This plots the historical data on a linechart by calling foreign_linechart.js
@app.route("/ForeignLine")
def foreignLine():
    if not logged_in:
        return render_template('intro.html',error=message)
    else:
        geo_ids = request.args
        focalentity = geo_ids.get('FocEnt')
        vals = geo_ids.get('AlertTable')
        
        
        ldat = db_linedata(focalentity, vals)
        
        
        ldat['TRANS_DATE'] = ldat['TransactionDate'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
        ldat.sort_values(by=['TRANS_DATE'], ascending=True, inplace=True)
    
        fd, ld = get_dates(ldat, 11)
        dat_dates = pd.date_range(start = fd, end = ld)
        ldat = pd.DataFrame(dat_dates, columns = ['Dates']).merge(ldat, how='left', left_on = 'Dates', right_on = 'TRANS_DATE')
        ldat['TransactionAmount'].fillna(value = 0, inplace = True)
        isocode['Country'] = isocode['Country'].str.upper()
        ldat['TerminalCountry'] = ldat['TerminalCountry'].str.strip()
        ldat = ldat.merge(isocode[['ISO2', 'Country']], how = 'left', left_on = "TerminalCountry", right_on = 'Country')
        
        ldata = ldat[['TransactionAmount', 'TRANS_DATE', 'Dates','AlertedTxn', 'ISO2']].to_string(header=True, index=False, index_names=False).split('\n')
        
        linedata = [','.join(ele.split()) for ele in ldata]
        
        ld= '\n'.join(linedata)
        return  ld
# ------------------------------------------------------------------------ END ---------------------------------------------------------- #
        
# Main function. In order to run the application you call it in the main function
# debug = 'True' will help with error catching
if __name__ == "__main__": 
    app.run(debug = 'True')
    
# ------------------------------------------------------------------------------------------------------------------------ #   
# Minor Things to consider #
# 1. All major columns like Focal Entity or Goods Type should not contain spaces
# 2. Spaces shoud be replace by '_'
# 3. Changes made to either column name or any data type change made in SQL must also be reflected in the python code above.
# 4. Any error encountered while using the application can be viewed in the error log present in WAMP Server.
# 5. Click on wamp server in the left hand bottom hidden icons and go to Apache and Apache error log
# ------------------------------------------------------------------------------------------------------------------------ #