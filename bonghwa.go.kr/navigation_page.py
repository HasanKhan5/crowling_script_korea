from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from insert_on_database import *
import re, wx, time, html
app = wx.App()
import Global_var

def chrome():
    options = webdriver.ChromeOptions()
    try:
        options.add_extension("C:\\Translation EXE\\FreeVPN-Proxy.crx")
    except:pass

    try:  
        service = Service(executable_path="C:\\Translation EXE\\chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        wx.MessageBox('-_-  ADD EXTENSION -_-','', wx.OK | wx.ICON_INFORMATION)
        driver.get("https://www.bonghwa.go.kr/open.content/ko/news/news/tender/?p=1")
        time.sleep(15)
    except Exception as e:
       print(e)
    navigation_page(driver)

def remove_html(text):
    return re.sub('<.*?>', '', str(text))
    
def navigation_page(driver): 
    list_html = []
    page_element = True

    while page_element:
        try:
            # switch to iframe
            driver.switch_to.default_content()
            main_frame = driver.find_element(By.XPATH, '//*[@id="content-main"]/iframe')
            driver.switch_to.frame(main_frame)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")

            for _ in driver.find_elements(By.XPATH, '/html/body/form/table[3]/tbody/tr/td/table[1]/tbody/tr/td[5]'):
                notic_number = driver.find_element(By.XPATH, '/html/body/form/table[3]/tbody/tr/td/table[1]/tbody/tr[' + str(Global_var.tr_count) + ']/td[2]').get_attribute('innerText').strip()
                tenders_details = driver.find_element(By.XPATH, '/html/body/form/table[3]/tbody/tr/td/table[1]/tbody/tr[' + str(Global_var.tr_count) + ']/td[3]').get_attribute('innerText').strip()
                closing_date = driver.find_element(By.XPATH, '/html/body/form/table[3]/tbody/tr/td/table[1]/tbody/tr[' + str(Global_var.tr_count) + ']/td[6]').get_attribute('innerText').strip()
                publish_date = driver.find_element(By.XPATH, '/html/body/form/table[3]/tbody/tr/td/table[1]/tbody/tr[' + str(Global_var.tr_count) + ']/td[5]').get_attribute('innerText').strip()
                publish_date_obj = datetime.strptime(publish_date, '%Y-%m-%d')
                selected_date_obj = datetime.strptime(Global_var.fromdate, '%Y-%m-%d')

                timedelta = publish_date_obj - selected_date_obj
                day = timedelta.days
                if day >= 0:
                    driver.find_element(By.XPATH, '/html/body/form/table[3]/tbody/tr/td/table[1]/tbody/tr[' + str(Global_var.tr_count) + ']/td[5]').click()
                    time.sleep(5)
                    driver.switch_to.default_content()
                    main_frame = driver.find_element(By.XPATH, '//*[@id="content-main"]/iframe')
                    driver.switch_to.frame(main_frame)
                    html_document = driver.find_element(By.XPATH, '/html/body/form[2]').get_attribute('outerHTML')
                    list_html.append({'DOC': html_document, 'notic_number': notic_number, 'tenders_details': tenders_details, 'closing_date': closing_date, 'publish_date': publish_date})
                
                    print(f"-------- HTML collected for scraping: {len(list_html)} ----------")

                    driver.back(),time.sleep(2)
                    
                    # Switch back to the necessary frames
                    driver.switch_to.default_content()
                    main_frame = driver.find_element(By.XPATH, '//*[@id="content-main"]/iframe')
                    driver.switch_to.frame(main_frame)

                    Global_var.tr_count += 2
                    time.sleep(1)  
                else:scrap(list_html,driver)
            print("Next page")
            time.sleep(2) 
 
            try:
                scroll_div = driver.find_element(By.CLASS_NAME, "page_no")
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_div)
                next_page = driver.find_element(By.XPATH,'//*[@alt="다음 페이지로 이동"]')
                if "다음 페이지로 이동" in next_page.get_attribute('alt'):
                    next_page.click()
                    time.sleep(5)   
                    Global_var.tr_count = 6
                    page_element = True
            except Exception as e:
                scrap(list_html, driver)
                print(e)
        except Exception as e:
            print(e) 
            
def scrap(list_html,driver):
    scrap_error = True
    while scrap_error:
        try:
            for i in list_html:
                segField = [''] * 50
                time.sleep(1)
                
                html_doc = ''
                html_doc = i['DOC'].replace('&nbsp;',' ')

                segField[2] = "봉화로 1111 봉화군청 ☎ 대표전화 : 054-679-6114 팩스 : 054-679-6619"
                segField[7] = "KR"
                segField[8] = "https://www.bonghwa.go.kr/"
                segField[12] = "봉화 군청"
                segField[13] = i['notic_number']
                segField[14] = Global_var.dms_entrynotice_tblnotice_type
                segField[18] = i['tenders_details']
                segField[19] = segField[18]
                TenderValue = remove_html(html_doc.partition('기초금액 : ')[2].partition('(')[0]).replace('금','').replace('원','')
                TenderValue = TenderValue.replace(",", "")
                # TenderValue = TenderValue[:-3] + "." + TenderValue[-3:]
                segField[20] = TenderValue
                if segField[20] != '':
                    segField[21] = "KRW"
                closing_d = i['closing_date']  
                deadline = closing_d.partition('~')[2].strip()
                segField[24] = deadline
                segField[27] = "0" 
                segField[28] = driver.current_url
                segField[31] = "bonghwa.go.kr"
                segField[46] = '게재기간: ' + str(i['publish_date'])
                segField[42] = segField[7]
                segField = validate_segField(segField)

                check_date(segField, html_doc)
                Global_var.Total += 1 
                print(" Total: " + str(Global_var.Total) + " | Duplicate: " + str(Global_var.duplicate) + " | Expired: " + str(Global_var.expired) + " | Inserted: " + str(Global_var.inserted) + " | Deadline Not given: " + str(Global_var.deadline_Not_given) + " | QC Tenders: " + str(Global_var.QC_Tender),"\n")                      
                scrap_error = False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",exc_tb.tb_lineno)    

    # wx.MessageBox(f'Total: {len(list_html)}\nDeadline Not given: {Global_var.deadline_Not_given}\nSkipped: {Global_var.skipped}\nDuplicate: {Global_var.duplicate}\nInserted: {Global_var.inserted}\nExpired: {Global_var.expired}\nQC Tenders: {Global_var.QC_Tender}', 'bonghwa.go.kr', wx.OK | wx.ICON_INFORMATION)
    wx.MessageBox(f'Total: {Global_var.Total}\nDeadline Not given: {Global_var.deadline_Not_given}\nSkipped: {Global_var.skipped}\nDuplicate: {Global_var.duplicate}\nInserted: {Global_var.inserted}\nExpired: {Global_var.expired}\nQC Tenders: {Global_var.QC_Tender}', 'bonghwa.go.kr', wx.OK | wx.ICON_INFORMATION)
    driver.close()
    sys.exit()

def check_date(segField, html_doc):     
        deadline = (segField[24])
        curdate = datetime.now()
        curdate_str = curdate.strftime("%Y-%m-%d")
        try:
            if deadline != '':
                datetime_object_deadline = datetime.strptime(deadline, '%Y-%m-%d')
                datetime_object_curdate = datetime.strptime(curdate_str, '%Y-%m-%d')
                timedelta_obj = datetime_object_deadline - datetime_object_curdate
                day = timedelta_obj.days
                is_new = False
                if day > 0:
                    is_new = check_Duplication(segField)
                    if is_new :
                        Fileid,Filename = create_html_file(segField, html_doc)

                        # if segField[44] != '':
                        #     adddoc_Filename = AdditionalDocs(segField,Fileid)
                        #     if adddoc_Filename != '':
                        #         segField[44] = adddoc_Filename 

                        insert_in_local(segField,Fileid)
                        insert_l2l_tbl(segField,Fileid,Filename)
                    else:
                        print('Duplicate Tender')
                        Global_var.duplicate += 1   
                else:
                    print("Expired Tender")
                    Global_var.expired += 1
            else:
                print("Deadline Not Given")
                Global_var.deadline_Not_given += 1
        except Exception as e:
            print(e)

def validate_segField(segField):
    for index, value in enumerate(segField):
        print(index, value)
        segField[index] = html.unescape(str(value)).strip()
        # segField[i] = segField[i].replace("'", "''")
    
    for index, value in enumerate(segField):
        if len(value) > 1500:
            segField[index] = value[:1500] + "..."
        if value == "":
            segField[index] = ""
            
    if segField[18] == '':
        segField[18] = segField[19]
        
    if len(segField[19]) > 200:
        if segField[18] != segField[19]:
            segField[18] = segField[19]+'<br>\n'+segField[18]
        segField[19] = segField[19][:200].strip() + "..."
   
    if len(segField[2]) > 500:
        segField[2] = segField[2][:500].strip() + "..."

    return segField
chrome()