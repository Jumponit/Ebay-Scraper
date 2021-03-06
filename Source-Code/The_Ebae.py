# The_Ebae.py
# The main program
# Taylor Morris & Nich Phillips & Lindsey Titus

from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
from datetime import date, timedelta, datetime
from collections import Counter
import numpy as np #requires a separate pip install
import matplotlib as mpl # requires a separate pip install
mpl.use('Tkagg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import FileDialog
import time
import socket
import Tkinter
from Tkinter import *
from PIL import ImageTk, Image

results_Text = ''
mean_Text = ''
med_Text = ''
startPoint_Text = ''
endPoint_Text = ''
change_Text = ''
quality_Text = ''
category_List = []
category_Lookup = {}
prev_cat_item = ''
USAGE_Item_Name = "ITEM NAME: this is where you will type in the name of the item you want to search for\n"
USAGE_Category = "CATEGORY: this is where categories for your item will be displayed, ordered by most frequent to " +\
                 "least frequent.\n\tClick on a category to select it for use in your search.\n\t" +\
                 "If no category is selected, results will come from all categories.\n"
USAGE_Results = "RESULTS: number of results found is displayed above the search buttons when a search finishes\n"
USAGE_Mean = "MEAN PRICE: this is the mean price of the results\n"
USAGE_Median = "MEDIAN PRICE: this is the median price of the results\n"
USAGE_Start = "START POINT: this is the start price of the line of best fit on the scatter plot of data\n"
USAGE_End = "END POINT: this is the end price of the line of best fit on the scatter plot of data\n"
USAGE_Change = "CHANGE IN AVERAGE PRICE: this is the difference between start point and end point\n"
USAGE_Confidence = "CONFIDENCE OF LINE: this is a rating of confidence of line from very weak to very strong\n"
USAGE_GetCat = "GET CATEGORIES: click this button to generate a list of categories to search\n"
USAGE_Search = "SEARCH: click this button to search ebay and get results"
USAGE_Text = "USAGE FOR Ebay PRICE CHECKER:\n" + USAGE_Results + USAGE_Mean + USAGE_Median + USAGE_Start +\
             USAGE_End + USAGE_Change + USAGE_Confidence + USAGE_GetCat + USAGE_Search


# The function that searches via the Ebay API
# Function :    search
# Description : function to make call to Ebay Finding API with a search request and return the dictionary
#               returned by the API
# Params :      itemInfo - list of specified item info to use in search
#               pageNum - int number of pages to search through
# Returns :     response - dictionary of results from Ebay Finding API
def search(itemInfo, pageNum):
    category = itemInfo[2]
    startDate = itemInfo[1]
    item = itemInfo[0]
    try:
        api = Finding(appid = "TaylorMo-1104-4ca1-bc59-34b44b585cf0", config_file = None)
        if category != None:
            api_request = {
                'keywords': item,
                'categoryId': [category],
                'itemFilter': [
                    {'name': 'SoldItemsOnly', 'value': True},
                    {'name': 'LocatedIn', 'value': 'US'},
                    {'name': 'EndTimeFrom', 'value': startDate}
                ],
                'paginationInput': [
                    {'pageNumber': pageNum}
                ]
            }
        else:
            api_request = {
                'keywords': item,
                'itemFilter': [
                    {'name': 'SoldItemsOnly', 'value': True},
                    {'name': 'LocatedIn', 'value': 'US'},
                    {'name': 'EndTimeFrom', 'value': startDate}
                ],
                'paginationInput': [
                    {'pageNumber': pageNum}
                ]
            }
        response = api.execute('findCompletedItems', api_request)
        return response.dict()
    except ConnectionError as e:
        print(e)
        print(e.response.dict())


# The method to parse the search response dictionary
# Function :    parseDict
# Description : function to parse through a dictionary returned from the Finding API and create a dictionary of
#               desired information
# Params :      dit - dictionary to parse
# Returns :     dataDict - dictionary of desired information obtained from parameter dictionary
def parseDict(dit):
    soldPrices = []
    sellDates = []
    results = dit.get('searchResult')
    itemList = results.get('item')
    if (itemList != None):
        for item in itemList:
            shipInfo = item.get('shippingInfo')
            if (type(shipInfo) == dict):
                shipServCost = shipInfo.get('shippingServiceCost')
                if (type(shipServCost) == dict):
                    shipCost = shipServCost.get('value')
                    shipping = float(shipCost)
                    sellStat = item.get('sellingStatus')
                    if (type(sellStat) == dict):
                        currentPrice = sellStat.get('convertedCurrentPrice')
                        if (type(currentPrice) == dict):
                            listInfo = item.get('listingInfo')
                            if (type(listInfo) == dict):
                                fullTime = listInfo.get('endTime')
                                times = fullTime.split('T')
                                aTime = times[0]
                                sellTime = datetime.strptime(aTime, "%Y-%m-%d")
                                sellDates.append(sellTime)
                            else:
                                continue
                            priceVal = currentPrice.get('value')
                            soldAmount = float(priceVal)
                            soldPrices.append((shipping + soldAmount))
                        else:
                            continue
                    else:
                        continue
                else:
                    continue
            else:
                continue

        dataDict = dict([('soldPrices', soldPrices), ('sellDates', sellDates)])
        return dataDict
    else:
        print "Error, invalid item name, no results"


# Function :    extendDict
# Description : function to extend a dictionary with information from a second dictionary
# Params :      dict1 - dictionary to be extended
#               dict2 - dictionary to get information from to add to the first dictionary
# Returns :     dict1 - dict1 parameter appended with information from dict2
def extendDict(dict1, dict2):
    keys = dict1.keys()
    for key in keys:
        dict1[key].extend(dict2[key])
    return dict1


# Function :    createDataDict
# Description : function to create a dictionary of search results with sell price and sell date
# Params :      itemInfo - list of item info used in search
# Returns :     data - dictionary of all search results with only useful information
def createDataDict(itemInfo):
    page = 1
    response = search(itemInfo, page)
    pageOutput = response.get('paginationOutput')
    pageNumbers = pageOutput.get('totalPages')
    if (int(pageNumbers) > 1):
        data = parseDict(response)
        page+= 1
        while page <= int(pageNumbers) and page < 100:
            print "Nap Time! Number: %s" % (page-1)
            time.sleep(3)
            try:
                data = extendDict(data, parseDict(search(itemInfo, page)))
            except socket.timeout:
                print "Caught a socket timeout! Moving on to next page"
            page+= 1
    else:
        data = parseDict(response)
    return data


# The function to get input from the user
# Function :    acquire
# Description : function to generate list of needed item info for search
# Params :      item_name - name of item
#               item_category - item category to search in
# Returns :     info - list of item info needed for search
def aquire(item_name, item_category):
    info = []
    time.sleep(1)
    name = item_name
    info.append(name)
    pastDate = date.today() - timedelta(days=90)
    datestr = pastDate.strftime('%Y-%m-%d') + 'T00:00:00.000Z'
    info.append(datestr)
    info.append(item_category)
    return info


# Function :    median
# Description : function to find median of list parameter
# Params :      lst - list to find median of
# Returns :     median of parameter lst
def median(lst):
    lst = sorted(lst)
    if len(lst) < 1:
            return None
    if len(lst) %2 == 1:
            return lst[((len(lst)+1)/2)-1]
    else:
            return float(sum(lst[(len(lst)/2)-1:(len(lst)/2)+1]))/2.0



#The function to get the desired category from the user
# Function :    initial_execute
# Description : function to perform initial search for specified item and generate a list of categories found
#               which are stored in global category_List in order of descending frequency
# Params :      item_name - name of item to search for
def initial_execute(item_name):
    global category_List
    global category_Lookup

    pastDate = date.today() - timedelta(days=90)
    datestr = pastDate.strftime('%Y-%m-%d') + 'T00:00:00.000Z'
    try:
        api = Finding(appid = "TaylorMo-1104-4ca1-bc59-34b44b585cf0", config_file = None)
        api_request = {
            'keywords': item_name,
            'itemFilter': [
                {'name': 'SoldItemsOnly', 'value': True},
                {'name': 'LocatedIn', 'value': 'US'},
                {'name': 'EndTimeFrom', 'value': datestr}
            ]
        }
        response = api.execute('findCompletedItems', api_request)
    except ConnectionError as e:
        print(e)

    results = response.dict().get('searchResult')
    itemList = results.get('item')
    catList = []
    if (itemList != None):
        for items in itemList:
            catList.append(items.get('primaryCategory').get('categoryName'))
            category_Lookup[items.get('primaryCategory').get('categoryName')] \
                = items.get('primaryCategory').get('categoryId')

    catDict = Counter(catList)
    category_List = sorted(catDict, key = catDict.__getitem__)
    category_List.reverse()



# Function :    execute
# Description : main function which handles execution of program
# Params :      item_name - name of item to search for
#               item_category - category to search in
def execute(item_name, item_category = None):
    global results_Text
    global mean_Text
    global med_Text
    global startPoint_Text
    global endPoint_Text
    global change_Text
    global quality_Text
    global prev_cat_item

    itemInfo = aquire(item_name, item_category)
    itemData = createDataDict(itemInfo)
    if (itemData is None):
        mean_Text = 'failed'
        return
    priceList = itemData.get('soldPrices')
    priceListLength = len(priceList)
    results_Text = str(priceListLength) + " Results Found"
    if (priceListLength <= 20):
        binNumber = priceListLength
    else:
        binNumber = priceListLength / 10

    mean = sum(priceList)/float(priceListLength)
    mean_Text = "${0:.2f}".format(mean)
    med = median(priceList)
    med_Text = "${0:.2f}".format(med)

    plt.clf()
    fig = plt.figure(1, figsize=(9, 6))  # create a figure object
    fig.suptitle("Scatter Plot and Histogram of %s Price Data Over Past 90 Days" % itemInfo[0])
    ax1 = fig.add_subplot(211)  # add a subplot to the figure object

    x = mpl.dates.date2num(itemData.get('sellDates'))
    y = priceList
    ax1.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m/%d/%y'))
    mpl.dates.DateFormatter("%d/%m/%y")
    plt.plot_date(x, y, 'k.')
    m, b = np.polyfit(x, y, 1)

    endPoint = np.polyval([m, b], x[0])
    startPoint = np.polyval([m, b], x[len(x)-1])

    startPoint_Text = "${0:.2f}".format(startPoint)
    endPoint_Text = "${0:.2f}".format(endPoint)
    if (endPoint < startPoint):
        change_Text = "-${0:.2f}".format(startPoint-endPoint)
    else:
        change_Text = "+${0:.2f}".format(endPoint-startPoint)

    ax1.yaxis.set_ticks_position('both')
    plt.tick_params(axis='both', length='4', width='2', labelright='on', labelleft='on')
    plt.ylabel('Sale Price in USD')
    if (priceListLength < 20):
        quality_Text = "Very Weak"
        plt.plot(x, m * x + b, 'r-', lw='2')
    elif (priceListLength < 50):
        quality_Text = "Weak"
        plt.plot(x, m * x + b, 'm-', lw='2')
    elif (priceListLength < 90):
        quality_Text = "Moderate"
        plt.plot(x, m * x + b, 'y-', lw='2')
    elif (priceListLength < 180):
        quality_Text = "Strong"
        plt.plot(x, m * x + b, 'c-', lw='2')
    else:
        quality_Text = "Very Strong"
        plt.plot(x, m * x + b, 'g-', lw='2')

    plt.subplot(212)
    plt.hist(priceList, bins=binNumber, histtype='step')
    plt.xlabel('Sale Price in USD')
    plt.ylabel('Frequency')
    plt.savefig("fig1.png", bbox_inches = 'tight')


# Function :    GUI
# Description : creates GUI and defines behavior for each button present in GUI
def GUI():
    root = Tkinter.Tk()
    item_entry = Tkinter.StringVar()

    # Function :    irun
    # Description : function connected to Get Categories button to generate categories for the user
    def irun():
        global prev_cat_item

        item_entry = search_Box.get()
        category_Select.delete(0, END)
        if item_entry != '' :
            initial_execute(item_entry)
            for cat in category_List:
                category_Select.insert(END, cat)
            results_Display.config(text = "")
            mean_Display.config(text = "$0.00")
            median_Display.config(text = "$0.00")
            startPoint_Display.config(text = "$0.00")
            endPoint_Display.config(text = "$0.00")
            change_Display.config(text = "$0.00")
            quality_Display.config(text = "")
            canvas.delete("all")
            prev_cat_item = item_entry

    # Function :    run
    # Description : function connected to Search button to search for an item, generate results, and display the results
    def run():
        global category_Lookup

        item_entry = search_Box.get()
        if item_entry != '':
            canvas.delete('all')
            canvas.create_text(250, 100, text='Searching...\nPlease Wait...')
            root.update_idletasks()
            if category_Select.curselection() != None and prev_cat_item == item_entry:
                execute(item_entry, category_Lookup.get(category_Select.get(ACTIVE)))
            else:
                execute(item_entry)
            canvas.delete('all')
            if (str(mean_Text) == 'failed'):
                canvas.background = PhotoImage(file="./SadSponge.gif")
                pic = canvas.create_image(400, 270, image=canvas.background)
                canvas.move(pic, -155, -125)
                canvas.create_text(250, 28, text='Search Failed\nTry Something Else')
                return

            results_Display.config(text=str(results_Text))
            mean_Display.config(text=str(mean_Text))
            median_Display.config(text=str(med_Text))
            startPoint_Display.config(text=str(startPoint_Text))
            endPoint_Display.config(text=str(endPoint_Text))
            change_Display.config(text=str(change_Text))
            quality_Display.config(text=quality_Text)
            graph = Image.open("fig1.png")
            graph = graph.resize((400, 270), Image.ANTIALIAS)
            im = Image.new('RGBA', graph.size, (255, 255, 255))
            im.paste(graph, graph)
            graph = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
            graph.save("fig.gif")
            canvas.background = PhotoImage(file="./fig.gif")
            pic = canvas.create_image(400, 270, image=canvas.background)
            canvas.move(pic, -155, -125)

    # Function :    help
    # Description : function connected to Help button to display a usage window for the user
    def help():
        help_Window = Toplevel()
        help_Window.title('Application Usage')
        message = Message(help_Window, text = USAGE_Text)
        message.pack()

    # Code to create GUI display

    root.wm_title("The Ebae")
    root.tk.call('wm', 'iconbitmap', root._w, '-default', './Price-Tag.ico')
    frame1 = Frame(root)
    frame1.pack()
    frame23 = Frame(root)
    frame23.pack()
    frame2 = Frame(frame23)
    frame2.grid(row = 0, column = 0, sticky = W)
    frame3 = Frame(frame23)
    frame3.grid(row = 0, column = 1, sticky = E)
    frame4 = Frame(root)
    frame4.pack()

    header_Label = Label(frame1, text = "Ebay Price Monitor", font = ("Ariel", "14"))
    header_Label.pack()

    search_Label = Label(frame2, text = "Item Name:")
    search_Label.grid(row = 0, column = 0, sticky = E)
    search_Box = Entry(frame2, textvariable = item_entry)
    search_Box.grid(row = 0, column = 1, columnspan = 2)
    search_Box.config(width = 30)

    category_Label = Label(frame2, text = "Category:")
    category_Label.grid(row = 1, column = 0, sticky = E)
    category_Select = Listbox(frame2, selectmode = 'SINGLE')
    category_Select.grid(row = 1, column = 1, columnspan = 2)
    category_Select.config(width = 30)

    results_Display = Label(frame3, text = "")
    results_Display.grid(row = 0, column = 0, columnspan = 2)

    initial_search_Button = Tkinter.Button(frame3,
                                   text = "Get Categories",
                                   font = ("Helvetica", 10),
                                   command = lambda: irun())
    initial_search_Button.grid(row = 1, column = 0)
    search_Button = Tkinter.Button(frame3,
                                   text = "Search",
                                   font = ("Helvetica", 10),
                                   command = lambda: run())
    search_Button.grid(row = 1, column = 1)

    mean_Label = Label(frame3, text = "Mean Price: ")
    mean_Label.grid(row = 2, column = 0, sticky = E)
    mean_Display = Label(frame3, text = "$0.00")
    mean_Display.grid(row = 2, column = 1, sticky = W)

    median_Label = Label(frame3, text = "Median Price: ")
    median_Label.grid(row = 3, column = 0, sticky = E)
    median_Display = Label(frame3, text = "$0.00")
    median_Display.grid(row = 3, column = 1, sticky = W)

    startPoint_Label = Label(frame3, text = "Start Point: ")
    startPoint_Label.grid(row = 4, column = 0, sticky = E)
    startPoint_Display = Label(frame3, text = "$0.00")
    startPoint_Display.grid(row = 4, column = 1, sticky = W)

    endPoint_Label = Label(frame3, text = "End Point: ")
    endPoint_Label.grid(row = 5, column = 0, sticky = E)
    endPoint_Display = Label(frame3, text = "$0.00")
    endPoint_Display.grid(row = 5, column = 1, sticky = W)

    help_Button = Tkinter.Button(frame3,
                                   text="Help",
                                   font=("Helvetica", 10),
                                   command=lambda: help())
    help_Button.grid(row = 6, column = 0, columnspan = 2)

    change_Label = Label(frame4, text = "Change in Average Price: ")
    change_Label.grid(row = 0, column = 0, sticky = E)
    change_Display = Label(frame4, text = "$0.00")
    change_Display.grid(row = 0, column = 1, sticky = W)

    quality_Label = Label(frame4, text = "Confidence of Line: ")
    quality_Label.grid(row = 1, column = 0, sticky = E)
    quality_Display = Label(frame4, text = "")
    quality_Display.grid(row = 1, column = 1, sticky = W)

    canvas = Canvas(root, width = 480, height = 290)
    canvas.pack()

    # Function :    close
    # Description : function to make program exit when GUI window is closed
    def close():
        root.quit()

    root.protocol("WM_DELETE_WINDOW", close)

    root.mainloop()


GUI()
