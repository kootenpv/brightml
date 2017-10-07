all:
	gcc -O3 -I/usr/include/CImg -lX11 -lpthread -lm -lstdc++ screensy.cpp -o screensy

