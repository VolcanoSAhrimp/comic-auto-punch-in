import os

import requests
import json

# 如果运行报错可能是换域名了，进官网会自动重定向新的域名，把老的换成新的域名后面路径不用改
# JM域名:    18comic-blackmyth.club/login        ->      18comic-hok.xyz/login
LOGIN_URL = 'https://18comic-hok.vip/login'  # 登录URL
SIGN_URL = 'https://18comic-hok.vip/ajax/user_daily_sign'  # 签到URL
LOGOUT_URL = 'https://18comic-hok.vip/logout'  # 退出URL

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Content-Type': 'application/javascript; charset=utf-8',
    'Cookie':'__cflb=02DiuDFSTg91mAHCXokVePBgH1pMSYFvSYiFDCTHY23Rv; AVS=f3vqmhcgo1ik1hlk7nkk9744s1; cover=1; ipcountry=IN; cf_clearance=JlzGNXMXvPz48FfY7fSZYGFchvYhty6GtdPX33UjGDk-1729995565-1.2.1.1-ECGRzbD53gwXrHCQBhqzTzjgwd_RekSpCJsI4hH_j4S1YPAAjq_MBthx.qsAE0OwU5nnSj5anaqAfD1d3KVRZYgkY.2uEqKbN55CGH6yuXgMZ4vBCXtidg99UXtn8YT4mCkSUgPHMASywXK5LTrl9szLA.SEKWXjK5mccEPjiTLI.DXfWP7yq6oAYQ7lGPGLKGo7HOJI9pZ6nHBiouZe3754lUDb8cVzyh_iVOc2SPmdzy5gG2Wtx00vpIoMuXPYArgx3uu8NxpkGo3d3xmgTVOVlzrD1e1u2kIWtSdkVBLSIAMhd2gxBIUeM7c1854Pg1.QiMnUnDS8OVaaI.iK7TrVKCMJ6fKMErlkKvYdiuYLc2i4ty5ZwqAat9lGbxkkDmgdZ1YuArCn2jZq4zNn_ne9SG1MD16IxLDuAFcOATi_D4cCe4pVmd_vWkgqWASqQ_i9EikjJcOpZatY3llxrw; yuo1=%7B%22objName%22:%22m9azIIc1YgO8%22,%22request_id%22:1,%22zones%22:%5B%7B%22idzone%22:%225067278%22,%22sub%22:%2277%22,%22container%22:%7B%7D,%22here%22:%7B%7D%7D%5D%7D; ipm5=037f1fc70de5f824b9d3b9aefd029c69'

}
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
#     'Content-Type': 'application/x-www-form-urlencoded;',
# }


def get_jinman_credentials():
    config_data = os.environ.get('ACCOUNTS')
    if not config_data:
        print("Configuration data not provided.")
        return None

    try:
        config = json.loads(config_data)
        jinman_data = next((item for item in config if item["type"] == "jinman"), None)
        if jinman_data:
            return jinman_data
    except json.JSONDecodeError as e:
        print(f"Failed to parse configuration data: {e}")

    return config_data

# 发送登录请求
with requests.Session() as session:
    jinman_data = get_jinman_credentials()
    # 用户名和密码
    payload = {
        'username': jinman_data.get('username'),
        'password': jinman_data.get('password'),
        'submit_login': '1',
    }
    # print("payload:", payload)
    LOGIN_response = session.post(LOGIN_URL, data=payload, headers=headers)
    print(LOGIN_response.status_code)
    # print(LOGIN_response.text)
    # 成功返回200，不成功返回301
    if LOGIN_response.status_code == 200:
        # 获取返回的json判断是否登录成功
        response_data = json.loads(LOGIN_response.text)
        print(response_data)
        # 成功 {"status":1,"errors":["https:\/\/18comic-hok.xyz"]}
        # 失败 {"status":2,"errors":["\u65e0\u6548\u7684\u7528\u6237\u540d\u548c\/\u6216\u5bc6\u7801!"]}
        if response_data["status"] == 1:
            print("账号登录成功\n")

            # 输出登录成功后的cookie
            # print(session.cookies)
            cookies = session.cookies.get_dict()
            # print(cookies)
            print("Cookies:")
            for key, value in cookies.items():
                print(f"{key}: {value}")
            print("")

            # 访问签到
            SIGN_response = session.post(SIGN_URL, headers=headers)

            # 返回签到内容
            SIGN_response_data = json.loads(SIGN_response.text)
            print(SIGN_response_data)
            if "error" in SIGN_response_data:
                print("签到失败,你已经签到过了")
            elif SIGN_response_data["msg"] == "":
                print("签到失败,可能尚未登录")
            else:
                print("签到成功:", SIGN_response_data['msg'])
                print("自动签到执行完成！")
            print()
            # 返回 {"msg":""} 没有登录
            # 返回 {"msg":"","error":"finished"} 已经签到过了
            # 返回 {"msg":"\u60a8\u5df2\u7d93\u5b8c\u6210\u6bcf\u65e5\u7c3d\u5230\uff0c\u7372\u5f97 [ JCoin:20 ]  [ EXP:20 ] \n"} 签到成功

            # 退出账号
            LOGOUT_response = session.get(LOGOUT_URL, headers=headers)

            # 退出账号会发生重定向，查找重定向网页内容来判断是否退出成功,内容很多很卡
            # if "您现在已经登出!" in LOGOUT_response.text:
            #     print("账号登出成功!")
            # else:
            #     print("账号退出失败!")

            # 输出cookie判断是否退出
            # cookies = session.cookies.get_dict()
            # print("Cookies:")
            # for key, value in cookies.items():
            #     print(f"{key}: {value}")

            # 访问签到页面判断是否登出，返回 {"msg":""} 就是退出了
            SIGN_response = session.post(SIGN_URL, headers=headers)
            if not "error" in json.loads(SIGN_response.text):
                print("账号登出成功")
            else:
                print("账号登出失败")
        else:
            print("登录失败:", response_data['errors'])
    else:
        print("登录失败")
