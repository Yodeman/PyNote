"""
A python/tkinter text file editor and component.
"""
import os, sys
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import Open, SaveAs, asksaveasfilename
from tkinter.messagebox import showerror, showinfo, askyesno
from tkinter.simpledialog import askstring, askinteger
from tkinter.colorchooser import askcolor
from p_python.GUI.Tools.guimaker import *

try:
    import textConfig
    configs = textConfig.__dict__
except:
    configs = {}

helptext = """PyNote
April, 2020

with the help of  Programming Python,
4th Edition.
Mark Lutz, O'Relly Media, Inc.

A text editor program embeddable object
component, written in Python/tkinter. Use
menu and Alt-keys shortcuts for menus.
"""

START = '1.0'
SEL_FIRST = SEL + '.first'
SEL_LAST = SEL + '.last'

FontScale = 0
if sys.platform == 'win':
    FontScale = 3

class TextEditor:
    startfiledir = '.'
    editwindows = []

    # Unicode configurations
    # imported in class to allow overrides in subclass or self

    if __name__ == "__main__":
        from textConfig import (openAskUser, 
                openEncoding, savesAskUser, 
                savesEncoding, savesUseKnownEncoding)

    else:
        from p_python.TextEditor.textConfig import (
            openEncoding, openEncoding, savesUseKnownEncoding,
            savesEncoding, savesAskUser)

    ftypes = [('All files', '*'),
              ('Text Documents (*.txt)', '*.txt'),
              ('Python files (*.py)', '.py')]

    colours = [{'fg':'black',       'bg':'white'},
              {'fg':'yellow',      'bg':'black'},
              {'fg':'white',       'bg':'blue'},
              {'fg':'black',       'bg':'beige'},
              {'fg':'yellow',      'bg':'purple'},
              {'fg':'black',       'bg':'brown'},
              {'fg':'lightgreen',  'bg':'darkgreen'},
              {'fg':'darkblue',    'bg':'orange'},
              {'fg':'orange',      'bg':'darkblue'}]

    fonts = [('courier',    9+FontScale,    'normal'),
             ('courier',    12+FontScale,   'normal'),
             ('courier',    10+FontScale,   'bold'),
             ('courier',    10+FontScale,   'italic'),
             ('times',      10+FontScale,   'normal'),
             ('helvetica',  10+FontScale,   'normal'),
             ('ariel',      10+FontScale,   'normal'),
             ('system',     10+FontScale,   'normal'),
             ('courier',    20+FontScale,   'normal')]
    def __init__(self, loadFirst='', loadEncode=''):
        if not isinstance(self, GuiMaker):
            raise TypeError('TextEditor needs a GuiMaker mixin')
        self.setFileName(None)
        #self.currfile = None
        self.lastFind = None
        self.openDialog = None
        self.saveDialog = None
        self.knownEncoding = None
        self.text.focus()

        if loadFirst:
            self.update()
            self.onOpen(loadFirst, loadEncode)

    def start(self):
        self.menuBar = [
            ('File', 0,
                [('New                                Ctrl+N', 0, self.onNew),
                 ('New Window      Ctrl+Shift+N', 1, self.onClone),
                 ('Open...                           Ctrl+O', 0, self.onOpen),
                 ('Save                                Ctrl+S', 0, self.onSave),
                 ('Save As...               Ctrl+Shif+S', 5, self.onSaveAs),
                 'separator',
                 ('Page Setup...        ', 2, self.notDone),
                 ('Print...                            Ctrl+P', 0, self.notDone),
                 ('Exit', 0, self.onQuit)
                 ]),
            ('Edit', 0,
                [('Undo                         Ctrl+Z', 0, self.onUndo),
                 'separator',
                 ('Cut                            Ctrl+X', 0, self.onCut),
                 ('Copy                         Ctrl+C', 0, self.onCopy),
                 ('Paste                         Ctrl+V', 0, self.onPaste),
                 ('Delete                           Del', 0, self.onDelete),
                 'separator',
                 ('Search with Bing...  Ctrl+E', 1, self.notDone),
                 ('Find...                        Ctrl+F', 0, self.onFind),
                 ('Find Next                        F3', 1, self.notDone),
                 ('Find Previous        Shift+F3', 1, self.notDone),
                 ('Replace...                 Ctrl+H', 0, self.onReplace),
                 ('Go To...                     Ctrl+G', 0, self.onGoto),
                 'separator',
                 ('Select All                   Ctrl+A', 0, self.onSelectAll),
                 ('Time/Date                        F5', 0, self.onTime)
                 ]),
            ('Format', 0,
                [('Word wrap            ', 0, self.notDone),
                 ('Font...', 0, self.onFont),
                 ('Pick Bg...', 0, self.onBg),
                 ('Pick Fg...', 0, self.onFg)
                 ]),
            ('View', 0,
                [('Zoom', 0,
                    [('Zoom In                          Ctrl+Plus', 1, self.notDone),
                     ('Zoom Out                   Ctrl+Minus', 1, self.notDone),
                     ('Restore Default Zoom       Ctrl+0', 1, self.notDone)]),
                 ('Status Bar', 0, self.notDone)
                 ]),
            ('Help', 0,
                [('View Help', 0, self.notDone),
                 ('Send Feedback', 0, self.notDone),
                 'separator',
                 ('About PyNote', 0, self.onAbout)
                 ])
            ]
    def makeWidgets(self):
        vbar = Scrollbar(self)
        hbar = Scrollbar(self, orient='horizontal')
        text = Text(self, padx=5, wrap='none')
        text.config(undo=1, autoseparators=1)

        vbar.pack(side=RIGHT, fill=Y)
        hbar.pack(side=BOTTOM, fill=X)

        text.pack(side=TOP, fill=BOTH, expand=YES)

        text.config(yscrollcommand = vbar.set)
        text.config(xscrollcommand = hbar.set)

        vbar.config(command = text.yview)
        hbar.config(command = text.xview)

        # apply user configurations or default
        startfont = configs.get('font', self.fonts[0])
        startbg = configs.get('bg', self.colours[0]['bg'])
        startfg = configs.get('fg', self.colours[0]['fg'])
        text.config(font=startfont, bg=startbg, fg=startfg)
        if 'height' in configs:
            text.config(height=configs['height'])
        if 'width' in configs:
            text.config(width=configs['width'])

        self.text = text

    # File menu commands
    def my_askopenfilename(self):
        if not self.openDialog:
            self.openDialog = Open(initialdir=self.startfiledir,
                                    filetypes=self.ftypes)
            return self.openDialog.show()
    
    def my_asksaveasfilename(self):
        if not self.saveDialog:
            self.saveDialog = SaveAs(initialdir=self.startfiledir,
                                     filetypes=self.ftypes)
            return self.saveDialog.show()
    
    def onOpen(self, loadFirst='', loadEncode=''):
        """
        Open file from system
        """
        if self.text.edit_modified():
            if not askyesno('PyNote', 'Save changes to file?'):
                return
            else:
                self.onSave()
                self.text.edit_modified(0)
        
        if not self.text.edit_modified():
            file = loadFirst or self.my_askopenfilename()
            if not file:
                return
            if not os.path.isfile(file):
                showerror('PyNote', 'Could not open file'+file)
                return
        
        # try known encoding if passed and acurate
        text = None
        if loadEncode:
            try:
                text = open(file, 'r', encoding=loadEncode).read()
                self.knownEncoding = loadEncode
            except (UnicodeError, LookupError, IOError):
                pass

        # try user input, prefill with next choice as default
        if text == None and self.openAskUser:
            self.update()
            askuser = askstring('PyNote', 'Enter Unicode encoding for open',
                                initialvalue=(self.openEncoding or 
                                sys.getdefaultencoding() or ''))

            if askuser:
                try:
                    text = open(file, 'r', encoding=askuser).read()
                    self.knownEncoding = askuser
                except (UnicodeError, LookupError, IOError):
                    pass
        
        #try config file
        if text == None and self.openEncoding:
            try:
                text = open(file, 'r', encoding=self.openEncoding).read()
                self.knownEncoding = self.openEncoding
            except (UnicodeError, LookupError, IOError):
                pass

        #try platform default
        if text == None:
            try:
                text = open(file, 'r', encoding=sys.getdefaultencoding()).read()
                self.knownEncoding = sys.getdefaultencoding()
            except (UnicodeError, LookupError, IOError):
                pass

        # last resort: use binary bytes and rely on Tk to decode
        if text == None:
            try:
                text = open(file, 'rb').read()
                text.replace(b'\r\n', b'\n')
                self.knownEncoding = None
            except IOError:
                pass
        
        if text == None:
            showerror('PyNote', 'Could not decode and open file' + file)
        else:
            self.setAllText(text)
            self.setFileName(file)
            self.text.edit_reset()
            self.text.edit_modified(0)

    def onSave(self):
        """
        save file to system
        """
        filename = self.currfile or self.my_asksaveasfilename()
        #print(filename)

        if filename == None:
            filename = asksaveasfilename(initialdir=self.startfiledir,
                                     filetypes=self.ftypes)
            #print(str(filename)+'1')
        
        text = self.getAllText()
        enpick = None

        if filename:
            # try known encoding at latest Open or Save, if any
            if self.knownEncoding and ((self.currfile and self.savesUseKnownEncoding >=1) or 
                                        (not self.currfile and self.savesUseKnownEncoding >=2)):

                try:
                    text.encode(self.knownEncoding)
                    enpick = self.knownEncoding
                except UnicodeError:
                    pass

            #try user input, prefill with known type, else next choice
            if not enpick and self.savesAskUser:
                self.update()
                askuser = askstring('PyNote', 'Enter unicode encoding for save',
                                    initialvalue = (self.knownEncoding or
                                                    self.savesEncoding or
                                                    sys.getdefaultencoding() or ''))
                if askuser:
                    try:
                        text.encode(askuser)
                        enpick = askuser
                    except (UnicodeError, LookupError):
                        pass

            #try config file
            if not enpick and self.savesEncoding:
                try:
                    text.encode(self.savesEncoding)
                    enpick = self.savesEncoding
                except (UnicodeError, LookupError):
                    pass

            #try platform default
            if not enpick:
                try:
                    text.encode(sys.getdefaultencoding())
                    enpick = sys.getdefaultencoding
                except (UnicodeError, LookupError):
                    pass

            # open in text mode for endlines + encoding
            if not enpick:
                showerror('PyNote', 'Could not encode for file'+filename)

            else:
                try:
                    file = open(filename, 'w', encoding=enpick)
                    file.write(text)
                    file.close()
                except:
                    showerror('PyNote', 'Could not save file'+filename)
                else:
                    self.setFileName(filename)
                    self.text.edit_modified(0)
                    self.knownEncoding = enpick

    def onSaveAs(self):
        """
        save file to system
        """
        filename = asksaveasfilename()

        if not filename:
            return
        
        text = self.getAllText()
        enpick = None

        # try known encoding at latest Open or Save, if any
        if self.knownEncoding and ((self.savesUseKnownEncoding >=1) or 
                                    ( self.savesUseKnownEncoding >=2)):

            try:
                text.encode(self.knownEncoding)
                enpick = self.knownEncoding
            except UnicodeError:
                pass

        #try user input, prefill with known type, else next choice
        if not enpick and self.savesAskUser:
            self.update()
            askuser = askstring('PyNote', 'Enter unicode encoding for save',
                                initialvalue = (self.knownEncoding or
                                                self.savesEncoding or
                                                sys.getdefaultencoding() or ''))
            if askuser:
                try:
                    text.encode(askuser)
                    enpick = askuser
                except (UnicodeError, LookupError):
                    pass

        #try config file
        if not enpick and self.savesEncoding:
            try:
                text.encode(self.savesEncoding)
                enpick = self.savesEncoding
            except (UnicodeError, LookupError):
                pass

        #try platform default
        if not enpick:
            try:
                text.encode(sys.getdefaultencoding())
                enpick = sys.getdefaultencoding
            except (UnicodeError, LookupError):
                pass

        # open in text mode for endlines + encoding
        if not enpick:
            showerror('PyNote', 'Could not encode for file'+filename)

        else:
            try:
                file = open(filename, 'w', encoding=enpick)
                file.write(text)
                file.close()
            except:
                showerror('PyNote', 'Could not save file'+filename)
            else:
                self.setFileName(filename)
                self.text.edit_modified(0)
                self.knownEncoding = enpick

    def onNew(self):
        """
        start editing a new file from scratch in current window;
        """
        if self.text.edit_modified():
            if not askyesno('PyNote', 'Discard changes made to file?'):
                return
        self.setFileName(None)
        self.clearAllText()
        self.text.edit_reset()
        self.text.edit_modified(0)
        self.knownEncoding = None

    def onClone(self):
        """
        open a new edit window
        """
        from p_python.launchmodes import PortableLauncher
        PortableLauncher('PyNote', 'PyNote.py')()


    def onQuit(self):
        assert False, 'onQuit must be defined in window specific subclass'

    #def text_edit_modified(self):
        #return self.te

    # Edit menu commands
    def onUndo(self):
        try:
            self.text.edit_undo()
        except TclError:
            pass

    def onRedo(self):
        try:
            self.text.edit_redo()
        except TclError:
            pass
    
    def onCopy(self):
        if not self.text.tag_ranges(SEL):
            pass
        else:
            text = self.text.get(SEL_FIRST, SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)

    def onDelete(self):
        if not self.text.tag_ranges(SEL):
            pass
        else:
            self.text.delete(SEL_FIRST, SEL_LAST)

    def onCut(self):
        if not self.text.tag_ranges(SEL):
            pass
        else:
            self.onCopy()
            self.onDelete()

    def onPaste(self):
        try:
            text = self.selection_get(selection='CLIPBOARD')
        except:
            pass
        self.text.insert(INSERT, text)
        self.text.tag_remove(SEL, '1.0', END)
        self.text.tag_add(SEL, INSERT+'%dc' %len(text), INSERT)
        self.text.see(INSERT)

    def onSelectAll(self):
        self.text.tag_add(SEL, '1.0', END+'-1c')
        self.text.mark_set(INSERT, '1.0')
        self.text.see(INSERT)

    def onGoto(self, forceline=None):
        """
        goes to a passes in line number
        """
        line = forceline or askinteger('PyNote', 'Enter line number')
        self.text.update()
        self.text.focus()
        if line is not None:
            maxindex = self.text.index(END+'-1c')
            maxline = int(maxindex.split('.')[0])
            if line > 0 and line <= maxline:
                self.text.mark_set(INSERT, '%d.0' %line)        # goto line
                self.text.tag_remove(SEL, '1.0', END)           # delete selects
                self.text.tag_add(SEL, INSERT, 'insert + 1l')   # select line
                self.text.see(INSERT)                           # scroll to line

            else:
                showerror('PyNote', 'line number is beyond total numbers of lines')

    def onFind(self, lastkey=None):
        """
        Finds particular passed word in text
        """
        key = lastkey or askstring('PyNote', 'Enter search string')
        self.text.update()
        self.text.focus()
        self.lastFind = key
        if key:
            nocase = configs.get('caseinsens', True)
            where = self.text.search(key, INSERT, END, nocase=nocase)
            if not where:
                showerror('PyNote', 'word not found')
            else:
                #pastkey = 
                #self.text.tag_remove(SEL, '1.0', END)       
                self.text.see(where)

    def onReplace(self):
        """
        non-modal find/replace dialog
        """
        new = Toplevel()
        new.title('PyNote-Replace')
        Label(new, text='Find', width=15).grid(row=0, column=0)
        Label(new, text='Replace', width=15).grid(row=1, column=0)
        entry1 = Entry(new)
        entry2 = Entry(new)
        entry1.grid(row=0, column=1, sticky=EW)
        entry2.grid(row=1, column=1, sticky=EW)

        def onFind():
            self.onFind(entry1.get())

        def onApply():
            self.onDoReplace(entry1.get(), entry2.get())

        ttk.Button(new, text='Find', command=onFind).grid(row=0, column=2, sticky=EW)
        ttk.Button(new, text='Replace', command=onApply).grid(row=1, column=2, sticky=EW)
        new.columnconfigure(1, weight=1)

    def onDoReplace(self, findtext, replace):
        # replace and find next
        if self.text.tag_ranges(SEL):
            self.text.delete(SEL_FIRST, SEL_LAST)
            self.text.insert(INSERT, replace)
            self.text.see(INSERT)
            self.onFind(findtext)
            self.text.update()

    def onTime(self):
        try:
            import time
            text = time.asctime()
        except:
            pass
        else:
            self.text.insert(END, text)
    
    # format menu command
    def onFont(self):
        """
        non-modal font input dialog
        """
        from p_python.GUI.shellgui.formrows import makeFormRow
        popup = Toplevel(self)
        popup.title('PyNote-font')
        var1 = makeFormRow(popup, label='Family', browse=False)
        var2 = makeFormRow(popup, label='Size', browse=False)
        var3 = makeFormRow(popup, label='Style', browse=False)
        var1.set('courier')
        var2.set('12')
        var3.set('bold italic')
        Button(popup, text='apply', command=
                        lambda:self.onDoFont(var1.get(), var2.get(), var3.get()))
        
    def onDoFont(self, family, size, style):
        try:
            self.text.config(font=(family, int(size), style))
        except:
            showerror('PyNote', 'Font is not registered.')

    def onFg(self):
        self.pickColour('fg')
    
    def onBg(self):
        self.pickColour('bg')

    def pickColour(self, part):
        (triple, hexstr) = askcolor()
        if hexstr:
            self.text.config(**{part:hexstr})

    def isEmpty(self):
        return not self.getAllText()

    def getAllText(self):
        return self.text.get('1.0', END+'-1c')

    def setAllText(self, text):
        self.text.delete('1.0', END)
        self.text.insert(END, text)
        self.text.mark_set(INSERT, '1.0')
        self.text.see(INSERT)

    def clearAllText(self):
        self.text.delete('1.0', END)

    def getFileName(self):
        return self.currfile

    def setFileName(self, name):
        self.currfile = name
        #self.filelabel.config

    def setKnownEncoding(self, encoding='utf-8'):
        self.knownEncoding = encoding

    def setBg(self, colour):
        self.text.config(bg=colour)

    def setFg(self, colour):
        self.text.config(fg=colour)

    def setFont(self, font):
        self.text.config(font=font)

    def setHeight(self, height):
        self.text.config(height=height)

    def setWidth(self, width):
        self.text.config(width=width)

    def clearModified(self):
        self.text.edit_modified(0)          # clear modified tag

    def isModified(self):
        return self.text.edit_modified()

    def onAbout(self):
        showinfo('About PyNote', helptext)

    def notDone(self):
        showerror('PyNote', 'Button not available')

class TextEditorMain(TextEditor, GuiMakerWindowMenu): 
    def __init__(self, parent=None, loadFirst='', loadEncode=''):
        GuiMaker.__init__(self, parent)
        TextEditor.__init__(self, loadFirst, loadEncode)
        self.title()
        self.master.iconname('pad')
        self.master.protocol('WM_DELETE_WINDOW', self.onQuit)
        TextEditor.editwindows.append(self)

    def title(self):
        if type(self.currfile) == str:
            name = os.path.basename(self.currfile).split('.')[0]
        else:
            name = self.currfile
        self.Title = name or 'Untitled' 
        self.master.title(self.Title+' - PyNote')
        self.after(1000, self.title)
    
    def onQuit(self):
        close = not self.text.edit_modified()   # check for modification
        if not close:
            close = askyesno('PyNote', 'Discard changes made to file?')
        if close:
            windows = TextEditor.editwindows
            changed = [w for w in windows if w != self and w.text.edit_modified()]
            if not changed:
                GuiMaker.quit(self)
            else:
                numchange = len(changed)
                verify = '%s other edit windows%s changed: quit and discard anyhow?'
                verify = verify %(numchange, 's' if numchange > 1 else '')
                if askyesno('PyNote', verify):
                    GuiMaker.quit(self)

class TextEditorMainPopup(TextEditor, GuiMakerWindowMenu):
    def __init__(self, parent=None, loadFirst='', loadEncode=''):
        self.popup = Toplevel(parent)
        GuiMaker.__init__(self, self.popup)
        TextEditor.__init__(self, loadFirst, loadEncode)
        assert self.master == self.popup
        self.popup.title('PyNote')
        self.popup.iconname('pad')
        self.popup.protocol('WM_DELETE_WINDOW', self.onQuit)
        TextEditor.editwindows.append(self)

    def onQuit(self):
        close = not self.text.edit_modified()
        if not close:
            close = askyesno('PyNote', 'Text changed: quit and discard changes?')
        if close:
            self.popup.destroy()
            TextEditor.editwindows.remove(self)
    
    def onClone(self):
        TextEditor.onClone(self)

class TextEditorComponent(TextEditor, GuiMakerFrameMenu):
    def __init__(self, parent=None, loadFirst='', loadEncode=''):
        GuiMaker.__init__(self, parent)
        TextEditor.__init__(self, loadFirst, loadEncode)

    def onQuit(self):
        close = not self.text.edit_modified()
        if not close:
            close = askyesno('PyNote', 'Text changed: quit and discard changes?')
        if close:
            self.destroy()

# standalone program run

def testPopup():
    root = Tk()
    TextEditorMainPopup(root)
    TextEditorMainPopup(root)
    Button(root, text='More', command=TextEditorMainPopup).pack(fill=X)
    Button(root, text='Quit', command=root.quit).pack(fill=X)
    root.mainloop()

def main():
    try:
        fname = sys.argv[1]
    except IndexError:
        fname = None
    TextEditorMain(loadFirst=fname).pack(expand=YES, fill=BOTH)
    mainloop()

if __name__ == '__main__':
    main()