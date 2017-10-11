import sys
import time
import zmq

if __name__ == "__main__":
    ctx = zmq.Context()
    pub = ctx.socket(zmq.PUSH)
    #pub.setsockopt(zmq.SNDHWM, 1)
    #pub.setsockopt(zmq.LINGER, 1)
    pub.bind("ipc:///tmp/screensy_socket")

    if len(sys.argv) > 1:
        pub.send_string("add_train " + sys.argv[1])
    else:
        while True:
            change = input(">>:)>>: ")
            pub.send_string("add_train " + change)
