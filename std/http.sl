@python module "requests" as req
@python module "json" as json

fn http_get(url):
    response = req.get(url)
    try:
        return json.loads(response.text)
    except:
        return response.text

fn http_post(url, data):
    response = req.post(url, json=data)
    try:
        return json.loads(response.text)
    except:
        return response.text

fn http_put(url, data):
    response = req.put(url, json=data)
    try:
        return json.loads(response.text)
    except:
        return response.text

fn http_delete(url):
    response = req.delete(url)
    try:
        return json.loads(response.text)
    except:
        return response.text

fn get_status(response):
    return response.status_code

fn get_text(response):
    return response.text