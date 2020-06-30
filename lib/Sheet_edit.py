import gspread
import threading
import re
from lib.Line_api import get_id_from_token

class SheetEditor(threading.Thread) :
    def __init__(self,queues,fevent,setting):
        self.gc = gspread.service_account(filename=setting["certification"])
        self.workbook = self.gc.open_by_url(setting["sheet_url"])
        self.worksheet = self.workbook.worksheets()[0]
        self.queues = queues
        self.setting = setting
        self.fevent = fevent
        threading.Thread.__init__(self)

    def getData(self):
        value_list = self.worksheet.get_all_values()
        return value_list

    def clearSheet(self):
        self.worksheet.clear()

    def run(self):
        print('Sheet thread runnning start')
        if(not self.setting["active"]):
            return None
        while not self.fevent.wait(timeout=self.setting["waittime"]):
            data = self.getData()
            self.clearSheet()
            for elem in data:
                additional_data = {self.setting["key"][i]:elem[i] for i in range(len(elem))}
                additional_data["dataType"] = 'message'
                additional_data["time"] = additional_data["time"].replace("/","-")
                additional_data["is_read"] = 0
                a = get_id_from_token(additional_data["token"])
                if(a == None):
                    a = {"sender":None,"userID":None}
                else:
                    self.queues["voice"].put(a["displayName"] + "さんからメッセージが届きました")
                    print(a)

                additional_data.update(a)
                self.queues['data'].put(additional_data)
            
            

if __name__ == "__main__":
    sheetEdit = SheetEditor(None,None,None)
    sheetEdit.getData()
    sheetEdit.clearSheet()