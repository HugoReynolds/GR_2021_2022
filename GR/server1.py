import socket
from warnings import catch_warnings


mibtext = []


class MIB:
    def __init__(self, oid, type, access, value):
        self.oid = oid
        self.type = type
        self.access = access
        self.value = value
        self.sub_mibs = {}

    def __str__(self) -> str:
        return str(self.__dict__)


class IdentMIB:
    def __init__(self, port, community_string, oid_MIB):
        self.port = port
        self.community_string = community_string
        self.oid_mib = oid_MIB
        self.sub_mibs = {}


def recursive_print_mib(i_mib):
    print(i_mib.__dict__)
    for p in i_mib.sub_mibs.values():
        recursive_print_mib(p)


def print_mib():
    print()
    print(mib_global.__dict__)
    for i in mib_global.sub_mibs.values():
        recursive_print_mib(i)


def add_recursive_mibs(split_text):
    oids = split_text[0].split('.')

    if not oids[1] in mib_global.sub_mibs.keys():
        mib_global.sub_mibs[oids[1]] = MIB(
            oids[1], split_text[1], split_text[2], eval(split_text[3]))

    prev_mib = mib_global.sub_mibs[oids[1]]

    for i in range(2, len(oids)):
        i_oid = oids[i]

        if not i_oid in prev_mib.sub_mibs.keys():
            prev_mib.sub_mibs[i_oid] = MIB(
                i_oid, split_text[1], split_text[2], eval(split_text[3]))

        prev_mib = prev_mib.sub_mibs[i_oid]

        # else:
        #    prev_dict = prev_dict[i_oid]


def parse_mib_text():
    with open('/home/hugo/Desktop/GR/MIB.txt', 'rt') as file:

        for myline in file:
            myline.split(' ')
            mibtext.append(myline)

    line2 = mibtext[1]
    lst = line2.split(' ')

    global mib_global
    mib_global = IdentMIB(eval(lst[0]), eval(
        lst[1]), lst[2].strip('[').split(']')[0])

    global mib_oids_sorted
    mib_oids_sorted = []

    for text_line in mibtext:
        if text_line.startswith("."):
            split_text = text_line.split()

            add_recursive_mibs(split_text)

            mib_oids_sorted.append(mib_global.oid_mib+split_text[0])
            mib_oids_sorted.sort()

    return mib_global


def get_from_mib(req_oid):
    if req_oid[1].startswith(mib_global.oid_mib):
        split_oid = req_oid[1].split(mib_global.oid_mib)
        split_point_oid = split_oid[1].split('.')

        prev_dict = mib_global.sub_mibs

        for i in range(1, len(split_point_oid)):
            if split_point_oid[i] in prev_dict:
                mib_ret = prev_dict[split_point_oid[i]]
                prev_dict = prev_dict[split_point_oid[i]].sub_mibs

        if mib_ret.sub_mibs == {}:
            return str(mib_ret.__dict__)

    return "This OID is not a value."


def get_next_from_mib(req_oid):
    if req_oid[1].startswith(mib_global.oid_mib):
        index = mib_oids_sorted.index(
            req_oid[1]) if req_oid[1] in mib_oids_sorted else -1

        if index != -1 and index+1 < len(mib_oids_sorted):
            return str(mib_oids_sorted[(index+1)])
        else:
            for oid_str in mib_oids_sorted:
                if oid_str > req_oid[1]:
                    print(oid_str)
                    return oid_str


    return "There is not a next OID."


def get_bulk_from_mib(req_oid):
    if req_oid[1].startswith(mib_global.oid_mib):
        split_oid = req_oid[1].split(mib_global.oid_mib)
        split_point_oid = split_oid[1].split('.')

        prev_dict = mib_global.sub_mibs
        ret_dict = prev_dict

        for i in range(1, len(split_point_oid)):
            if split_point_oid[i] in prev_dict:
                mib_ret = prev_dict[split_point_oid[i]]
                prev_dict = prev_dict[split_point_oid[i]].sub_mibs

            ret_dict = mib_ret.sub_mibs

        lst_ret = [ req_oid[1] + "." + next_mib.oid for next_mib in ret_dict.values()]

        return str(lst_ret)

    return "Unable to perform get-bulk with this OID"


def set_from_mib(req_oid):
    if req_oid[1].startswith(mib_global.oid_mib):
        split_oid = req_oid[1].split(mib_global.oid_mib)
        split_point_oid = split_oid[1].split('.')

        prev_dict = mib_global.sub_mibs

        for i in range(1, len(split_point_oid)):
            if split_point_oid[i] in prev_dict:
                mib_ret = prev_dict[split_point_oid[i]]
                prev_dict = prev_dict[split_point_oid[i]].sub_mibs

        try:
            new_value = eval(req_oid[2]) 

            if 'W' in mib_ret.access:
                if type(new_value) == type(mib_ret.value):
                    mib_ret.value = new_value
                    return "New Value => " + str(mib_ret.value)
                else:
                    return "Type Does Not Match."

        except:
            return "Bad Value Input."

    return "Premission Denied"


def server_options(client_request):
    split_request = client_request.split()

    switcher = {
        "get": get_from_mib,
        "get-next": get_next_from_mib,
        "get-bulk": get_bulk_from_mib,
        "set": set_from_mib
    }
    func = switcher.get(split_request[0], lambda a: 'Invalid')

    return func(split_request)


def run_server():

    parse_mib_text()

    host = "127.0.0.1"

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(mib_global.community_string)
    server.bind((host, mib_global.port))

    print("Server Running...")

    while True:
        try:
            data, addr = server.recvfrom(1024)
            data = data.decode("utf-8")

            if data != "exit":

                print(f"Client {addr}: {data}")

                if data.startswith(mib_global.community_string):
                    spl_data = data.replace(mib_global.community_string, "", 1)
                    data = server_options(spl_data)
                else:
                    data = "Community String is Wrong."

                data = data.encode("utf-8")

                server.sendto(data, addr)

        except KeyboardInterrupt:
            break
        except:
            continue

    server.close()


run_server()
