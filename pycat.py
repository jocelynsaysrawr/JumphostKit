#!/usr/bin/env python

import sys
import socket
import argparse
import threading
import subprocess

# global variables
listen = False
command = False
upload = False
execute = ''
target = ''
upload_destination = ''
port = 0

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to our target host
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)
        
        while True:          
            recv_len = 1
            response = b''

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                print('recv_len: ', recv_len)
                response += data

                if recv_len < 4096:
                    break

            print(response.decode())

            # wait for more input
            buffer = input('').encode()
            buffer += b'\n'

            # send the input
            client.send(buffer)

    except:
        print('Exiting!')
        client.close()


def server_loop():
    global target
    
    try:
        # if no target is defined, we listen on all interfaces
        if not len(target):
            target = '0.0.0.0'

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((target, port))
        server.listen(5)

        while True:
            client_socket, addr = server.accept()
        
            # spin off a thread to handle our new client
            client_thread = threading.Thread(target=client_handler, args=(client_socket, command))
            client_thread.start()
    
    except KeyboardInterrupt:
        print('keyboard interrupt')


def run_command(command):
    # trim the newline
    command = command.rstrip()

    # run the command and get the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

    except:
        output = 'Failed to execute command.\r\n'.encode()

    # send the output back to the client
    return output


def client_handler(client_socket, command):
    global upload
    global execute

    # check for upload
    if len(upload_destination):
        
        # read in all of the bytes and write to our destination
        file_buffer = ''

        # keep reading data until none is available
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        # now we take these bytes and try to write them out
        try:
            file_descriptor = open(upload_destination, 'wb')
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # acknowledge that we wrote the file out
            client_socket.send('Successfully saved file to {}\r\n'.format(upload_destination))

        except:
            client_socket.send('Failed to save file to {}\r\n'.format(upload_destination))

    # check for command execution
    if len(execute):

        # run the command
        output = run_command(execute)

        client_socket.send(output)

    # now we go into another loop if a command shell was requested
    if command:
        
        while True:
            # show a simple prompt
            client_socket.send('<Pycat:#>'.encode())
            
                # now we receive until we see a linefeed (enter key)
            cmd_buffer = ''.encode()
            while '\n'.encode() not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            # send back the command output
            response = run_command(cmd_buffer)

            # send back the response
            client_socket.send(response)




def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    # read commandline options
    try:
        
        parser = argparse.ArgumentParser(description='Pycat - A Python Substitution for Netcat')
        parser.add_argument('-t', '--target', help='target host ip address')
        parser.add_argument('-p', '--port', help='target port')
        parser.add_argument('-l', '--listen', action='store_true', help='listen on [host]:[port] for incoming connections')
        parser.add_argument('-e', '--execute', nargs=1, help='execute the given file upon receiving a connection')
        parser.add_argument('-c', '--command', action='store_true', help='initialize a command shell')
        parser.add_argument('-u', '--upload', nargs=1, help='upon receiving connection upload a file and write to [destination]')
        args = parser.parse_args()
 
        if args.listen == True:
            listen = args.listen
        if args.execute != None:
            execute = args.execute[0]
        if args.command != False:
            command = args.command
        if args.upload != None:
            upload_destination = args.upload[0]
        if args.target != None:
            target = args.target
            

        port = int(args.port)
        # NETCAT client
        if not listen and len(target) and port > 0:
            print('in client')
            buffer = sys.stdin.read()
            client_sender(buffer)

        # NETCAT server
        if listen:
            print('in server')
            # if not len(target):
            #     target = '0.0.0.0'   
            server_loop()

    except:
        print('error')
        

if __name__ == '__main__':
    main()