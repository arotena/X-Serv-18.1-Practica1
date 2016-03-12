#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import webapp
import csv

class recorte(webapp.webApp):

    diccionario = {}
    originales = {}
    numero = 0
    fichs = [ "urls_acortadas.csv", "urls.csv"]
    def parse(self,request):
        clase = request.split(" ",1)[0]
        parametro = request.split(" ",2)[1][1:]
        cuerpo = request.split("\r\n\r\n")[1]
        return clase,parametro,cuerpo

    def procUrl(self, url):
        if("http%3A%2F%2F" in url):
            partido = url.split("%3A%2F%2F")[1]
            valor_guardar = "http://" + partido
        elif("https%3A%2F%2F" in url):
            partido = url.split("%3A%2F%2F")[1]
            valor_guardar = "https://" + partido
        else:
            valor_guardar = "http://" + url
        return valor_guardar

    def leer(self):
        with open(self.fichs[0]) as csvarchivo:
            entrada = csv.reader(csvarchivo)
            for reg in entrada:
                self.diccionario[reg[0]]=reg[1]
        with open(self.fichs[1]) as csvarchivo:
            entrada = csv.reader(csvarchivo)
            for reg in entrada:
                self.originales[reg[0]]=reg[1]
                self.numero = int(reg[0]) + 1

    def escribir (self,key,valor,fich):
        datos = [(key, valor),]
        with open(fich, 'a') as csvsalida:
            salida = csv.writer(csvsalida)
            salida.writerows(datos)
    def sustituir (self, url):
        cambio = url
        cadena = url.split("%2F")
        i = len(cadena)
        if i > 1:
            cambio = ""
            vueltas = 0
            for parte in cadena:
                if(vueltas == i-1):
                    cambio += parte
                else:
                    cambio += parte + "/"
                vueltas += 1
        return cambio

    def process(self,parsedRequest):
        [clase,parametro,cuerpo] = parsedRequest
        if clase == "GET":
            httpCode = "200 OK"
            if(parametro in self.originales) == 1:
                httpBody = "<html><head><meta http-equiv='refresh' content='1;"
                httpBody += "url=" + self.originales[parametro]
                httpBody += "'></head>" + "<body></body></html>\r\n"
            else:
                httpBody = "<html><body>"
                for key, corte in self.diccionario.items():
                    httpBody += key + "  ->  http://localhost:1234/" + corte +"<br/>"
                httpBody += "<form method='post' >"
                httpBody += "URL:<input type='text' name='url'>"
                httpBody += "</form></body></html>"

        elif clase == "POST":
            httpCode = "200 OK"
            qsvalida = cuerpo.split("=")[0]
            if (qsvalida == "url"):
                url_real = cuerpo.split("=")[1]
                nueva = self.procUrl(url_real)
                url_acortar = self.sustituir(nueva)
                if (url_acortar in self.diccionario)==1:
                    httpBody = "<html><body>URL original: " + url_acortar
                    httpBody += " - URL acortada: http://localhost:1234/" + self.diccionario[url_acortar]
                    httpBody += "</body></html>"
                else:
                    self.escribir(url_acortar,str(self.numero), self.fichs[0])
                    self.escribir(str(self.numero),url_acortar, self.fichs[1])
                    self.diccionario[url_acortar] = str(self.numero)
                    self.originales[str(self.numero)] = url_acortar
                    self.numero = self.numero + 1
                    httpBody = "<html><body>Nueva URL acortada: "
                    httpBody += "URL original: " + url_acortar
                    httpBody += " - URL acortada: http://localhost:1234/" + self.diccionario[url_acortar]
                    httpBody += "</body></html>"

            else:
                httpCode = "404 NOT FOUND"
                httpBody = "invalid qs"
        else:
            httpCode = "404 NOT FOUND"
            httpBody = "Not Found"
        return (httpCode,httpBody)

if __name__ == "__main__":
    testWebApp = recorte("localhost", 1234)
