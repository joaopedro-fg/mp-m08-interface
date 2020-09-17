# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 16:47:24 2020

@author: milal
"""
from tkinter import filedialog, Tk
import os

def _open_dialog_file():
	"""Abre uma janela de diálogo para selecionar o magick.exe no diretório do ImageMagick
		retorno: o caminho do arquivo
	"""

	file_types = [('Arquivo executável', '*.html')]
	file_name = None
	title = 'Selecione o diretório raiz'

	root = Tk()
	root.withdraw()
	root.filename = filedialog.askopenfilename(initialdir = os.getcwd(), title = title, filetypes = file_types)
	file_name = root.filename
	root.destroy()

	print(file_name)
	return 