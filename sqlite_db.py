# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 10:18:18 2020

@author: Александр
"""

import sqlite3

#Convert digital data to binary format
def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

def insertBLOB(dbpath,empId, name, photo, resumeFile):
    try:
        sqliteConnection = sqlite3.connect(dbpath)
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")
        sqlite_insert_blob_query = """ INSERT INTO Telega
                                  (id, uid, audio, imgface) VALUES (?, ?, ?, ?)"""

        empPhoto = convertToBinaryData(photo)
        resume = convertToBinaryData(resumeFile)
        # Convert data into tuple format
        data_tuple = (empId, name, empPhoto, resume)
        cursor.execute(sqlite_insert_blob_query, data_tuple)
        sqliteConnection.commit()
        print("Image and file inserted successfully as a BLOB into a table")
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("the sqlite connection is closed")

#insertBLOB(dbpath,1, "Smith", "E:\pynative\Python\photos\smith.jpg", "E:\pynative\Python\photos\smith_resume.txt")
#insertBLOB(dbpath,2, "David", "E:\pynative\Python\photos\david.jpg", "E:\pynative\Python\photos\david_resume.txt")


# Convert binary data to proper format and write it on Hard Disk
def writeTofile(data, filename):
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored blob data into: ", filename, "\n")

def saveBlobData(dbpath,empId,output):
    try:
        sqliteConnection = sqlite3.connect(dbpath)
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sql_fetch_blob_query = """SELECT * from new_employee where id = ?"""
        cursor.execute(sql_fetch_blob_query, (empId,))
        record = cursor.fetchall()
        for row in record:
            print("Id = ", row[0], "Name = ", row[1])
            name  = row[1]
            audio = row[2]
            faces = row[3]

            print("Storing employee image and resume on disk \n")
            audioPath = output+"\\" + name + ".jpg"
            facesPath  = output+"\\" + name + "_resume.txt"
            writeTofile(audio, audioPath)
            writeTofile(faces, facesPath)

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read blob data from sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("sqlite connection is closed")

#readBlobData(1)
#readBlobData(2)





  
""" Класс управления базой данных """
class DB():
    
    """ Инициализируем класс """     
    def __init__(self, path):
        try:
            self.conn = sqlite3.connect(path)
            self.conn.isolation_level = None # для транзакций (режим автоматической фиксации)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print('При инициализации класса возникла ошибка: '+ str(e))
        
    """ Закрываем соединение с базой """
    def close(self):
        try:
            self.cursor.close()
            self.conn.close()
        except Exception as e:
            print('При уничтожения класса возникла ошибка: '+ str(e))      
 
    
    """ Создаем таблицу """
    def creat_table(self,title, fields):
        try:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS '%s' (%s)"%(title,fields)) 
            self.conn.commit()
        except Exception as e:
            print('При создании таблицы "'+title+' ('+fields+')" возникла ошибка: '+ str(e))
            print("CREATE TABLE IF NOT EXISTS '%s' (%s)"%(title,fields))
        
    """ Редактируем запись в таблице """
    def edit_table(self,title, field_set,fs_content,field_where,fw_content):
        try:
            SQL = "UPDATE "+title+"  SET "+field_set+" = '"+fs_content+"' WHERE "+field_where+" = '"+fw_content+"' "
            self.cursor.execute(SQL)
            self.conn.commit() 
        except Exception as e:
            print('При редактирование записи в таблице "'+title+'" возникла ошибка: '+ str(e))  
            
    """ Простое чтение из таблицы """
    def select_simple(self, What, From, Where=''):
        try:
            sql = 'SELECT '+What+' FROM '+From if Where=='' else 'SELECT '+What+' FROM '+From+' WHERE '+Where
            self.cursor.execute(sql)
            result = []
            for i in self.cursor.fetchall():
                result.append(list(i))
            return result
        except Exception as e:
            print('При чтении таблицы "'+From+'" возникла ошибка: '+ str(e))     


    """ Выполняем SQL команду """
    def execute(self, SQL):
        try:
            self.cursor.execute(SQL)
            result = []
            for i in self.cursor.fetchall():
                result.append(list(i))
            return result
        except Exception as e:
            print('При выполнении команды "'+SQL+'" возникла ошибка: '+ str(e)) 
    
    
    """ Указываем на начало транзакции """
    def beginCommit(self):
        try:
            self.cursor.execute("begin")
#        except Exception as e:
#            print('Ошибка указания на начало транзакции: '+ str(e))    
        except:
            print('Ошибка указания на начало транзакции')     

            
    """ Выполняем транзакцию """    
    def doCommit(self):
        try:
            self.conn.commit()  
#        except Exception as e:
#            print('При выполнении запроса возникла ошибка: '+ str(e))             
        except:
            print('При выполнении запроса возникла ошибка')     
        
        
    """ Добавляем в транзакцию запись в таблицу """
    def contentCommit_insert(self, table, **fields):
        try:
            fields_title=list(fields.keys())
            fields_title = ",".join("'"+str(x)+"'" for x in fields_title)
            fields_values=list(fields.values())
            fields_values = ",".join("'"+str(x)+"'" for x in fields_values)
            self.cursor.execute("INSERT INTO '"+table+"' ("+fields_title+") VALUES ("+fields_values+")")
#        except Exception as e:
#            print('При добавлении в транзакцию таблицы "'+table+'" с полями "'+fields_title+'" и значениями "'+fields_values+'" возникла ошибка: '+ str(e))          
        except:
            print('При добавлении в транзакцию таблицы возникла ошибка')         

        return fields
 
    """ Добавляем колонку в таблицу """
    def TableAddFields(self, tbl_name, fields_lst):
        if len(fields_lst)>0:
            try:
                self.cursor.execute("begin")
                for f in fields_lst:
                    self.cursor.execute("ALTER TABLE "+tbl_name+" ADD COLUMN '"+f+"' TEXT") # добавляем столбец
                self.conn.commit()
            except Exception as e:
                print('При добавлении нового столбца возникла ошибка: '+ str(e))
        else:
            print('При добавлении нового столбца возникла ошибка: Передан пустой список с заголовками.')


    """ Возвращаем список полей таблицы """
    def get_columnsName(self, table_name):
        try:
            desc=self.conn.execute('select * from '+table_name)
            return list(map(lambda x: x[0], desc.description)) #cursor.description is description of columns | return [description[0] for description in cursor.description]
        except Exception as e:
            print('При получении списка полей таблицы "'+table_name+'" возникла ошибка: '+ str(e)) 







