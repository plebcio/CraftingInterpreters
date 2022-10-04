main: main.o chunk.o debug.o memory.o value.o vm.o compiler.o scanner.o
	gcc -o main main.o chunk.o debug.o memory.o value.o vm.o compiler.o scanner.o
main.o: main.c common.h chunk.h debug.h
	gcc -c main.c
chunk.o: chunk.c chunk.h memory.h value.h 
	gcc -c chunk.c
memory.o: memory.c memory.h common.h
	gcc -c memory.c
value.o: value.c value.h common.h
	gcc -c value.c
vm.o: vm.c vm.h common.h debug.h compiler.h
	gcc -c vm.c
compiler.o: compiler.c compiler.h common.h scanner.h
	gcc -c compiler.c
scanner.o: scanner.c scanner.h common.h
	gcc -c scanner.c
debug.o: debug.c debug.h value.h
	gcc -c debug.c
clean:
	del *.o *.exe