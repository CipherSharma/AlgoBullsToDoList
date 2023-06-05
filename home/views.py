from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, timedelta
from AlgoBullsToDoList import settings
from rest_framework import status
from .models import CustomUserModel,Task,TaskSerializer,Tag
import bcrypt
import jwt


# Get a List of available Tags
@api_view(["GET"])
def get_tags(request):
    try:
        # Validating the Auth Token
        auth_header_value = request.META.get('HTTP_AUTHORIZATION',None)
        email = validate_user_auth_token(auth_header_value)
        if email==False:
            return Response({"Response":"The auth token is either expired or incorrect"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        taglist=''
        tags= Tag.objects.all()
        for tag in tags:
            taglist += tag.name+", "
        return Response({"List of available Tags: "+ taglist}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"Response":"error is "+str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)

# Creating a New Task  
@api_view(["POST"])
def create_task(request):
    try:
        # Validating the Auth Token
        auth_header_value = request.META.get('HTTP_AUTHORIZATION',None)
        email = validate_user_auth_token(auth_header_value)
        if email==False:
            return Response({"Response":"The auth token is either expired or incorrect"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        data=request.data
        
        # checking Due Date input  
        due_date=datetime.strptime(data["due_date"], "%d-%m-%Y")
        if due_date<=datetime.now():
            return Response({"Response":"Due Date should be Greated than Current time"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        # cheching if the task with the same title already exists  
        if Task.objects.filter(author=CustomUserModel.objects.get(email=email),title=data["title"]).first():
            return Response({"Response":"A Task with the same name for the same user Already Exists"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        # creating and saving a Task Object   
        task=Task()
        task.author = CustomUserModel.objects.get(email=email)
        task.title = data["title"]
        task.description = data["description"]
        task.due_date =due_date
        task.status=data["status"]
        task.save()
        # saving Many to Many Tag Feild
        for i in data["tags"]:
            tag=Tag.objects.get(name=i)
            task.tags.add(tag)
        task.save()
        
        return Response({"Response": "Task Created Successfully"}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"Response":"error is "+str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)

# Update an existing Task properties
@api_view(["POST"])
def update_task(request,title):
    try:
        # Validating the Auth Token
        auth_header_value = request.META.get('HTTP_AUTHORIZATION',None)
        email = validate_user_auth_token(auth_header_value)
        if email==False:
            return Response({"Response":"The auth token is either expired or incorrect"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        data=request.data
        author=CustomUserModel.objects.get(email=email)
        
        # checking if the logged in user is indeed the author of the task
        try:
            task=Task.objects.get(author=author,title=title)
        except Exception as e :
            return Response({"Response":"No such Task Exists"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        # checking Due Date input  
        due_date=datetime.strptime(data["new_due_date"], "%d-%m-%Y")
        if due_date<=datetime.now():
            return Response({"Response":"Due Date should be Greated than Current time"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        # cheching if the task with the same title already exists 
        if Task.objects.filter(author=CustomUserModel.objects.get(email=email),title=data["new_title"]).first():
            return Response({"Response":"A Task with the same name for the same user Already Exists"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        # updating the tag object attributes
        task.title = data["new_title"]
        task.description = data["description"]
        task.due_date =due_date
        task.status=data["status"]
        
        # updating the Many to Many Tag Feild
        for i in data["tags"]["add"]:
            tag=Tag.objects.get(name=i)
            task.tags.add(tag)
        for i in data["tags"]["remove"]:
            tag=Tag.objects.get(name=i)
            task.tags.remove(tag)
        task.save()
        
        return Response({"Response": "Task Updated Successfully"}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"Response":"error is "+str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)
 
# Deleting a Task from the datrabase 
@api_view(["GET"])
def delete_task(request,title):
    try:
        # Validating the Auth Token
        auth_header_value = request.META.get('HTTP_AUTHORIZATION',None)
        email = validate_user_auth_token(auth_header_value)
        if email==False:
            return Response({"Response":"The auth token is either expired or incorrect"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        author=CustomUserModel.objects.get(email=email)
        
        # checking if the logged in user is indeed the author of the task
        try:
            task=Task.objects.get(author=author,title=title)
        except Exception as e :
            return Response({"Response":"No such Task Exists"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        # deleting the task object 
        task.delete()
        
        return Response({"Response": "Task Deleted Successfully"}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"Response":"error is "+str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)
    
 
# Get all the Tasks Authored By the Logged in User   
@api_view(["GET"])
def get_tasks(request):
    try:
        # Validating the Auth Token
        auth_header_value = request.META.get('HTTP_AUTHORIZATION',None)
        email = validate_user_auth_token(auth_header_value)
        if email==False:
            return Response({"Response":"The auth token is either expired or incorrect"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        tasklist=[]
        tasks= Task.objects.filter(author=CustomUserModel.objects.get(email=email))
        for task in tasks:
            tasklist.append(task.title)
        return Response({"List of Tasks": tasklist}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"Response":"error is "+str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)

#Get The Details of a Specific Task 
@api_view(["POST"])
def get_task(request):
    try:
        # Validating the Auth Token
        auth_header_value = request.META.get('HTTP_AUTHORIZATION',None)
        email = validate_user_auth_token(auth_header_value)
        if email==False:
            return Response({"Response":"The auth token is either expired or incorrect"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        # Getting the Specified Task Object 
        data=request.data
        author=CustomUserModel.objects.get(email=email)
        
        # checking if the logged in user is indeed the author of the task
        try:
            task=Task.objects.get(author=author,title=data["title"])
        except Exception as e :
            return Response({"Response":"No such Task Exists"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        # Making the task JSON serializable
        task=TaskSerializer(task)
        task_data=task.data
        return Response({"Task Details": task_data}, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"Response":"error is "+str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)
      
# User Signup API Creates a New User in the database
@api_view(["POST"])
def signup_api(request):
    try:
        data=request.data
        #converting the Provided password into hash for user Privacy
        password=bcrypt.hashpw(data["password"].encode("utf-8"),bcrypt.gensalt(10))
        
        #checkingt if the email provided is already registered 
        if CustomUserModel.objects.filter(email=data["email"]).first():
            return Response({"Response":"User with email already exists"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        #Creating the new user Entry in the Database 
        CustomUserModel.objects.create(
            email = data["email"],
            password = password,
        )
        return Response({"Response":"User Created Successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"Response":"error is "+str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)

#User login API Creates an Authentication token for User verification in future
@api_view(['POST'])
def login_api(request):
    try:
        data=request.data
        password=data["password"]
        if 'email' not in data or 'password' not in data:
            print("Please provide both email and password for logging in.")
            return Response({"status":"failed","message": "Please provide both email and password for logging in." },status=status.HTTP_400_BAD_REQUEST)
        
        #Checking if the user with the provided email exists or not 
        if CustomUserModel.objects.filter(email=data["email"]).first():
            user = CustomUserModel.objects.get(email=data["email"])
        else:
            error_stmt = "User : " + data['email'] +  ' not a valid user email'
            return Response({"status":"failed","message":error_stmt},status=status.HTTP_401_UNAUTHORIZED)
        
        # Cross Checcking the password in the Database and the input
        if user :
            if bcrypt.checkpw(password.encode("utf-8"), user.password[2:-1].encode("utf-8")):
                token=generate_auth_token(data["email"])
            else:
                return Response({"Response":"incorrect Password."}, status=status.HTTP_200_OK)
       
        return Response({"Response": "User Authenticated Succesfully","Authtoken":token}, status=status.HTTP_200_OK)

    except Exception as e:
        error_txt = "An error occured while logging in : " + str(e.__class__) + " " + str(e)
        return Response({"status":"failed","message": error_txt },status=status.HTTP_400_BAD_REQUEST)

# Generating a jwt token
def generate_auth_token(email):
    try:
        iat = datetime.utcnow()
        exp = iat + timedelta(days=30)
        nbf = iat
       
        payload = {
            'exp': exp,
            'iat': iat,
        }
       
        payload['email'] = email
          
        jwt_stmt = 'JWT Auth Token Generated for User with email : '+email
        print(jwt_stmt) 
        
        # Encoding the payload and generating a jwt token
        JWTtoken = jwt.encode(
            payload,
            str(settings.SECRET_KEY),
            algorithm='HS256'
        )
        return JWTtoken
    except Exception as e:
           print(e)     
           return None

# Decoding the jwt token to get the user email
def validate_user_auth_token(auth_header_value):
    
    auth_header_value = str(auth_header_value).split(" ")
    if auth_header_value == ['None']:
        return False
             
    token = jwt.decode(auth_header_value[1], str(settings.SECRET_KEY), algorithms='HS256')
    email = token['email']
    if not token:
        return False

    if CustomUserModel.objects.get(email=email) is None:
        return False

    return email