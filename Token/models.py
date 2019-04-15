from .views import *
from .settings import *
def register(data):
	generatedId = db.registerUser.insert_one(data).inserted_id
	return generatedId

def userLoginConditionSetModels(conditionSet):
	print(conditionSet)
	response= json.loads(dumps(db.registerUser.find(conditionSet,{"_id":0})))
	return response

def insertCategories(data):
	# if data[0]["parent"] != "":
	print("iffffffffffffff",data)
	db.Categories.insert(data)
	# else:
	# 	data[0]["parent"] = "null"
	# 	print("else", data)
	# 	db.Categories.insert(data)

def retrievCategoriesmodel(conditionSet):
	response = json.loads(dumps(db.Categories.find(conditionSet,{"_id":0})))
	return response
def dropTheCategory(conditionSet):
	db.Categories.remove(conditionSet)

def updateCreatormodel(conditionSet,myDict):
	if myDict !="":
		print("mydictrrrrrr",myDict)
		db.Categories.update(conditionSet,{'$set': myDict})

