Tenemos 3 clases principales, creador_chips.py, visualizador_pro.py y qubit_routing.mzn.

Basicamente el creador de chips interactivamente te permite colocar los qubits y el tablero del problema que se va a resolver y se reescribe dentro del test.dzn para ello.

qubit_routing es la clase en minizinc que resulve el problema propuesto, lee los datos de test.dzn.

Finalmente el visualizador nos muestra una solucion al problema enseñando las parejas formadas y como se mueven para lograr la solución.

Adicionalmente tenemos la clase BibliotecaAlgoritmos la cual tiene unos casos basicos para explicar y enseñar en la presentación sobre usos reales del
qubit routing.

Para ejecutar el programa se debe ejecutar la clase creador_chips.py y nada más el resto se ejecuta desde dentro.

Las librerias necesarias para la ejecucion son:
networkx, matplotlib, scipy
Además, utilizamos uv para la gestion de librerias, para instalarlas todas valdria con el comando:
uv pip install networkx matplotlib scipy

Sin contar con Python, minizinc y todas las librerias que ya vienen por defecto en la extension de Python.
