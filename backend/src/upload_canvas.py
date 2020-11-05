import requests

def upload_to_canvas():
    urlaccess_token = input("Please enter url access token of your canvas account:")
    api_url = input("Please enter api url")

    #Manish's account:
    #urlaccess_token = "7~PZBVbNXainK4lzAwSPVpXsiGEoxo1HW8v1I050sM78k0wHD0rF320vfdESjKJGEt"
    #api_url_to_upload_qti_quiz https://canvas.instructure.com/api/v1/courses/2328731/content_migrations

    #donot use this: this is for general file upload
    #api_url_to_upload_course_file ="https://canvas.instructure.com/api/v1/courses/2328731/files"

    #Jorgen's account:
    #urlaccess_token = "7~P5SzQi2QKP7tvoOAc0jgsF0IGYY5mrTac3kQMenNwK6cEsX4UkjBAJK7NDABPbuV"
    #api_url ="https://canvas.instructure.com/api/v1/courses/2325486/content_migrations"


# Set up a session
    session = requests.Session()
    session.headers = {'Authorization': 'Bearer %s' % urlaccess_token}

# Step 1 - tell Canvas you want to upload a file
    file_path = input("Please enter qti zip file path:")
    payload = {}
    payload['migration_type'] = 'qti_converter'
    payload['pre_attachment[name]'] = file_path
    payload['parent_folder_path'] = '/'
    r = session.post(api_url, data=payload)
    print(r.text)
    r.raise_for_status()
    r = r.json()
    print( ' ')
    print(r)     # This successfully returns the expected response...

# Step 2 - upload file

    with open(file_path, 'rb') as f:
        r1 = requests.post(
        r['pre_attachment']['upload_url'],
        data=r['pre_attachment']['upload_params'],
        files={'file': ('files',f) },
        )
        r1.raise_for_status()
        r1 = r1.json()
        print(r1)

if __name__ == '__main__':
    upload_to_canvas()






