

FC = s.f90
CC = s.cc



SOURCES_C = $(wildcard *.c) 
SOURCES_F = $(wildcard *.f)
OBJ = $(patsubst %.c, %.o, $(notdir $(SOURCES_C))) \
      $(patsubst %.f, %.o, $(notdir $(SOURCES_F))) 

INC = $(foreach d, $(EC_INCLUDE_PATH), -I$d)


#V = /sb/software/areas/armnssm/ssm-domains-base/libs/rmnlib-dev/linux24-x86-64/lib/Linux_x86-64/gfortran

rmnlib_folder = $(dir $(shell s.locate --lib rmnshared_013))


all : $(OBJ) 
	@echo $(OBJ)
	$(FC) -shared $(OBJ) -o libpyrmn.so -Wl,-rpath,$(rmnlib_folder)  -lrmnshared_013 
	

%.o: $(SOURCES_C)
	$(CC) -c -g $< -o $@ 

%.o : $(SOURCES_F)
	$(FC) -c -g $< -o $@
	#gfortran -fPIC -c -g $< -o $@



clean:
	rm -f $(OBJ)
	rm -f *.so
