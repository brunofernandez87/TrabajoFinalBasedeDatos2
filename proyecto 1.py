from pymongo import MongoClient
from datetime import datetime, timezone
from bson.objectid import ObjectId
def get_database():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['libreria']
    return db
#--------CREATE------------
def crear_libro():
    titulo=input("escriba el titulo del libro ")
    autor=input("escriba el autor ")
    isbn=input("escriba el isbn ")
    genero=input("escriba el genero ")
    anioPublicacion=int(input("escriba el anio de publicacion "))
    copias=int(input("escriba la cantidad de copias "))
    disponibles=int(input ("escriba la cantidad de copias disponibles "))
    libro_nuevo={
        "titulo": titulo,
        "autor": autor,
        "isbn": isbn,
        "genero": genero,
        "anioPublicacion": anioPublicacion,
        "copias": copias,
        "disponibles": disponibles
        }
    return libro_nuevo

def agregar_libro(libro,libros_collection):
    for i in libros_collection.find():
        if i["isbn"] == libro["isbn"]:
            print ("este libro ya lo crearon")
            return
    resultado=libros_collection.insert_one(libro)
    print(f"Libro creado con la id:{resultado.inserted_id}")
    return

#--------READ--------------

def buscarLibros(criterio,libros_collection):
    print ("Opcion 1 autor")
    print ("Opcion 2 titulo")
    print ("Opcion 3 genero")
    opcion= int(input ("esto es: "))
    if opcion == 1 :
        resultado=libros_collection.find({"autor":{"$regex":criterio,"$options":"i"}})
        cantidad=libros_collection.count_documents({"autor":{"$regex":criterio,"$options":"i"}})
    elif opcion == 2:
        resultado=libros_collection.find_one({"titulo":{"$regex":criterio,"$options":"i"}})
        cantidad=libros_collection.count_documents({"titulo":{"$regex":criterio,"$options":"i"}})
    else:
        resultado=libros_collection.find({"genero":{"$regex":criterio,"$options":"i"}})
        cantidad=libros_collection.count_documents({"genero":{"$regex":criterio,"$options":"i"}})

    if resultado == None or cantidad == 0:
        print ("No se encontro el libro")
    return resultado

def prestarLibro(isbn, usuario,prestamos_collection,disponibles):
    for i in prestamos_collection.find():
        if i["libroId"] == isbn and i["usuario"] == usuario and i["devuelto"]==False:
            print ("este libro ya lo reservaste")
            return
    if disponibles == 0:
        print ("no hay mas copias de este libro lo lamentamos")
        return
    prestamo_nuevo={
        "libroId": isbn,
        "usuario": usuario,
        "fechaPrestamo": datetime.now(timezone.utc),
        "FechaDevolucion" : None,
        "devuelto": False
    }
    resultado=prestamos_collection.insert_one(prestamo_nuevo)
    print(f"Prestamo creado con la id:{resultado.inserted_id}")
    return resultado.inserted_id

def buscarPrestamo(usuario,isbn,prestamos_collection):
    for i in prestamos_collection.find():
        if i["libroId"] == isbn and i["usuario"] == usuario and i["devuelto"]==False:
            return i["_id"]

def reportePopulares(libros_collection,prestamos_collection):
    populares=prestamos_collection.aggregate([{"$group":{
        "_id":"$libroId",
        "cantidad":{"$sum":1}
    }},
    {"$sort":{"cantidad":-1}},
    {"$limit":5}
    ])
    for i in populares:
        libro=libros_collection.find_one({"isbn":i["_id"]})
        if libro != None:
            titulo=libro["titulo"]
        else:
            titulo="Titulo no encontrado"
        print (f"{titulo} se presto una cantidad de {i["cantidad"]} vez/veces")
    return

#--------UPDATE------------

def modificar_libro(libro,libros_collection,devolucion):            #Esta funcion es utiliza para gestionar las devoluciones o los prestamos y para la modificacion del libro
    if devolucion == False and libro["copias"] >= libro["disponibles"]:
        disponibles=libro["disponibles"]
        disponibles-=1
        libros_collection.update_one({"_id":libro["_id"]},{"$set":{"disponibles":disponibles}})
        return
    elif devolucion == True and libro["copias"] >= libro["disponibles"]:
        disponibles=libro["disponibles"]
        disponibles+=1
        libros_collection.update_one({"_id":libro["_id"]},{"$set":{"disponibles":disponibles}})
        return
    else:
        modificar=input("Escriba la modificacion ")
        opcion=input("Escriba a que pertenece: " \
        "Genero,Autor,Titulo,Copias,Anio de publicacion, isbn o disponibles ").lower()
        match opcion:
            case "autor":
                libros_collection.update_one({"_id":libro["_id"]},{"$set":{"autor":modificar}})
                print ("se modifico el libro")
            case "genero":
                libros_collection.update_one({"_id":libro["_id"]},{"$set":{"genero":modificar}})
                print ("se modifico el libro")
            case "titulo":
                libros_collection.update_one({"_id":libro["_id"]},{"$set":{"titulo":modificar}})
                print ("se modifico el libro")
            case "copias":
                if libro["disponibles"] <= int(modificar):
                    libros_collection.update_one({"_id":libro["_id"]},{"$set":{"copias":int(modificar)}})
                    print ("se modifico el libro")
                else:
                    print("no se puede tener menos copias que disponibles")
            case "anio de publicacion":
                libros_collection.update_one({"_id":libro["_id"]},{"$set":{"anioPublicacion":int(modificar)}})
                print ("se modifico el libro")
            case "isbn":
                libros_collection.update_one({"_id":libro["_id"]},{"$set":{"isbn":modificar}})
                print ("se modifico el libro")
            case "disponibles":
                if libro["copias"] >= int(modificar):
                    libros_collection.update_one({"_id":libro["_id"]},{"$set":{"disponibles":int(modificar)}})
                    print ("se modifico el libro")
                else:
                    print("no se puede tener mas disponibles que copias en la libreria")
    return

def devolverLibro(prestamoId,prestamos_collection):
    prestamos_collection.update_one({"_id":prestamoId},{"$set":{"devuelto":True,"FechaDevolucion": datetime.now(timezone.utc)} })
    print ("se devolvio el libro")
    return

#--------DELETE-------------

def eliminar_libro(libroID,libros_collection):
    libros_collection.delete_one({"_id":libroID})
    print (f"se elimino el libro con el id {libroID}")
    return

#-------Otras Funciones-----

def menu_opciones():
        print("-----Biblioteca El Palacio del Libro-----")
        print ("Bienvenidos")
        print("Opción 1: Agregar libro")
        print ("Opcion 2: Obtener prestado un libro")
        print ("Opcion 3: Buscar un libro")
        print ("Opcion 4: Devolver un libro")
        print ("Opcion 5: Modificar un libro")
        print ("Opcion 6: Eliminar un libro")
        print ("Opcion 7: Reporte Populares")
        print("Opcion 8: Salir")
        return int(input ("¿Que desea hacer? "))

def menu_administrador():
    print("Para entrar en esta seccion tiene que ser administrador")
    admin=input("Ingrese el usuario ")
    contra=input("Ingrese la contrasenia ")
    return admin,contra

def imprimir_libro(libros):         #Esta funcion se utliza para mostrar los libros que se buscaron y para comprobar si los libros se pueden eliminar o modificar
    if type(libros) == dict:
        print (f"Titulo:{libros['titulo']}\n"
            f"Autor: {libros['autor']}\n"
            f"Genero: {libros['genero']}\n"
            f"Anio Publicacion: {libros['anioPublicacion']}\n"
            f"Copias: {libros['copias']}\n"
            f"Disponibles {libros['disponibles']}\n"
            )
        return
    else:
        for libro in libros:
            print (f"Titulo:{libro['titulo']}\n"
            f"Autor: {libro['autor']}\n"
            f"Genero: {libro['genero']}\n"
            f"Anio Publicacion: {libro['anioPublicacion']}\n"
            f"Copias: {libro['copias']}\n"
            f"Disponibles {libro['disponibles']}\n"
            )
        return libros
#--------MAIN--------------

def main():
    menu=True
    usuario_admin="admin"
    contra_admin="1234"
    db = get_database()
    libros_collection = db["libros"]
    prestamos_collection = db["prestamos"]
    while menu == True :
        resultado=menu_opciones()
        match resultado:
            case 1:
                admin,contrasenia=menu_administrador()
                if admin == usuario_admin and contrasenia == contra_admin:
                    libro=crear_libro()
                    agregar_libro(libro,libros_collection)
                else:
                    print ("No tiene acceso")
            case 2:
                usuario=input("ingrese su nombre y apellido con espacio ")
                criterio=input("ingrese el autor,genero o titulo del libro que busca ")
                libro=buscarLibros(criterio,libros_collection)
                if libro != None:
                    comprobacion=imprimir_libro(libro)
                    opcion=input("¿este es el libro? Y/N ").upper()
                    if opcion == "Y":
                        if comprobacion == None:
                            prestador=prestarLibro(libro["_id"],usuario,prestamos_collection,libro["disponibles"])
                            if prestador != None:
                                modificar_libro(libro,libros_collection,devolucion=False)
                        else:
                            print ("No se modifica o elimina debido a que se busco por autor o genero")
                            print ("Recomendamos buscar por titulo")
            case 3:
                criterio=input("ingrese el autor, genero o titulo del libro que desea buscar ")
                resultado=buscarLibros(criterio,libros_collection)
                if resultado != None:
                    imprimir_libro(resultado)
            case 4:
                usuario=input("ingrese su nombre y apellido con espacio ")
                criterio=input("ingrese el autor,genero o titulo del libro que busca ")
                libro=buscarLibros(criterio,libros_collection)
                if libro != None:
                    comprobacion=imprimir_libro(libro)
                    opcion=input("¿este es el libro? Y/N ").upper()
                    if opcion == "Y":
                        if comprobacion == None:
                            prestamoID=buscarPrestamo(usuario,libro["_id"],prestamos_collection)
                            if prestamoID != None:
                                    devolverLibro(prestamoID,prestamos_collection)
                                    modificar_libro(libro,libros_collection,devolucion=True)
                            else:
                                print("Prestamo no encontrado")
                        else:
                            print ("No se modifica o elimina debido a que se encontraron varios libros")
                            print ("Recomendamos buscar por titulo")
            case 5:
                admin,contrasenia=menu_administrador()
                if admin == usuario_admin and contrasenia == contra_admin:
                    criterio=input("Ingrese el autor, genero o titulo del libro que desea modificar ")
                    libro=buscarLibros(criterio,libros_collection)
                    if libro != None:
                        comprobacion=imprimir_libro(libro)
                        opcion=input("¿este es el libro? Y/N ").upper()
                        if opcion == "Y":
                            if comprobacion == None:
                                modificar_libro(libro,libros_collection,devolucion=None)
                            else:
                                print ("No se modifica o elimina debido a que se busco por autor o genero")
                                print ("Recomendamos buscar por titulo")
                else:
                    print("No tiene acceso")    
            case 6:
                admin,contrasenia=menu_administrador()
                if admin == usuario_admin and contrasenia == contra_admin:
                    criterio=input("Ingrese el autor, genero o titulo del libro que desea eliminar ")
                    libro=buscarLibros(criterio,libros_collection)
                    if libro != None:
                        comprobacion=imprimir_libro(libro)
                        opcion=input("¿este es el libro? Y/N ").upper()
                        if opcion == "Y":
                            if comprobacion == None:
                                eliminar_libro(libro["_id"],libros_collection)
                            else:
                                print ("No se modifica o elimina debido a que se busco por autor o genero")
                                print ("Recomendamos buscar por titulo")
                        else:
                            print("no se eliminara el libro")
            case 7:
                reportePopulares(libros_collection,prestamos_collection)
            case 8:
                print("Adios")
                menu=False
if __name__ == "__main__":
    main() 