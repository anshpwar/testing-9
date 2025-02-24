CC      ?= cc
CFLAGS  ?= -std=c11 -Wall -Wextra -Werror -O2 -fPIC
CFLAGS  += -Ic/include

UNAME := $(shell uname)
ifeq ($(UNAME),Darwin)
LIBEXT := dylib
SHARED := -dynamiclib
else
LIBEXT := so
SHARED := -shared
endif

LIB   := build/libgate.$(LIBEXT)
SRCS  := $(wildcard c/src/*.c)
TESTS := $(patsubst c/tests/%.c,build/%,$(wildcard c/tests/test_*.c))

.PHONY: build test test-c clean
build: $(LIB)

$(LIB): $(SRCS) $(wildcard c/include/*.h)
	@mkdir -p build
	$(CC) $(CFLAGS) $(SHARED) -o $@ $(SRCS) -lm

build/test_%: c/tests/test_%.c $(SRCS) $(wildcard c/include/*.h) c/tests/check.h
	@mkdir -p build
	$(CC) $(CFLAGS) -Ic/tests -o $@ $< $(SRCS) -lm

test-c: $(TESTS)
	@for t in $(TESTS); do echo "== $$t"; $$t || exit 1; done

test: build test-c
	python3 -m pytest -q tests

clean:
	rm -rf build
