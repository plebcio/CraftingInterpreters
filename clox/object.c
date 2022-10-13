#include <stdio.h> 
#include <string.h>

#include "memory.h" 
#include "object.h"
#include "table.h" 
#include "value.h"
#include "vm.h"

#define ALLOCATE_OBJ(type, objectType) \
    (type*)allocateObject(sizeof(type), objectType)

static Obj* allocateObject(size_t size, ObjType type) { 
    Obj* object = (Obj*)reallocate(NULL, 0, size); 
    object->type = type; 

    object->next = vm.objects;
    vm.objects = object;
    return object;
}

static ObjString* allocateString(const char* chars, int length, uint32_t hash) { 
    size_t size = sizeof(ObjString) + sizeof(char)*(length+1);
    ObjString* string = (ObjString*)allocateObject(size, OBJ_STRING); 
    string->hash = hash;
    string->length = length; 
    memcpy(string->chars, chars, length);
    string->chars[length] = '\0';

    tableSet(&vm.strings, string, NIL_VAL);
    return string;
}

static uint32_t hashString(const char* key, int length) { 
    uint32_t hash = 2166136261u;
    for (int i = 0; i < length; i++) { 
        hash ^= key[i]; 
        hash *= 16777619;
    } 
    return hash; 
}

// ----------- string alloc entry points -------------

ObjString* takeString(char* chars, int length){
    uint32_t hash = hashString(chars, length);

    ObjString* interned = tableFindString(&vm.strings, chars, length, hash);
    if (interned != NULL) { 
        FREE_ARRAY(char, chars, length + 1); return interned;
    }

    return allocateString(chars, length, hash);
}

// alternative to copy string (kind of)
ObjString* StringConcat(int length, ObjString* a, ObjString* b){
    size_t size = sizeof(ObjString) + sizeof(char)*(length+1);
    ObjString* string = (ObjString*)allocateObject(size, OBJ_STRING); 
    string->length = length; 
    memcpy(string->chars, a->chars, a->length);
    memcpy(string->chars + a->length, b->chars, b->length);
    string->chars[length] = '\0';
    string->hash = hashString(string->chars, length);

    ObjString* interned = tableFindString(&vm.strings, string->chars, length, string->hash);
    if (interned != NULL) return interned;

    return string;
}


ObjString* copyString(const char* chars, int length) { 
    uint32_t hash = hashString(chars, length);

    ObjString* interned = tableFindString(&vm.strings, chars, length, hash);
    if (interned != NULL) return interned;

    return allocateString(chars, length, hash); 
}


// --------------------------------------------------



void printObject(Value value){
    switch (OBJ_TYPE(value))
    {
    case OBJ_STRING:
        printf("%s", AS_CSTRING(value));
        break;
    }
}