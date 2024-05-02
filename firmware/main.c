// This file is Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
// License: BSD

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <generated/csr.h>
#include <irq.h>
#include <libbase/console.h>
#include <libbase/uart.h>

/*-----------------------------------------------------------------------*/
/* Uart                                                                  */
/*-----------------------------------------------------------------------*/

static char *readstr(void) {
  char c[2];
  static char s[64];
  static int ptr = 0;

  if (readchar_nonblock()) {
    c[0] = getchar();
    c[1] = 0;
    switch (c[0]) {
    case 0x7f:
    case 0x08:
      if (ptr > 0) {
        ptr--;
        fputs("\x08 \x08", stdout);
      }
      break;
    case 0x07:
      break;
    case '\r':
    case '\n':
      s[ptr] = 0x00;
      fputs("\n", stdout);
      ptr = 0;
      return s;
    default:
      if (ptr >= (sizeof(s) - 1))
        break;
      fputs(c, stdout);
      s[ptr] = c[0];
      ptr++;
      break;
    }
  }

  return NULL;
}

static char *get_token(char **str) {
  char *c, *d;

  c = (char *)strchr(*str, ' ');
  if (c == NULL) {
    d = *str;
    *str = *str + strlen(*str);
    return d;
  }
  *c = 0;
  d = *str;
  *str = c + 1;
  return d;
}

static void prompt(void) { printf("\e[92;1mSadScope\e[0m> "); }

/*-----------------------------------------------------------------------*/
/* Help                                                                  */
/*-----------------------------------------------------------------------*/

static void help(void) {
  puts("\nLiteX minimal demo app built "__DATE__
       " "__TIME__
       "\n");
  puts("Available commands:");
  puts("help               - Show this command");
  puts("clear              - clear the screen");
  puts("reboot             - Reboot CPU");
#ifdef CSR_LEDS_BASE
  puts("led                - Led demo");
#endif
  puts("donut              - Spinning Donut demo");
  puts("helloc             - Hello C");
#ifdef WITH_CXX
  puts("hellocpp           - Hello C++");
#endif
}

/*-----------------------------------------------------------------------*/
/* Commands                                                              */
/*-----------------------------------------------------------------------*/

static void reboot_cmd(void) { ctrl_reset_write(1); }

#ifdef CSR_LEDS_BASE
static void led_cmd(void) {
  int i;
  printf("Led demo...\n");

  printf("Counter mode...\n");
  for (i = 0; i < 32; i++) {
    leds_out_write(i);
    busy_wait(100);
  }

  printf("Shift mode...\n");
  for (i = 0; i < 4; i++) {
    leds_out_write(1 << i);
    busy_wait(200);
  }
  for (i = 0; i < 4; i++) {
    leds_out_write(1 << (3 - i));
    busy_wait(200);
  }

  printf("Dance mode...\n");
  for (i = 0; i < 4; i++) {
    leds_out_write(0x55);
    busy_wait(200);
    leds_out_write(0xaa);
    busy_wait(200);
  }
}
#endif

extern void donut(void);

static void donut_cmd(void) {
  printf("Donut demo...\n");
  donut();
}

extern void helloc(void);

static void helloc_cmd(void) {
  printf("Hello C demo...\n");
  helloc();
}

#ifdef WITH_CXX
extern void hellocpp(void);

static void hellocpp_cmd(void) {
  printf("Hello C++ demo...\n");
  hellocpp();
}
#endif

/*-----------------------------------------------------------------------*/
/* Console service / Main                                                */
/*-----------------------------------------------------------------------*/

static void console_service(void) {
  char *str;
  char *token;
  int pos;
  int lev;

  str = readstr();

  /* Channel Number */
  int CHAN;
  /* Channel Name */
  char CHAN_Name[10];

  if (str == NULL)
    return;
  token = get_token(&str);
  if (strcmp(token, "WAV:DATAQ") == 0)
    for (int i = 0; i < 2000; i++) {
      printf("%d", i & 0xF);
      busy_wait(1);
      printf("\n");
    }
  else if (strcmp(token, "help") == 0)
    help();

  else if (strcmp(token, "reboot") == 0)
    reboot_cmd();

  else if (strcmp(token, "*IDN?") == 0)
    printf("SD,SadOscilloscope,0,0.01-0.0-0.0\n");

  else if (sscanf(token, ":ch%i:DISPQ%n", &CHAN, &pos) == 1 &&
           pos == strlen(token))
    printf("1\n"); // FIXME: Dynamically send

  else if (sscanf(token, "WAV:SOUR %s%n", CHAN_Name, &pos) == 1 &&
           pos == strlen(token))
    ; // FIXME: Select Source!

  else if (strcmp(token, "WAV:PREQ") == 0)
    /* printf("%d,%d,%zu,%d,%f,%f,%f,%f,%f,%f\n", */
    printf("0,2,1000,1,1e-6,-3.e-03,0,1.0,0,0");
  /* 0,            // unused */
  /* 0,            // unused */
  /* (size_t)1000, // npoints, */
  /* 1             // unused3, */
  /* 1e-6,         // sec_per_sample, */
  /* 0.0,          // xorigin, */
  /* 0.0,          // xreference, */
  /* 1.0,          // yincrement, */
  /* 0.0,          // yorigin, */
  /* 122.0         // yreference); */
  /* ); // FIXME: Dynamically send */

  else if (strcmp(token, ":TRIG:MODEQ") == 0)
    printf("EDGE\n"); // FIXME: Dynamically send

  else if (strcmp(token, ":TRIG:STATQ") == 0)
    printf("RUN\n"); // FIXME: Dynamically send

  else if (strcmp(token, ":TRIG:EDGE:SOURQ") == 0)
    printf("CHAN1\n"); // FIXME: Dynamically send

  else if (sscanf(token, "TRIG:EDGE:LEV  %d", &lev) == 1) {
    leds_out_write((int)lev);
    printf("LEVVV\n");

  } else if (strcmp(token, ":TRIG:EDGE:SLOPEQ") == 0)
    printf("POS\n"); // FIXME: Dynamically send

  else if (strcmp(token, ":TRIG:EDGE:LEVQ") == 0)
    printf("0\n"); // FIXME: Dynamically send

  else if (strcmp(token, "clear") == 0)
    printf("\e[1;1H\e[2J");

#ifdef CSR_LEDS_BASE
  else if (strcmp(token, "led") == 0)
    led_cmd();
#endif
  else if (strcmp(token, "donut") == 0)
    donut_cmd();

  else if (strcmp(token, "helloc") == 0)
    helloc_cmd();

#ifdef WITH_CXX
  else if (strcmp(token, "hellocpp") == 0)
    hellocpp_cmd();
#endif

  else
    printf("Error!\n");
  /* prompt(); */
}

int main(void) {
#ifdef CONFIG_CPU_HAS_INTERRUPT
  irq_setmask(0);
  irq_setie(1);
#endif
  uart_init();

  /* help(); */
  /* prompt(); */

  while (1) {
    console_service();
  }

  return 0;
}
