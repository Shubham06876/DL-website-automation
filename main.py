import requests
from bs4 import BeautifulSoup
from PIL import Image
import re
import json

input_d_no = ['DL0420110149646']
input_dob = ['09-02-1976']

url = "https://parivahan.gov.in/rcdlstatus/?pur_cd=101"

header = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
    'X-Requested-With': 'XMLHttpRequest',
    'Faces-Request': 'partial/ajax'
}

captcha_data = {
    'form_rcdl': 'form_rcdl',
    'form_rcdl:tf_dlNO': None,
    'form_rcdl:tf_dob_input': None,
    'form_rcdl:j_idt31:CaptchaID': '',
    'javax.faces.ViewState': None,
    'javax.faces.source': 'form_rcdl:j_idt31:CaptchaID',
    'javax.faces.partial.event': 'blur',
    'javax.faces.partial.execute': 'form_rcdl:j_idt31:CaptchaID',
    'javax.faces.partial.render': 'form_rcdl:j_idt31:CaptchaID',
    'CLIENT_BEHAVIOR_RENDERING_MODE': 'OBSTRUSIVE',
    'javax.faces.behavior.event': 'blur',
    'javax.faces.partial.ajax': "true"

}

dl_inp = {
    'javax.faces.partial.ajax': "true",
    'javax.faces.source': 'form_rcdl:tf_dlNO',
    'javax.faces.partial.execute': 'form_rcdl:tf_dlNO',
    'javax.faces.partial.render': 'form_rcdl:tf_dlNO',
    'javax.faces.behavior.event': 'valueChange',
    'javax.faces.partial.event': 'change',
    'form_rcdl': 'form_rcdl',
    'form_rcdl:tf_dlNO': None,
    'form_rcdl:tf_dob_input': '',
    'form_rcdl:j_idt31:CaptchaID': '',
    'javax.faces.ViewState': None
}

dob = {
    'javax.faces.partial.ajax': "true",
    'javax.faces.source': 'form_rcdl:tf_dob',
    'javax.faces.partial.execute': 'form_rcdl:tf_dob',
    'javax.faces.partial.render': 'form_rcdl:tf_dob',
    'javax.faces.behavior.event': 'valueChange',
    'javax.faces.partial.event': 'change',
    'form_rcdl:tf_dob_input': None,
    'javax.faces.ViewState': None

}

form_input = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': "form_rcdl:j_idt42",
    'javax.faces.partial.execute': "@all",
    'javax.faces.partial.render': ['form_rcdl:pnl_show','form_rcdl:pg_show','form_rcdl:rcdl_pnl'],
    'form_rcdl:j_idt42': "form_rcdl:j_idt42",
    'form_rcdl': 'form_rcdl',
    'form_rcdl:j_idt31:CaptchaID': '',
    'form_rcdl:tf_dlNO': None,
    'form_rcdl:tf_dob_input': None,
    'javax.faces.ViewState': None
              }



def form_parsing(res):
    # print(res.text)
    pattern = re.compile('>[0-9A-Za-z: ,_\'-/\\.]+<')
    l = []
    temp_arr = []
    for lines in res.iter_lines():

        # print(lines)
        lines = lines.decode("utf-8")
        if ('Details Of Driving License' in lines):
            temp_arr = lines.split(":")
            temp_arr = [ele.strip() for ele in temp_arr]
            # print(temp_arr)
        m = pattern.findall(lines)
        if(m):
            for i in range(len(m)):
                w = m[i]
                w = w[1:-1:1].strip()
                m[i] = w
            # print(m)
            l.append(m)

    # print(l)
    output_dict = {
        'Details Of Driving License':temp_arr[1],
        'Current Status': l[1][0],
        'Holder\'s Name':l[3][0],
        'Date Of Issue':l[5][0],
        'Last Transaction At':l[7][0],
        'Old / New DL No.':l[9][0],
        'Non-Transport':{'From': l[11][1], 'To':l[12][1]},
        'Transport':{'From': l[14][1], 'To':l[15][1]},
        'Hazardous Valid Till':l[17][0],
        'Hill Valid Till':l[19][0],
        'COV Category':l[20][3],
        'Class Of Vehicle':l[20][4],
        'COV Issue Date':l[20][5]
    }

    return output_dict


def get_captcha(img = None):
    #dummy code
    captcha_val = input("Enter captcha value:   ")
    return captcha_val


def fetch_licence_details(url, header, captcha_data, dl_inp, dob, form_input):
    with requests.Session() as s:

        r = s.get(url)

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Whoops it wasn't a 200
            return "Error: " + str(e)
        soup = BeautifulSoup(r.content, "lxml")

        # print(soup.prettify())
        param = soup.find('input', attrs={"name": 'javax.faces.ViewState'})
        form_input['javax.faces.ViewState'] = param["value"]
        dl_inp['javax.faces.ViewState'] = param["value"]
        dob['javax.faces.ViewState'] = param["value"]
        captcha_data['javax.faces.ViewState'] = param["value"]

        var = soup.find("img", attrs={"id": "form_rcdl:j_idt31:j_idt37"})
        captcha_img_url = var["src"]

        base = "https://parivahan.gov.in/"

        img_data = s.get(base + captcha_img_url)

        f = open('yourcaptcha.png', 'wb')
        f.write(img_data.content)
        f.close()
        form_input['form_rcdl:j_idt31:CaptchaID'] = get_captcha(Image.open("yourcaptcha.png"))
        captcha_data['form_rcdl:j_idt31:CaptchaID'] = form_input['form_rcdl:j_idt31:CaptchaID']

        # partial updates
        cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(s.cookies))
        url = "https://parivahan.gov.in/rcdlstatus/vahan/rcDlHome.xhtml"
        r = s.post(url, data=dl_inp, cookies=cookies, headers=header)
        # print(r.text)
        r = s.post(url, data=dob, cookies=cookies, headers=header)
        # print(r.text)
        r = s.post(url, data=captcha_data, cookies=cookies, headers=header)
        # print(r.text)

        req = s.post(url, data=form_input, cookies=cookies, headers=header)

        #check for incorrect captcha and driving licence nbr
        if('Verification code does not match.' in req.text):
            print("Incorrect captcha!!! Try again")
            return 0
        elif('No DL Details Found' in req.text):
            print(dl_inp['form_rcdl:tf_dlNO'] ,": No DL Details found")
            return 1
        try:
            output = form_parsing(req)
        except:
            print("Error while fetching fields from xml")

        # print(output)
        json_output = json.dumps(output, indent=4)
        print(json_output)
        return 1


index = 0
tries_count = 0
while(index < len(input_d_no)):
    captcha_data['form_rcdl:tf_dlNO'] = input_d_no[index]
    captcha_data['form_rcdl:tf_dob_input'] = input_dob[index]
    dl_inp['form_rcdl:tf_dlNO'] = input_d_no[index]
    dob['form_rcdl:tf_dob_input'] = input_dob[index]
    form_input['form_rcdl:tf_dlNO'] = input_d_no[index]
    form_input['form_rcdl:tf_dob_input'] = input_dob[index]

    try:
        if(fetch_licence_details(url, header, captcha_data, dl_inp, dob, form_input) == 1):
            index += 1
            tries_count = 0
        else:
            tries_count += 1
            if(tries_count > 5):
                print("Too many incorrect tries")
                break
    except:
        print("Error")






