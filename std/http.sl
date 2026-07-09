# HTTP client module
@python module "requests" as requests

fn get(url: str):
    requests.get(url).json()

fn post(url: str, data: dict):
    requests.post(url, json=data).json()

fn put(url: str, data: dict):
    requests.put(url, json=data).json()

fn delete(url: str):
    requests.delete(url).json()

fn set_headers(headers: dict):
    global _default_headers
    global _default_timeout
    _default_headers = headers
    _default_timeout = 30.0

fn upload_file(url: str, path: str):
    requests.post(url, files={'file': open(path, 'rb')}).json()

fn download_file(url: str, path: str):
    response = requests.get(url)
    with open(path, 'wb') as f:
        f.write(response.content)

fn listen(port: int, handler: fn):
    @python module "flask" as flask
    app = flask.Flask(__name__)
    
    @app.route('/', methods=['GET', 'POST'])
    def route_handler():
        return str(handler(request=flask.request))
    
    app.run(port=port)