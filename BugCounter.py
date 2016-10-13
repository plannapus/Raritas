# -*- coding: utf-8 -*-

import os, time, csv, math, sys, re
import wx
import wx.html
import wx.lib.mixins.listctrl as listmix
import matplotlib
matplotlib.use('wxagg')
import matplotlib.pyplot as plt

class CountingFrame(wx.Frame):
    def __init__(self, parent, title, config):
        wx.Frame.__init__(self, parent, size=(1000,1000), title="Bug Counter")
        self.panel = wx.Panel(self)

        #Instantiating variables
        self.n_track = 1
        self.last_normal_track = 1
        self.selection = []
        self.mode = 'normal'
        self.specimens = 0
        self.dirname = os.path.dirname(os.path.realpath(config['Taxa File']))
        self.All = []
        self.metadata = config

        #Reading taxa file
        taxafile = csv.reader(open(config['Taxa File'],'rUb'),delimiter='\t')
        keys = taxafile.next()
        for i in taxafile:
            b = {}
            for k,v in zip(keys,i):
                b[k] = v
            self.All.append(b)
        for d in self.All:
            d['species_name'] = d['Genus']+d['GQ']+' '+d['Species']+d['SQ']+' '+d['Subspecies']
            d['Normal Count'] = 0
            d['Estimated'] = ''
            d['Rare Count'] = 0
        species_on_button = [k['species_name'] for k in self.All if k['onButton']=='y']
        abbreviations = [k['abbreviation'] for k in self.All if k['onButton']=='y']
        N = len(species_on_button)
        n1 = round(math.sqrt(N))

        #Create Menubar
        menubar = wx.MenuBar()
        File = wx.Menu()
        File1 = File.Append(wx.ID_ANY, 'Load unfinished count')
        File2 = File.Append(wx.ID_ANY, 'Save unfinished count')
        File3 = File.Append(wx.ID_ANY, 'Save finished count')
        File4 = File.Append(wx.ID_EXIT, '&Quit\tCtrl+Q')
        View = wx.Menu()
        View1 = View.Append(wx.ID_ANY, 'Inspect entries')
        View2 = View.Append(wx.ID_ANY, 'Show Collector\'s curve')
        View3 = View.Append(wx.ID_ANY, 'Save Diversity data')
        View4 = View.Append(wx.ID_ANY, 'Help')
        menubar.Append(File, 'File')
        menubar.Append(View, 'View')
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.Continue, File1)
        self.Bind(wx.EVT_MENU, self.Save1, File2)
        self.Bind(wx.EVT_MENU, self.Save2, File3)
        self.Bind(wx.EVT_MENU, self.Quit, File4)
        self.Bind(wx.EVT_MENU, self.Inspect, View1)
        self.Bind(wx.EVT_MENU, self.SAC, View2)
        self.Bind(wx.EVT_MENU, self.Save3, View3)
        self.Bind(wx.EVT_MENU, self.Help, View4)

        #Build GUI
        BigSizer = wx.GridBagSizer(5,5)
        g1 = wx.GridSizer(n1,math.ceil(N/n1),1,1)
        self.button_map = {}
        for i in range(0, N):
            b = wx.Button(self.panel, wx.ID_ANY,name=species_on_button[i], label=abbreviations[i])
            b.Bind(wx.EVT_BUTTON, self.BClick)
            self.button_map[species_on_button[i]] = b
            g1.Add(b,1,wx.ALL|wx.EXPAND,3)
        BigSizer.Add(g1, pos=(0,0), span=(1,1), flag=wx.EXPAND)
        Groups = set([k['HigherTaxon'] for k in self.All])
        if ' ' in Groups: Groups.remove(' ')
        if '' in Groups: Groups.remove('')
        Gsizer = wx.FlexGridSizer(len(Groups),2,5,5)
        self.list_map = {}
        for z, i in enumerate(Groups):
            t = wx.StaticText(self.panel, label = i)
            Gsizer.Add(t)
            listsp = [k['species_name'] for k in self.All if k['HigherTaxon'] == i]
            l = wx.ComboBox(self.panel, z, size = (300,-1), choices=listsp, style=wx.CB_READONLY|wx.CB_DROPDOWN)
            l.Bind(wx.EVT_COMBOBOX,self.LSelect)
            self.list_map[i] = l
            l.SetSelection(-1)
            Gsizer.Add(l)
        for j in xrange(len(Groups)):
            Gsizer.AddGrowableRow(j)
        Gsizer.AddGrowableCol(1)
        BottomSizer = wx.GridBagSizer(5,5)
        BottomSizer.Add(Gsizer, pos=(0,0),span=(1,2),flag=wx.EXPAND)
        self.sel = wx.TextCtrl(self.panel, size = (400,200), value="\n".join(reversed([k['species'] for k in self.selection])), style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL)
        BottomSizer.Add(self.sel, pos=(0,3),span=(1,2), flag=wx.EXPAND)
        ColumnButtons = wx.GridBagSizer(10,10)
        self.t1 = wx.StaticText(self.panel, size = (150,25), label= 'Track %s' % self.n_track, style=wx.ALIGN_LEFT)
        self.t2 = wx.StaticText(self.panel, size = (150,25), label= '%s specimen' % self.specimens, style=wx.ALIGN_LEFT)
        b1 = wx.Button(self.panel, wx.ID_ANY, size=(100,25), label='Next Track')
        b1.Bind(wx.EVT_BUTTON, self.NextTrack)
        self.b2 = wx.Button(self.panel, wx.ID_ANY, size=(100,25), label='Rare Count Mode')
        self.b2.Bind(wx.EVT_BUTTON, self.RCM)
        b3 = wx.Button(self.panel, wx.ID_ANY, size=(100,25), label='Remove Last Entry')
        b3.Bind(wx.EVT_BUTTON, self.Remove)
        b4 = wx.Button(self.panel, wx.ID_ANY, size=(100,25), label='Add a species')
        b4.Bind(wx.EVT_BUTTON, self.AddSpecies)
        ColumnButtons.Add(self.t1, pos=(0,0))
        ColumnButtons.Add(self.t2, pos=(1,0))
        ColumnButtons.Add(b1, pos=(2,0),span=(1,2), flag=wx.EXPAND)
        ColumnButtons.Add(self.b2, pos=(3,0),span=(1,2), flag=wx.EXPAND)
        ColumnButtons.Add(b3, pos=(4,0),span=(1,2), flag=wx.EXPAND)
        ColumnButtons.Add(b4, pos=(5,0),span=(1,2), flag=wx.EXPAND)
        BottomSizer.Add(ColumnButtons, pos=(0,6), span=(1,2), flag=wx.EXPAND)
        BottomSizer.Add((5,5),pos=(0,8))
        BottomSizer.Add((5,5),pos=(1,0))
        BottomSizer.AddGrowableCol(3)
        BottomSizer.AddGrowableCol(4)
        BigSizer.Add(BottomSizer,pos=(1,0), span=(5,1), flag=wx.EXPAND)
        BigSizer.AddGrowableRow(0)
        BigSizer.AddGrowableRow(1)
        BigSizer.AddGrowableCol(0)
        widthB, heightB = [math.ceil(N/n1)*105, n1*25]
        widthR, heightR = [1050,260]
        self.SetSize((max([widthB, widthR]),heightB+heightR))
        self.panel.SetSizer(BigSizer)
        self.panel.Layout()
        minSize = self.GetSize()
        self.SetMinSize(minSize)
        self.Show(True)

    def AddSpecies(self, event):
        nsd = NewSpeciesDialog(self, self.list_map)
        if nsd.ShowModal() == wx.ID_OK:
            d = {'Species': nsd.species.GetValue(),
                      'SQ': nsd.sq.GetValue(),
                      'Genus': nsd.genus.GetValue(),
                      'GQ': nsd.gq.GetValue(),
                      'Subspecies': nsd.subspecies.GetValue(),
                      'HigherTaxon': nsd.higher.GetValue(),
                      'Author': nsd.author.GetValue(),
                      'Comment': nsd.comment.GetValue(),
                      'onButton':'n',
                      'abbreviation': '',
                      'Normal Count': 0,
                      'Estimated': '',
                      'Rare Count': 0,
                      'species_name': nsd.genus.GetValue()+nsd.gq.GetValue()+' '+nsd.species.GetValue()+nsd.sq.GetValue()+' '+nsd.subspecies.GetValue()
                     }
            self.All.append(d)
            widg_to_mod = self.list_map[d['HigherTaxon']]
            widg_to_mod.Append(d['species_name'])
        nsd.Destroy()

    def BClick(self, event): #What happens when clicking a button
        button = event.GetEventObject()
        d = button.GetName()
        self.selection.append({'species':d, 'track':self.n_track, 'mode':self.mode})
        self.specimens += 1
        if self.specimens > 1:
            sp_text = '%s specimens' % self.specimens
        else:
            sp_text = '%s specimen' % self.specimens
        self.t2.SetLabel(sp_text)
        self.sel.SetValue("\n".join(reversed([k['species'] for k in self.selection])))

    def LSelect(self,event): #What happens when choosing from the list
        d = event.GetString()
        if [k['Estimated'] for k in self.All if k['species_name']==d][0] != '*':
            self.specimens += 1
            self.selection.append({'species':d, 'track':self.n_track, 'mode':self.mode})
            if self.specimens > 1:
                sp_text = '%s specimens' % self.specimens
            else:
                sp_text = '%s specimen' % self.specimens
            self.t2.SetLabel(sp_text)
            self.sel.SetValue("\n".join(reversed([k['species'] for k in self.selection])))
        else:
            self.sel.SetValue("!Species estimated in rare count mode\n"+"\n".join(reversed([k['species'] for k in self.selection])))
        event.GetEventObject().SetSelection(-1)

    def NextTrack(self, event): #What happens at track change
    	if self.mode == 'normal':
            track_content = [k for k in self.selection if k['track']==self.n_track]
            for i in self.All:
                i['Normal Count'] += len([k for k in track_content if k['species'] == i['species_name']])
            self.n_track += 1
    	if self.mode == 'rare':
            track_content = [k for k in self.selection if k['track']==self.n_track]
            estimated = 0
            for i in self.All:
                if i['Estimated']=='*':
                    estimated_i = math.ceil(i['Normal Count']/self.last_normal_track)
                    i['Rare Count'] += estimated_i
                    estimated += estimated_i
                else:
                    i['Rare Count'] += len([k for k in track_content if k['species'] == i['species_name']])
            self.specimens += int(estimated)
            self.n_track += 1
        self.t2.SetLabel('%s specimens' % self.specimens)
        self.t1.SetLabel('Track %s' % self.n_track)

    def RCM(self,event): #Switching to Rare Count Mode
        self.mode = 'rare'
        list_d =[]
        for i in self.All:
            i['Normal Count'] = len([k for k in self.selection if k['species'] == i['species_name'] and k['mode']=='normal'])
            i['Percentage'] = float(i['Normal Count'])*100/float(len(self.selection))
            list_d.append((i['species_name'],i['Normal Count'], str(round(i['Percentage'],3))+' %'))
        list_d.sort(key= lambda x: -x[1])
        LST = [k[0]+'    '+str(k[2]) for k in list_d]
        dlg = wx.MultiChoiceDialog(self,"Pick species to exclude from Rare Count mode","Rare Count Mode", LST)
        if (dlg.ShowModal() == wx.ID_OK):
            selections = dlg.GetSelections()
            strings = [list_d[x][0] for x in selections]
            for j in self.All:
                if j['species_name'] in strings:
                    j['Estimated'] = '*'
            for i,b in self.button_map.items():
                if i in strings:
                    b.Enable(False)
            self.last_normal_track = self.n_track
            self.n_track += 1
            self.t1.SetLabel('Track %s' % self.n_track)
            self.b2.Enable(False)

    def Remove(self, event): #Removing last entry
        self.selection.pop()
        self.specimens -= 1
        self.t2.SetLabel('%s specimens' % self.specimens)
        self.sel.SetValue("\n".join(reversed([k['species'] for k in self.selection])))

    def Continue(self, event): #Load unfinished count
        wildcard = "Tab-separated files (*.csv)|*.csv"
        dlg = wx.FileDialog(self, 'Choose your file', self.dirname, wildcard=wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            openfile = dlg.GetPath()
            a = csv.reader(open(openfile,'r'),delimiter='\t')
            self.selection = []
            for i in a:
                if ' estimated' not in i[1]:
                    self.selection.append({'species':i[1], 'track':int(i[0]), 'mode':i[2]})
                else:
                    sp = i[1].split(' estimated')
                    for j in [k for k in self.All if k['species_name']==sp]:
                        j['Estimated'] = '*'
            self.n_track = max([k['track'] for k in self.selection])
            for i in self.All:
                i['Normal Count'] = len([k for k in self.selection if k['species'] == i['species_name'] and k['mode']=='normal'])
            estimated = 0
            if 'rare' in [k['mode'] for k in self.selection]:
                self.mode = 'rare'
                self.last_normal_track = max([k['track'] for k in self.selection if k['mode']=='normal'])
                for i in self.All:
                    if i['Estimated']=='*':
                        estimated_i = math.ceil(i['Normal Count']/self.last_normal_track)*(self.n_track-self.last_normal_track)
                        i['Rare Count'] += estimated_i
                        estimated += estimated_i
                    else:
                        i['Rare Count'] = len([k for k in self.selection if k['species'] == i['species_name'] and k['mode']=='rare'])
            self.specimens = len(self.selection) + estimated
            self.n_track += 1
            self.t2.SetLabel('%s specimens' % self.specimens)
            self.sel.SetValue("\n".join(reversed([k['species'] for k in self.selection])))
            self.t1.SetLabel('Track %s' % self.n_track)
        dlg.Destroy()

    def Save1(self, event): #Save unfinished count
        wildcard = "Tab-separated files (*.csv)|*.csv"
        dlg = wx.FileDialog(self, 'Choose your file', self.dirname, wildcard=wildcard, style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            savefile1 = dlg.GetPath()
            a = csv.writer(open(savefile1,'w'),delimiter='\t')
            for i in self.selection:
                a.writerow([i['track'],i['species'],i['mode']])
            if self.mode=='rare':
                for i in [k['species_name'] for k in self.All if k['Estimated']=='*']:
                    a.writerow(['',i+' estimated',''])
        dlg.Destroy()

    def Save2(self, event): #Save finished count in SOD-OFF format
        wildcard = "Tab-separated files (*.csv)|*.csv"
        dlg = wx.FileDialog(self, 'Choose your file for count data', self.dirname, wildcard=wildcard, style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            savefile2 = dlg.GetPath()
            a = csv.writer(open(savefile2,'w'),delimiter='\t')
            ord_keys = ['Genus','GQ','Species','SQ','Subspecies','Author','HigherTaxon','Comment','Normal Count', 'Rare Count', 'Total', 'Estimated']
            if self.metadata['File Type:']=='O':
                a.writerow(['SOD-OFF v.:','2.0b1','File Type', 'O', 'Fossil Group', self.metadata['Fossil Group:'],'','','','','',''])
                a.writerow(['Source:','','','','','','','','','Site', self.metadata['Site'], ''])
                a.writerow(['Entered By:', self.metadata['Entered By:'], self.metadata['Entry Date:'],'Checked By:', '', '','','','','','Hole', self.metadata['Hole'],''])
                a.writerow(['Leg Info:', self.metadata['Leg'],'', '', '', '', '', '', '', 'Core', self.metadata['Core'],''])
                a.writerow(['', '', '', '', '', '', '', '', '', 'Section', self.metadata['Section'],''])
                a.writerow(['Occurrences:', 'C', '', '', '', '', '', '', '', 'Interval', self.metadata['Interval'],''])
                a.writerow(['Comments:',str(self.n_track)+' tracks observed', '', '', '', '', '', '', '', 'Depth(mbsf)', '',''])
                a.writerow(['','', '', '', '', '', '', '', '', 'Abundance', '',''])
                a.writerow(['', '', '', '', '', '', '', '', '', 'Preservation', '',''])
            elif self.metadata['File Type:']=='L':
                a.writerow(['SOD-OFF v.:','2.0b1','File Type', 'L', 'Fossil Group', self.metadata['Fossil Group:'],'','','','','',''])
                a.writerow(['Source ID:','','Source Citation:','','Comments:','','','','','Formation', self.metadata['Formation'], ''])
                a.writerow(['Entered By:', self.metadata['Entered By:'], 'Occ. D.type:', 'C', 'Key:','','','','','Sample Name', self.metadata['Sample Name'],''])
                a.writerow(['Entry Date', self.metadata['Entry Date:'],'Country:', self.metadata['Country'], '', '', '', '', '', 'Lithology', '',''])
                a.writerow(['Checked By:', '', 'Latitude', self.metadata['Latitude'], '', '', '', '', '', 'Age', self.metadata['Age'],''])
                a.writerow(['Check Date:', '', 'Longitude', self.metadata['Longitude'], '', '', '', '', '', 'Zone', self.metadata['Zone'],''])
                a.writerow(['Uploaded by:', '', 'scale', '', '', '', '', '', '', 'meter level', self.metadata['meter level'],''])
                a.writerow(['Upload Date:', '', '', '', '', '', '', '', '', 'Abundance', '',''])
                a.writerow(['', '', '', '', '', '', '', '', '', 'Preservation', '',''])
            a.writerow(ord_keys)
            if self.n_track in [k['track'] for k in self.selection]:
                if self.mode == 'normal':
                    track_content = [k for k in self.selection if k['track']==self.n_track]
                    for i in self.All:
                        i['Normal Count'] += len([k for k in track_content if k['species'] == i['species_name']])
                if self.mode == 'rare':
                    track_content = [k for k in self.selection if k['track']==self.n_track]
                    estimated = 0
                    for i in self.All:
                        if i['Estimated']=='*':
                            estimated_i = math.ceil(i['Normal Count']/self.last_normal_track)
                            i['Rare Count'] += estimated_i
                            estimated += estimated_i
                        else:
                            i['Rare Count'] += len([k for k in track_content if k['species'] == i['species_name']])
                    self.specimens += estimated
            for i in self.All:
                i['Total'] =i['Normal Count']+i['Rare Count']
                a.writerow([i[k] for k in ord_keys])
            savefile3 = os.path.join(os.path.dirname(savefile2),'Div_'+os.path.basename(savefile2))
            b = csv.writer(open(savefile3,'w'),delimiter='\t')
            b.writerow(('Specimens','Species'))
            x,y = self.ComputeDiv(self.selection,self.All,self.last_normal_track)
            p = zip(x,y)
            for i in p:
                b.writerow(i)
        dlg.Destroy()

    def ComputeDiv(self,selection, All, last_normal_track):
        x = [0,]
        y = [0,]
        sp = []
        for i in xrange(len(selection)-1):
            x.append(x[-1]+1)
            if selection[i]['species'] not in sp:
                sp.append(selection[i]['species'])
                y.append(y[-1]+1)
            else:
                y.append(y[-1])
            if selection[i]['mode']=='rare' and selection[i]['track']!=selection[i+1]['track']:
                EstimatedSpecimens = math.ceil(sum([k['Normal Count'] for k in All if k['Estimated']=='*'])/last_normal_track)
                x.append(x[-1]+EstimatedSpecimens)
                y.append(y[-1])
        x.append(x[-1]+1)
        if self.selection[-1]['species'] not in sp:
            sp.append(selection[-1]['species'])
            y.append(y[-1]+1)
        else:
            y.append(y[-1])

        return([x,y])

    def SAC(self, event):
        x,y = self.ComputeDiv(self.selection,self.All,self.last_normal_track)
        plt.plot(x, y, color='red', marker='o')
        plt.ylabel('Number of Species')
        plt.xlabel('Number of Specimens')
        plt.title('Collector\'s curve')
        plt.show()
        self.Show(True)

    def Inspect(self, event):
        ins = InspectFrame(None, title='Specimens counted', data1=self.All)

    def Save3(self, event): #Unchecked
        wildcard = "Tab-separated files (*.csv)|*.csv"
        dlg = wx.FileDialog(self, 'Choose your file', self.dirname, wildcard=wildcard, style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            savefile3 = dlg.GetPath()
            a = csv.writer(open(savefile3,'w'),delimiter='\t')
            a.writerow(('Specimens','Species'))
            x,y = self.ComputeDiv(self.selection,self.All,self.last_normal_track)
            p = zip(x,y)
            for i in p:
                a.writerow(i)
        dlg.Destroy()

    def Quit(self,event):
        self.Close()

    def Help(self,event):
        help = HelpFrame(None)

class NewSpeciesDialog(wx.Dialog):
    def __init__(self, parent, list_map):
        wx.Dialog.__init__(self, parent, -1, 'Add new species to the list', size=(400,180))
        flex = wx.FlexGridSizer(9,2,5,5)
        flex.Add(wx.StaticText(self, label= ' Genus: ', style=wx.ALIGN_LEFT))
        self.genus = wx.TextCtrl(self, size=(300,-1))
        flex.Add(self.genus)
        flex.Add(wx.StaticText(self, label= ' Genus Qualifier: ', style=wx.ALIGN_LEFT))
        self.gq = wx.TextCtrl(self, size=(300,-1))
        flex.Add(self.gq)
        flex.Add(wx.StaticText(self, label= ' Species: ', style=wx.ALIGN_LEFT))
        self.species = wx.TextCtrl(self, size=(300,-1))
        flex.Add(self.species)
        flex.Add(wx.StaticText(self, label= ' Species Qualifier: ', style=wx.ALIGN_LEFT))
        self.sq = wx.TextCtrl(self, size=(300,-1))
        flex.Add(self.sq)
        flex.Add(wx.StaticText(self, label= ' Subspecies: ', style=wx.ALIGN_LEFT))
        self.subspecies = wx.TextCtrl(self, size=(300,-1))
        flex.Add(self.subspecies)
        flex.Add(wx.StaticText(self, label= ' HigherTaxon: ', style=wx.ALIGN_LEFT))
        self.higher = wx.ComboBox(self, size=(300,-1), choices=list_map.keys(), style=wx.CB_READONLY|wx.CB_DROPDOWN)
        flex.Add(self.higher)
        flex.Add(wx.StaticText(self, label= ' Author: ', style=wx.ALIGN_LEFT))
        self.author = wx.TextCtrl(self, size=(300,-1))
        flex.Add(self.author)
        flex.Add(wx.StaticText(self, label= ' Comment: ', style=wx.ALIGN_LEFT))
        self.comment = wx.TextCtrl(self, size=(300,-1))
        flex.Add(self.comment)
        hor = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, wx.ID_OK, "OK")
        okButton.SetDefault()
        hor.Add(okButton)
        hor.Add((20,20))
        cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        hor.Add(cancelButton)
        flex.Add((20,20))
        flex.Add(hor)
        flex.AddGrowableCol(1)
        self.SetSizerAndFit(flex)
        self.Layout()

class InspectFrame(wx.Frame, listmix.ColumnSorterMixin):
    def __init__(self, parent, title, data1):
        wx.Frame.__init__(self, parent, size=(750,500), title="Entries so far")
        panel = wx.Panel(self, wx.ID_ANY)
        self.index = 0
        warning = wx.StaticText(panel, label='Warning: This list only updates once every track.', style=wx.ALIGN_CENTER)
        self.list_ctrl = wx.ListCtrl(panel, size=(-1,450), style = wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_SORT_DESCENDING)
        self.list_ctrl.InsertColumn(0,'Species')
        self.list_ctrl.InsertColumn(1,'Normal Count')
        self.list_ctrl.InsertColumn(2,'Rare Count')
        self.list_ctrl.InsertColumn(3,'Total')
        self.list_ctrl.InsertColumn(4,'Percentage')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(warning)
        sizer.Add(self.list_ctrl, 0, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)
        list_d ={}
        ind = 0
        for i in data1:
            total =i['Normal Count']+i['Rare Count']
            percent = float(total)*100/float((sum([k['Normal Count'] for k in data1])+sum([k['Rare Count'] for k in data1])))
            list_d[ind] = (i['species_name'],i['Normal Count'], i['Rare Count'], total, str(round(percent,3))+' %')
            ind +=1
        items = list_d.items()
        for key, data in items:
            self.list_ctrl.InsertStringItem(self.index, data[0])
            self.list_ctrl.SetStringItem(self.index, 1, str(data[1]))
            self.list_ctrl.SetStringItem(self.index, 2, str(data[2]))
            self.list_ctrl.SetStringItem(self.index, 3, str(data[3]))
            self.list_ctrl.SetStringItem(self.index, 4, str(data[4]))
            self.list_ctrl.SetItemData(self.index, key)
            self.index += 1
        self.itemDataMap = list_d
        listmix.ColumnSorterMixin.__init__(self, 5)
        self.Show(True)
    def GetListCtrl(self):
        return self.list_ctrl

class HelpFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, size=(800,500))
        html = wx.html.HtmlWindow(self)
        if getattr(sys, 'frozen', False):
            if re.search('/Contents/',sys.executable):
                PATH = os.path.join(re.sub('/MacOS.+','',sys.executable),'Resources')
            else:
                PATH = os.path.dirname(sys.executable)
        else:
            PATH = os.path.dirname(os.path.realpath(__file__))
        html.LoadFile(os.path.join(PATH,'help.html'))
        self.Show()

class StartingFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, size= (600,250), title='BugCounter')
        #Preparing files
        self.config = {}
        self.configfile = os.path.join(os.path.expanduser('~'),"bugconfig.txt")
        self.filename = ''
        if os.path.exists(self.configfile):
            a = csv.reader(open(self.configfile,'r'),delimiter='\t')
            for i in a:
                if len(i)>1:
        		  self.config[i[0]] = i[1]
        #Create Menubar
        menubar = wx.MenuBar()
        File = wx.Menu()
        File1 = File.Append(wx.ID_EXIT, '&Quit\tCtrl+Q')
        View = wx.Menu()
        View1 = View.Append(wx.ID_ANY, 'Help')
        menubar.Append(File, 'File')
        menubar.Append(View, 'View')
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.Quit, File1)
        self.Bind(wx.EVT_MENU, self.Help, View1)
        #Building the GUI
        self.StartingPanel = wx.Panel(self)
        topSizer = wx.GridBagSizer(5,5)
        sizerO = wx.GridBagSizer(5,5)
        sizerO.Add(wx.StaticText(self.StartingPanel, label='Entered By ', style=wx.ALIGN_CENTER), pos=(1,0))
        self.ent2 = wx.TextCtrl(self.StartingPanel, size=(150,-1))
        sizerO.Add(self.ent2, pos=(1,1), span=(1,2))
        sizerO.Add(wx.StaticText(self.StartingPanel, label='Entry date ', style=wx.ALIGN_CENTER), pos=(2,0))
        self.dat2 = wx.TextCtrl(self.StartingPanel, value= time.strftime("%d %b %Y"), size=(150,-1))
        sizerO.Add(self.dat2, pos=(2,1), span=(1,2))
        sizerO.Add(wx.StaticText(self.StartingPanel, label='Fossil Group ', style=wx.ALIGN_CENTER), pos=(3,0))
        self.fg2 = wx.TextCtrl(self.StartingPanel, size=(150,-1))
        sizerO.Add(self.fg2, pos=(3,1), span=(1,2))
        sizerO.Add(wx.StaticText(self.StartingPanel, label='Leg ', style=wx.ALIGN_CENTER),pos=(1,3))
        self.l2 = wx.TextCtrl(self.StartingPanel, size=(100,-1))
        sizerO.Add(self.l2, pos=(1,4), span=(1,2))
        sizerO.Add(wx.StaticText(self.StartingPanel, label='Site ', style=wx.ALIGN_CENTER), pos=(2,3))
        self.s2 = wx.TextCtrl(self.StartingPanel, size=(100,-1))
        sizerO.Add(self.s2, pos=(2,4), span=(1,2))
        sizerO.Add(wx.StaticText(self.StartingPanel, label='Hole ', style=wx.ALIGN_CENTER), pos=(3,3))
        self.h2 = wx.TextCtrl(self.StartingPanel, size=(100,-1))
        sizerO.Add(self.h2, pos=(3,4), span=(1,2))
        sizerO.Add(wx.StaticText(self.StartingPanel, label='Core ', style=wx.ALIGN_CENTER), pos=(1,6))
        self.c2 = wx.TextCtrl(self.StartingPanel, size=(100,-1))
        sizerO.Add(self.c2, pos=(1,7), span=(1,2))
        sizerO.Add(wx.StaticText(self.StartingPanel, label='Section ', style=wx.ALIGN_CENTER), pos=(2,6))
        self.sc2 = wx.TextCtrl(self.StartingPanel, size=(100,-1))
        sizerO.Add(self.sc2, pos=(2,7), span=(1,2))
        sizerO.Add(wx.StaticText(self.StartingPanel, label='Interval ', style=wx.ALIGN_CENTER), pos=(3,6))
        self.int2 = wx.TextCtrl(self.StartingPanel, size=(100,-1))
        sizerO.Add(self.int2, pos=(3,7), span=(1,2))
        topSizer.Add(sizerO, pos=(0,0), span=(3,1))
        sizButton1 = wx.GridBagSizer(5,5)
        sizButton2 = wx.GridBagSizer(5,5)
        tex = wx.StaticText(self.StartingPanel,label='Taxa Name File : ')
        self.filedir = wx.TextCtrl(self.StartingPanel, value=self.filename, size=(300,-1))
        but1 = wx.Button(self.StartingPanel,wx.ID_ANY, label='Find taxa name file')
        but1.Bind(wx.EVT_BUTTON, self.LookUp)
        but2 = wx.Button(self.StartingPanel,wx.ID_ANY, label='Start Counting')
        but2.Bind(wx.EVT_BUTTON, self.Start)
        sizButton1.Add(tex, pos=(0,0))
        sizButton1.Add(self.filedir, pos=(0,1),span=(1,4), flag=wx.EXPAND)
        sizButton1.Add(but1, pos=(0,5))
        sizButton2.Add(but2, pos=(0,0))
        topSizer.Add(sizButton1, pos=(4,0), span=(1,1),flag=wx.ALIGN_CENTER)
        topSizer.Add(sizButton2, pos=(6,0), span=(1,1),flag=wx.ALIGN_CENTER)
        if self.config.get('Entered By:',False): self.ent2.SetValue(self.config['Entered By:'])
        if self.config.get('Fossil Group:',False): self.fg2.SetValue(self.config['Fossil Group:'])
        if self.config.get('Leg',False): self.l2.SetValue(self.config['Leg'])
        if self.config.get('Site',False): self.s2.SetValue(self.config['Site'])
        if self.config.get('Hole',False): self.h2.SetValue(self.config['Hole'])
        if self.config.get('Section',False): self.sc2.SetValue(self.config['Section'])
        if self.config.get('Core',False): self.c2.SetValue(self.config['Core'])
        if self.config.get('Interval',False): self.int2.SetValue(self.config['Interval'])
        if self.config.get('Taxa File',False): self.filedir.SetValue(self.config['Taxa File'])
        self.StartingPanel.SetSizerAndFit(topSizer)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.StartingPanel, 1, wx.EXPAND|wx.ALIGN_CENTER)
        self.SetSizer(self.sizer)
        self.Show(True)

    def LookUp(self, event):
        self.dirname = os.path.dirname(os.path.realpath(self.filename))
        dlg = wx.FileDialog(self, 'Choose your file', self.dirname)
        if dlg.ShowModal() == wx.ID_OK:
            self.filedir.SetValue(dlg.GetPath())
        dlg.Destroy()

    def Start(self, event):
        # Save metadata
        filedir = self.filedir.GetValue()
        metadata = {'Entered By:':self.ent2.GetValue(),'Entry Date:':self.dat2.GetValue(),'File Type:':'O','Fossil Group:':self.fg2.GetValue(),'Leg':self.l2.GetValue(), 'Site':self.s2.GetValue(), 'Hole':self.h2.GetValue(), 'Core': self.c2.GetValue(), 'Section': self.sc2.GetValue(), 'Interval': self.int2.GetValue()}
        self.config = metadata
        self.config['Taxa File'] = filedir
        if os.path.exists(self.configfile):
            os.remove(self.configfile)
        a = csv.writer(open(self.configfile,'w'),delimiter='\t')
        for i, j in self.config.items():
            a.writerow([i,j])
        # Launch 2nd Frame
        w = CountingFrame(None, title='BugCounter', config = self.config)

    def Quit(self,event):
        self.Close()

    def Help(self,event):
        help = HelpFrame(None)

#Boilerplate
if __name__ == '__main__':
    app = wx.App(False)
    frame = StartingFrame(None)
    app.MainLoop()
