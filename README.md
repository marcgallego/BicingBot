# TheRealBicingBot

TheRealBicingBot, un bot de Telegram que permet obtenir informació en temps real sobre el servei del Bicing. Des de

Try our bot at [t.me/TheRealBicingBot](https://t.me/TheRealBicingBot)

## Getting Started

D'entrada, cal clonar aquest repositori a la vostra màquina local, feu-ho amb la comanda següent:

```
git clone https://github.com/rorencio/BicingBot.git
```
En cas de no tenir `git` instal·lat, podeu obteir-lo des d'[aquí](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### Prerequisits

Per a instal·lar el projecte, es requereix Python 3. Si no el teniu, podeu descarregar-lo des de la [web oficial](https://www.python.org/).

### Instal·lació

Sigui quin sigui el vostre sistema operatiu, per a fer la instal·lació tan sols cal que obriu un terminal a aquest directori i feu:
```
pip3 install -r requirements.txt
```
Això instalarà automàticament tots els paquets que fan falta. I ja està, no cal res més!

Ara podeu provar localment les funcions de l'arxiu `data.py` o bé executar el vostre propi bot (vegeu [Deployment](#Deployment)).

## Running the tests

Per a executar els tests, simplement executeu el programa `data.py`, amb la comanda següent:
```
python3 data.py
```
Això, per defecte, executarà un parell de vegades cada una de les funcions principals del programa, amb uns paràmtetres predeterminats. Sentiu-vos lliure de modificar la funció `tests` per a alterar aquests paràmetres.


## Deployment

Per a disposar del vostre propi bot de Telegram, farà falta crear-lo (vegeu [BotFather](https://core.telegram.org/bots#6-botfather)). Un cop tingueu el vostre token deseu-lo al mateix directori on teniu el nostre projecte en un arxiu anomenat `token.txt`. Llavors, des d'un ordinador amb connexió a Internet llençeu el programa `bot.py` (tot fent `python3 bot.py`).
Mentre estigui corrent, podreu usar el bot. Si voleu executar-lo de forma més consistent, considereu usar un servidor.

## Eines usades

* [Hydrogen](https://atom.io/packages/hydrogen) - Execució de codi de forma interactiva
* [Jupyter Notebook](https://jupyter.org/) - Execucuió de codi per blocs


## Autors

* **Marc Vernet** - [marc.vernet@est.fib.upc.edu](mailto:marc.vernet@est.fib.upc.edu)
* **Marc Gàllego** - [marc.gallego.asin@est.fib.upc.edu](mailto:marc.gallego.asin@est.fib.upc.edu)

Vegeu tambè la llista de [col·laboradors](https://github.com/rorencio/BicingBot/contributors) que han participat al projecte.

## Agraïments

* Part del codi ha estat desenvolupada pels nostres professors d'Algorisimia i Programació II, en Jordi Petit i en Jordi Cortadella.
