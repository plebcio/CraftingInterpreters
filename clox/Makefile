CC = gcc -g -Wall

main: main.o chunk.o debug.o memory.o value.o vm.o compiler.o scanner.o
	$(CC) -o main main.o chunk.o debug.o memory.o value.o vm.o compiler.o scanner.o
main.o: main.c common.h chunk.h debug.h
	$(CC) -c main.c
chunk.o: chunk.c chunk.h memory.h value.h 
	$(CC) -c chunk.c
memory.o: memory.c memory.h common.h
	$(CC) -c memory.c
value.o: value.c value.h common.h
	$(CC) -c value.c
vm.o: vm.c vm.h common.h debug.h compiler.h
	$(CC) -c vm.c
compiler.o: compiler.c compiler.h common.h scanner.h debug.h
	$(CC) -c compiler.c
scanner.o: scanner.c scanner.h common.h
	$(CC) -c scanner.c
debug.o: debug.c debug.h value.h
	$(CC) -c debug.c
clean:
	del *.o *.exe