# Compiler and flags
CC = gcc
CFLAGS = `pkg-config --cflags gio-2.0`
LDFLAGS = `pkg-config --libs gio-2.0`

# Target executable
TARGET = calculator_service

# Source files
SRCS = calculator_service.c

# Object files
OBJS = $(SRCS:.c=.o)

# Default target
all: $(TARGET)

# Rule to link the executable
$(TARGET): $(OBJS)
	$(CC) -o $(TARGET) $(OBJS) $(LDFLAGS)

# Rule to compile source files into object files
%.o: %.c
	$(CC) -c $(CFLAGS) $< -o $@

# Install target
install: $(TARGET)
	install -d $(DESTDIR)/usr/local/bin
	install -m 755 $(TARGET) $(DESTDIR)/usr/local/bin/

# Clean up build files
clean:
	rm -f $(TARGET) $(OBJS)

.PHONY: all clean install