# coding: utf-8

import tkinter
from tkinter import Tk, IntVar, Radiobutton, \
			Entry, filedialog, Button, END, Label, messagebox, \
			Checkbutton, BooleanVar, CENTER

from glob import glob
from os.path import basename, splitext

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

from platform import system
if system()=="Windows" :
	fType = [("CSV/TSV", "*.csv;*.tsv")]
	
else :
	fType = [("CSV", "*.csv"), ("TSV", "*.tsv")]

def factor_processing(s) :
	try :
		if int(s)==0 :
			out = ""
		else :
			out = int(s)
	except ValueError :
		out = ""

	return out

def plot(csvname, save=False) :
	try :
		min_ = entryMin.get()
		max_ = entryMax.get()

		if float(min_)!=int(min_) or float(max_)!=float(max_) :
			min_ = float(min_)
			max_ = float(max_)
		else :
			min_ = int(min_)
			max_ = int(max_)

	except :
		min_ = None
		max_ = None

	try :
		capsize = int(entryCap.get())
	except :
		capsize = 5

	ERR = int(errV.get())

	A = factor_processing(entryA.get())
	B = factor_processing(entryB.get())
	C = factor_processing(entryC.get())
	D = factor_processing(entryD.get())

	#print(A, B, C, D)

	Nfactor = 0
	try :
		A = ["a"+str(i+1) for i in range(A)]
		Nfactor += 1

		B = ["b"+str(i+1) for i in range(B)]
		Nfactor += 1

		C = ["c"+str(i+1) for i in range(C)]
		Nfactor += 1

		D = ["D"+str(i+1) for i in range(D)]
		Nfactor += 1
	except TypeError :
		pass
	#print(Nfactor)

	conditions = []
	if Nfactor==1 :
		conditions = A
	elif Nfactor==2 :
		for a in A :
			for b in B :
				conditions.append(a+b)
	elif Nfactor==3 :
		for a in A :
			for b in B :
				for c in C :
					conditions.append(a+b+c)
	elif Nfactor==4 :
		for a in A :
			for b in B :
				for c in C :
					for d in D :
						conditions.append(a+b+c+d)

	if H.get() :
		header = 0
	else :
		header = None

	if I.get() :
		index = 0
	else :
		index = None

	if splitext(csvname)[1]==".tsv" :
		delimiter = "\t"
	elif splitext(csvname)[1]==".csv" :
		delimiter = ","

	try :
		df = pd.read_csv(csvname, header=header, index_col=index, delimiter=delimiter)
	except OSError :
		df = pd.read_csv(csvname, header=header, index_col=index, delimiter=delimiter, engine="python")

	data = df.values.astype(np.float64)
	mean = np.mean(data, axis=0)

	SDs = np.std(data, axis=0, ddof=1)
	if ERR==0 :
		err = SDs / np.sqrt(data.shape[0])		# SEM: standard error of the mean
	elif ERR==1 :
		err = SDs
	#print(means)
	#print(err)

	if len(conditions)!=mean.shape[0] :
		messagebox.showwarning("ERROR", "Any \"Number of Factor\"s are missing.\nNumber of conditions is %d" %mean.shape[0])


	X = range(mean.shape[0])

	fig = plt.figure()

	plt.bar(X, mean, yerr=err, capsize=capsize, color="0.7")
	
	try :
		rotation = int(entryXR.get())
	except :
		messagebox.showwarning("WARNING", "\"X-ticks\' rotation\" is only numeric.")
		rotation = 0

	if Nfactor!=0 :
		plt.xticks(X, conditions, rotation=rotation)

	ylabel = entryY.get()
	if ylabel!="" :
		plt.ylabel(ylabel)

	if min_ is None or max_ is None :
		pass
	elif type(min_) == float :
		plt.ylim(min_, max_)
	elif type(min_) == int :
		plt.ylim(min_, max_)
		plt.yticks(range(min_, max_+1), [str(i) for i in range(min_, max_+1)])

	if flagT.get() :
		plt.title(basename(splitext(csvname)[0]))

	outname = splitext(csvname)[0]+".png"
	if save :
		plt.savefig(outname, dpi=300)
	else :
		plt.show()
	plt.close(fig)
	return outname

def __get_dir_name() :
	dir_name = filedialog.askdirectory(title="Choose target directory", initialdir=".")
	if dir_name!="" :
		entry1.delete(0, END)
		entry1.insert(END, dir_name)
		targetV.set(0)
	return 1

def __get_file_name() :
	#ftype = (["CSV", "*.csv"], ["TSV", "*.tsv"])
	dir_name = filedialog.askopenfilename(title="Choose target directory", initialdir=".", filetypes=ftype)
	if dir_name!="" :
		entry2.delete(0, END)
		entry2.insert(END, dir_name)
		targetV.set(1)
	return 1

def __main() :
	flag = int(targetV.get())

	#if entryA.get()=="" :
	#	messagebox.showwarning("ERROR", "Number of Factor is not correct.")
		

	S = flagS.get()

	if flag==0 :
		outnames = ""
		dir_name = entry1.get()
		if dir_name[-1]!="/" :
			dir_name += "/"
		filenames = glob(dir_name+"*.csv")
		for filename in filenames :
			out = plot(filename, S)
			outnames += str(out) + "\n"
	elif flag==1 :
		outnames = plot(entry2.get(), S)

	if S :
		messagebox.showinfo("INFORMATIONS", "Figure is saved.\n%s" %outnames)

if __name__ == "__main__" :
	root = Tk()
	root.title("Plot")
	root.geometry("600x500")

	targetV = IntVar()
	targetV.set(0)

	radio1 = Radiobutton(root, text="Target directory", value=0, variable=targetV)
	radio1.place(x=10, y=10)

	entry1 = Entry(root, width=20)
	entry1.place(x=200, y=10)

	button1 = Button(root, text="Choose target directory", command=__get_dir_name)
	button1.place(x=400, y=10)

	radio2 = Radiobutton(root, text="Target CSV/TSV-file", value=1, variable=targetV)
	radio2.place(x=10, y=30)

	entry2 = Entry(root, width=20)
	entry2.place(x=200, y=30)

	button2 = Button(root, text="Choose target CSV/TSV-file", command=__get_file_name)
	button2.place(x=400, y=30)


	errV = IntVar()
	errV.set(0)

	radio3= Radiobutton(root, text="SEM", value=0, variable=errV)
	radio3.place(x=10, y=60)

	radio4 = Radiobutton(root, text="SD", value=1, variable=errV)
	radio4.place(x=10, y=80)

	H = BooleanVar()
	H.set(True)
	checkH = Checkbutton(root, variable=H, text="Header")
	checkH.place(x=100, y=60)

	I = BooleanVar()
	I.set(True)
	checkI = Checkbutton(root, variable=I, text="Index")
	checkI.place(x=100, y=80)

	"""水準数のセット"""

	labelA = Label(root, text="N of Factor A")
	labelA.place(x=10, y=150)
	entryA = Entry(root, width=3)
	entryA.place(x=100, y=150)

	labelB = Label(root, text="N of Factor B")
	labelB.place(x=10, y=180)
	entryB = Entry(root, width=3)
	entryB.place(x=100, y=180)

	labelC = Label(root, text="N of Factor C")
	labelC.place(x=10, y=210)
	entryC = Entry(root, width=3)
	entryC.place(x=100, y=210)

	labelD = Label(root, text="N of Factor D")
	labelD.place(x=10, y=240)
	entryD = Entry(root, width=3)
	entryD.place(x=100, y=240)


	"""グラフの設定"""

	labelMax = Label(root, text="Maximam value of response")
	labelMax.place(x=150, y=150)
	entryMax = Entry(root, width=3)
	entryMax.place(x=350, y=150)

	labelMin = Label(root, text="Minimam value of response")
	labelMin.place(x=150, y=180)
	entryMin = Entry(root, width=3)
	entryMin.place(x=350, y=180)

	labelY = Label(root, text="Y-label of graph")
	labelY.place(x=150, y=210)
	entryY = Entry(root, width=20)
	entryY.place(x=350, y=210)

	flagT = BooleanVar()
	flagT.set(False)
	checkT = Checkbutton(root, text="CSV/TSV\'s name to Title of graph", variable=flagT)
	checkT.place(x=150, y=240)

	labelCap = Label(root, text="Capsize of error-bar")
	labelCap.place(x=150, y=270)

	entryCap = Entry(root, width=3)
	entryCap.insert(END, "5")
	entryCap.place(x=300, y=270)

	labelXR = Label(root, text="X-ticks\' rotation")
	labelXR.place(x=150, y=300)
	entryXR = Entry(root, width=3)
	entryXR.insert(END, "0")
	entryXR.place(x=300, y=300)

	"""グラフ描画"""
	flagS = BooleanVar()
	flagS.set(False)
	checkS = Checkbutton(root, text="Save Figure", variable=flagS)
	checkS.place(relx=0.5, y=400, anchor=CENTER)

	button = Button(root, text="Drawing Graph", command=__main)
	button.place(relx=0.5, y=450, anchor=CENTER)

	buttonE = Button(root, text="Exit", command=exit)
	buttonE.place(relx=0.5, y=480, anchor=CENTER)


	root.mainloop()

	exit()


