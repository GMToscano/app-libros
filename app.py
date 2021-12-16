from re import DEBUG
import bcrypt
from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:1234@localhost:5432/db3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SecretKey'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app) 
bcryp = Bcrypt(app)


    
#####################################################################
class Usuarios(db.Model, UserMixin):
    __tablename__= "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80))
    password = db.Column(db.String(255))

    def __init__(self, email, password):
        self.email=email
        self.password=password

@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))
###################################################################
class Editorial(db.Model):
    __tablaname__ = "editorial"
    id_editorial = db.Column(db.Integer, primary_key=True)
    nombre_editorial = db.Column(db.String(80))

    def __init__(self, nombre_editorial):
        self.nombre_editorial=nombre_editorial
 ###########################################################       
class Libro(db.Model):
    __tablename__ = "libro"
    id_libro = db.Column(db.Integer, primary_key=True)
    titulo_libro = db.Column(db.String(80))
    fecha_publicacion = db.Column(db.Date)
    numero_paginas = db.Column(db.Integer)
    formato = db.Column(db.String(30))
    volumen = db.Column(db.Integer)

    #Relacion
    id_editorial = db.Column(db.Integer, db.ForeignKey("editorial.id_editorial"))
    id_autor = db.Column(db.Integer, db.ForeignKey("autor.id_autor"))
    id_genero = db.Column(db.Integer, db.ForeignKey("genero.id_genero"))

    def __init__(self, titulo_libro, fecha_publicacion, numero_paginas, formato, volumen, id_editorial, id_autor, id_genero):
        self.titulo_libro = titulo_libro
        self.fecha_publicacion = fecha_publicacion
        self.numero_paginas = numero_paginas
        self.formato = formato
        self.volumen = volumen
        self.id_editorial = id_editorial
        self.id_autor = id_autor
        self.id_genero = id_genero

################################################
class Autor(db.Model):
    __tablaname__ = "autor"
    id_autor = db.Column(db.Integer, primary_key=True)
    nombre_autor = db.Column(db.String(80))
    fecha_nac = db.Column(db.Date)
    nacionaliad = db.Column(db.String(40))

    def __init__(self, nombre_autor, fecha_nac, nacionalidad):
        self.nombre_autor = nombre_autor
        self.fecha_nac = fecha_nac
        self.nacionaliad = nacionalidad
##################################################################
class Genero(db.Model):
    __tablaname__ = "genero"
    id_genero = db.Column(db.Integer, primary_key=True)
    nombre_genero = db.Column(db.String(80))

    def __init__(self, nombre_genero):
        self.nombre_genero = nombre_genero

###################################################################

class MisFavoritos(db.Model):
    __tablaname__ = "misfavoritos"
    id_lista_favoritos = db.Column(db.Integer, primary_key=True)
    
    #Relacion
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    id_libro = db.Column(db.Integer, db.ForeignKey("libro.id_libro"))

    def __init__(self, id_usuario, id_libro):
        self.id_usuario = id_usuario
        self.id_libro = id_libro

######################################################################        

@app.route("/")
def index():
    return render_template("index.html")
#######################################################################
@app.route("/login", methods=['POST'])
def login():
    email = request.form["email"]
    password = request.form["password"]
    #password_cifrado = bcryp.generate_password_hash(password)

    consulta_usuario = Usuarios.query.filter_by(email=email).first()
    pass_cifrado = bcryp.check_password_hash(consulta_usuario.password,password)
    print(consulta_usuario.email)

    if bcryp.check_password_hash(consulta_usuario.password,password) == pass_cifrado:
            login_user(consulta_usuario)
            return redirect("/leerfav")
    else:
        return redirect("/")
#############################################################################
@app.route("/vista")
def menu():
    return render_template("vistaPrincipal.html")


######################################################################
@app.route("/registrar")
def registrar():
    #return "Hizo click en registrar"
    return render_template("registro.html");
#########################################################
@app.route("/registrar_usuario", methods=['POST'])
def registrar_usuario():
    email = request.form["email"]
    password = request.form["password"]
    print(email)
    print(password)

    password_cifrado = bcryp.generate_password_hash(password).decode('utf-8')
    print(password_cifrado)

    usuario = Usuarios(email = email, password=password_cifrado)
    db.session.add(usuario)
    db.session.commit()
    return redirect("/")
########################################################################################    
@app.route("/iniciar_sesion")
def iniciar_sesion():
    redirect("/")
########################REGISTRO LIBRO##################################
@app.route("/registralibro")
def registrar_libro():
    autorConsulta = Autor.query.all()
    generoConsulta = Genero.query.all()
    editorialConsulta = Editorial.query.all()
    return render_template("registrolibro.html", autores = autorConsulta, generos = generoConsulta, editoriales = editorialConsulta)
##########################################################################

@app.route("/registrar_libro", methods=["POST"])
def registrarlibro():
    nombreLibro = request.form["nombreLibro"]
    fechaPublic = request.form["fecha"]
    paginas = request.form["numeroLibro"]
    formato = request.form["formato"]
    volumen = request.form["volumen"]
    editorial = request.form["editorial"]
    genero = request.form["genero"]
    autor = request.form["autor"]

    libro = Libro(titulo_libro=nombreLibro, fecha_publicacion=fechaPublic, numero_paginas=paginas, formato=formato, volumen=volumen, id_editorial=editorial, id_genero=genero, id_autor=autor)
    db.session.add(libro)
    db.session.commit()

    return redirect("/leerlibros")

##############################Registro Genero###########################################
@app.route("/registrogenero")
def registrogenero():
    return render_template("registrogenero.html")
##################################################
@app.route("/registrar_genero", methods=["POST"])
def registrargenero():
    nombreG = request.form["nombreGenero"]

    genero = Genero(nombre_genero = nombreG)
    db.session.add(genero)
    db.session.commit()

    return redirect("/leergenero")

###################################Registro editorial##############################################
@app.route("/registrarEditorial")
def registroeditorial():
    return render_template("registroeditorial.html")
##################################################
@app.route("/registrar_editorial", methods=["POST"])
def registrareditorial():
    nombreE = request.form["nombreEditorial"]

    editorial = Editorial(nombre_editorial= nombreE)
    db.session.add(editorial)
    db.session.commit()

    return redirect("/leeredit")
#######################################Registro autor#########################################################
@app.route("/registrarAutor")
def registrar_autor():
    return render_template("registroautor.html")
#######################################################################################################
@app.route("/registrar_autor", methods=["POST"])
def registrarAutor():
    nombreA = request.form["nombreAutor"]
    fechaN = request.form["FeNac"]
    nac = request.form["nacionalidad"]
    autor = Autor(nombre_autor = nombreA, fecha_nac = fechaN, nacionalidad = nac )
    db.session.add(autor)
    db.session.commit()

    return redirect("/leerautores")


###########################################Libros funciones#########################################################
@app.route("/leerlibros")
@login_required
def leerlibros():
    Libros = Libro.query.join(Genero, Libro.id_genero == Genero.id_genero).join(Autor, Libro.id_autor == Autor.id_autor).join(Editorial, Libro.id_editorial == Editorial.id_editorial).add_columns(Libro.id_libro, Genero.nombre_genero, Libro.titulo_libro, Libro.volumen, Libro.fecha_publicacion, Libro.numero_paginas, Libro.formato, Autor.nombre_autor, Editorial.nombre_editorial)
    
    return render_template("librovista.html", consulta = Libros)

@app.route("/eliminarlibro/<ID>")
@login_required
def eliminar(ID):
    libro = Libro.query.filter_by(id_libro = int(ID)).delete()
    print(libro)
    db.session.commit()
    return redirect("/leerlibros")

@app.route("/modificarlibro", methods=['POST'])
@login_required
def modificarlibro():
    idlibro = request.form['idlibro']
    nombreLibro = request.form['nombreLibro']
    fechaPublic = request.form['fecha']
    paginas = request.form['numeroLibro']
    formato = request.form['formato']
    volumen = request.form['volumen']
    editorial = request.form['editorial']
    genero = request.form['genero']
    autor = request.form['autor']
    libro = Libro.query.filter_by(id_libro = int(idlibro)).first()
    libro.titulo_libro = nombreLibro
    libro.fecha_publicacion = fechaPublic
    libro.numero_paginas = paginas
    libro.formato = formato
    libro.volumen = volumen
    libro.id_editorial = editorial
    libro.id_autor = autor
    libro.id_genero = genero
    
    db.session.commit()
    return redirect("/leerlibros")

@app.route("/editarlibro/<ID>")
@login_required
def editar(ID):
    autorConsulta = Autor.query.all()
    generoConsulta = Genero.query.all()
    editorialConsulta = Editorial.query.all()
    libro = Libro.query.filter_by(id_libro = int(ID)).first()
    return render_template("modificarlibro.html", libro = libro, autores = autorConsulta, generos = generoConsulta, editoriales = editorialConsulta )

###################################################Autores Funciones##############################################################################
@app.route("/leerautores")
@login_required
def leerautor():
    consulta_autores = Autor.query.all()
    return render_template("autorvista.html", consulta = consulta_autores)

@app.route("/eliminarautor/<ID>")
@login_required
def eliminarautor(ID):
    autor = Autor.query.filter_by(id_autor = int(ID)).delete()
    print(autor)
    db.session.commit()
    return redirect("/leerautores")

@app.route("/modificarA", methods=['POST'])
@login_required
def modificarautor():
    idautor = request.form['idautor']
    nombreautor = request.form['nombreAutor']
    fechaN = request.form['FeNac']
    nac = request.form['nacionalidad']
    autor = Autor.query.filter_by(id_autor = int(idautor)).first()
    autor.nombre_autor = nombreautor
    autor.fecha_nac = fechaN
    autor.nacionaliad = nac
    db.session.commit()
    return redirect("/leerautores")

@app.route("/editarautor/<ID>")
@login_required
def editarautor(ID):
    autor = Autor.query.filter_by(id_autor = int(ID)).first()
    return render_template("modificarautor.html", autor = autor)

####################################################################Editoriales Funciones#####################################################################
@app.route("/leeredit")
@login_required
def leeredit():
    consulta_edit = Editorial.query.all()
    return render_template("editvista.html", consulta = consulta_edit)

@app.route("/eliminaredit/<ID>")
@login_required
def eliminareditorial(ID):
    edit = Editorial.query.filter_by(id_editorial = int(ID)).delete()
    print(edit)
    db.session.commit()
    return redirect("/leeredit")

@app.route("/modificarE", methods=['POST'])
@login_required
def modificareditorial():
    idedit = request.form['idedit']
    nombreedit = request.form['nombreedit']
    edit = Editorial.query.filter_by(id_editorial = int(idedit)).first()
    edit.nombre_editorial = nombreedit
    db.session.commit()
    return redirect("/leeredit")

@app.route("/editaredit/<ID>")
@login_required
def editareditorial(ID):
    edit = Editorial.query.filter_by(id_editorial = int(ID)).first()
    return render_template("modificaredit.html", edit = edit)
#######################################################################Generos Funciones###################################################
@app.route("/leergenero")
@login_required
def leergenero():
    consulta_genero = Genero.query.all()
    return render_template("generovista.html", consulta = consulta_genero)

@app.route("/eliminargenero/<ID>")
@login_required
def eliminargenero(ID):
    genero = Genero.query.filter_by(id_genero = int(ID)).delete()
    print(genero)
    db.session.commit()
    return redirect("/leergenero")

@app.route("/modificarG", methods=['POST'])
@login_required
def modificargenero():
    idge = request.form['idgenero']
    nombregenero = request.form['nombregenero']
    genero = Genero.query.filter_by(id_genero = int(idge)).first()
    genero.nombre_genero = nombregenero
    db.session.commit()
    return redirect("/leergenero")

@app.route("/editargenero/<ID>")
@login_required
def editargenero(ID):
    genero = Genero.query.filter_by(id_genero = int(ID)).first()
    return render_template("modificargenero.html", genero = genero)

#############################################################################Mis favoritos##############################################################
@app.route("/leerfav")
@login_required
def leerfavoritos():
    Libros = Libro.query.join(MisFavoritos, Libro.id_libro == MisFavoritos.id_libro).join(Autor, Libro.id_autor == Autor.id_autor).add_columns(Libro.titulo_libro, Autor.nombre_autor, MisFavoritos.id_lista_favoritos)
    print(Libros)
    return render_template("vistaPrincipal.html", consulta = Libros, iduser = current_user.id)

@app.route("/agregarfav/<ID>")
@login_required
def agregarfav(ID):
    fav = MisFavoritos(id_libro = ID, id_usuario=current_user.id)
    db.session.add(fav)
    db.session.commit()
    return redirect("/leerlibros")

@app.route("/eliminarfav/<ID>")
@login_required
def eliminarfavorito(ID):
    fav = MisFavoritos.query.filter_by(id_lista_favoritos = int(ID)).delete()
    print(fav)
    db.session.commit()
    return redirect("/vista")


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True);
    