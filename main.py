import csv
import PyPDF2
import re
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import os

# Abrir el archivo PDF en modo de lectura binaria
def extraccion_data(pagina, archivo_pdf):
    with open(archivo_pdf, 'rb') as archivo:
        # Crear un objeto PDFReader
        lector_pdf = PyPDF2.PdfReader(archivo)
        texto_extraido = ''
        pagina = lector_pdf.pages[pagina]
        texto_extraido += pagina.extract_text()
        return texto_extraido
    
def extract_text_from_pdf(pdf_path, pagina):
    # extraer texto de la páagina de la variable pagina 
    text = extract_text(pdf_path, page_numbers=[pagina], laparams=LAParams())
    return text


def obtener_referencia(texto):
    referencia = re.search(r'(VER\d{2}-\d+)', texto)
    if referencia:
        return referencia.group(1)
    else:
        return None

def obtener_pedimento(texto):
    pedimento = re.search(r'(\d{7}\s\d{4}\s\d{2}\s\d{2})', texto)
    if pedimento:
        cadena = pedimento.group(1)
        numeros = cadena.split()  # Separa la cadena en una lista de números
        numeros = [int(num) for num in numeros]  # Convierte los elementos en números enteros
        numeros.sort()  # Ordena la lista en orden ascendente
        numeros = [str(num) for num in numeros]  # Convierte los números ordenados en cadenas de texto
        pedimento = " ".join(numeros) 
        return pedimento
    else:
        return None
    
def extraer_fechas(texto):
    patron = r"\d{2}/\d{2}/\d{4}"  # Expresión regular para encontrar fechas en formato dd/mm/yyyy
    fechas = re.findall(patron, texto)
    fecha_entrada = fechas[0]
    fecha_pago = fechas[1]
    return fecha_entrada, fecha_pago

def tipo_cambio(texto):
    patron = r"\s+(\d+\.\d+)"
    coincidencias = re.findall(patron, texto)
    if coincidencias:
        tipo_cambio = coincidencias[0]
        return tipo_cambio
    else:
        return None


def dta(texto):
    expresion_regular = r"DTA (\d+)"
    # Buscar el valor en el texto
    coincidencias = re.findall(expresion_regular, texto)
    if coincidencias:
        valor = coincidencias[1]
        return valor
    else:
        return None

def prv(texto):
    expresion_regular = r"OTROS 0 (\d+)"
    # Buscar el valor en el texto
    coincidencias = re.findall(expresion_regular, texto)
    if coincidencias:
        valor = coincidencias[0]
        return valor
    else:
        expresion_regular = r"PRV (\d+)"
        coincidencias = re.findall(expresion_regular, texto)
        if coincidencias:
            valor = coincidencias[3]
            return valor
        else:
            return None


def total_pagado(texto):
    expresion_regular = r"TOTAL (\d+)"
    # Buscar el valor en el texto
    coincidencias = re.findall(expresion_regular, texto)
    if coincidencias:
        valor = coincidencias[0]
        return valor
    else:
        return None

def peso(texto):
    expresion_regular = r"(\d+)\.\d+ VER"

    # Buscar el peso en el texto
    resultado = re.search(expresion_regular, texto)

    if resultado:
        peso = resultado.group(1)
        return peso
    else:
        return None

def fecha_factura(texto):
    # patron de fecha donde si hay un 14/06/2023 16:23:44 ignorar la fecha y tomar la siguiente
    patron = r"\d{2}/\d{2}/\d{4}\s\d{2}:\d{2}:\d{2}"
    patron2 = r"\d{2}/\d{2}/\d{4}"

    coincidencias_patron_1 = re.findall(patron, texto)
    coincidencias_patron_2 = re.findall(patron2, texto)
    numero = (len(coincidencias_patron_2))

    if len(coincidencias_patron_1) > 0:
        if len(coincidencias_patron_2) == 3:
            fecha_factura_1 = coincidencias_patron_2[1]
            fecha_factura_2 = coincidencias_patron_2[2]
            lista_fechas = [fecha_factura_1, fecha_factura_2]
            return lista_fechas
        elif len(coincidencias_patron_2) == 2:
            fecha_factura = coincidencias_patron_2[1]
            return fecha_factura
        elif len(coincidencias_patron_2) == 1:
            fecha_factura = coincidencias_patron_2[0]
            return fecha_factura
        else:
            return "Numero de facturas no soporatadas"
    else:
        # si el numero de coincidencia del patron es = 3 existen dos fechas de factura
        if len(coincidencias_patron_2) == 2:
            fecha_factura_1 = coincidencias_patron_2[0]
            fecha_factura_2 = coincidencias_patron_2[1]
            return fecha_factura_1, fecha_factura_2
        elif len(coincidencias_patron_2) == 2:
            fecha_factura = coincidencias_patron_2[1]
            return fecha_factura
        elif len(coincidencias_patron_2) == 1:
            fecha_factura = coincidencias_patron_2[0]
            return fecha_factura
        else:
            return "Numero de facturas no soporatadas"
    

def extraer_nombre_proveedor(texto):
    patron = r"(?i)NOMBRE, DENOMINACION O RAZON SOCIAL\s*(.*)"

    resultado = re.search(patron, texto)

    if resultado:
        nombre_proveedor = resultado.group(1)
        return nombre_proveedor
    else:
        return None 
    
def extrer_id_fiscal(texto):
    patron = r"(?i)ID FISCAL\s*(.*)"

    resultado = re.search(patron, texto)

    if resultado:
        id_fiscal = resultado.group(1)
        return id_fiscal
    else:
        return None
    
def extraer_folio_factura(texto):
    patron = r"(?i)NUM\. FACTURA\s*(\d+)\s*(?:NUMERO DE ACUSE DE VALOR:\s*(\d+))?(\n|$)"
    patron2 = r"(?i)NUM. FACTURA\s*(.*)"
    coincidencias_2 = re.findall(patron2, texto)
    coincidencias = re.findall(patron, texto)
    if not coincidencias:
        if coincidencias_2:
            folio = coincidencias_2[0]
            return folio
        else:
            return None
    else:
        conteo = len(coincidencias)
        if conteo > 3:
            return 'Cantidad de folios no soportada'
        if coincidencias:
            # seperar la tupla
            folio = coincidencias[0][0]
            folio2 = coincidencias[0][1]
            if not folio2:
                return folio
            else:
                return folio, folio2
    
        

def extraerdataped(archivo_pdf):
    #pagina 1
    texto_extraido = extraccion_data(0, archivo_pdf)
    texto_extraidominer = extract_text_from_pdf(archivo_pdf, 0)
    referencia = obtener_referencia(texto_extraido)
    pedimento = obtener_pedimento(texto_extraido)
    fecha_entrada, fecha_pago = extraer_fechas(texto_extraido)
    tipo_vcamcbio = tipo_cambio(texto_extraidominer)
    valor_dta = dta(texto_extraido)
    valor_prv = prv(texto_extraido)
    valor_total_pagado = total_pagado(texto_extraido)
    valor_peso = peso(texto_extraido)

    #pagina 2
    texto_extraido_pag_2 = extraccion_data(1, archivo_pdf)
    texto_extraidominer_pag_2 = extract_text_from_pdf(archivo_pdf, 1)
    val_fecha_factura = fecha_factura(texto_extraido_pag_2)
    val_nombre_proveedor = extraer_nombre_proveedor(texto_extraidominer_pag_2)
    val_id_fiscal = extrer_id_fiscal(texto_extraidominer_pag_2)
    folio_1 = extraer_folio_factura(texto_extraidominer_pag_2)

    #
    lista_datos = {
            'Referencia': referencia,
            'Pedimento': pedimento,
            'Fecha de entrada': fecha_entrada,
            'Fecha de pago': fecha_pago,
            'Tipo de cambio': tipo_vcamcbio,
            'DTA': valor_dta,
            'PRV': valor_prv,
            'Total pagado': valor_total_pagado,
            'Peso': valor_peso,
            'Fecha de factura': val_fecha_factura,
            'Nombre del provedor': val_nombre_proveedor,
            'ID fiscal': val_id_fiscal,
            'Folio': folio_1
        }
    # impresion de colecion
    print(" ")
    print('Referencia:', referencia)
    print('Pedimento:', pedimento)
    print('Fecha de entrada:', fecha_entrada)
    print('Fecha de pago:', fecha_pago)
    print('Tipo de cambio:', tipo_vcamcbio)
    print('DTA:', valor_dta)
    print('PRV:', valor_prv)
    print('Total pagado:', valor_total_pagado)
    print('Peso:', valor_peso)
    print('Fecha de factura:', val_fecha_factura)
    print('Nombre del provedor:', val_nombre_proveedor)
    print('ID fiscal:', val_id_fiscal)
    if isinstance(folio_1, tuple):
        folio_1, folio_2 = folio_1
        print("Folio 1: ", folio_1)
        print("Folio 2: ", folio_2)
    else:
        print("Folio: ", folio_1)
    return lista_datos


# obtener los archivos pdf en la carpeta pdfs
def extraer_nombres ():
    nombres = []
    for archivo in os.listdir('pdfs'):
        if archivo.endswith('.pdf'):
            nombres.append(archivo)
    return nombres

def extraer_datos_pdfs():
    nombres = extraer_nombres()
    for nombre in nombres:
        extraerdataped(nombre)
    with open('datos.csv', 'w', newline='') as csvfile:
        fieldnames = ['Referencia', 'Pedimento', 'Fecha de entrada', 'Fecha de pago', 'Tipo de cambio', 'DTA', 'PRV', 'Total pagado', 'Peso', 'Fecha de factura', 'Nombre del provedor', 'ID fiscal', 'Folio']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for nombre in nombres:
            writer.writerow(extraerdataped(nombre))




    






            