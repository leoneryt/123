from requests.sessions import Session


def base_request(url, method=None, params=None, data=None, headers=None, cookies=None,
                 files=None, auth=None, timeout=None, allow_redirects=True, proxies=None,
                 hooks=None, stream=None, verify=None, cert=None, json=None):
    method = "get" if method is None else method
    resp = Session().request(url=url, method=method, params=params, data=data, headers=headers, cookies=cookies,
                             files=files, auth=auth, timeout=timeout, allow_redirects=allow_redirects, proxies=proxies,
                             hooks=hooks, stream=stream, verify=verify, cert=cert, json=json)
    return resp


def contrast(json_data: dict):
    params_list = []
    type_list = []
    for key in json_data.keys():
        params_list.append(key)
        # print(type(json_data[key]))
        if (type(json_data[key]) == list) or (type(json_data[key]) == dict):
            type_list.append(json_data[key])
    # print(type_list)
    for value in type_list:
        if type(value) == dict:
            params_list += contrast(value)
        else:
            for inner in value:
                if type(inner) == dict:
                    params_list += contrast(inner)
    return params_list


def seng_req(json_data: dict):
    url = json_data["url"].format(**json_data["url_path"]) if ("url_path" in json_data.keys()) else json_data["url"]
    method = json_data["method"] if ("method" in json_data.keys()) else "get"
    params = json_data["params"] if ("params" in json_data.keys()) else None
    data = json_data["data"] if ("data" in json_data.keys()) else None
    headers = json_data["headers"] if ("headers" in json_data.keys()) else None
    cookies = json_data["cookies"] if ("cookies" in json_data.keys()) else None
    files = json_data["files"] if ("files" in json_data.keys()) else None
    auth = json_data["auth"] if ("auth" in json_data.keys()) else None
    timeout = json_data["timeout"] if ("timeout" in json_data.keys()) else None
    stream = json_data["stream"] if ("stream" in json_data.keys()) else None
    verify = json_data["verify"] if ("verify" in json_data.keys()) else None
    cert = json_data["cert"] if ("cert" in json_data.keys()) else None
    json_body = json_data["json"] if ("json" in json_data.keys()) else None
    proxies = json_data["proxies"] if ("proxies" in json_data.keys()) else None
    hooks = json_data["hooks"] if ("hooks" in json_data.keys()) else None
    # print(url, method, json_body)
    return base_request(url=url, method=method, params=params, data=data, headers=headers, cookies=cookies,
                        files=files, auth=auth, timeout=timeout, proxies=proxies, hooks=hooks, stream=stream,
                        verify=verify, cert=cert, json=json_body)

