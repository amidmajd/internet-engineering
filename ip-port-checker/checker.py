
import os
import socket
import platform
import concurrent.futures
import subprocess


def get_input():
    print('Enter IP Ranges line by line (format : X.X.X.0/24) [Double Enter to add ips] :\n')

    ip_ranges = []
    while True:
        # getting the input until user double presses the enter button
        current_input = input().strip()

        if current_input == '':
            break
        else:
            # adding only first 3 parts of ip to ip_ranges as we are using ip ranges
            try:
                ip_ranges.append('.'.join(current_input.split('.')[:-1]))
            except:
                raise ValueError('Bad Input Values/Format')

    return ip_ranges


def create_ip_list(ip_ranges):
    ip_list = []

    for ip_range in ip_ranges:
        for i in range(1, 255):
            ip_list.append(ip_range + '.' + str(i))

    return ip_list


def ping_check(ip):
    # creating right command for all platforms
    if platform.system().lower() == 'windows':
        param = '-n'
    else:
        param = '-c'
    command = ['ping', param, '2', ip]

    # returning ping call result (Successfull ping => True , Error in ping => False)
    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) == 0


def port_check(ip, port):
    # checking for open given port

    server_address = (ip, port)

    # create the socket with IPv4 and Stream type (TCP/ip4)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect(server_address)
        # print(f'connected to {server_address}')
        return True
    except ConnectionRefusedError as e:
        # print(e)
        return False


def sort_vulnerable_ip_list(ip_list):
    # sorting ip addresses with built-in string ip to hex converter in socket lib
    # then comparing them as key of sort function
    return sorted(ip_list, key=lambda item: socket.inet_aton(item))


def save_vulnerable_ip_list(ip_list):
    # checking for right input type
    if type(ip_list) != type([]):
        raise TypeError('Input variable is not a list object')

    # writing ip list to txt file
    with open('vulnerable_ip_list.txt', 'w+') as vulnerable_ip_list_file:
        vulnerable_ip_list_file.writelines([str(ip)+'\n' for ip in ip_list])


def __check(ip, port):
    if ping_check(ip):
        if port_check(ip, port):
            return ip
        else:
            return None


def main(port, max_workers=16):
    # wrapping all functions together

    # getting user input
    ip_ranges = get_input()

    # converting ip ranges to ip list
    print('Creating IP lists based on Given IP ranges...')
    ip_list = create_ip_list(ip_ranges)

    # running checks asynchronously
    print('Running Async IP checks (ping + port)...')
    with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
        checked_ip_list = []
        for ip in ip_list:
            checked_ip_list.append(executor.submit(__check, ip, port))

        vulnerable_ip_list = []
        for i, func in enumerate(concurrent.futures.as_completed(checked_ip_list)):
            ip = func.result()
            if ip is not None:
                vulnerable_ip_list.append(ip)
            print(f'Checked {i+1}/{len(ip_list)}')

    # sorting vulnerable ip list
    print('\n\nSorting vulnerable IP list...')
    sorted_vulnerable_ip_list = sort_vulnerable_ip_list(vulnerable_ip_list)

    # saving vulnerable ip list
    print('Saving vulnerable IP list...\n')
    save_vulnerable_ip_list(sorted_vulnerable_ip_list)

    print('Done!\n')


if __name__ == "__main__":
    main(port=917)
