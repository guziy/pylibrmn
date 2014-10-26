

FC = s.f90
CC = s.cc



SOURCES_C = $(wildcard *.c) 
SOURCES_F = $(wildcard *.f)
OBJ = $(patsubst %.c, %.o, $(notdir $(SOURCES_C))) \
      $(patsubst %.f, %.o, $(notdir $(SOURCES_F))) 

INC = $(foreach d, $(EC_INCLUDE_PATH), -I$d)


#V = /sb/software/areas/armnssm/ssm-domains-base/libs/rmnlib-dev/linux24-x86-64/lib/Linux_x86-64/gfortran

rmnlib_folder = $(dir $(shell s.locate --lib rmnshared_013))
rmnlib_name = -lrmnshared_013

ifeq ($(strip $(rmnlib_folder)), )
rmnlib_folder=$(dir $(shell s.locate --lib rmn_013))
rmnlib_name = -lrmn_013
endif

all : $(OBJ) 
	@echo $(OBJ)
	@echo $(rmnlib_folder)
	$(FC) -shared $(OBJ) -o libpyrmn.so -Wl,-rpath,$(rmnlib_folder) $(rmnlib_name)
	

%.o: %.c
	$(CC) -c -g $< -o $@ 

%.o : %.f
	$(FC) -c -g $< -o $@
	#gfortran -fPIC -c -g $< -o $@



clean:
	rm -f $(OBJ)
	rm -f *.so
