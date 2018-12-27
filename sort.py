# coding: utf-8

import tkinter
from tkinter import Tk, Button, filedialog, Entry, Label, END, messagebox

import numpy as np
import pandas as pd
from glob import glob
import subprocess
from os.path import splitext

"""
***How To Use***

Choose target directoryを押して，読み込み対象CSVの入ったディレクトリを選択
CONVERTを押して変換→変換後のファイルはChoote target directoryで選択したディレクトリに保存

読み込み対象CSVの名前は英数字に直しておくのが良い
日本語が混じってると，読み込めないor読み込みに時間がかかる，可能性がある

読み込み対象CSVはA列から順番に「タイムスタンプ」→「被験者ID」→「回答」となっている想定
ただし，Subject's IDのチェックを外せば，「タイムスタンプ」→「回答」となっていても良い	

条件数（読み込み対象CSVの数）が10を超える場合，CSVの名前に入っている数字は「01」「02」とかにしておくとよい
しなかった場合，順番が狂う可能性がある
"""

def main(dir_name) :
	if dir_name[-1] != "/" :
		dir_name += "/"
		target = dir_name + "*.csv"
	filenames = glob(target)
	if filenames == [] :
		raise FileNotFoundError

	try :			# csvファイルを読み込む前にUTF-8に変換する（要nkf）
		for filename in filenames :
			subprocess.run(["nkf", "-w", "--overwrite", filename])
		messagebox.showinfo("Information", "all csv-files are converted to UTF-8 by nkf.")
	except FileNotFoundError :
		pass		# nkfが入ってなかったら実行しない

	try :
		df = pd.read_csv(filenames[0])
	except OSError:		# ファイル名に日本語が入ってる時にこのエラーが出ることがある
		# 解決策の1つが，engin="python"とすること（defaultは"c"）．ただし，大容量ファイルの場合に遅くなる
		df = pd.read_csv(filenames[0], engine="python")
	quesN = df.values.shape[1] - 2		# 自由記述を含む質問項目数

	H = ["condition"+str(i+1) for i in range(len(filenames))]		# pandas.DataFrameで書き出しするときのheader

	outnames = ""
	for i in range(quesN) :
		for x, filename in enumerate(filenames) :
			try :
				df = pd.read_csv(filename)
			except OSError:
				df = pd.read_csv(filename, engine="python")
			csv = df.values

			if bln1.get() :
				data = np.array([csv[:, i+2]])
			else :
				data = np.array([csv[:, i+1]])

			if x == 0 :
				out = data
			else :
				out = np.append(out, data, axis=0)

		out = out.T

		# 森下: MOS変換
		"""
		answers = ["全くそう思わない", "あまりそう思わない", "どちらでもない", "ややそう思う", "非常にそう思う"]
		for x2, answer in enumerate(answers) :
			out = np.where(out==answer, x2+1, out)
		"""

		outname = dir_name + "Q" + str(i+1) + ".csv"
		outnames += outname + "\n"

		if bln1.get() :
			ID = np.array([csv[:, 1]]).T
		else :
			ID = range(1, out.shape[0]+1)

		df_out = pd.DataFrame(out.astype(np.str), index=ID, columns=H)
		df_out.to_csv(outname)

	return outnames, quesN

def __get_dir_name() : # 変換対象CSVの入ったディレクトリ名を取得する
	dir_name = dir_name = filedialog.askdirectory(title="Choose target directory", initialdir=".")
	if dir_name!="" :
		entry1.delete(0, END)
		entry1.insert(END, dir_name)
	return 1

def __main() :
	dir_name = entry1.get()
	if dir_name=="" :
		messagebox.showwarning("Error", "\"Target directory\" is not defined.")
		return 0

	try :
		rslt, N = main(dir_name)
		messagebox.showinfo("Information", "The process is done\nNumber of questions is %d\n\n%s" %(N, rslt[:-1]))
	except FileNotFoundError :
		messagebox.showwarning("Error", "Your choosen directory does not have any csv-files.")

	return 1
		

if __name__ == "__main__" :
	try :
		X, Y = 500, 200

		root = Tk()
		root.title("Convert CSV")
		root.geometry("%dx%d" %(X, Y))


		label1 = Label(root, text="Target directory")
		label1.place(x=10, y=10)


		entry1 = Entry(root, width=20)
		entry1.place(x=10, y=30)

		button1 = Button(root, text="Choose target directory", command=__get_dir_name)
		button1.place(x=210, y=30)


		bln1 = tkinter.BooleanVar()			# 被験者IDが入っているかどうか（defatul: True）
		bln1.set(True)
		check1 = tkinter.Checkbutton(root, variable=bln1, text="Subjects\' ID")
		check1.place(x=10, y=60)

		button3 = Button(root, text="CONVERT", width=20, command=__main)
		button3.place(relx=0.5, y=100, anchor=tkinter.CENTER)


		button0 = Button(root, text="Exit", command=exit)
		button0.place(relx=0.5, y=150, anchor=tkinter.CENTER)

		root.mainloop()

		exit("done")
	except KeyboardInterrupt :
		exit("done")