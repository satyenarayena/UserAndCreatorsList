import json
import os
import time,decimal
from bson.json_util import dumps
from django.http import HttpResponse
import jwt
from .settings import *
from .models import *
import re

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.generic.base import View


class Register(View):
    def post(self,request):
        callBack='Register'
        startTime=time.time()
        result = {"message": "", "status": "failed", "code": "200", "statustext": "ok", "callback": callBack,"start_time":startTime}
        try:
            result.update({"message": "Please pass name"})
            if 'name' in request.POST and request.POST['name'] != '':
                result.update({"message": "Please pass email"})
                if 'email' in request.POST and request.POST['email'] != '':
                    result.update({"message": "Please pass password"})
                    if 'password' in request.POST and request.POST['password'] != '':
                        result.update({"message": "Please pass profilePhoto"})
                        if 'profilePhoto' in request.FILES and  request.FILES.getlist('profilePhoto') != '':
                            filePath,fileName = fileProcessor(request.FILES.getlist("profilePhoto"))
                            result.update({"message": "Please pass phone"})
                            if 'phone' in request.POST and request.POST['phone'] != '':
                                result = createRegisterDef(request.POST['name'] ,request.POST['email'],request.POST['password'],filePath,fileName, request.POST['phone'],result)
        except KeyError as e:  # whether an KeyError occurs#
            result.update({"message": "please pass " + e.message.replace("", "") + " parameter", "responsetime": str(round(decimal.Decimal('{}'.format(time.time() - startTime)), 3)) + " sec", "code": "400","status": "failed", "callback": callBack})
        return HttpResponse(dumps(result))

def createRegisterDef(name,email,password,filePath,fileName,phone,result):
    userId=str(int(time.time()))
    payload = {
        'id': userId,
        'email': name,
    }
    token = jwt.encode(payload, "SECRET", algorithm="HS256")
    print(token)
    conditionSet = {"userName": email}
    checkUserName=userLoginConditionSetModels(conditionSet)
    print("abcdffff",checkUserName)
    result.update({"message":"UserName Already exists"})
    if len(checkUserName) == 0:
        filePath = refine(filePath)
        data = {"userName":email,"password":password,"name":name,"profilePath":filePath,"phone":phone,"email":email,"userId":userId,"profilePhoto":fileName ,"token":str(token)}
        generatedId = register(data)
        result.update({"status": "failure", "message": "User Registration failure"})
        if generatedId:
            conditionSet = {"userName": email, "password": password}
            response=userLoginConditionSetModels(conditionSet)
            result.update({"status":"success","message":"User Registration created successfully","response":response})
    return result


def fileProcessor(files):

    filePath = ""
    fileName = files[0].name
    fileType = fileName.split('.')[-1]
    # message = "only 'xls', 'xlsx' and csv files are allowed."
    # message = "only txt files are allowed."
    # if fileType == "":# or fileType == "xls" or fileType == "xlsx" or fileType == "csv":
    filePath = os.path.join(MEDIA_ROOT,"files", str(int(time.time())) + "_" + fileName)
    filePath = filePath.replace(" ", '_')
    print(filePath)
    default_storage.save("%s" % (filePath), ContentFile(files[0].read()))  ##to default stroage filepath address
    message = ""
    return filePath,fileName


def refine(address): ## def refine starts here
    dir1 = address.split(os.sep)[-3]
    dir0 = address.split(os.sep)[-4]
    dir2 = address.split(os.sep)[-2]
    fn = address.split(os.sep)[-1]
    path = dir0+os.sep+dir1+os.sep+dir2+os.sep+fn
    return path

def getHeaders(request):
    print("abc")
    regex = re.compile('^HTTP_')
    headers = dict((regex.sub('', header), value) for (header, value) in request.META.items() if header.startswith('HTTP_'))
    return headers


class LoginUser(View):
	def get(self,request):
		start_time = time.time() #getting current system time
		callback = "LoginUser"
		result = {"message": "", "status": "failed", "code": "200", "statustext": "ok", "callback": callback,"start_time":start_time}
		try:
			emailId=''
			parameters = dict(request.GET)
			if "emailId" in parameters and parameters['emailId'][0] != "":
				emailId = parameters['emailId'][0]

			result.update({"message": "please pass userName and must be non empty value"})
			if "userName" in parameters and (not parameters['userName'][0].isspace()) and parameters['userName'][0] != "" and parameters['userName'][0] != "null":
				result.update({"message": "please pass password and must be non empty value"})
				if "password" in parameters and (not parameters['password'][0].isspace()) and parameters['password'][0] != "" and parameters['password'][0] != "null":

					result = userLogin(emailId,parameters['userName'][0],parameters['password'][0],result)  # calling GetSingleUserDef and return the function result
		#
		except KeyError as e: #whether an KeyError occurs then pass the code
			result.update({"message": "parameter " + e.args[0].replace("'", "") + " is missing", "code": "400","statustext": "bad request"})
		result.update({"responsetime": str(round(decimal.Decimal('{}'.format(time.time() - start_time)), 3)) + " sec"}) #updating response time in result
		return HttpResponse(dumps(result)) #return response to browser

def userLogin(emailId,userName,password,result):
    conditionSet={}
    if userName != '':
        conditionSet = {"userName": userName,"password":password} ## Even Not a verified User Considers as Not Exist
    dbUserData =userLoginConditionSetModels(conditionSet)
    result.update({'status': 'failed', 'message': 'Login failed. Unknown userName or password'})
    if dbUserData:# check the user with email exists or not.
        result.update({'message': 'User Data Successfully retrieved',"code":"200","status":"success","response":dbUserData})
    return  result


class Categories(View):
    def post(self,request):
        callBack='Categories'
        startTime=time.time()
        parent = ''
        result = {"message": "", "status": "failed", "code": "200", "statustext": "ok", "callback": callBack,"start_time":startTime}
        try:
            requestHeaders = getHeaders(request)  # getting values from headers
            result.update({"message": "Please pass name"})
            if 'name' in request.POST and request.POST['name'] != '':
                result.update({"message": "Please pass name_ar"})
                if 'name_ar' in request.POST and request.POST['name_ar'] != '':
                    result.update({"message": "Please pass category_banner"})
                    if 'category_banner' in request.FILES and request.FILES.getlist('category_banner') != '':
                        filePath,fileName = fileProcessor(request.FILES.getlist("category_banner"))
                        if "parent" in request.POST and request.POST['parent'] != "":
                            parent = request.POST['parent']
                        result.update({"message": "please pass TOKEN in headers and must be non empty value"})
                        if str("TOKEN") in requestHeaders and (not str(requestHeaders["TOKEN"]).isspace()) and str(requestHeaders["TOKEN"]) != "" and str(requestHeaders["TOKEN"]) != "null":  # check  TOKEN is null or not
                            print(requestHeaders["TOKEN"])
                            result = createCategoriesDef(str(requestHeaders["TOKEN"]),request.POST['name'] ,request.POST['name_ar'],filePath,fileName,parent,result)
        except KeyError as e:  # whether an KeyError occurs#
            result.update({"message": "please pass " + e.message.replace("", "") + " parameter", "responsetime": str(round(decimal.Decimal('{}'.format(time.time() - startTime)), 3)) + " sec", "code": "400","status": "failed", "callback": callBack})
        return HttpResponse(dumps(result))

def createCategoriesDef(token,name,name_ar,filePath,fileName,parent,result):
    id = 1
    tokenIsExistOrNot = validateUserToken(token)
    result.update({"message":"Invalid Token"})
    if tokenIsExistOrNot:
        userId = tokenIsExistOrNot[0]["userId"]
        response = retrievCategoriesmodel({"userId":userId})
        filePath = refine(filePath)
        data = [{"id": id, "name": name, "name_ar": name_ar, "category_bannerPath": str(filePath),"category_banner": str(fileName), "parent": parent, "userId": userId}]
        if response:
            id = response[-1]["id"]
            id += 1
            data[0]["id"] = id
            response.extend(data)
            print(response)
            dropTheCategory({"userId":userId})
            insertCategories(response)
        else:
            insertCategories(data)
        responseOP=retrievCategoriesmodel({"userId":userId})
        result.update({"message":"categories inserted  succesfully","status":"success","response":responseOP})
    return result

def validateUserToken(token):
    conditionSet={"token":token}
    res = userLoginConditionSetModels(conditionSet)
    return res

class retieveCategories(View):
	def get(self,request):
		start_time = time.time() #getting current system time
		callback = "retieveCategories"
		result = {"message": "", "status": "failed", "code": "200", "statustext": "ok", "callback": callback,"start_time":start_time}
		try:
			requestHeaders = getHeaders(request)
			result.update({"message": "please pass TOKEN in headers and must be non empty value"})
			if str("TOKEN") in requestHeaders and (not str(requestHeaders["TOKEN"]).isspace()) and str(requestHeaders["TOKEN"]) != "" and str(requestHeaders["TOKEN"]) != "null":  # check  TOKEN is null or not
				result = retieveCategoriesDef(requestHeaders["TOKEN"],result)  # calling GetSingleUserDef and return the function result
		#
		except KeyError as e: #whether an KeyError occurs then pass the code
			result.update({"message": "parameter " + e.args[0].replace("'", "") + " is missing", "code": "400","statustext": "bad request"})
		result.update({"responsetime": str(round(decimal.Decimal('{}'.format(time.time() - start_time)), 3)) + " sec"}) #updating response time in result
		return HttpResponse(dumps(result)) #return response to browser

def retieveCategoriesDef(token,result):
    tokenIsExistOrNot = validateUserToken(token)
    result.update({"message": "Invalid Token"})
    if tokenIsExistOrNot:
        userId = tokenIsExistOrNot[0]["userId"]
        response = retrievCategoriesmodel({"userId": userId})
        result.update({"message": "categories retrieved  succesfully", "status": "success", "response": response})
    return result



# def getPutOrDeleteParameters(request, result):
#
# 	try:
# 		cat = dict(QueryDict(request.body))
# 	except Exception as e:
# 		if e.message == "Invalid Content-Type: text/plain":
# 			result.update({"message": "Please provide input values", "status": "failed", "code": "200", "statustext": "ok"})
# 			return result
# 		else:
# 			return exceptionHandler(e, result)
# 	parameters = dict(cat)
# 	result.update({"status": "success", "parameters": parameters})
# 	return result




class UpdateCategories(View):
    def post(self,request):
        callBack='UpdateCategories'
        startTime=time.time()
        result = {"message": "", "status": "failed", "code": "200", "statustext": "ok", "callback": callBack,"start_time":startTime}
        try:
            requestHeaders = getHeaders(request)
            parameters = dict(request.POST)
            result.update({"message": "please pass TOKEN in headers and must be non empty value"})
            if str("TOKEN") in requestHeaders and (not str(requestHeaders["TOKEN"]).isspace()) and str(requestHeaders["TOKEN"]) != "" and str(requestHeaders["TOKEN"]) != "null":
                result.update({"message": "please pass id and must be non empty value"})
                if "id" in parameters and parameters["id"][0] !="":
                    result.update({"message": "Please pass name"})
                    if 'name' in parameters :
                        result.update({"message": "Please pass name_ar"})
                        if 'name_ar' in parameters :
                            result.update({"message": "Please pass parent"})
                            if 'parent' in parameters :
                                result = updateCreatorsDef(requestHeaders["TOKEN"], parameters['name'][0], parameters['name_ar'][0], parameters['parent'][0],parameters["id"][0],result)
        except KeyError as e:  # whether an KeyError occurs#
            result.update({"message": "please pass " + e.message.replace("", "") + " parameter", "responsetime": str(round(decimal.Decimal('{}'.format(time.time() - startTime)), 3)) + " sec", "code": "400","status": "failed", "callback": callBack})
        return HttpResponse(dumps(result))

def updateCreatorsDef(token, name, name_ar, parent,id,result):
    tokenIsExistOrNot = validateUserToken(token)
    result.update({"message": "Invalid Token"})
    if tokenIsExistOrNot:
        userId = tokenIsExistOrNot[0]["userId"]
        print(userId)
        response = retrievCategoriesmodel({"userId": userId,"id":int(id)})
        result.update({"message": "No categories found"})
        if response:
            if name!="":
                myDict = {"name":name}
            if name_ar !="":
                myDict.update({"name_ar":name_ar})
            if parent !="":
                myDict.update({"parent":parent})
            updateCreatormodel({"userId":str(userId),"id":int(id)},myDict)
            result.update({"message": 'categories updated successfully', "status": "success"})
        return result

class DeleteCategories(View):
	def get(self,request):
		start_time = time.time() #getting current system time
		callback = "DeleteCategories"
		result = {"message": "", "status": "failed", "code": "200", "statustext": "ok", "callback": callback,"start_time":start_time}
		try:
			requestHeaders = getHeaders(request)
			result.update({"message": "please pass TOKEN in headers and must be non empty value"})
			if str("TOKEN") in requestHeaders and (not str(requestHeaders["TOKEN"]).isspace()) and str(requestHeaders["TOKEN"]) != "" and str(requestHeaders["TOKEN"]) != "null":  # check  TOKEN is null or not
				result.update({"message": "please pass id and must be non empty value"})
				if "id" in request.GET and request.GET["id"] != "":
					result = deleteCategoriesDef(requestHeaders["TOKEN"],request.GET["id"],result)  # calling GetSingleUserDef and return the function result
		except KeyError as e: #whether an KeyError occurs then pass the code
			result.update({"message": "parameter " + e.args[0].replace("'", "") + " is missing", "code": "400","statustext": "bad request"})
		result.update({"responsetime": str(round(decimal.Decimal('{}'.format(time.time() - start_time)), 3)) + " sec"}) #updating response time in result
		return HttpResponse(dumps(result)) #return response to browser

def deleteCategoriesDef(token,id,result):
    tokenIsExistOrNot = validateUserToken(token)
    result.update({"message": "Invalid Token"})
    if tokenIsExistOrNot:
        userId = tokenIsExistOrNot[0]["userId"]
        response = retrievCategoriesmodel({"userId": str(userId),"id":int(id)})
        result.update({"message":"No data is found to delete"})
        if response:
            dropTheCategory({"userId":str(userId),"id":int(id)})
            result.update({"message": "categories deleted  succesfully", "status": "success"})
    return result



























