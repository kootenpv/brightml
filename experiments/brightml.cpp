
/*
  Adapted by Pascal van Kooten
  -----------------------------------------------

  Grabs a screenshot of the root window.

  Usage   : ./scr_tool <display> <output file>
  Example : ./scr_tool :0 /path/to/output.png

  Author: S Bozdag <selcuk.bozdag@gmail.com>

  requirements: xdotool
*/

#include <fstream>
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
//#include <cairo.h>
//#include <cairo-xlib.h>
#include <X11/Xlib.h>
#include <CImg.h>
#include <fcntl.h>

#include <chrono>
#include <thread>


using namespace cimg_library;

// https://github.com/poliva/lightum/blob/27720ef7658a2b1e8f3cf2ac866a65e08b22c289/functions.c

int getMaxBrightness() {
  // if value is same as current value, i should not write
  int fd, max_backlight;
  //const char *scr_maxbacklight="/sys/class/backlight/acpi_video0/max_brightness";
  const char *scr_maxbacklight="/sys/class/backlight/gmux_backlight/max_brightness";
  ssize_t cnt;
  char buf[5];
  /* read screen max backlight value */
  fd = open(scr_maxbacklight, O_RDONLY);
  if (fd < 0) {
    perror (scr_maxbacklight);
    fprintf (stderr, "Can't open %s\n",scr_maxbacklight);
    exit(1);
  }
  cnt=read(fd, buf, sizeof(buf)-1);
  buf[cnt]='\0';
  close(fd);
  max_backlight=atoi(buf);
  return max_backlight;
}

int getBrightMLValue() {
  // if value is same as current value, i should not write
  int fd, max_backlight;
  //const char *scr_maxbacklight="/sys/class/backlight/acpi_video0/max_brightness";
  const char *brightmlValue="/home/pascal/egoroot/brightml/brightml_value";
  ssize_t cnt;
  char buf[5];
  /* read screen max backlight value */
  fd = open(brightmlValue, O_RDONLY);
  if (fd < 0) {
    return 100;
  }
  cnt=read(fd, buf, sizeof(buf)-1);
  buf[cnt]='\0';
  close(fd);
  max_backlight=atoi(buf);
  return max_backlight;
}

int getLightSensorValue() {

  int fd;
  size_t i,n=0;
  char buf[10];
  char a_light[10];
  const char *light_sensor="/sys/devices/platform/applesmc.768/light";
  ssize_t cnt;

  /* read light sensor value */
  fd = open(light_sensor, O_RDONLY);
  if (fd < 0) {
    perror (light_sensor);
    fprintf (stderr, "Can't open %s\n",light_sensor);
    exit(1);
  }
  cnt=read(fd, buf, sizeof(buf)-1);
  buf[cnt]='\0';
  close(fd);

  /* convert light sensor string value to integer */
  for (i=0;buf[i]!='\0';i++) {
    if (buf[i]==',') break;
    if (buf[i]!='(') {
      a_light[n]=buf[i];
      n++;
    }
  }
  a_light[n]='\0';

  return atoi(a_light);
}

int max(int a, int b) {
  if (a > b) {
    return a;
  } else {
    return b;
  }
}

int min(int a, int b) {
  if (a < b) {
    return a;
  } else {
    return b;
  }
}

float getAveragePixel(Display *disp, XImage *image) {
  // mouse related
  // Bool query_result;
  // int root_x, root_y;
  // int win_x, win_y;
  // unsigned int mask_return;
  // Window window_returned;
  Window focus;
  int revert;

  /* try to connect to display, exit if it's NULL */
  disp = XOpenDisplay( ":0" );
  if( disp == NULL ) {
    fprintf(stderr, "Given display cannot be found, exiting\n");
    return 1;
  }
  // scr = DefaultScreen(disp);
  // root = DefaultRootWindow(disp);

  // mouse stuff
  // query_result = XQueryPointer(disp, root, &window_returned,
  //                              &window_returned, &root_x, &root_y, &win_x, &win_y,
  //                              &mask_return);

  // printf("Mouse is at (%d,%d)\n", root_x, root_y);

  XWindowAttributes gwa;


  XGetInputFocus(disp, &focus, &revert);
  // char *window_name;
  // XFetchName(disp, focus, &window_name);

  XGetWindowAttributes(disp, focus, &gwa);

  // printf("wd %d\n", gwa.width);
  // printf("wd %d\n", gwa.height);

  int small_width = (int)gwa.width / 10;
  int small_height = (int)gwa.height / 10;

  image = XGetImage(disp,focus, small_width, small_height, small_width, small_height, XAllPlanes(), ZPixmap);

  long img_size = small_width * small_height * 3;
  unsigned char *array = new unsigned char[img_size];
  CImg<unsigned char> pic(array, small_width, small_height,1,3);


  int sumPixel = 0;

  for (int x = 0; x < small_width; x++) {
    for (int y = 0; y < small_height ; y++){
      pic(x,y,0) = (XGetPixel(image,x,y) & image->red_mask ) >> 16;
      pic(x,y,1) = (XGetPixel(image,x,y) & image->green_mask ) >> 8;
      pic(x,y,2) = XGetPixel(image,x,y) & image->blue_mask;
    }
  }

  for (int x = 0; x < small_width; x++) {
    for (int y = 0; y < small_height ; y++){
      sumPixel = sumPixel + (int)pic(x, y, 0);
      sumPixel = sumPixel + (int)pic(x, y, 1);
      sumPixel = sumPixel + (int)pic(x, y, 2);
    }
  }

  float averagePixel = (float)sumPixel / (float)img_size;

  //pic.save_png("blah.png");

  delete[] array;
  ~pic;
  //XDestroyImage(image);
  XCloseDisplay(disp);

  return averagePixel;


  //    Window root;
  //  cairo_surface_t *surface;
  //  int scr;
  // /* get the root surface on given display */
  // surface = cairo_xlib_surface_create(disp, root, DefaultVisual(disp, scr),
  //                                     100,
  //                                     1000);
  // // cairo_xlib_surface_set_size(surface, 100, 1000);
  // /* right now, the tool only outputs PNG images */
  // cairo_surface_write_to_png( surface, argv[1] );
  // /* free the memory*/
  // cairo_surface_destroy(surface);
}

void writePCI(float value) {
  std::ofstream newFile("/sys/class/backlight/gmux_backlight/brightness");

    if(newFile.is_open())
    {
      newFile << (int)value;
    }
    newFile.close();

}

int main(int argc, char** argv) {
  /* The only checkpoint only concerns about the number of parameters, see "Usage" */

  int lightSensorValue;
  float newValue;
  float averagePixel;
  int maxBrightness = getMaxBrightness();

  float brightmlValue = getBrightMLValue();
  int oldValue = maxBrightness;

  XImage *image;
  Display *disp;

  while (true) {
    lightSensorValue = getLightSensorValue();
    averagePixel = getAveragePixel(disp, image);
    brightmlValue = getBrightMLValue();

    newValue = pow(1 - (averagePixel / 255), brightmlValue / 100) * maxBrightness;

    if (lightSensorValue <= 10) {
      newValue = newValue * 0.5;
    }

    newValue = max(10, min(newValue, maxBrightness));

    if (brightmlValue == 0) {
      newValue = maxBrightness;
    }

    if (brightmlValue == 500) {
      newValue = 0;
    }

    if (oldValue > newValue && oldValue - newValue < 40) {
      newValue = oldValue;
    } else if (newValue > oldValue && newValue - oldValue < 40) {
      newValue = oldValue;
    }

    oldValue = newValue;

    printf("maxB %d\n", maxBrightness);
    printf("avg %f\n", averagePixel);
    printf("newValue %f\n", newValue);
    printf("brightmlValue %f\n", brightmlValue);
    printf("lightSensorValue %d\n", lightSensorValue);


    printf("new value %f\n", newValue);

    writePCI(newValue);

    std::this_thread::sleep_for(std::chrono::milliseconds(300));


  }

  /* return with success */
  return 0;
}
