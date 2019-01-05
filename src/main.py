from tkinter import *
from tkinter import ttk
import tkinter.simpledialog
import json
import io
import base64
from datetime import *



def iso_to_gregorian(iso_year, iso_week, iso_day):
	def iso_year_start(iso_year):
		fourth_jan = date(iso_year, 1, 4)
		delta = timedelta(fourth_jan.isoweekday()-1)
		return fourth_jan - delta 
	year_start = iso_year_start(iso_year)
	return year_start + timedelta(days=iso_day-1, weeks=iso_week-1)

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
		this.cat=['default']
		this.item={}
		this.totalMoney=0.0
		this.money = []
		this.receipts = []
		try:this.load()
		except:this.create()
	
	def load(this):
		with open(dataFileName) as data_file:
			this._data = json.load(data_file)
		this.user = this._data['user']
		this.cat = this._data['cat']
		this.item = this._data['item']
		this.money = this._data['money']
		this.totalMoney = this._data['totalMoney']
		this.receipts = this._data['receipts']
		
	def getItems(this,cat):
		return {k:v for k,v in this.item.items() if v['cat'] == cat}
		
	def getItemsForDD(this,cat):
		return [str(v['price']) +' - '+str(v['unit']) + ' ' + str(v['qty']) + ' - ' + name for name,v in this.getItems(cat).items()]
		
	def prepareData(this):
		global currReceipt
		if currReceipt: 
			this.receipts.append(currReceipt)
			currReceipt = {}
		this._data = {'user':this.user, 'cat':this.cat, 'item':this.item,'totalMoney':this.totalMoney, 'money':this.money, 'receipts':this.receipts}
		
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
		if len(cat)<2 or cat in data.cat : return
		data.cat.append(cat)
		data.save() 
		fillNewItemCatOm()
		fillAddToInvCatOm()
		log.set('Category added')
		
	def addItemAction():
		cat = catDd.get()
		name = itemName.get()
		price = itemPrice.get()
		qty = itemQty.get()
		unit = unitDd.get()
		if len(name)<2 or name in data.item : return
		data.item[name] ={
			'cat':cat,
			'price':price,
			'qty':qty,
			'unit':unit
		}
		data.save() 
		fillItemsTree()
		fillItemsOm()
		log.set('Item added')
		
	win = Toplevel()
	win.title(text['inventoryWinTitle'])
	win.protocol("WM_DELETE_WINDOW", showMainView)
	Label(win, textvariable=log).pack(anchor=N)
	f = Frame(win,width=800, height=500)
	f.pack(expand=True, fill='both')
	f.pack_propagate(0)
	f.pack()
	topFrame = Frame(f)
	topFrame.pack(expand=True, fill=X)

	topFrame.pack(anchor=NW)
	hud = Frame(topFrame, height=40)
	hud.pack(expand=True, fill=X,side=TOP)
	hud.pack_propagate(0)
	Button(hud,text=text['goBackBtn'],command=showMainView).pack(side=RIGHT, expand=True,fill=X)
	
	Label(hud,textvariable=totalMoneyLabelVar).pack(side=LEFT, expand=True,fill=X)
	
	#Add Category
	addCatFrame = Frame(topFrame, height=40)
	addCatFrame.pack(expand=True, fill=X,side=TOP)
	addCatFrame.pack_propagate(0)
	catName = StringVar()
	Entry(addCatFrame,textvariable=catName,width=15).pack(side=LEFT,fill=Y)
	Button(addCatFrame,text=text['addCatBtn'],command=addCatAction,width=15).pack(side=RIGHT,fill=Y)

	#Add Item
	def fillNewItemCatOm():
		newItemCatOm['menu'].delete(0,'end')
		cats = data.cat
		for c in cats:newItemCatOm['menu'].add_command(label=c,command=lambda x=c:catDd.set(x))
	
	addItemFrame = Frame(topFrame, height=40)
	addItemFrame.pack(expand=True, fill=X,side=TOP)
	addItemFrame.pack_propagate(0)
	
	catDd = StringVar()
	try:catDd.set(data.cat[0])
	except:catDd.set('N/A')
	newItemCatOm = OptionMenu(addItemFrame, catDd, *data.cat)
	newItemCatOm.pack(side=LEFT,fill=Y)
	newItemCatOm.config(width=10)
	fillNewItemCatOm()
	
	itemName = StringVar()
	Entry(addItemFrame,textvariable=itemName,width=25).pack(side=LEFT,fill=Y)
	itemPrice = DoubleVar()
	itemPrice.set(1)
	Entry(addItemFrame,textvariable=itemPrice,width=4).pack(side=LEFT,fill=Y)
	itemQty = IntVar()
	itemQty.set(1)
	Entry(addItemFrame,textvariable=itemQty,width=4).pack(side=LEFT,fill=Y)
	unitDd = StringVar()
	unitDd.set(unit[0])
	unitOm = OptionMenu(addItemFrame, unitDd, *unit)
	unitOm.pack(side=LEFT,fill=Y)
	unitOm.config(width=3)
	Button(addItemFrame,text=text['addItemBtn'],command=addItemAction,width=15).pack(side=RIGHT,fill=Y)
	
	#Add to inventory
	def fillItemsOm(cat=None):
		if cat == None: cat= addToInvCatOmVar.get();
		itemsOm['menu'].delete(0,'end')
		items = data.getItemsForDD(cat)
		itemDd.set(items[0] if len(items) else '')
		for i in items:itemsOm['menu'].add_command(label=i,command=lambda x=i:itemDd.set(x))
	def addItemToInvAction():
		cat = addToInvCatOmVar.get()
		name = itemDd.get()
		name = name[name.rfind('-')+2:]
		qty = itemQtyForItem.get()
		data.item[name]['qty'] += qty
		data.save() 
		fillItemsTree()
		log.set('Item updated')
	def catCommand(x):
			addToInvCatOmVar.set(x)
			fillItemsOm(x)
	def fillAddToInvCatOm():
		addToInvCatOm['menu'].delete(0,'end')
		cats = data.cat
		for c in cats:addToInvCatOm['menu'].add_command(label=c,command=lambda x=c:catCommand(x))
	addToInveFrame = Frame(topFrame, height=40)
	addToInveFrame.pack(expand=True, fill=X,side=TOP)
	addToInveFrame.pack_propagate(0)
	addToInvCatOmVar = StringVar()
	addToInvCatOmVar.set(data.cat[0])
	addToInvCatOm = OptionMenu(addToInveFrame, addToInvCatOmVar, *data.cat,command=fillItemsOm)
	addToInvCatOm.pack(side=LEFT,fill=Y)
	addToInvCatOm.config(width=10)
	fillAddToInvCatOm()
	itemDd = StringVar()
	itemsOm = OptionMenu(addToInveFrame, itemDd, '')
	itemsOm.pack(side=LEFT,fill=Y)
	itemsOm.config(width=20)
	fillItemsOm(addToInvCatOmVar.get())
	itemQtyForItem = IntVar()
	itemQtyForItem.set(1)
	Entry(addToInveFrame,textvariable=itemQtyForItem,width=4).pack(side=LEFT,fill=Y)
	Button(addToInveFrame,text=text['addItemToInvBtn'],command=addItemToInvAction,width=15).pack(side=RIGHT,fill=Y)
	
	#View inventory
	invTree = ttk.Treeview(f,selectmode='browse',height=50)
	invTree["columns"]=("name","price","qty","unit")
	invTree.column("#0", width=100)
	invTree.column("name", width=400)
	invTree.column("price", width=80)
	invTree.column("qty", width=80)
	invTree.column("unit", width=80)
	invTree.heading("#0", text=text['catHeading'])
	invTree.heading("name", text=text['nameHeading'])
	invTree.heading("price", text=text['priceHeading'])
	invTree.heading("qty", text=text['qtyHeading'])
	invTree.heading("unit", text=text['unitHeading'])
	
	def fillItemsTree():
		invTree.delete(*invTree.get_children())
		for i in data.cat:
			items = data.getItems(i)
			if not items: continue
			catId = invTree.insert("" , 'end', text=i, values=('','',str(len(items)) ,''))
			for k,v in items.items():
				if v['qty'] < 10:
					invTree.insert(catId, "end", values=(k,v['price'],v['qty'],v['unit']),tags=('item','low'))
					invTree.item(catId, tags="low	")
				else:
					invTree.insert(catId, "end", values=(k,v['price'],v['qty'],v['unit']),tags=('item'))
	fillItemsTree()
	invTree.tag_configure('low', background='red')
	#tree.tag_bind('item','<1>',changeLog)
	invTree.pack(expand=True,fill='both')
	return win

def showInventoryView():
	inventoryWindow.deiconify()
	inventoryWindow.grab_set()
	
def showMainView():
	root.grab_set()
	updateMainView()
	inventoryWindow.withdraw()
	
def drawMainView():
	Label(root, textvariable=log).pack(side=TOP,anchor=N)
	Button(root, text=text['inventoryBtn'], command=showInventoryView).pack(side=TOP,fill=X,anchor=N)
	
	def fillAddRecItemsOm(cat=None):
		if cat == None: cat= addRecCatOmVar.get();
		addRecItemOm['menu'].delete(0,'end')
		items = data.getItemsForDD(cat)
		addRecItemOmVar.set(items[0] if len(items) else '')
		for i in items:addRecItemOm['menu'].add_command(label=i,command=lambda x=i:addRecItemOmVar.set(x))
	
	def catCommand(x):
		addRecCatOmVar.set(x)
		fillAddRecItemsOm(x)
			
	def fillAddRecCatOm():
		addRecCatOm['menu'].delete(0,'end')
		cats = data.cat
		for c in cats:addRecCatOm['menu'].add_command(label=c,command=lambda x=c:catCommand(x))
		
	global updateMainView
	def localUpdateMainView():
		fillAddRecCatOm()
		fillAddRecItemsOm()
	updateMainView = localUpdateMainView
	
	def addItemRecAction():
		qty = addRecQtyVar.get()
		name = addRecItemOmVar.get()
		name = name[name.rfind('-')+2:]
		item = data.item[name]
		availableQty = item['qty']
		if name in currReceipt.keys():
			if currReceipt[name]['qty']+qty>availableQty:return
			currReceipt[name]['qty']+=qty
		else:
			if qty > availableQty:return
			newItem = dict(item)
			newItem['qty']=qty
			currReceipt[name]=newItem
		try:currReceipt['totalMoney']+= qty * item['price']
		except:currReceipt['totalMoney']= qty * item['price']
		recTotalLabelVar.set(currReceipt['totalMoney'])
		fillReceiptItemsTree()
		log.set('Item updated')
		
	def clearRecAction():
		global currReceipt
		currReceipt={}
		recTotalLabelVar.set(0.0)
		fillReceiptItemsTree()
		
	def confirmRecAction():
		for k,v in currReceipt.items():
			if k == 'totalMoney':continue
			data.item[k]['qty']-=v['qty']
		data.money.append(recTotalLabelVar.get())
		data.totalMoney+=recTotalLabelVar.get()
		data.save()
		updateTotalMoneyLabel()
		clearRecAction()
		
	addRecFrame = Frame(root, height=40)
	addRecFrame.pack(expand=True, fill=X)
	addRecFrame.pack_propagate(0)
	
	addRecCatOmVar = StringVar()
	addRecCatOmVar.set(data.cat[0])
	addRecCatOm = OptionMenu(addRecFrame, addRecCatOmVar, *data.cat,command=fillAddRecItemsOm)
	addRecCatOm.pack(side=LEFT,fill=Y)
	addRecCatOm.config(width=10)
	fillAddRecCatOm()
	
	addRecItemOmVar = StringVar()
	addRecItemOm = OptionMenu(addRecFrame, addRecItemOmVar, '')
	addRecItemOm.pack(side=LEFT,fill=Y)
	addRecItemOm.config(width=35)
	fillAddRecItemsOm(addRecCatOmVar.get())
	
	addRecQtyVar = IntVar()
	addRecQtyVar.set(1)
	Entry(addRecFrame,textvariable=addRecQtyVar,width=4).pack(side=LEFT,fill=Y)
	
	Button(addRecFrame,text=text['addItemRecBtn'],command=addItemRecAction,width=15).pack(side=RIGHT,fill=Y)
	
	recOpsFrame = Frame(root, height=40)
	recOpsFrame.pack(expand=True, fill=X)
	recOpsFrame.pack_propagate(0)
	
	recTotalLabelVar = DoubleVar()
	recTotalLabelVar.set(0.0)
	Label(recOpsFrame,textvariable=recTotalLabelVar,width=15).pack(side=LEFT,fill=Y)
	
	Button(recOpsFrame,text=text['confirmRecBtn'],command=confirmRecAction,width=25).pack(side=LEFT,fill=Y)
	
	Button(recOpsFrame,text=text['clearRecBtn'],command=clearRecAction,width=15).pack(side=RIGHT,fill=Y)
	
	recTree = ttk.Treeview(root,selectmode='browse',height=50)
	recTree["columns"]=("name","price","qty","unit")
	recTree.column("#0", width=0)
	recTree.column("name", width=400)
	recTree.column("price", width=80)
	recTree.column("qty", width=80)
	recTree.column("unit", width=80)

	recTree.heading("name", text=text['nameHeading'])
	recTree.heading("price", text=text['priceHeading'])
	recTree.heading("qty", text=text['qtyHeading'])
	recTree.heading("unit", text=text['unitHeading'])
	
	def fillReceiptItemsTree():
		recTree.delete(*recTree.get_children())
		for k,v in currReceipt.items():
				if k=='totalMoney':continue
				recTree.insert('', "end", values=(k,v['price'],v['qty'],v['unit']),tags=('receiptItem'))
		
	fillReceiptItemsTree()
	#tree.tag_bind('receiptItem','<1>',changeLog)
	recTree.pack(expand=True,fill='both',side=BOTTOM,anchor=S)
	

def changeLog(event):
	item = tree.identify('item',event.x,event.y)
	log.set(item)
	
	
try:to_unicode = unicode
except NameError:to_unicode = str
'''
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
'addItemToInvBtn':'Add to inventory',
'catHeading':'Cat',
'nameHeading':'Name',
'priceHeading':'Unit price',
'qtyHeading':'Quantity',
'unitHeading':'Unit type',
'addItemRecBtn':'Add to receipt',
'clearRecBtn':'Clear',
'confirmRecBtn':'Confirm',
'rootTitle':'CashierApp'
}
'''
text={
"name":"اسم المستخدم",
'password':'كلمة المرور',
'loginBtn':'تسجيل الدخول',
'registerBtn':'إنشاء حساب جديد',
'loginTitle':'تسجيل الدخول',
'masterPassTitle': 'كلمة المرور الرئيسيه',
'masterPassPrompt':'ادخل كلمة المرور الرئيسيه',
'inventoryBtn':'اعرض المخزن',
'inventoryWinTitle':'المخزن',
'goBackBtn':'اغلق المخزن',
'addCatBtn':'مجموعه جديده',
'addItemBtn':'صنف جديد',
'piece':'قطعه',
'liter':'لتر',
'addItemToInvBtn':'اضف للمخزن',
'catHeading':'مجموع',
'nameHeading':'صنف',
'priceHeading':'سعر الوحده',
'qtyHeading':'الكميه',
'unitHeading':'الوحده',
'addItemRecBtn':'اضف للفاتوره',
'clearRecBtn':'امسح الفاتوره',
'confirmRecBtn':'تاكيد الفاتوره',
'rootTitle':'برنامج الكاشير'
}

unit=[
text['piece'],
text['liter']
]
masterPassword = '12349876'
dataFileName = 'data.json'

IN_DEVELOPMENT = True
	
data = Data()
currReceipt={}
root = Tk()
root.title(text['rootTitle'])
w = 800
h = 650
ws = root.winfo_screenwidth() 
hs = root.winfo_screenheight()
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

log = StringVar()
log.set('LOG')

loginName = StringVar()
loginPass = StringVar()

def updateTotalMoneyLabel():
	totalMoneyLabelVar.set(data.totalMoney)
	
totalMoneyLabelVar = DoubleVar()
updateTotalMoneyLabel()

loginWindow = drawLoginView()
inventoryWindow = drawInventoryView()

updateMainView = None

root.withdraw()
inventoryWindow.withdraw()
if IN_DEVELOPMENT:
	loginWindow.destroy()
	User('ahmed','123456')
	User.cur.login()
	root.deiconify()
	drawMainView()
	root.mainloop()
else:
	root.wait_window(loginWindow)
	if User.auth:
		root.deiconify()
		drawMainView()
		root.mainloop()

