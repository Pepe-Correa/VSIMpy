# -*- coding: cp1252 -*

import os
import xlrd

import wx
import wx.lib.sheet as sheet #Planillas

from math import exp

import matplotlib 
matplotlib.use('WXAgg') # Mejor forma de usar matplotlib con wxPython
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec


os.chdir("files") # Cambiar al directorio 'files'
directorio = os.getcwd() # Establecer directorio base

class Splash():
    """---Clase que define saludo en formato 'splash'---"""
    def __init__(self):
        image = wx.Image("splash.png", wx.BITMAP_TYPE_PNG)
        bmp = image.ConvertToBitmap()
        wx.SplashScreen(bmp, wx.SPLASH_CENTRE_ON_SCREEN |
        wx.SPLASH_TIMEOUT, 5000, None, -1)

class MySheet(sheet.CSheet):
    """---Clase que define planillas---"""
    def __init__(self, parent):
        sheet.CSheet.__init__(self, parent)

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        ScreenSize = wx.GetDisplaySize()
        wx.Frame.__init__(self, parent, title=title, size=(ScreenSize[0]*0.45,ScreenSize[1]*0.575), style= wx.SYSTEM_MENU | wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX)
        
        # Agregar ícono:
        ib = wx.IconBundle()
        ib.AddIconFromFile("inia_logo.ico", wx.BITMAP_TYPE_ANY)
        self.SetIcons(ib)

        # Barra de estado en parte inferior de la ventana:
        self.CreateStatusBar()
        
        """----------"""
        """---MENÚ---"""
        """----------"""
        # Barras de menús
        self.menuBar = wx.MenuBar()
        self.SetMenuBar(self.menuBar)  # Adding the MenuBar to the Frame content (self).
         
        # Creando el menú 'Archivo'.
        self.filemenu= wx.Menu()
        self.menuBar.Append(self.filemenu,"&Archivo") # Adding the "filemenu" to the MenuBar
        self.menuSave = self.filemenu.Append(wx.ID_ANY, "Guardar como\tCtrl+Shift+S"," Guardar resultados en una planilla Excel (*.xls)")  # wx.ID_ABOUT and wx.ID_EXIT are standard ids provided by wxWidgets.
        self.Bind(wx.EVT_MENU, self.onSaveFile, self.menuSave) # Definiendo eventos.
        self.menuSave.Enable(False) # DISABLE: deshabilita menuRun
        self.menuExit = self.filemenu.Append(wx.ID_EXIT,"Cerrar\tCtrl+Q"," Salir del programa")
        self.Bind(wx.EVT_MENU, self.OnExit, self.menuExit)

        # Creando el menú 'Modelo'.
        self.modelmenu = wx.Menu()
        self.menuBar.Append(self.modelmenu,"&Modelo") # Adding the "filemenu" to the MenuBar
        self.menuOpciones = self.modelmenu.Append(wx.ID_ANY, "Opciones","Cambiar parámetros por defecto") # when creating a new window you may specify wxID_ANY to let wxWidgets assign an unused identifier to it automatically
        self.Bind(wx.EVT_MENU, self.OnOptions, self.menuOpciones)
        self.modelmenu.AppendSeparator() # Linea horizontal separador
        self.menuModel = self.modelmenu.Append(wx.ID_ANY, "&Correr\tF5","Ingresar parámetros y correr el modelo")
        self.Bind(wx.EVT_MENU, self.OnInputs, self.menuModel)

        # Creando el menú 'Ayuda'.
        self.helpmenu = wx.Menu()
        self.menuBar.Append(self.helpmenu,"&Ayuda") # Adding the "filemenu" to the MenuBar
        self.menuAbout = self.helpmenu.Append(wx.ID_ANY, "&About"," Información del programa")
        self.Bind(wx.EVT_MENU, self.OnAboutBox, self.menuAbout)
        self.helpmenu.AppendSeparator() # Linea horizontal separador
        self.menuHelp = self.helpmenu.Append(wx.ID_HELP, "&Documentación\tF1"," Documentación acerca del modelo")
        self.Bind(wx.EVT_MENU, self.OnOpen, self.menuHelp)

        """---------------------------"""
        """---PLANILLAS EN PESTAÑAS---"""
        """---------------------------"""
        # Creando Pestañas con planillas
        self.notebookOutputs = wx.Notebook(self, -1, style=wx.NB_FIXEDWIDTH)

        # Imagen de fondo
        imagen = wx.Image("Presentación.jpg", wx.BITMAP_TYPE_JPEG)# Fotografía gentileza del Ing. Agr. Dr. (c) Alexis Esteban Vergara V.
        imagen = imagen.Scale(ScreenSize[0]*0.45,ScreenSize[1]*0.5)
        self.VerImagen = wx.StaticBitmap(self.notebookOutputs, -1, wx.BitmapFromImage(imagen))

        """-----------------------"""
        """-----------------------"""
        self.Show(True) # Mostrar GUI

        
    """---------------"""
    """---FUNCIONES---"""
    """---------------"""

    def onSaveFile(self, event):
        """ Crea y muestra diálogo para guardar un archivo """
        from xlwt import Workbook
        self.wbk = Workbook()
        self.sheet = self.wbk.add_sheet('Resultados')

        #Head:
        self.sheet.write(0,0,"Fecha")
        self.sheet.write(0,1,u"Tm (°C)")
        self.sheet.write(0,2,"ET0 (mm)")
        self.sheet.write(0,3,"Pp (mm)")
        self.sheet.write(0,4,u"SDG10 (°C)")
        self.sheet.write(0,5,u"IAF (m\u00b2/m\u00b2)")
        self.sheet.write(0,6,"Kc")
        self.sheet.write(0,7,"LWP scaler")
        self.sheet.write(0,8,"Crop Kc")
        self.sheet.write(0,9,"Kcc")
        self.sheet.write(0,10,"ETc (mm)")
        self.sheet.write(0,11,"ETcc (mm)")
        self.sheet.write(0,12,"SimIrrig (mm)")
        self.sheet.write(0,13,u"Balance hídrico (mm)")
        self.sheet.write(0,14,"Humedad del suelo  (mm)")
        self.sheet.write(0,15,u"Escorrentía (mm)")
        self.sheet.write(0,16,"Riego (mm)")
        self.sheet.write(0,17,u"\N{GREEK CAPITAL LETTER PSI} tallo (MPa)")
  
        #Ingresando datos a Excel:
        for i in range(1, len(self.Tm)+1):
            self.sheet.write(i,0,self.Date[i-1].strftime('%d-%m-%Y'))
            self.sheet.write(i,1,float(self.Tm[i-1]))
            self.sheet.write(i,2,float(self.ET0[i-1]))
            self.sheet.write(i,3,float(self.Pp[i-1]))
            self.sheet.write(i,4,float(self.SDG10[i-1]))
            self.sheet.write(i,5,float(self.LAI[i-1]))
            self.sheet.write(i,6,float(self.Kc[i-1]))
            self.sheet.write(i,7,float(self.LWP[i-1]))
            self.sheet.write(i,8,float(self.CropKc[i-1]))
            self.sheet.write(i,9,float(self.Kcc[i-1]))
            self.sheet.write(i,10,float(self.ETc[i-1]))
            self.sheet.write(i,11,float(self.ETcc[i-1]))
            self.sheet.write(i,12,float(self.SimIrrig[i-1]))
            self.sheet.write(i,13,float(self.WB[i-1]))
            self.sheet.write(i,14,float(self.SM[i-1]))
            self.sheet.write(i,15,float(self.RunOff[i-1]))
            self.sheet.write(i,16,float(self.Irrig[i-1]))
            self.sheet.write(i,17,float(self.SWP[i-1]))

        # Fenología, si se desea:
        if self.Phenology.GetValue():
            self.sheet.write(0,18,u"Fenología")
            [self.sheet.write(i, 18, "%s" % self.PhenologySDG10[i-1]) for i in range(1, len(self.Tm)+1)]

        
        self.dlgSave = wx.FileDialog(
            self, 
            message="Guardar Archivo",
            defaultFile= "",
            wildcard="Archivos Excel (*.xls)|*.xls", # Tipos de archivos a guardar
            style=wx.SAVE|wx.OVERWRITE_PROMPT
        )
  
        if self.dlgSave.ShowModal() == wx.ID_OK:
            os.chdir(self.dlgSave.GetDirectory()) # Directorio propuesto por el usuario
            self.wbk.save(self.dlgSave.GetFilename()) # Guardar archivo con nombre y directorio propuesto por el usuario
            os.chdir(directorio) # Volver al directorio base
            
        self.dlgSave.Destroy()


    def onOpenFile(self, event):
        """ Crea y muestra diálogo para abrir un archivo """
        self.dlgOpen = wx.FileDialog(
            self.panelInputs, # Hace referencia al panel de 'Inputs'
            message="Seleccionar Archivo",
            defaultFile= "",
            wildcard="Archivos Excel (*.xlsx,*.xls)|*.xlsx;*.xls", # Tipos de archivos a abrir
            style=wx.OPEN
        )
        
        if self.dlgOpen.ShowModal() == wx.ID_OK:
            self.Path = self.dlgOpen.GetPath()
            self.excelfile.SetValue(self.Path) # Modificar text

        self.dlgOpen.Destroy()
            
    
    def ActRun(self,event):

        self.OnOptions(event, Show = False) # Correr función con valores por defecto sin desplegar frame 
        
        def ISEXCEL(entrada):
            """---Funcion para chequear si hay un archivo Excel---"""
            """---try: chequear si hay un error (IOError o AttributeError), de haberlo entrega el statement dado por 'except'---"""
            try: 
                book = xlrd.open_workbook(entrada)
                return True
            except IOError: # El directorio no lleva a un archivo excel
                return False
            except AttributeError: # No corresponde a un directorio
                return False

        def ISNUM(entrada):
            """---Funcion para chequear si una entrada es númerica---"""
            """---try: chequear si hay un error (ValueError), de haberlo entrega el statement dado por 'except'---"""
            try: 
                float(entrada) if '.' in entrada else int(entrada)
                return True
            except ValueError:
                return False
            
        # Chequear entradas:
        if len(self.excelfile.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar archivo!", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISEXCEL(self.excelfile.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "La ruta no corresponde a un archivo Excel!", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
            
        elif len(self.SDGb.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar la SDG para la brotación", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.SDGb.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "La SDG para la brotación debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        elif len(self.SDGmiaf.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar la SDG para el máximo valor de IAF", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.SDGmiaf.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "La SDG para el máximo valor de IAF debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        elif len(self.SDGf.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar la SDG para la caída de hojas", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.SDGf.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "La SDG para la caída de hojas debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        elif len(self.MaxIAF.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar máximo valor IAF", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.MaxIAF.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "El máximo valor IAF debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        elif len(self.ExtCoeff.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar el coeficiente de extinción", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.ExtCoeff.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "El coeficiente de extinción debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        elif len(self.LWP_KcMax.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar el 'Potencial hídrico tallo para iniciar la reducción en Kc'", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.LWP_KcMax.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "'El potencial hídrico de tallo para iniciar la reducción en Kc' debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        elif len(self.LWP_Kc0.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar el 'Potencial hídrico de tallo en el cual Kc = 0'", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.LWP_Kc0.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "'El potencial hídrico de tallo en el cual Kc = 0' debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        elif len(self.Sand.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar el '% de Arena'", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.Sand.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "El '% de Arena' debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        elif len(self.Clay.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar el '% de Arcilla'", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.Clay.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "El '% de Arcilla' debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        elif len(self.Gravel.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar el '% de Grava'", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.Gravel.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "El '% de Grava' debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        elif len(self.RootDepth.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar la 'Profundidad raíces'", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.RootDepth.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "La 'Profundidad raíces' debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        elif len(self.OptLWP.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar el 'Óptimo potencial hídrico de tallo al medio día'", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.OptLWP.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "El 'Óptimo potencial hídrico de tallo al medio día' debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        elif len(self.OptLWP.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar el 'Óptimo potencial hídrico de tallo al medio día'", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.OptLWP.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "El 'Óptimo potencial hídrico de tallo al medio día' debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        elif len(self.CCLastDay.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar el 'Último día del cultivo'", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.CCLastDay.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "El 'Último día del cultivo' debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        elif len(self.CC_cover.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar la 'Fracción de la superficie del suelo cubierta por el cultivo'", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.CC_cover.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "La 'Fracción de la superficie del suelo cubierta por el cultivo' debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        elif len(self.CC_SMdeath.GetValue()) == 0 :
            dlg = wx.MessageDialog(self.panelInputs, "Se debe ingresar la 'Fracción de la humedad suelo donde \n comienza la senescencia del cultivo'", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza
        elif ISNUM(self.CC_SMdeath.GetValue()) == False:
            dlg = wx.MessageDialog(self.panelInputs, "La 'Fracción de la humedad suelo donde \n comienza la senescencia del cultivo' debe ser númerico", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() # Muestra diálogo
            dlg.Destroy() # Finalmente lo destruye cuando se finaliza

        else:
            dlg = wx.MessageDialog(
                self.panelInputs,
                "¿Seguro que desea correr el modelo?",
                "Correr VSIMpy",
                wx.ICON_QUESTION|wx.YES_NO)
            if dlg.ShowModal() == wx.ID_YES:
                self.OnRun()
                dlg.Destroy() # Destruye diálogo
        
    def OnExit(self,event):
        self.Close(True)  # Close the frame.
        
    def OnRun(self):

        def Phenologyfx(x):
            """---Funcion para estimar fenología a través de la suma térmica según ecuación logística---"""
            if x != 0:
                Asym = 36.3237
                xmid = 185.1850
                scal = 199.7018
                return Asym/(1+exp((xmid-x)/scal))
            else:
                return 1

        def GetCtgPhenologyfx(n):
            """---Funcion para transformar el output de la función Phenology a categorías---"""
            if n == int(n):
                return str(int(n))
            else:
                return str(int(n)) + '-' + str(int(n + 1))

        def Datefx(x):
            import datetime
            """---Funcion para transformar fechas de Excel a fechas Python---"""
            t = datetime.datetime(*xlrd.xldate_as_tuple(x, 0))
            return t

        def LAIfx(SDG10Tomorrow, SDG10MaxLAI, MaxLAI):
            """---Funcion para calcular el Índice de Área Foliar---"""
            return (1.0066-1.0118*exp(-5.0278*(SDG10Tomorrow/SDG10MaxLAI)**1.9331))*MaxLAI
        
        def Kccfx(Day, CCLastDay, SMYesterday, CC_SMdeath, SMatFC, CC_cover):
            """---Función para calcular Kcc (cultivo cobertura)---"""
            if CC_cover > 0:
                if Day < CCLastDay:
                    if SMYesterday > CC_SMdeath * SMatFC and Day != 0:
                        return ((SMYesterday - (CC_SMdeath * SMatFC)) / (SMatFC - (CC_SMdeath * SMatFC))) * CC_cover
                    else:
                        return 0
                else:
                    return 0
            else:
                return 0

        def LWPfx(SWPYesterday, LWP_KcMax, LWP_Kc0):
            """---Función para calcular LWPscaler (LWP = daily predawn leaf water potential (bars))---"""
            if SWPYesterday > LWP_KcMax:
                if SWPYesterday < LWP_Kc0:
                    return (1.0 - ((SWPYesterday - LWP_KcMax) / (LWP_Kc0 - LWP_KcMax)))
                else:
                    return 0
            else:
                return 1
            
        def SWPfx(SoilA, SM, RootDepth, Gravel, SoilB):
            """---Función para calcular el potencial hídrico del tallo---"""
            return (1.0 / 100.0) * SoilA * ((SM / ((RootDepth * 1000.0) * (1 - (Gravel / 100.0)))) ** SoilB)

        def CropKcfx(AlterKc, Kc, LWP):
            """---Función para calcular CropKc---"""
            if AlterKc:
                return Kc * LWP
            else:
                return Kc
            
        def WBfx(Day, P, ETc, ETcc, Irrig, SMonDay1, SMYesterday):
            """---Función para calcular el balance hídrico---"""
            if Day == 0: # Primer día de medición, se debe considerar la humedad del suelo existente a esa fecha
                return P + ETc + ETcc + Irrig + SMonDay1
            else:
                return P + ETc + ETcc + Irrig + SMYesterday

        def Irrfx(SimIrr, SMYesterday, SMatIrrig, SMatOptLWP, ActIrrig):
            """---Función para calcular el riego---"""
            if SimIrr:
                if SMYesterday != 0:
                    if SMYesterday < SMatIrrig:
                        return (SMatOptLWP - SMatIrrig) * 2
                    else:
                        return 0
                else:
                    return 0
            else:
                return ActIrrig
        
        def RunOfffx(WB, SMatFC, Runoff_proportion_per_Day):
            """---Función para calcular el RunOff---"""
            if WB > SMatFC:
                return (WB - SMatFC) * (-Runoff_proportion_per_Day)
            else:
                return 0

        def IrrConvfx(Rowspace, Vinespace):
            return 0.264/(1.0/((Rowspace*0.3048)*(Vinespace*0.3048)))*(20.0/(Rowspace*Vinespace))
                   
        self.book = xlrd.open_workbook(self.Path)
        SheetNames =  self.book.sheet_names()
        if any([n == 'Input' for n in SheetNames]):
            Input = self.book.sheet_by_name('Input')
            nrows = Input.nrows 
            ncols = Input.ncols
            names = [Input.cell(0, i).value for i in range(ncols)]
            
            if not any([n == 'Fecha' for n in names]):
                dlg = wx.MessageDialog(self.panelInputs, "No existe la columna 'Fecha'!", "Advertencia", wx.ICON_ERROR)
                dlg.ShowModal() 
                dlg.Destroy()
            elif not any([n == 'Tm' for n in names]):
                dlg = wx.MessageDialog(self.panelInputs, "No existe la columna 'Tm'!", "Advertencia", wx.ICON_ERROR)
                dlg.ShowModal() 
                dlg.Destroy()
            elif not any([n == 'ET0' for n in names]):
                dlg = wx.MessageDialog(self.panelInputs, "No existe la columna 'ET0'!", "Advertencia", wx.ICON_ERROR)
                dlg.ShowModal() 
                dlg.Destroy()
            elif not any([n == 'Pp' for n in names]):
                dlg = wx.MessageDialog(self.panelInputs, "No existe la columna 'Pp'!", "Advertencia", wx.ICON_ERROR)
                dlg.ShowModal() 
                dlg.Destroy()
            elif not self.SimIrr.GetValue() and not any([n == 'ActIrrig' for n in names]):
                dlg = wx.MessageDialog(self.panelInputs, "No existe la columna 'ActIrrig'!", "Advertencia", wx.ICON_ERROR)
                dlg.ShowModal() 
                dlg.Destroy()
            else:
                
                self.frameInputs.Hide() # Esconde Frame de Inputs
                
                iTm = names.index("Tm") # Número columna "Tm"
                self.Tm = Input.col_values(iTm, start_rowx=1) # Leer datos de la columna i desde fila 1
                
                iDate = names.index("Fecha")
                self.Date = map(Datefx, Input.col_values(iDate, start_rowx=1))
                
                iET0 = names.index("ET0")
                self.ET0 = Input.col_values(iET0, start_rowx=1)

                iPp = names.index("Pp")
                self.Pp = Input.col_values(iPp, start_rowx=1)

                # Riego activo:
                if not self.SimIrr.GetValue():
                    iActIrrig = names.index("ActIrrig")
                    self.ActIrrig = Input.col_values(iActIrrig, start_rowx=1)
                else:
                    self.ActIrrig = [0]*len(self.Tm)

                # Sumas térmica e índice de área foliar:
                self.dgg0 = [i if (i-0)>0 else 0 for i in self.Tm]
                self.dgg10 = [self.Tm[i]-10 if sum(self.dgg0[:i+1]) > float(self.SDGb.GetValue()) and (self.Tm[i]-10)>0 else 0 for i in range(len(self.Tm))]
                self.SDG10 = [sum(self.dgg10[:i+1]) if sum(self.dgg10[:i+1]) <= float(self.SDGf.GetValue()) else 0 for i in range(len(self.Tm))] # Fecha por SDG
                #self.SDG10 = [sum(self.dgg10[:i+1]) if i < float(self.SDGf.GetValue())-1 else 0 for i in range(len(self.Tm))]
                self.LAI = [LAIfx(self.SDG10[i+1], float(self.SDGmiaf.GetValue()), float(self.MaxIAF.GetValue())) if self.SDG10[i]>0 else 0 for i in range(len(self.Tm))]
                self.Kc = [1-exp(-1*float(self.ExtCoeff.GetValue())*lai) for lai in self.LAI]

        
                # Fenología, si se desea:
                if self.Phenology.GetValue():
                    self.PhenologySDG10 = [GetCtgPhenologyfx(Phenologyfx(i)) for i in self.SDG10]

                # Relaciones hídricas:
                # Parámetros (entradas):
                SWPYesterday = 0
                LWP_KcMax = float(self.LWP_KcMax.GetValue())/0.1
                AlterKc = self.AlterKc.GetValue() # Parámetro tipo switch
                LWP_Kc0 = float(self.LWP_Kc0.GetValue())/0.1
                Sand = float(self.Sand.GetValue())
                Clay = float(self.Clay.GetValue())
                Gravel = float(self.Gravel.GetValue())
                SoilA = exp((-4.396-0.0715*Clay-0.000488*(Sand*Sand)-0.00004285*(Sand*Sand)*(Clay)))*100 # (Saxton et al. 1986)
                SoilB = -3.14-0.00222*(Clay*Clay)-0.00003484*(Sand*Sand)*Clay # (Saxton et al. 1986)
                RootDepth = float(self.RootDepth.GetValue())/0.305
                OptLWP = float(self.OptLWP.GetValue())/0.1
                CCLastDay = float(self.CCLastDay.GetValue())
                CC_SMdeath = float(self.CC_SMdeath.GetValue())
                CC_cover = float(self.CC_cover.GetValue())
                SMatFC = ((15/SoilA)**(1/SoilB))*(RootDepth*1000)*(1-(Gravel/100)) # (Saxton et al. 1986)
                SMatWP = ((1000/SoilA)**(1/SoilB))*(RootDepth*1000)*(1-(Gravel/100)) # (Saxton et al. 1986)
                SMatOptLWP = (((OptLWP*100)/SoilA)**(1/SoilB))*(RootDepth*1000)*(1-(Gravel/100))
                SimIrr = self.SimIrr.GetValue() # Parámetro tipo switch
                SMatIrrig = SMatOptLWP - 5
                IrrConv = IrrConvfx(float(self.Rowspace.GetValue()), float(self.Vinespace.GetValue()))
                Runoff_proportion_per_Day = 0.5              
                SMonDay1 = SMatFC
                SMYesterday = SMonDay1 # Parámetros inciales
                SWPYesterday = 1 # Parámetros inciales

                self.LWP = []
                self.CropKc = []
                self.Kcc = []
                self.ETc = []
                self.ETcc = []
                self.Irrig = []
                self.SimIrrig = []
                self.WB = []  
                self.RunOff = []
                self.SM = []
                self.SWP = []

                for i in range(len(self.Tm)):
                    self.LWP.append(LWPfx(SWPYesterday, LWP_KcMax, LWP_Kc0))
                    self.CropKc.append(CropKcfx(AlterKc, self.Kc[i], self.LWP[i]))
                    self.Kcc.append(Kccfx(i, 1 + CCLastDay, SMYesterday, CC_SMdeath, SMatFC, CC_cover))
                    self.ETc.append(self.ET0[i] * self.CropKc[i] * (-1))
                    self.ETcc.append(self.ET0[i] * self.Kcc[i] * (-1))
                    self.Irrig.append(Irrfx(SimIrr, SMYesterday, SMatIrrig, SMatOptLWP, self.ActIrrig[i]))
                    self.SimIrrig.append(self.Irrig[i] * IrrConv)
                    self.WB.append(WBfx(i, self.Pp[i], self.ETc[i], self.ETcc[i], self.Irrig[i], SMonDay1, SMYesterday))
                    self.RunOff.append(RunOfffx(self.WB[i], SMatFC, Runoff_proportion_per_Day))
                    self.SM.append(self.WB[i] + self.RunOff[i])
                    SWPYesterday = SWPfx(SoilA, self.SM[i], RootDepth, Gravel, SoilB)
                    self.SWP.append(SWPYesterday)
                    SMYesterday = self.WB[i] + self.RunOff[i]

                self.SWP =  [swp*0.1 for swp in self.SWP] # Potencial hídrico suelo = tallo,  de bares a MPa

                """----------Planilla----------"""
                #self.VerImagen.Destroy() # Destruir imagen fondo notebook
                self.VerImagen.Hide() # Esconder imagen fondo notebook (permite comando una vez ya corrido anteriormente a diferencia de 'Destroy')

                # Ajustar dimensiones planilla a los datos obtenidos:
                self.sheet1 = MySheet(self.notebookOutputs) # Planilla
                self.sheet1.SetNumberRows(len(self.Tm))
                    
                # Número de columnas
                if not self.Phenology.GetValue():
                    ncols = self.sheet1.SetNumberCols(18)
                else:
                    ncols = self.sheet1.SetNumberCols(19)
                    self.sheet1.SetColLabelValue(18, u"Fenología")
                    [self.sheet1.SetCellValue(i, 18, "%s" % self.PhenologySDG10[i]) for i in range(len(self.Tm))]
                    
                # Cambiar nombre columnas
                self.sheet1.SetColLabelValue(0, "Fecha") 
                self.sheet1.SetColLabelValue(1, u"Tm (°C)")
                self.sheet1.SetColLabelValue(2, "Pp (mm)")
                self.sheet1.SetColLabelValue(3, "ET0 (mm)")
                self.sheet1.SetColLabelValue(4, u"SDG10 (°C)") 
                self.sheet1.SetColLabelValue(5, u"IAF (m\u00b2/m\u00b2)")
                self.sheet1.SetColLabelValue(6, "Kc")
                self.sheet1.SetColLabelValue(7, "LWP scaler")
                self.sheet1.SetColLabelValue(8, "CropKc (mm)")
                self.sheet1.SetColLabelValue(9, "Kcc (mm)")
                self.sheet1.SetColLabelValue(10, "ETc (mm)")
                self.sheet1.SetColLabelValue(11, "ETcc (mm)")
                self.sheet1.SetColLabelValue(12, "SimIrrig (mm)")
                self.sheet1.SetColLabelValue(13, "Balance hídrico (mm)")
                self.sheet1.SetColLabelValue(14, "Humedad del suelo (mm)")
                self.sheet1.SetColLabelValue(15, "Escorrentía (mm)")
                self.sheet1.SetColLabelValue(16, "Riego (mm)")
                self.sheet1.SetColLabelValue(17, u"\N{GREEK CAPITAL LETTER PSI} tallo (MPa)")

                for i in range(len(self.Tm)):
                        self.sheet1.SetCellValue(i, 0, "%s" % self.Date[i].strftime('%d-%m-%Y'))
                        self.sheet1.SetCellValue(i, 1, "%0.2f" % self.Tm[i])
                        self.sheet1.SetCellValue(i, 2, "%0.2f" % self.Pp[i]) 
                        self.sheet1.SetCellValue(i, 3, "%0.2f" % self.ET0[i])
                        self.sheet1.SetCellValue(i, 4, "%0.2f" % self.SDG10[i])
                        self.sheet1.SetCellValue(i, 5, "%0.2f" % self.LAI[i])
                        self.sheet1.SetCellValue(i, 6, "%0.2f" % self.Kc[i])
                        self.sheet1.SetCellValue(i, 7, "%0.2f" % self.LWP[i])
                        self.sheet1.SetCellValue(i, 8, "%0.2f" % self.CropKc[i])
                        self.sheet1.SetCellValue(i, 9, "%0.2f" % self.Kcc[i])
                        self.sheet1.SetCellValue(i, 10, "%0.2f" % self.ETc[i])
                        self.sheet1.SetCellValue(i, 11, "%0.2f" % self.ETcc[i])
                        self.sheet1.SetCellValue(i, 12, "%0.2f" % self.SimIrrig[i])
                        self.sheet1.SetCellValue(i, 13, "%0.2f" % self.WB[i])
                        self.sheet1.SetCellValue(i, 14, "%0.2f" % self.SM[i])
                        self.sheet1.SetCellValue(i, 15, "%0.2f" % self.RunOff[i])
                        self.sheet1.SetCellValue(i, 16, "%0.2f" % self.Irrig[i])
                        self.sheet1.SetCellValue(i, 17, "%0.2f" % self.SWP[i])                                              

                self.notebookOutputs.AddPage(self.sheet1, "Resultados")
                self.menuSave.Enable(True) # Para habilitar menú para guardar planilla
                self.sheet1.SetFocus() # Poner foco sobre pestaña de resultados

                """----------Marco Gráficos----------"""
                # Definir gráfico
                self.fig = matplotlib.figure.Figure()
                self.gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1]) # Dos filas y una columna

                """----------Gráfico 1----------"""
                # Primer eje 'y':
                self.ax = self.fig.add_subplot(self.gs[0])
                self.ax.grid(color = "gray") #self.ax.grid(color="r", linestyle="-", linewidth=2)

                # Segundo eje 'y':
                self.ax2 = self.ax.twinx()
                
                a1, = self.ax.plot_date(x = self.Date, y = self.LAI, fmt="g-")
                a2, = self.ax.plot_date(x = self.Date, y = self.CropKc, fmt="r-")
                a3, = self.ax.plot_date(x = self.Date, y = self.Kcc, fmt="m-")
                a4, = self.ax2.plot_date(x = self.Date, y = self.SWP, fmt="-")

                # Leyenda:
                self.ax.legend([a1, a2, a3, a4], ["LAI", "Crop Kc", "Kcc", r"$\Psi$ Tallo"], prop={'size':11},bbox_to_anchor=(0., 1.02, 1., .102), loc = 3, ncol=4, mode="expand",)

                # Etiquetas plot: self.ax.set_title("Ejemplo")
                self.ax.set_ylabel(u"IAF (m\u00b2/m\u00b2), Crop Kc, Kcc")
                self.ax2.set_ylabel(r"$\Psi$ Tallo (MPa)") #u"text" para poner símbolos

                # Formato Fecha en eje x:
                monthsFmt = matplotlib.dates.DateFormatter('%b') # Formato sólo para meses
                self.ax.xaxis.set_major_formatter(monthsFmt) # Aplicar formato seleccionado

                """----------Gráfico 2----------"""
                self.ax = self.fig.add_subplot(self.gs[1], sharex = self.ax)
                self.ax.grid(color = "gray") #self.ax.grid(color="r", linestyle="-", linewidth=2)

                # Primer eje 'y':
                b1, = self.ax.plot_date(x = self.Date, y = self.ETcc, fmt="m-", label = "ETcc")
                b2, = self.ax.plot_date(x = self.Date, y = self.ETc, fmt="r-", label = "ETc")
                b3, = self.ax.plot_date(x = self.Date, y = self.Irrig, fmt="g-", label = "Riego")
                

                # Segundo eje 'y':
                self.ax2 = self.ax.twinx()
                b4, = self.ax2.plot_date(x = self.Date, y = self.Pp, fmt="b-", label = "Precipitaciones")
                b5, = self.ax2.plot_date(x = self.Date, y = self.RunOff, fmt="c-", label = "Escorrentía")
                b6, = self.ax2.plot_date(x = self.Date, y = self.SM, fmt="y-", label = "Humedad del suelo")

                # Fills
                self.ax.fill_between(self.Date, self.ETcc,0,color='m', alpha = 0.25)
                self.ax.fill_between(self.Date, self.ETc,0,color='r', alpha = 0.25)
                self.ax.fill_between(self.Date, self.Irrig,0,color='g', alpha = 0.25)
                self.ax2.fill_between(self.Date, self.Pp,0,color='b', alpha = 0.25)
                self.ax2.fill_between(self.Date, self.RunOff,0,color='c', alpha = 0.25)
                self.ax2.fill_between(self.Date, self.SM,0,color='y', alpha = 0.25)

                # Leyenda:
                self.ax.legend([b1, b2, b3, b4, b5, b6], ["ETcc", "ETc", "Riego", "Precip.", "Escorr.", "H. Suelo"], prop={'size':11},bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=6, mode="expand")
                
                # Etiquetas plot: self.ax.set_title("Ejemplo")
                self.ax.set_xlabel("Fecha")
                self.ax.set_ylabel(u"ETcc, ETc, Riego (mm)") #u"text" para poner símbolos
                self.ax2.set_ylabel(u"Precip., Escorr., H. Suelo (mm)") #u"text" para poner símbolos

                # Formato Fecha en eje x:
                monthsFmt = matplotlib.dates.DateFormatter('%b') # Formato sólo para meses
                self.ax.xaxis.set_major_formatter(monthsFmt) # Aplicar formato seleccionado

                # Parámetros para ajustar distancia entre los subplots:
                self.fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.30)

                """----------Pestaña 2----------""" 
                # Pestaña 2
                self.sheet2 = wx.ScrolledWindow(self.notebookOutputs,wx.ID_ANY)# Futuro gráfico en ventana con barras
                self.sheet2.SetScrollbars(20, 20, 50, 50)

                # Definir canvas:
                self.canvasPlot = FigCanvas(self.sheet2, -1, self.fig)
                self.toolbar = NavigationToolbar(self.canvasPlot)
                self.toolbar.Realize()
                sizer = wx.BoxSizer(wx.VERTICAL) # Caja para gráfico y barra de herramientas
                sizer.Add(self.canvasPlot, 1, wx.ALL|wx.EXPAND, 5)
                sizer.Add(self.toolbar, 0 , wx.LEFT | wx.EXPAND)
                self.sheet2.SetSizer(sizer) # Tamaño caja correspondiente a la pestaña
                self.notebookOutputs.AddPage(self.sheet2, " Gráficos ") # Crear pestaña con gráfico

                self.SetWindowStyle(self.GetWindowStyle()| wx.MAXIMIZE_BOX | wx.RESIZE_BORDER) # Actualizar style de la frame (self)
                self.book.release_resources()
        else:
            dlg = wx.MessageDialog(self.panelInputs, "El archivo no tiene hoja 'Input'!", "Advertencia", wx.ICON_ERROR)
            dlg.ShowModal() 
            dlg.Destroy()

    def OnInputs(self, event):
        try:
            self.frameInputs.Show() # Si existe ventana de Inputs lo muestra nuevamente
        except AttributeError: # Si no existe, la crea: reconoce que 'MainWindow', self, no posee el atributo 'frameInputs' ("AttributeError")
            self.frameInputs = wx.Frame(self, wx.ID_ANY, "Entradas", size=(500,380), style= wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX) # Crear Frame, style: para Frame de tamaño fijo

            # Agregar ícono:
            self.ib = wx.IconBundle()
            self.ib.AddIconFromFile("inia_logo.ico", wx.BITMAP_TYPE_ANY)
            self.frameInputs.SetIcons(self.ib)
            
            self.panelInputs = wx.Panel(self.frameInputs, wx.ID_ANY) # Crear panel de ENTRADAS dentro frame

            # Marco Archivo:
            self.archivo = wx.StaticBox(self.panelInputs, label="Archivo: ")
            self.boxsizer1 = wx.StaticBoxSizer(self.archivo, wx.HORIZONTAL)

            self.excelfile = wx.TextCtrl(self.panelInputs, -1, "Ingresar archivo", size = (250,10))
            self.button = wx.Button(self.panelInputs, id=wx.ID_ANY, label="Buscar")
            self.button.Bind(wx.EVT_BUTTON, self.onOpenFile)

            self.boxsizer1.AddSpacer(8) #Agrega espacio
            self.boxsizer1.Add(self.excelfile, flag=wx.EXPAND|wx.CENTER)
            self.boxsizer1.AddSpacer(8) #Agrega espacio
            self.boxsizer1.Add(self.button, flag=wx.EXPAND|wx.CENTER)

            # Marco Modelo:
            self.modelo = wx.StaticBox(self.panelInputs, label="Modelo: ")
            self.boxsizer3 = wx.StaticBoxSizer(self.modelo, wx.HORIZONTAL)
            self.button = wx.Button(self.panelInputs, id=wx.ID_ANY, label="    Correr VSIM   ")
            self.button.Bind(wx.EVT_BUTTON, self.ActRun)
            self.boxsizer3.Add(self.button, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT)

            # Pestañas Parámetros:     
            self.notebook = wx.Notebook(self.panelInputs, -1, style=wx.NB_TOP) # Creando Pestañas 
            self.panelNb1 = wx.Panel(self.notebook, -1, style=wx.NO_BORDER) # Crear panel dentro notebook
            self.panelNb2 = wx.Panel(self.notebook, -1, style=wx.NO_BORDER) # Crear panel dentro notebook
            self.panelNb3 = wx.Panel(self.notebook, -1, style=wx.NO_BORDER) # Crear panel dentro notebook
            self.panelNb4 = wx.Panel(self.notebook, -1, style=wx.NO_BORDER) # Crear panel dentro notebook
            self.notebook.AddPage(self.panelNb1, "     Planta     ") # Agregar panel al notebook
            self.notebook.AddPage(self.panelNb2, "     Suelo     ") # Agregar panel al notebook
            self.notebook.AddPage(self.panelNb3, u"  Relaciones hídricas  ") # Agregar panel al notebook
            self.notebook.AddPage(self.panelNb4, "  Cultivo cobertera  ") # Agregar panel al notebook

            
            """Pestaña Planta ----------------------------------------------------------------------------"""
            # Marco Suma de Días Grados:
            self.SumDiaGra= wx.StaticBox(self.panelNb1, label="Suma días grados (SDG): ")
            self.boxsizerPanelNb10 = wx.StaticBoxSizer(self.SumDiaGra, wx.VERTICAL)
            
            self.etiquetaSDGb = wx.StaticText(self.panelNb1, 1, label = "SDG brotación: ")
            self.SDGb = wx.TextCtrl(self.panelNb1, 1, "865")


            self.etiquetaSDGmiaf = wx.StaticText(self.panelNb1, 1, label = "SDG máximo IAF: ")
            self.SDGmiaf = wx.TextCtrl(self.panelNb1, 1, "600")

            self.etiquetaSDGf = wx.StaticText(self.panelNb1, 1, label = "SDG10 caída hojas: ")
            self.SDGf = wx.TextCtrl(self.panelNb1, 1, "1630")

            self.boxsizerPanelNb10.Add(self.etiquetaSDGb, flag=wx.ALL, border = 5)
            self.boxsizerPanelNb10.Add(self.SDGb, flag=wx.LEFT, border=5)
            self.boxsizerPanelNb10.AddSpacer(10) #Agrega espacio
            self.boxsizerPanelNb10.Add(self.etiquetaSDGmiaf, flag=wx.ALL, border = 5)
            self.boxsizerPanelNb10.Add(self.SDGmiaf,flag=wx.LEFT, border=5)
            self.boxsizerPanelNb10.AddSpacer(10) #Agrega espacio
            self.boxsizerPanelNb10.Add(self.etiquetaSDGf, flag=wx.ALL, border = 5)
            self.boxsizerPanelNb10.Add(self.SDGf,flag=wx.LEFT, border=5)
            self.boxsizerPanelNb10.AddSpacer(10) #Agrega espacio

            # Marco Estructura vegetativa:2
            self.Phenotype= wx.StaticBox(self.panelNb1, label=u"Estructura vegetativa: ")
            self.boxsizerPanelNb11 = wx.StaticBoxSizer(self.Phenotype, wx.VERTICAL)

            self.etiquetaIAF = wx.StaticText(self.panelNb1, 1, label = u"Máximo IAF (m\u00b2/m\u00b2): ")
            self.MaxIAF = wx.TextCtrl(self.panelNb1, 1, "1.5")

            self.etiquetaRootDepth = wx.StaticText(self.panelNb1, 1, label = "Profundidad raíces (m):    ")
            self.RootDepth = wx.TextCtrl(self.panelNb1, 1, "0.305")

            self.boxsizerPanelNb11.Add(self.etiquetaIAF, flag=wx.ALL, border = 5)
            self.boxsizerPanelNb11.Add(self.MaxIAF, flag=wx.LEFT, border=5)
            self.boxsizerPanelNb11.AddSpacer(10) #Agrega espacio
            self.boxsizerPanelNb11.Add(self.etiquetaRootDepth, flag=wx.ALL, border = 5)
            self.boxsizerPanelNb11.Add(self.RootDepth, flag=wx.LEFT, border=5)
            self.boxsizerPanelNb11.AddSpacer(10) #Agrega espacio

            # Organizar en sizer:
            self.sizerPanelNb1 = wx.GridBagSizer(2, 17) # Sizer
            self.sizerPanelNb1.Add(self.boxsizerPanelNb10, pos=(1, 0), span=(1, 8), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT)
            self.sizerPanelNb1.Add(self.boxsizerPanelNb11, pos=(1, 8), span=(1, 6), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT)
            self.panelNb1.SetSizer(self.sizerPanelNb1) # Asociar Sizer al panel
            """-------------------------------------------------------------------------------------------"""

            """Pestaña Suelo -----------------------------------------------------------------------------"""
            
            # Marco Textura del suelo:
            self.TextSuelo= wx.StaticBox(self.panelNb2, label="Textura del suelo: ")
            self.boxsizerPanelNb20 = wx.StaticBoxSizer(self.TextSuelo, wx.VERTICAL)

            self.etiquetaSand = wx.StaticText(self.panelNb2, 1, label = "% de Arena: ")
            self.Sand = wx.TextCtrl(self.panelNb2, 1, "25")

            self.etiquetaClay = wx.StaticText(self.panelNb2, 1, label = "% de Arcilla: ")
            self.Clay = wx.TextCtrl(self.panelNb2, 1, "30")

            self.etiquetaGravel = wx.StaticText(self.panelNb2, 1, label = "% de Grava: ")
            self.Gravel = wx.TextCtrl(self.panelNb2, 1, "15")
            
            self.boxsizerPanelNb20.Add(self.etiquetaSand, flag=wx.ALL, border = 5)
            self.boxsizerPanelNb20.Add(self.Sand, flag=wx.LEFT, border=5)
            self.boxsizerPanelNb20.AddSpacer(10) #Agrega espacio
            self.boxsizerPanelNb20.Add(self.etiquetaClay, flag=wx.ALL, border = 5)
            self.boxsizerPanelNb20.Add(self.Clay, flag=wx.LEFT, border=5)
            self.boxsizerPanelNb20.AddSpacer(10) #Agrega espacio
            self.boxsizerPanelNb20.Add(self.etiquetaGravel, flag=wx.ALL, border = 5)
            self.boxsizerPanelNb20.Add(self.Gravel, flag=wx.LEFT, border=5)
            self.boxsizerPanelNb20.AddSpacer(10) #Agrega espacio

            # Marco Marco de Plantación:
            self.Planta= wx.StaticBox(self.panelNb2, label= u"Marco de plantación: ")
            self.boxsizerPanelNb21 = wx.StaticBoxSizer(self.Planta, wx.VERTICAL)

            self.etiquetaRowspace = wx.StaticText(self.panelNb2, 1, label = "Espacio entre hileras (m):")
            self.Rowspace = wx.TextCtrl(self.panelNb2, 1, "1.22")

            self.etiquetaVinespace = wx.StaticText(self.panelNb2, 1, label = "Espacio sobre hileras (m):")
            self.Vinespace = wx.TextCtrl(self.panelNb2, 1, "1.22")

            self.boxsizerPanelNb21.Add(self.etiquetaRowspace, flag=wx.ALL, border=5)
            self.boxsizerPanelNb21.Add(self.Rowspace, flag=wx.LEFT, border=5)
            self.boxsizerPanelNb21.AddSpacer(10) #Agrega espacio
            self.boxsizerPanelNb21.Add(self.etiquetaVinespace, flag=wx.ALL, border=5)
            self.boxsizerPanelNb21.Add(self.Vinespace, flag=wx.LEFT, border=5)
            self.boxsizerPanelNb21.AddSpacer(10) #Agrega espacio

            # Organizar en sizer:
            self.sizerPanelNb2 = wx.GridBagSizer(2, 17) # Sizer
            self.sizerPanelNb2.Add(self.boxsizerPanelNb20, pos=(1, 0), span=(1, 8), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT)
            self.sizerPanelNb2.Add(self.boxsizerPanelNb21, pos=(1, 8), span=(1, 6), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT)
            self.panelNb2.SetSizer(self.sizerPanelNb2) # Asociar Sizer al panel

            """-------------------------------------------------------------------------------------------"""

            """Pestaña relaciones hídricas ---------------------------------------------------------------"""
            
            # Marco Cultivo de cobertera:
            self.CulCob= wx.StaticBox(self.panelNb3, label= u"Potencial hídrico de tallo (\N{GREEK CAPITAL LETTER PSI}): ")
            self.boxsizerPanelNb30 = wx.StaticBoxSizer(self.CulCob, wx.VERTICAL)

            self.etiquetaLWP_KcMax = wx.StaticText(self.panelNb3, 1, label =    u"\N{GREEK CAPITAL LETTER PSI} para iniciar la reducción en Kc (Mpa): ")
            self.LWP_KcMax = wx.TextCtrl(self.panelNb3, 1, "0.5")

            self.etiquetaLWP_Kc0 = wx.StaticText(self.panelNb3, 1, label = u"\N{GREEK CAPITAL LETTER PSI} en el cual Kc = 0 (MPa): ")
            self.LWP_Kc0 = wx.TextCtrl(self.panelNb3, 1., "1.2")

            self.etiquetaOptLWP = wx.StaticText(self.panelNb3, 1, label = u"Óptimo \N{GREEK CAPITAL LETTER PSI} al medio día (MPa):                    ")
            self.OptLWP = wx.TextCtrl(self.panelNb3, 1, "0.9")

            self.boxsizerPanelNb30.Add(self.etiquetaLWP_KcMax, flag=wx.ALL, border = 5)
            self.boxsizerPanelNb30.Add(self.LWP_KcMax, flag=wx.LEFT, border=5)
            self.boxsizerPanelNb30.AddSpacer(10) #Agrega espacio
            self.boxsizerPanelNb30.Add(self.etiquetaLWP_Kc0, flag=wx.ALL, border = 5)
            self.boxsizerPanelNb30.Add(self.LWP_Kc0, flag=wx.LEFT, border=5)
            self.boxsizerPanelNb30.AddSpacer(10) #Agrega espacio
            self.boxsizerPanelNb30.Add(self.etiquetaOptLWP, flag=wx.ALL, border = 5)
            self.boxsizerPanelNb30.Add(self.OptLWP, flag=wx.LEFT, border=5)
            self.boxsizerPanelNb30.AddSpacer(10) #Agrega espacio

            self.sizerPanelNb3 = wx.GridBagSizer(2, 17) # Sizer
            self.sizerPanelNb3.Add(self.boxsizerPanelNb30, pos=(1, 1), span=(1, 8), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT)
            self.panelNb3.SetSizer(self.sizerPanelNb3) # Asociar Sizer al panel
            
            """-------------------------------------------------------------------------------------------"""

            """Pestaña cobertera vegetal -----------------------------------------------------------------"""
            
            # Marco Cultivo de cobertera:
            self.CulCob= wx.StaticBox(self.panelNb4, label="Parámetros cultivo: ")
            self.boxsizerPanelNb40 = wx.StaticBoxSizer(self.CulCob, wx.VERTICAL)

            self.etiquetaCCLastDay = wx.StaticText(self.panelNb4, 1, label = "Último día del cultivo: ")
            self.CCLastDay = wx.TextCtrl(self.panelNb4, 1, "150")

            self.etiquetaCC_cover = wx.StaticText(self.panelNb4, 1, label = "Fracción de la superficie del \n suelo cubierta por el cultivo: ")
            self.CC_cover = wx.TextCtrl(self.panelNb4, 1, "0.5")

            self.etiquetaCC_SMdeath = wx.StaticText(self.panelNb4, 1, label = "Fracción de la humedad suelo donde \n comienza la senescencia del cultivo:    ")
            self.CC_SMdeath = wx.TextCtrl(self.panelNb4, 1, "0.6")

            self.boxsizerPanelNb40.Add(self.etiquetaCCLastDay, flag=wx.ALL, border = 5)
            self.boxsizerPanelNb40.Add(self.CCLastDay, flag=wx.LEFT, border=5)
            self.boxsizerPanelNb40.AddSpacer(10) #Agrega espacio
            self.boxsizerPanelNb40.Add(self.etiquetaCC_cover, flag=wx.ALL, border = 5)
            self.boxsizerPanelNb40.Add(self.CC_cover, flag=wx.LEFT, border=5)
            self.boxsizerPanelNb40.AddSpacer(10) #Agrega espacio
            self.boxsizerPanelNb40.Add(self.etiquetaCC_SMdeath, flag=wx.ALL, border = 5)
            self.boxsizerPanelNb40.Add(self.CC_SMdeath, flag=wx.LEFT, border=5)
            self.boxsizerPanelNb40.AddSpacer(10) #Agrega espacio

            # Organizar en sizer:
            self.sizerPanelNb4 = wx.GridBagSizer(2, 17) # Sizer
            self.sizerPanelNb4.Add(self.boxsizerPanelNb40, pos=(1, 1), span=(1, 8), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT)
            self.panelNb4.SetSizer(self.sizerPanelNb4) # Asociar Sizer al panel
                        
            """-------------------------------------------------------------------------------------------"""

            # Dimensiones de gradilla
            self.sizer = wx.GridBagSizer(3, 4)
            self.line = wx.StaticLine(self.panelInputs) # Linea 
            self.sizer.Add(self.boxsizer1, pos=(1, 1), span=(1, 2), flag = wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT)
            self.sizer.Add(self.boxsizer3, pos=(1, 3), span=(1, 1), flag = wx.CENTER)
            self.sizer.Add(self.line, pos=(2, 1), span=(1, 4), flag = wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT)
            self.sizer.Add(self.notebook, pos=(3, 1), span=(1, 4), flag = wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT)
            
            self.panelInputs.SetSizer(self.sizer)
            self.frameInputs.CentreOnScreen() 
            self.frameInputs.Show(True)
            

    def OnOptions(self, event, Show = True):
     
        try:
            if Show == True:
                self.frameOptions.Show() # Si existe ventana de Inputs lo muestra nuevamente si se desea
            else:
                self.frameOptions.Show(False) 
        except AttributeError: # Si no existe, la crea: reconoce que 'MainWindow', self, no posee el atributo 'frameInputs' ("AttributeError")
            self.frameOptions = wx.Frame(self, wx.ID_ANY, "Opciones", size=(205,310), style= wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX) # Crear Frame, style: para Frame de tamaño fijo

            # Agregar ícono:
            self.ib = wx.IconBundle()
            self.ib.AddIconFromFile("inia_logo.ico", wx.BITMAP_TYPE_ANY)
            self.frameOptions.SetIcons(self.ib)
            
            self.panelOptions = wx.Panel(self.frameOptions, wx.ID_ANY) # Crear panel de ENTRADAS dentro frame

            # Boxsizer 1:
            self.opciones = wx.StaticBox(self.panelOptions)
            self.boxsizer1 = wx.StaticBoxSizer(self.opciones, wx.VERTICAL)

            self.Phenology = wx.CheckBox(self.panelOptions, label= "¿Simular Fenología?")
            self.Phenology.SetValue(False)

            self.AlterKc = wx.CheckBox(self.panelOptions, label= "¿Ajustar Kc al estrés hídrico?")
            self.AlterKc.SetValue(True)

            self.SimIrr = wx.CheckBox(self.panelOptions, label= "¿Simular el riego?")
            self.SimIrr.SetValue(True)

            self.etiquetaExtCoeff = wx.StaticText(self.panelOptions, 1, label = "Coeficiente de extinción (k): ")
            self.ExtCoeff = wx.TextCtrl(self.panelOptions, 1, "0.6")
      
            self.boxsizer1.AddSpacer(8) #Agrega espacio
            self.boxsizer1.Add(self.AlterKc, flag=wx.RIGHT)
            self.boxsizer1.AddSpacer(15) #Agrega espacio
            self.boxsizer1.Add(self.SimIrr, flag=wx.RIGHT)
            self.boxsizer1.AddSpacer(15) #Agrega espacio
            self.boxsizer1.Add(self.Phenology, flag=wx.RIGHT)
            self.boxsizer1.AddSpacer(15) #Agrega espacio
            self.boxsizer1.Add(self.etiquetaExtCoeff, flag=wx.CENTER)
            self.boxsizer1.Add(self.ExtCoeff, flag=wx.CENTER)
            self.boxsizer1.AddSpacer(15) #Agrega espacio

            # Boxsizer 2:
            self.Defecto = wx.StaticBox(self.panelOptions)
            self.boxsizer2 = wx.StaticBoxSizer(self.Defecto, wx.VERTICAL)

            self.button0 = wx.Button(self.panelOptions, id=wx.ID_ANY, label="Restaurar valores")
            self.button0.Bind(wx.EVT_BUTTON, self.RestoreDefaultSettings)

            self.boxsizer2.Add(self.button0, flag=wx.CENTER)
            
            # Boxsizer 3:
            self.AceptarCancelar = wx.StaticBox(self.panelOptions)
            self.boxsizer3 = wx.StaticBoxSizer(self.AceptarCancelar, wx.HORIZONTAL)
            
            self.button1 = wx.Button(self.panelOptions, id=wx.ID_ANY, label="Aceptar")
            self.button1.Bind(wx.EVT_BUTTON, self.OptionsHide)

            self.button2 = wx.Button(self.panelOptions, id=wx.ID_ANY, label="Cancelar")
            self.button2.Bind(wx.EVT_BUTTON, self.OptionsKill)
            self.boxsizer3.Add(self.button1, flag=wx.CENTER)
            self.boxsizer3.AddSpacer(15) #Agrega espacio
            self.boxsizer3.Add(self.button2, flag=wx.CENTER)
            
            # Dimensiones de gradilla
            self.sizer = wx.GridBagSizer(3, 1)
            self.sizer.Add(self.boxsizer1, pos=(1, 1), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT)
            self.sizer.Add(self.boxsizer2, pos=(2, 1), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT)
            self.sizer.Add(self.boxsizer3, pos=(3, 1), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT)

            self.panelOptions.SetSizer(self.sizer)
            self.frameOptions.CentreOnScreen() 
            self.frameOptions.Show(Show)

    def OptionsHide(self, event):
            self.frameOptions.Hide()

    def OptionsKill(self, event):
            self.frameOptions.Close()
            
    def RestoreDefaultSettings(self, event):
            self.Phenology.SetValue(False)
            self.AlterKc.SetValue(True)
            self.SimIrr.SetValue(True)
            self.ExtCoeff.SetValue("0.6")

    def OnAboutBox(self, event):
        
        description = """VSIMpy es un modelo de gestión vitivinícola...
            VSIMpy fue escrito en Python 2.7.3"""

        licence = """VSIMpy es un software libre y viene sin GARANTIA ALGUNA.
            Usted puede redistribuirlo bajo ciertas circunstancias.
            Vea la Licencia Pública General de GNU para más detalles. Usted debe haber
            recibido una copia de la Licencia Pública General de GNU junto con VSIMpy"""

        info = wx.AboutDialogInfo()

        info.SetIcon(wx.Icon('inia_logo.png', wx.BITMAP_TYPE_PNG))
        info.SetName('VSIMpy')
        info.SetVersion('1.0')
        info.SetDescription(description)
        info.SetCopyright(u'(C) 2012-13 Miembros del Grupo de Escalamiento. \n Fotografía: gentiliza del Ing. Agr. Alexis Vergara.')
        info.SetWebSite('http://www.inia.cl/')
        info.SetLicence(licence)
        info.AddDeveloper('Miembros del Grupo de Escalamiento.')

        wx.AboutBox(info)  

    def OnOpen(self,event):
        os.popen("Manual.pdf")
        
"""-------------------------"""
"""---CORRER APLICACIONES---"""
"""-------------------------"""

#Splash:
app0 = wx.App(False)
splash = Splash()
app0.MainLoop()

#Frame más menús:
app1 = wx.App(False)
frame = MainWindow(None, title = "VSIMpy 1.0")
frame.CentreOnScreen() #Centrar aplicación 
app1.MainLoop()



