def get_curl_command(method, url, content_type=None, accept=None, post_data=None, local_file=None, form=None):
    request_opt = "-X"
    if method == "GET" and post_data is not None:
        request_opt = "-G"

    curl_cmd = f"curl {request_opt} {method}"
    
    if content_type is not None:
        curl_cmd += f" -H \"Content-Type:{content_type}\""
    if accept is not None:
        curl_cmd += f" -H \"Accept:{accept}\""
    if post_data is not None:
        curl_cmd += f" -d \"{post_data}\""
    if local_file is not None:
        curl_cmd += f" -T \"{local_file}\""
    if form is not None:
        curl_cmd += f" -F \"{form}\""
    curl_cmd += f" {url}"

    return curl_cmd