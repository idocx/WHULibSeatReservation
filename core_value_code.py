#############################################################
#                        作者：我.doc
# Github地址：https://github.com/idocx/WHULibSeatReservation
#############################################################

data_dict = {"富强": "0", "民主": "1", "文明": "2", "和谐": "3",
             "爱国": "4", "敬业": "5", "诚信": "6", "友善": "7",
             "公正": "8", "自由": "9", "平等": "0", "法制": "0"}

data_list = ["富强", "民主", "文明", "和谐",
             "爱国", "敬业", "诚信", "友善",
             "公正", "自由", "平等", "法制"]


def str2cvc(string):
    """
    将其转化为core value编码
    :param string: 需要编码的字符串
    :return: 编码好的字符串
    """
    encoded_list = ["{:03}".format(word) for word in string.encode("utf-8")]
    core_value_code = ""
    i = 0
    tmp = (0, 10, 11)
    for each_code in encoded_list:
        for each_num in each_code:
            if each_num == 0:
                core_value_code += data_list[tmp[i]]
                i += 1
                if i == 2:
                    i = 0
            else:
                core_value_code += data_list[int(each_num)]
    return core_value_code


def cvc2str(encoded_string):
    """
    进行解码
    :param encoded_string: 需要解码的字符串
    :return:
    """
    str_stack = code_stack = ""
    result = b""
    count = i = 0
    for each_str in encoded_string:
        str_stack += each_str
        i += 1
        if not i % 2:
            code_stack += data_dict[str_stack]
            count += 1
            str_stack = ""
            if not count % 3:
                result += (int(code_stack)).to_bytes(1, "big")
                code_stack = ""
    return result.decode("utf-8")


if __name__ == "__main__":
    result = str2cvc(input())
    print(result)
    print(cvc2str(result))
