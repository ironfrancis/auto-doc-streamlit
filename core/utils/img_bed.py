import requests

url = 'https://img.scdn.io/api/v1.php'
file_path = '/Users/xuchao/Projects/Auto-doc-streamlit/core/utils/test.png'

with open(file_path, 'rb') as f:
    files = {'image': f}
    response = requests.post(url, files=files)

print(response.json())