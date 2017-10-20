import sys
import time
import zmq

def main(change_value=None):
    ctx = zmq.Context()
    pub = ctx.socket(zmq.PUSH)
    #pub.setsockopt(zmq.SNDHWM, 1)
    #pub.setsockopt(zmq.LINGER, 1)
    pub.bind("ipc:///tmp/brightml_socket")

    if change_value is not None:
        pub.send_string("add_train " + change_value)
    else:
        while True:
            change = input(">>:)>>: ")
            pub.send_string("add_train " + change)

if __name__ == "__main__":
    main()
