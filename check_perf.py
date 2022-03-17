from datetime import datetime
import requests
import json
import sys, getopt

_usage_str = """
Options:
    -n <n> -url <url>
"""

def fetch_info_from_url(url):
    data = requests.get(url)
    json_data = json.loads(data.content)
    return json_data

g_zero_time = datetime.strptime("0:00:00",'%H:%M:%S')
def convert_string_to_datetime(str):
    return datetime.strptime(str,'%H:%M:%S.%f') - g_zero_time

def usage():
    print(_usage_str)

if __name__ == "__main__":
    n = 1
    url = "http://localhost:5000/list?markets=w_cac"

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hn:u:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-n", "--n"):
            n = int(arg)
        elif opt in ("-u", "--url"):
            url = arg
    print("n : {}".format(n))
    print("url : {}".format(url))
    
    if url == "":
        usage()
        sys.exit()

    server_times = g_zero_time
    total_times = g_zero_time
    for i in range(n):
        start = datetime.now()

        json_data = fetch_info_from_url(url)

        end = datetime.now()
        elapsed_time = str(end - start)

        server_elapsed_time = convert_string_to_datetime(json_data["elapsed_time"])
        server_times += server_elapsed_time

        total_time = convert_string_to_datetime(elapsed_time)
        total_times += total_time

    print("server times mean : {}".format((server_times - g_zero_time) / 3))
    print("total times mean : {}".format((total_times - g_zero_time) / 3))
