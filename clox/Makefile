CC = gcc -g -Wall

main: main.o chunk.o debug.o memory.o value.o vm.o compiler.o scanner.o object.o
	$(CC) -o main main.o chunk.o debug.o memory.o value.o vm.o compiler.o scanner.o object.o
main.o: main.c common.h chunk.h debug.h
	$(CC) -c main.c
chunk.o: chunk.c chunk.h memory.h value.h 
	$(CC) -c chunk.c
memory.o: memory.c memory.h common.h
	$(CC) -c memory.c
value.o: value.c value.h common.h object.h memory.h object.h
	$(CC) -c value.c
vm.o: vm.c vm.h common.h debug.h object.h compiler.h
	$(CC) -c vm.c
compiler.o: compiler.c compiler.h common.h scanner.h object.h debug.h
	$(CC) -c compiler.c
scanner.o: scanner.c scanner.h common.h
	$(CC) -c scanner.c
object.o: object.c object.h common.h vm.h memory.h value.h
	$(CC) -c object.c
debug.o: debug.c debug.h value.h
	$(CC) -c debug.c
clean:
	del *.o *.exe