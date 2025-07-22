import requests
import re
print('lấy mã r thì chờ tầm 80s r nhập')
type = input('enter quest type: ')

if type == 'm88':
    response = requests.post(f'https://traffic-user.net/GET_MA.php?codexn=taodeptrai&url=https://bet88ec.com/cach-danh-bai-sam-loc&loai_traffic=https://bet88ec.com/&clk=1000')
    html = response.text
    match = re.search(r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>', html)
    if match:
        code = match.group(1)
        print(f"code: {code}")
    else:
        print("ko tìm thấy mã")

elif type == 'fb88':
    response = requests.post(f'https://traffic-user.net/GET_MA.php?codexn=taodeptrai&url=https://fb88dq.com/cach-choi-ca-cuoc-golf&loai_traffic=https://fb88dq.com/&clk=1000')
    html = response.text
    match = re.search(r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>', html)
    if match:
        code = match.group(1)
        print(f"code: {code}")
    else:
        print("ko tìm thấy mã")

elif type == '188bet':
    response = requests.post(f'https://traffic-user.net/GET_MA.php?codexn=taodeptrailamnhe&url=https://88betag.com/cach-choi-game-bai-pok-deng&loai_traffic=https://88betag.com/&clk=1000')
    html = response.text
    match = re.search(r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>', html)
    if match:
        code = match.group(1)
        print(f"code: {code}")
    else:
        print("ko tìm thấy mã")

elif type == 'w88':
    response = requests.post(f'https://traffic-user.net/GET_MA.php?codexn=taodeptrai&url=https://188.166.185.213/tim-hieu-khai-niem-3-bet-trong-poker-la-gi&loai_traffic=https://188.166.185.213/&clk=1000')
    html = response.text
    match = re.search(r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>', html)
    if match:
        code = match.group(1)
        print(f"code: {code}")
    else:
        print("ko tìm thấy mã")

elif type == 'v9bet':
    response = requests.post(f'https://traffic-user.net/GET_MA.php?codexn=taodeptrai&url=https://v9betho.com/ca-cuoc-bong-ro-ao&loai_traffic=https://v9betho.com/&clk=1000')
    html = response.text
    match = re.search(r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>', html)
    if match:
        code = match.group(1)
        print(f"code: {code}")
    else:
        print("ko tìm thấy mã")

elif type == 'vn88':
    response = requests.post(f'https://traffic-user.net/GET_MA.php?codexn=bomaydeptrai&url=https://vn88sv.com/cach-choi-bai-gao-gae&loai_traffic=https://vn88sv.com/&clk=1000')
    html = response.text
    match = re.search(r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>', html)
    if match:
        code = match.group(1)
        print(f"code: {code}")
    else:
        print("ko tìm thấy mã")


elif type == 'bk8':
    response = requests.post(f'https://traffic-user.net/GET_MA.php?codexn=taodeptrai&url=https://bk8ze.com/cach-choi-bai-catte&loai_traffic=https://bk8ze.com/&clk=1000')
    html = response.text
    match = re.search(r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>', html)
    if match:
        code = match.group(1)
        print(f"code: {code}")
    else:
        print("ko tìm thấy mã")
elif type == '88betag':
    response = requests.post(f'https://traffic-user.net/GET_MD.php?codexnd=bomaylavua&url=https://88betag.com/keo-chau-a-la-gi&loai_traffic=https://88betag.com/&clk=1000')
    html = response.text
    match = re.search(r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>', html)
    if match:
        code = match.group(1)
        print(f"code: {code}")
    else:
        print("ko tìm thấy mã")

elif type == 'w88abc' or type == '188.166.185.213':
    response = requests.post(f'https://traffic-user.net/GET_MD.php?codexnd=bomaylavua&url=https://w88abc.com/cach-choi-ca-cuoc-lien-quan-mobile&loai_traffic=https://w88abc.com/&clk=1000')
    html = response.text
    match = re.search(r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>', html)
    if match:
        code = match.group(1)
        print(f"code: {code}")
    else:
        print("ko tìm thấy mã")

elif type == 'v9betlg':
    response = requests.post(f'https://traffic-user.net/GET_MD.php?codexnd=bomaylavua&url=https://v9betlg.com/phuong-phap-cuoc-flat-betting&loai_traffic=https://v9betlg.com/&clk=1000')
    html = response.text
    match = re.search(r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>', html)
    if match:
        code = match.group(1)
        print(f"code: {code}")
    else:
        print("ko tìm thấy mã")

elif type == 'bk8xo':
    response = requests.post(f'https://traffic-user.net/GET_MD.php?codexnd=bomaylavua&url=https://bk8xo.com/lo-ba-cang-la-gi&loai_traffic=https://bk8xo.com/&clk=1000')
    html = response.text
    match = re.search(r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>', html)
    if match:
        code = match.group(1)
        print(f"code: {code}")
    else:
        print("ko tìm thấy mã")

elif type == 'vn88ie':
    response = requests.post(f'https://traffic-user.net/GET_MD.php?codexnd=bomaylavua&url=https://vn88ie.com/cach-nuoi-lo-khung&loai_traffic=https://vn88ie.com/&clk=1000')
    html = response.text
    match = re.search(r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>', html)
    if match:
        code = match.group(1)
        print(f"code: {code}")
    else:
        print("ko tìm thấy mã")

elif type == 'w88xlm':
    response = requests.post(f'https://traffic-user.net/GET_MA.php?codexn=taodeptrai&url=https://w88xlm.com/cach-choi-bai-solitaire&loai_traffic=https://w88xlm.com/&clk=1000')
    html = response.text
    match = re.search(r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>', html)
    if match:
        code = match.group(1)
        print(f"code: {code}")
    else:
        print("ko tìm thấy mã")
