# Librairie(s) utilisee(s)
from flask import *
from PIL.Image import *
from PIL import Image

# Creation d'un objet application web Flask
app = Flask(__name__)

list_pixel = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

# Creation d'une fonction accueillir() associee a l'URL "/"
# pour generer une page web dynamique
@app.route("/stegano")
def accueillir():
    """Affiche la page web"""
    return render_template("stegano.html")


def telecharger_fichiers(fichier):
    """Telecharge le résultat du code"""
    
    fichier.save(f"static/upload/{nom_fichier}")
    flash(f"{nom_fichier} est telechargé")



def cacher(image_front, image_back):
    """
    Cette fonction récupère les codes r,v,b de chaque pixel
    des deux images (image_front et image_back) et  les convertie
    en binaire pour les redistribuer et creer les pixels d'une troisième image
    (img_coder).
    """
    pixels_image = image_front.size
    img_coder = Image.new(mode="RGB", size=(pixels_image))
    for x in range(pixels_image[0]):
        for y in range(pixels_image[1]):
            # on récupère les pixels à la position x,y de image_front
            (r_fake, v_fake, b_fake) = image_front.getpixel((x, y))
            # conversion du code RVB en binaire
            r_wait = bin(r_fake)
            v_wait = bin(v_fake)
            b_wait = bin(b_fake)
            r_wait = str(r_wait[2:])
            v_wait = str(v_wait[2:])
            b_wait = str(b_wait[2:])
            if len(r_wait) < 8:
                r_wait = (8 - len(r_wait)) * "0" + r_wait
            if len(v_wait) < 8:
                v_wait = (8 - len(v_wait)) * "0" + v_wait
            if len(b_wait) < 8:
                b_wait = (8 - len(b_wait)) * "0" + b_wait
            # découpage du code RVB pour récupérer les 5 bits de point fort
            r_fort = r_wait[:5]
            v_fort = v_wait[:5]
            b_fort = b_wait[:5]
            # on récupère les pixels à la position x,y de image_back
            (r2_cacher, v2_cacher, b2_cacher) = image_back.getpixel((x, y))
            # conversion du code RVB en binaire
            r2_wait = bin(r2_cacher)
            v2_wait = bin(v2_cacher)
            b2_wait = bin(b2_cacher)
            r2_wait = str(r2_wait[2:])
            v2_wait = str(v2_wait[2:])
            b2_wait = str(b2_wait[2:])
            if len(r2_wait) < 8:
                r2_wait = (8 - len(r2_wait)) * "0" + r2_wait
            if len(v2_wait) < 8:
                v2_wait = (8 - len(v2_wait)) * "0" + v2_wait
            if len(b2_wait) < 8:
                b2_wait = (8 - len(b2_wait)) * "0" + b2_wait
            # découpage du code RVB pour récupérer les 3 bits de point faible
            r2_fort = r2_wait[:3]
            v2_fort = v2_wait[:3]
            b2_fort = b2_wait[:3]
            # on assemble les 5 bits de image_front et les 3 de image_back
            r = r_fort + r2_fort
            v = v_fort + v2_fort
            b = b_fort + b2_fort
            # assemblage du code RVB pour l'image finale
            list_pixel[0] = r
            list_pixel[1] = v
            list_pixel[2] = b
            # reconversion en décimal
            rconv = int(list_pixel[0], 2)
            vconv = int(list_pixel[1], 2)
            bconv = int(list_pixel[2], 2)
            # formation du pixel sur l'image finale
            img_coder.putpixel((x, y), (rconv, vconv, bconv))
    img_coder.save("img_code.bmp","BMP")
    #img_coder.show()


#img_code = open("img_code.bmp")


def decoder(img_coder):
    """
    Cette fonction part de l'image créée par cacher()
    et récupère les bits de points forts des deux images cachées.
    """
    pixels_image = img_coder.size
    img_decoder = Image.new(mode="RGB", size=(pixels_image))
    img_decoder1 = Image.new(mode="RGB", size=(pixels_image))
    for x in range(pixels_image[0]):
        for y in range(pixels_image[1]):
            # on récupère le pixel à la position x,y de img_coder
            pixels_wait_coder = img_coder.getpixel((x, y))
            rc_wait = bin(pixels_wait_coder[0])
            vc_wait = bin(pixels_wait_coder[1])
            bc_wait = bin(pixels_wait_coder[2])
            # on supprime le 0b
            r0b = rc_wait[2:]
            v0b = vc_wait[2:]
            b0b = bc_wait[2:]
            # on ajoute des '0' pour coder sur 8 bits
            r1 = (8 - len(r0b)) * "0" + str(r0b)
            v1 = (8 - len(v0b)) * "0" + str(v0b)
            b1 = (8 - len(b0b)) * "0" + str(b0b)
            # on récupere les bits de la premiere image
            r3_fort = r1[:5]
            v3_fort = v1[:5]
            b3_fort = b1[:5]
            # on récupère les bits de la deuxième image
            r3_faible = r1[5:]
            v3_faible = v1[5:]
            b3_faible = b1[5:]
            # on ajoute des '0' pour coder le pixel sur 8 bits
            r9 = str(r3_fort) + (8 - len(r3_fort)) * "0"
            v9 = str(v3_fort) + (8 - len(v3_fort)) * "0"
            b9 = str(b3_fort) + (8 - len(b3_fort)) * "0"
            r8 = str(r3_faible) + (8 - len(r3_faible)) * "0"
            v8 = str(v3_faible) + (8 - len(v3_faible)) * "0"
            b8 = str(b3_faible) + (8 - len(b3_faible)) * "0"
            # conversion en décimal
            rconv = int(r9, 2)
            vconv = int(v9, 2)
            bconv = int(b9, 2)
            img_decoder.putpixel((x, y), (rconv, vconv, bconv))
            rconv1 = int(r8, 2)
            vconv1 = int(v8, 2)
            bconv1 = int(b8, 2)
            img_decoder1.putpixel((x, y), (rconv1, vconv1, bconv1))
    img_decoder.show()
    img_decoder1.show()


    

# Lancement de l'application web et son serveur
# accessible Ã  l'URL : http://127.0.0.1:1664
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1662, debug=True)
