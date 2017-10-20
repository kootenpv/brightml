//
//  Hello World client in C++
//  Connects REQ socket to tcp://localhost:5555
//  Sends "Hello" to server, expects "World" back
//
#include <zmq.hpp>

int main ()
{
    //  Prepare our context and socket
    zmq::context_t context (1);
    zmq::socket_t socket (context, ZMQ_PUSH);

    //std::cout << "Connecting to hello world server…" << std::endl;
    socket.bind("ipc:///tmp/brightml_socket");

    zmq::message_t request (5);
    memcpy (request.data (), "Hello", 5);
    socket.send(request);
    return 0;
}
