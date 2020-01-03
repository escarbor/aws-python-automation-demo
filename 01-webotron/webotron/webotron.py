import boto3
import click
import mimetypes
from pathlib import Path
from botocore.exceptions import ClientError

session = boto3.Session(profile_name='default')
s3 = session.resource('s3')


@click.group()
def cli():
    "Webtron deploys websites to AWS"
    pass


@cli.command('list-buckets')
def list_buckets():
    "List all s3 buckets"
    for bucket in s3.buckets.all():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    "List object in an s3 bucket"
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    "Create and configure S3 bucket"
    s3_bucket = None
    try:
        if session.region_name == 'us-east-1':
            s3_bucket = s3.create_bucket(Bucket=bucket)
        else:
            s3_bucket = s3.create_bucket(
                Bucket=bucket,
                CreateBucketConfiguration={'LocationConstraint': session.region_name})
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print("You already own this bucket.")
            s3_bucket = s3.Bucket(bucket)
            
        else:
            raise e

    policy = """
    {
        "Version":"2012-10-17",
        "Statement":[{
            "Sid":"PublicReadGetObject",
            "Effect":"Allow",
            "Principal": "*",
            "Action":["s3:GetObject"],
            "Resource":["arn:aws:s3:::%s/*"]
        }]
    }
    """ % s3_bucket.name
    policy = policy.strip()
    pol = s3_bucket.Policy()
    pol.put(Policy=policy)
    ws = s3_bucket.Website()
    ws.put(WebsiteConfiguration={
        'ErrorDocument': {'Key': 'error.html'},
        'IndexDocument': {'Suffix': 'index.html'},
    })

    return

def upload_file(s3_bucket, path, key):
    content_type = mimetypes.guess_type(key)[0] or 'text/plain'
    s3_bucket.upload_file(
        path,
        key,
        ExtraArgs={
            'ContentType': content_type
        })

@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket ):
    "Sync contents of PATHNAME to BUCKET"
    s3_bucket = s3.Bucket(bucket)
    
    root = Path(pathname).expanduser().resolve()

    def handle_directory(target): 
        for p in target.iterdir(): 
            if p.is_dir(): handle_directory(p) 
            if p.is_file(): upload_file(s3_bucket, str(p), str(p.relative_to(root)))

    handle_directory(root)



if __name__ == '__main__':
    cli()

# In [2]: from pathlib import Path                                                                                 

# In [3]: pathname = "kitten_web"                                                                                  

# In [4]: path = Path(pathname)                                                                                    

# In [5]: path                                                                                                     
# Out[5]: PosixPath('kitten_web')

# In [6]: path.resolve()                                                                                           
# Out[6]: PosixPath('/Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/kitten_web')

# In [7]: list(path.iterdir())                                                                                     
# Out[7]: 
# [PosixPath('kitten_web/index.html'),
#  PosixPath('kitten_web/css'),
#  PosixPath('kitten_web/images')]

# In [8]: path.is_dir()                                                                                            
# Out[8]: True

# In [9]: path.is_file()                                                                                           
# Out[9]: False

# In [10]: def handle_directory(target): 
#     ...:     for p in target.iterdir()                                                                           
#   File "<ipython-input-10-1e8433d32c64>", line 2
#     for p in target.iterdir()
#                              ^
# SyntaxError: invalid syntax


# In [11]: def handle_directory(target): 
#     ...:     for p in target.iterdir(): 
#     ...:         if p.is_dir(): handle_directory(p) 
#     ...:         if p.is_file(): print(p) 
#     ...:                                                                                                         

# In [12]: def handle_directory(target): 
#     ...:     for p in target.iterdir(): 
#     ...:         if p.is_dir(): handle_directory(p) 
#     ...:         if p.is_file(): print(p.as_posix()) 
#     ...:          
#     ...:                                                                                                         

# In [13]: handle_directory(path)                                                                                  
# kitten_web/index.html
# kitten_web/css/main.css
# kitten_web/images/Balinese-kitten1.jpg
# kitten_web/images/Maine_coon_kitten_roarie.jpg
# kitten_web/images/SFSPCA_Kitten.jpg

# In [14]: path = Path(pathname)                                                                                   

# In [15]: path.expanduser()                                                                                       
# Out[15]: PosixPath('kitten_web')

# In [16]: pwd                                                                                                     
# Out[16]: '/Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron'

# In [17]: ~                                                                                                       
#   File "<ipython-input-17-f73ee080cfb5>", line 1
#     ~
#      ^
# SyntaxError: invalid syntax


# In [18]: pathname = "~/Desktop/Workspace/Personal/Acloud/python-authomation/01-webotron"                         

# In [19]: path = Path(pathname)                                                                                   

# In [20]: path.expanduser()                                                                                       
# Out[20]: PosixPath('/Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-authomation/01-webotron')

# In [21]: path                                                                                                    
# Out[21]: PosixPath('~/Desktop/Workspace/Personal/Acloud/python-authomation/01-webotron')

# In [22]: root = pathname                                                                                         

# In [23]: path.relative_to(root)                                                                                  
# Out[23]: PosixPath('.')

# In [24]: def handle_directory(target): 
#     ...:     for p in target.iterdir(): 
#     ...:         if p.is_dir(): handle_directory(p) 
#     ...:         if p.is_file(): print("Path: {}\n Key:{}".format(p, p.relative_to(root)) 
#     ...:                                                                                                         
#   File "<ipython-input-24-ce0caedd8ae0>", line 5
    
#     ^
# SyntaxError: unexpected EOF while parsing


# In [25]: def handle_directory(target): 
#     ...:     for p in target.iterdir(): 
#     ...:         if p.is_dir(): handle_directory(p) 
#     ...:         if p.is_file(): print("Path: {}\n Key:{}".format(p, p.relative_to(root))) 
#     ...:                                                                                                         

# In [26]: root                                                                                                    
# Out[26]: '~/Desktop/Workspace/Personal/Acloud/python-authomation/01-webotron'

# In [27]: handle_directory(root)                                                                                  
# ---------------------------------------------------------------------------
# AttributeError                            Traceback (most recent call last)
# <ipython-input-27-399ea2cb21fb> in <module>
# ----> 1 handle_directory(root)

# <ipython-input-25-31d8887e4872> in handle_directory(target)
#       1 def handle_directory(target):
# ----> 2     for p in target.iterdir():
#       3         if p.is_dir(): handle_directory(p)
#       4         if p.is_file(): print("Path: {}\n Key:{}".format(p, p.relative_to(root)))
#       5 

# AttributeError: 'str' object has no attribute 'iterdir'

# In [28]: handle_directory(Path(root))                                                                            
# ---------------------------------------------------------------------------
# FileNotFoundError                         Traceback (most recent call last)
# <ipython-input-28-b73c02df6562> in <module>
# ----> 1 handle_directory(Path(root))

# <ipython-input-25-31d8887e4872> in handle_directory(target)
#       1 def handle_directory(target):
# ----> 2     for p in target.iterdir():
#       3         if p.is_dir(): handle_directory(p)
#       4         if p.is_file(): print("Path: {}\n Key:{}".format(p, p.relative_to(root)))
#       5 

# /usr/local/Cellar/python/3.7.6_1/Frameworks/Python.framework/Versions/3.7/lib/python3.7/pathlib.py in iterdir(self)
#    1100         if self._closed:
#    1101             self._raise_closed()
# -> 1102         for name in self._accessor.listdir(self):
#    1103             if name in {'.', '..'}:
#    1104                 # Yielding a path object for these makes little sense

# FileNotFoundError: [Errno 2] No such file or directory: '~/Desktop/Workspace/Personal/Acloud/python-authomation/01-webotron'

# In [29]: pwd                                                                                                     
# Out[29]: '/Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron'

# In [30]: root = pwd                                                                                              
# ---------------------------------------------------------------------------
# NameError                                 Traceback (most recent call last)
# <ipython-input-30-2b5ba34e5c84> in <module>
# ----> 1 root = pwd

# NameError: name 'pwd' is not defined

# In [31]: root = '/Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron'        

# In [32]: handle_directory(Path(root))                                                                            
# Path: /Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/index.html
#  Key:index.html
# Path: /Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/webotron/webotron.py
#  Key:webotron/webotron.py
# Path: /Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/Pipfile
#  Key:Pipfile
# Path: /Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/ipythonsession.py
#  Key:ipythonsession.py
# Path: /Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/kitten_web/index.html
#  Key:kitten_web/index.html
# Path: /Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/kitten_web/css/main.css
#  Key:kitten_web/css/main.css
# Path: /Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/kitten_web/images/Balinese-kitten1.jpg
#  Key:kitten_web/images/Balinese-kitten1.jpg
# Path: /Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/kitten_web/images/Maine_coon_kitten_roarie.jpg
#  Key:kitten_web/images/Maine_coon_kitten_roarie.jpg
# Path: /Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/kitten_web/images/SFSPCA_Kitten.jpg
#  Key:kitten_web/images/SFSPCA_Kitten.jpg
# Path: /Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/Pipfile.lock
#  Key:Pipfile.lock

# In [33]: pwd                                                                                                     
# Out[33]: '/Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron'

# In [34]: root = '/Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/kitten_w
#     ...: eb'                                                                                                     

# In [35]: handle_directory(Path(root))                                                                            
# Path: /Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/kitten_web/index.html
#  Key:index.html
# Path: /Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/kitten_web/css/main.css
#  Key:css/main.css
# Path: /Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/kitten_web/images/Balinese-kitten1.jpg
#  Key:images/Balinese-kitten1.jpg
# Path: /Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/kitten_web/images/Maine_coon_kitten_roarie.jpg
#  Key:images/Maine_coon_kitten_roarie.jpg
# Path: /Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/kitten_web/images/SFSPCA_Kitten.jpg
#  Key:images/SFSPCA_Kitten.jpg

# In [36]: %history                                                                                                
# form pathlib import Path
# from pathlib import Path
# pathname = "kitten_web"
# path = Path(pathname)
# path
# path.resolve()
# list(path.iterdir())
# path.is_dir()
# path.is_file()
# def handle_directory(target):
#     for p in target.iterdir()
# def handle_directory(target):
#     for p in target.iterdir():
#         if p.is_dir(): handle_directory(p)
#         if p.is_file(): print(p)
# def handle_directory(target):
#     for p in target.iterdir():
#         if p.is_dir(): handle_directory(p)
#         if p.is_file(): print(p.as_posix())
# handle_directory(path)
# path = Path(pathname)
# path.expanduser()
# pwd
# ~
# pathname = "~/Desktop/Workspace/Personal/Acloud/python-authomation/01-webotron"
# path = Path(pathname)
# path.expanduser()
# path
# root = pathname
# path.relative_to(root)
# def handle_directory(target):
#     for p in target.iterdir():
#         if p.is_dir(): handle_directory(p)
#         if p.is_file(): print("Path: {}\n Key:{}".format(p, p.relative_to(root))
# def handle_directory(target):
#     for p in target.iterdir():
#         if p.is_dir(): handle_directory(p)
#         if p.is_file(): print("Path: {}\n Key:{}".format(p, p.relative_to(root)))
# root
# handle_directory(root)
# handle_directory(Path(root))
# pwd
# root = pwd
# root = '/Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron'
# handle_directory(Path(root))
# pwd
# root = '/Users/eliasscarborough/Desktop/Workspace/Personal/Acloud/python-automation/01-webotron/kitten_web'
# handle_directory(Path(root))