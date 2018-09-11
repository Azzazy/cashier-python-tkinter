from tkinter import *
from tkinter import ttk
import tkinter.simpledialog
import json
import io
import base64

def checkMasterPassword():
	answer = tkinter.simpledialog.askstring(title=text['masterPassTitle'], prompt=text['masterPassPrompt'],show='*')
	if answer != masterPassword: 
		log.set('Master mismatch')
		return False
	return True

class Data:
	def __init__(this):
		this._data=None
		this.user={}
		this.cat=[]
		this.item={}
		try:this.load()
		except:this.create()
	
	def load(this):
		with open(dataFileName) as data_file:
			this._data = json.load(data_file)
		this.user = this._data['user']
		this.cat = this._data['cat']
		this.item = this._data['item']
		
	def getItems(this,cat):
		return {k:v for k,v in this.item.items() if v['cat'] == cat}
		
	def getItemsForDD(this,cat):
		return ['' + k + ' - ' + str(v['unit'])  for k,v in this.getItems(cat).items()]
		
	def prepareData(this):
		this._data = {'user':this.user, 'cat':this.cat, 'item':this.item}
		
	def create(this):
		this.prepareData()
		this.save()
		
	def save(this):
		this.prepareData()
		with io.open(dataFileName, 'w', encoding='utf8') as outfile:
			str_ = json.dumps(this._data,
							indent=4, sort_keys=True,
							separators=(',', ': '), ensure_ascii=False)
			outfile.write(to_unicode(str_))
	
class User:
	cur = None
	auth = False
	def __init__(this, raw_name, raw_password):
		this.raw_name = raw_name
		this.raw_password = raw_password
		User.cur = this
		
	def login(this):
		if len(this.raw_name) < 3 or len(this.raw_password) < 6:return
		this.name = encode(this.raw_name)
		this.password = encode(this.raw_password)
		if this.name in data.user and data.user[this.name] == this.password: 	
			User.auth = True
			loginWindow.destroy()
				
	def register(this):
		if len(this.raw_name) < 3 or len(this.raw_password) < 6:return
		this.name = encode(this.raw_name)
		this.password = encode(this.raw_password)
		if checkMasterPassword() and this.name not in data.user:
			data.user[this.name] = this.password
			data.save()

def encode(s):
	return base64.b64encode(bytes(s,'utf-8')).decode('utf-8')
	
def decode(s):
	return base64.b64decode(s)
	
def loginAction():
	User(loginName.get(),loginPass.get())
	User.cur.login()
	
def registerAction():
	User(loginName.get(),loginPass.get())
	User.cur.register()
	
def drawLoginView():
	win = Toplevel()
	win.title(text['loginTitle'])
	win.grab_set()
	nameInput = Entry(win, textvariable=loginName)
	nameInput.grid(row=1,column=1)
	nameInput.focus_set()
	Entry(win,show="*", textvariable=loginPass).grid(row=2,column=1)
	Label(win, text=text['name']).grid(row=1)
	Label(win, text=text['password']).grid(row=2)
	Label(win, textvariable=log).grid(columnspan=2)
	Button(win, text=text['loginBtn'],width=25, command=loginAction).grid(columnspan=2)
	Button(win, text=text['registerBtn'],width=25, command=registerAction).grid(columnspan=2)
	return win
	
def drawInventoryView():
	def addCatAction():
		cat = catName.get()
		if len(cat)<5 or cat in data.cat : return
		data.cat.append(cat)
		data.save() 
		log.set('Category added')
		
	def addItemAction():
		cat = catDd.get()
		name = itemName.get()
		price = itemPrice.get()
		qty = itemQty.get()
		unit = unitDd.get()
		if len(name)<5 or name in data.item : return
		data.item[name] ={
			'cat':cat,
			'price':price,
			'qty':qty,
			'unit':unit
		}
		data.save() 
		log.set('Item added')
		
	win = Toplevel()
	win.title(text['inventoryWinTitle'])
	win.protocol("WM_DELETE_WINDOW", showMainView)
	Label(win, textvariable=log).pack(anchor=N)
	f = Frame(win,width=1500, height=460)
	f.pack(expand=True, fill='both')
	f.pack_propagate(0)
	f.pack()
	topFrame = Frame(f, height=40)
	topFrame.pack(expand=True, fill=X)
	topFrame.pack_propagate(0)
	topFrame.pack(anchor=NW)
	Button(topFrame,text=text['goBackBtn'],command=showMainView).pack(side=LEFT,fill=Y)
	
	#Add Category
	addCatFrame = Frame(topFrame)
	addCatFrame.pack(expand=True, fill=Y,side=LEFT)
	catName = StringVar()
	Entry(addCatFrame,textvariable=catName).pack(side=LEFT,fill=Y)
	Button(addCatFrame,text=text['addCatBtn'],command=addCatAction).pack(side=LEFT,fill=Y)

	#Add Item
	addItemFrame = Frame(topFrame)
	addItemFrame.pack(expand=True, fill=Y,side=LEFT)
	catDd = StringVar()
	catDd.set(data.cat[0])
	OptionMenu(addItemFrame, catDd, *data.cat).pack(side=LEFT,fill=Y)
	itemName = StringVar()
	Entry(addItemFrame,textvariable=itemName).pack(side=LEFT,fill=Y)
	itemPrice = DoubleVar()
	itemPrice.set(1)
	Entry(addItemFrame,textvariable=itemPrice,width=5).pack(side=LEFT,fill=Y)
	itemQty = IntVar()
	itemQty.set(1)
	Entry(addItemFrame,textvariable=itemQty,width=5).pack(side=LEFT,fill=Y)
	unitDd = StringVar()
	unitDd.set(unit[0])
	OptionMenu(addItemFrame, unitDd, *unit).pack(side=LEFT,fill=Y)
	Button(addItemFrame,text=text['addItemBtn'],command=addItemAction).pack(side=LEFT,fill=Y)
	
	#Add to inventory
	def updateItems(cat):
		itemsOm['menu'].delete(0,'end')
		items = data.getItemsForDD(cat)
		itemDd.set(items[0] if len(items) else '')
		for i in items:itemsOm['menu'].add_command(label=i,command=lambda x=i:itemDd.set(x))
	addToInveFrame = Frame(topFrame)
	addToInveFrame.pack(expand=True, fill=Y,side=LEFT)
	catDdForItem = StringVar()
	catDdForItem.set(data.cat[0])
	catOm = OptionMenu(addToInveFrame, catDdForItem, *data.cat,command=updateItems)
	catOm.grid(row=0,column=0,sticky=NSEW)
	catOm.config(width=10)
	itemDd = StringVar()
	itemsOm = OptionMenu(addToInveFrame, itemDd, '')
	itemsOm.config(width=20)
	itemsOm.grid(row=0,column=1,sticky=NSEW)
	updateItems(catDdForItem.get())
	itemQtyForItem = IntVar()
	itemQtyForItem.set(1)
	Entry(addToInveFrame,textvariable=itemQtyForItem,width=5).grid(row=0,column=2,sticky=NSEW)
	def addItemToInvAction():
		cat = catDdForItem.get()
		name = itemDd.get()
		name = name[:name.rfind('-')-1]
		qty = itemQtyForItem.get()
		data.item[name]['qty'] += qty
		data.save() 
		log.set('Item updated')
	Button(addToInveFrame,text=text['addItemToInvBtn'],command=addItemToInvAction).grid(row=0,column=3,sticky=NSEW)
	return win

def showInventoryView():
	inventoryWindow.deiconify()
	inventoryWindow.grab_set()
	
def showMainView():
	root.grab_set()
	inventoryWindow.withdraw()
	
def drawMainView():
	l = Label(f, text="Welcome to the main view").pack()
	
	Button(f, text=text['inventoryBtn'], command=showInventoryView).pack()
	tree["columns"]=("one","two")
	tree.column("#0", width=0)
	tree.column("one", width=100 )
	tree.column("two", width=100)
	tree.heading("one", text="coulmn A")
	tree.heading("two", text="column B")
	tree.insert("" , 0, values=("1A","1b"))
	
	id2 = tree.insert("", 1, "dir2")
	tree.insert(id2, "end", "dir 2", values=("2A","2B"),tags=('item'))

	tree.insert("", 3, "dir3")
	tree.insert("dir3", 3,values=("3A"," 3B"))
	tree.tag_bind('item','<1>',changeLog)
	tree.pack()

def changeLog(event):
	item = tree.identify('item',event.x,event.y)
	log.set(item)
	
	
try:to_unicode = unicode
except NameError:to_unicode = str
	
text={
"name":"Name",
'password':'Password',
'loginBtn':'Login',
'registerBtn':'New Account',
'loginTitle':'Login',
'masterPassTitle': 'Master Password',
'masterPassPrompt':'Please enter the Master Password',
'inventoryBtn':'Inventory',
'inventoryWinTitle':'Inventory',
'goBackBtn':'Back to Main',
'addCatBtn':'Add new Category',
'addCatTitle':'Add new Category',
'addCatPrompt':'What is the Category name?',
'addItemBtn':'Add new Item',
'piece':'piece',
'liter':'liter',
'addItemToInvBtn':'Add to inventory'
}

unit=[
text['piece'],
text['liter']
]
masterPassword = '12345678'
dataFileName = 'data.json'

IN_DEVELOPMENT = True
	
data = Data()
root = Tk()
log = StringVar()
log.set('LOG')
Label(root, textvariable=log).pack()
Button(root,text="The best button ever").pack()
loginName = StringVar()
loginPass = StringVar()

loginWindow = drawLoginView()
inventoryWindow = drawInventoryView()

root.withdraw()
inventoryWindow.withdraw()
if IN_DEVELOPMENT:
	loginWindow.destroy()
	User('ahmed','123456')
	User.cur.login()
	root.deiconify()
	f = Frame(root, width=500, height=500).pack()
	tree = ttk.Treeview(f,selectmode='browse')
	drawMainView()
	showInventoryView()
	root.mainloop()
else:
	root.wait_window(loginWindow)
	if User.auth:
		root.deiconify()
		f = Frame(root, width=500, height=500).pack()
		tree = ttk.Treeview(f,selectmode='browse')
		drawMainView()
		root.mainloop()

