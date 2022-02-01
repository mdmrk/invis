# Invis

Script semi-automático para canjear un código de invitación nuevo en ForoCoches. Los saca de el NewsLetter.

### ¿Como funciona?
1. Realiza constantes comprobaciones a las publicaciones del NewsLetter.
2. Detecta una nueva publicación _(Ocurre los lunes, por lo que es inútil usarlo otro día de la semana)_.
3. Saca lo que posiblemente sean los códigos y hace las operaciones pertinentes _(sumar, restar, sanear string...)_
4. Escribe los resultados a un fichero `invis.txt`.
5. A continuación, abre un navegador web (Firefox) y te copia una invi en el recuadro de canjeo para hacerlo un poco más rápido, y luego **TÚ resuelves el Captcha**.

### ¿Como lo ejecuto?
##### A partir del código fuente
Instala (Python3)[https://www.python.org/downloads/] y en tu ordenador.

```
git clone https://github.com/mariod8/invis
cd invis
pip install -r requirements.txt
python3 invis.py
```

##### A partir del ejecutable
En el apartado Releases del GitHub puedes bajarte el .exe del programa