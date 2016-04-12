import httplib
import json
import requests

# conn = httplib.HTTPSConnection("http://0.0.0.0:5100")
base = "ref/v0.1"
headers = {"Accept": "application/json"}
host = "0.0.0.0"
port = 5100


def set_upload(file_name=""):
    url = "http://{0}:{1}/{2}/set/upload".format(host,port,base)
    files = {'file': open('%s'%file_name)}
    response = requests.post(url, files=files)
    return response.content

def set_change(file_name="", set_id=""):
    url = "http://{0}:{1}/{2}/set/change/{3}".format(host,port,base, set_id)
    files = {'file': open('%s'%file_name)}
    response = requests.post(url, files=files)
    return response.content

def set_evaluate_data(file_name="", ref_id=""):
    url = "http://{0}:{1}/{2}/reference/evaluate/data/{3}".format(host,port,base, ref_id)
    files = {'file': open('%s'%file_name)}
    response = requests.post(url, files=files)
    return response.content

def set_evaluate_plot(file_name="", ref_id="", aliq="aliq1"):
    url = "http://{0}:{1}/{2}/reference/evaluate/plot/{3}/{4}".format(host,port,base, ref_id, aliq)
    files = {'file': open('%s'%file_name)}
    response = requests.post(url, files=files)
    with open('evaluation-{0}.png'.format(aliq), 'wb') as eval_file:
        eval_file.write(response.content)
    # return response.content
    
if __name__ == '__main__':

    # print set_upload("../data-sets/Lab_3.xlsx")
    # print set_upload("../data-sets/Lab_1.xlsx")
    # print set_upload("../data-sets/Lab_4.xlsx")
    print set_upload("../data-sets/Lab_6.xlsx")
    # print set_upload("../data-sets/Lab_5.xlsx")
    # print set_upload("../data-sets/Lab_9.xlsx")

    # print set_upload("../data-sets/Lab_8.xlsx")
    # print set_upload("../data-sets/Lab_2.xlsx")
    # print set_upload("../data-sets/Lab_7.xlsx")

    # print set_change("../data-sets/Lab_6.xlsx", "57099b6ecdca240d9ef65f72")

    # print set_evaluate_data("../data-sets/Lab_6.xlsx", "5709b948cdca24118d4d94cc")
    # set_evaluate_plot("../data-sets/Lab_6.xlsx", "5709b948cdca24118d4d94cc", "aliq1")
    # set_evaluate_plot("../data-sets/Lab_6.xlsx", "5709b948cdca24118d4d94cc", "aliq2")