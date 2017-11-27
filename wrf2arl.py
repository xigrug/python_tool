# -*- coding: utf-8 -*-
#~ #----------------------------------------------------------------------
#~ module:wlab
#~  Filename:wgetfilelist.py
#~  Function :
#~  def IsSubString(SubStrList,Str)
#~  def GetFileList(FindPath,FlagStr=[]):
#~  功能:读取指定目录下特定类型的文件名列表
#~  Data: 2013-08-08,星期四
#~  Author:吴徐平
#~  Email:wxp07@qq.com
#~ #----------------------------------------------------------------------
#~ #----------------------------------------------------------------------
# Author: Yaqiang Wang                                           
# Date: 2015-12-2                                            
# Purpose: Convert WRF out netCDF data to ARL data  
# Note: Sample                                                   
#-----------------------------------------------------------
#---- Set data folder

##########
import os
def IsSubString(SubStrList,Str):  
    ''' 
    #判断字符串Str是否包含序列SubStrList中的每一个子字符串 
    #>>>SubStrList=['F','EMS','txt'] 
    #>>>Str='F06925EMS91.txt' 
    #>>>IsSubString(SubStrList,Str)#return True (or False) 
    '''  
    flag=True  
    for substr in SubStrList:  
        if not(substr in Str):  
            flag=False  
  
    return flag  
#~ #----------------------------------------------------------------------  
def GetFileList(FindPath,FlagStr=[]):  
    ''' 
    #获取目录中指定的文件名 
    #>>>FlagStr=['F','EMS','txt'] #要求文件名称中包含这些字符 
    #>>>FileList=GetFileList(FindPath,FlagStr) # 
    '''  
    #import os  
    FileList=[]  
    FileNames=os.listdir(FindPath)  
    if (len(FileNames)>0):  
       for fn in FileNames:  
           if (len(FlagStr)>0):  
               #返回指定类型的文件名  
               if (IsSubString(FlagStr,fn)):  
                   fullfilename=os.path.join(fn+'.arl')  
                   FileList.append(fullfilename)  
           else:  
               #默认直接返回所有文件名  
               fullfilename=os.path.join(fn+'.arl')  
               FileList.append(fullfilename)  
  
    #对文件名排序  
    if (len(FileList)>0):  
        FileList.sort()  
  
    return FileList

def GetFilePathList(FindPath,FlagStr=[]):  
    ''' 
    #获取目录中指定的文件名 
    #>>>FlagStr=['F','EMS','txt'] #要求文件名称中包含这些字符 
    #>>>FileList=GetFileList(FindPath,FlagStr) # 
    '''  
    #import os  
    FileList=[]  
    FileNames=os.listdir(FindPath)  
    if (len(FileNames)>0):  
       for fn in FileNames:  
           if (len(FlagStr)>0):  
               #返回指定类型的文件名  
               if (IsSubString(FlagStr,fn)):  
                   fullfilename=os.path.join(FindPath,fn)  
                   FileList.append(fullfilename)  
           else:  
               #默认直接返回所有文件名  
               fullfilename=os.path.join(FindPath,fn)  
               FileList.append(fullfilename)  
  
    #对文件名排序  
    if (len(FileList)>0):  
        FileList.sort()  
  
    return FileList
###########
###########
datadir = '/data/forecast/simulation/rain/WRFV3/test/em_real/rain_wrf_100chem'
FILEout_list=GetFileList(datadir,['wrfout','d01'])
FILEin_list=GetFilePathList(datadir,['wrfout','d01'])
#---- Set output data file
#outfn=[]
#for i in FILEout_list :
#    changename=i+'.arl'
#    outfn.append(changename)
#---- Read a netCDF data file
for outfn,infn in zip(FILEout_list,FILEin_list):
    if os.path.exists(outfn):
        os.remove(outfn)
    print(outfn,infn)
    inf = addfile(infn)
    print 'NetCDF file has been opened...'
    #---- Set output ARL data file
    arlf = addfile(outfn, 'c', dtype='arl')
    #---- Set variable and level list
    wvar2d = ['HGT','PSFC','PBLH','UST','SWDOWN','HFX','LH','T2','U10','V10','RAINNC']
    wvar3d = ['P','T','U','V','W','QVAPOR']
    avar2d = ['SHGT','PRSS','PBLH','USTR','DSWF','SHTF','LHTF','T02M','U10M','V10M','TPPA']
    avar3d = ['PRES','TEMP','UWND','VWND','WWND','SPHU']
    wv = inf['P']
    nx = wv.dimlen(wv.ndim - 1)
    ny = wv.dimlen(wv.ndim - 2)
    levels = wv.dimvalue(wv.ndim - 3)
    nz = len(levels)
    arlf.setlevels(levels)
    arlf.set2dvar(avar2d)
    for l in levels:
        arlf.set3dvar(avar3d)
    #---- Constant for poisson's equation
    cp = 1004.0         # J/kg/K; specific heat
    grav = 9.81         # m/s**2; gravity
    rdry = 287.04       # J/kg/K; gas constant
    rovcp = rdry / cp   # constant for poisson's equation
    #---- Write ARL data file
    arlf.setx(wv.dimvalue(wv.ndim - 1))
    arlf.sety(wv.dimvalue(wv.ndim - 2))
    tNum = inf.timenum()
    fhour = 0
    for t in range(0, tNum):
        print 'Time index: ' + str(t)
        atime = inf.gettime(t)   
        print atime.strftime('%Y-%m-%d %H:00') 
        dhead = arlf.getdatahead(inf.proj, 'AWRF', 1, fhour)  
        #Pre-write index record without checksum - will be over-write latter
        arlf.writeindexrec(atime, dhead)
        #Checksum list
        ksumlist = []
        # Write 2d variables
        ksums = []
        for avname,wvname in zip(avar2d, wvar2d):        
            #print avname + ' ' + wvname
            gdata = inf[wvname][t,:,:]
            if avname == 'PRSS':
                gdata = gdata * 0.01
            elif avname == 'TPPA':
                gdata = gdata * 0.001
            ksum = arlf.writedatarec(atime, 0, avname, fhour, 99, gdata)
            ksums.append(ksum)
        ksumlist.append(ksums)
        # Write 3d variables
        for lidx in range(0, nz):
            ksums = []
            #print lidx
            pp = inf['P'][t,lidx,:,:]
            pb = inf['PB'][t,lidx,:,:]
            pres = pp + pb        
            uwnd = inf['U'][t,lidx,:,:]               
            vwnd = inf['V'][t,lidx,:,:]        
            temp = inf['T'][t,lidx,:,:]
            #potential to ambient temperature
            temp = (temp + 300.) * (pres / 100000.) ** rovcp        
            sphu = inf['QVAPOR'][t,lidx,:,:]        
            wwnd = inf['W'][t,lidx+1,:,:]
            #convert vertical velocity from m/s to hPa/s using omega = -W g rho
            wwnd = -wwnd * grav * pres * 0.01 / (rdry * temp * (1.0 + 0.6077 * sphu))
    
            pres = pres * 0.01
            ksum = arlf.writedatarec(atime, lidx + 1, 'PRES', fhour, 99, pres)
            ksums.append(ksum)
            ksum = arlf.writedatarec(atime, lidx + 1, 'TEMP', fhour, 99, temp)
            ksums.append(ksum)
            ksum = arlf.writedatarec(atime, lidx + 1, 'UWND', fhour, 99, uwnd[:,:nx])
            ksums.append(ksum)
            ksum = arlf.writedatarec(atime, lidx + 1, 'VWND', fhour, 99, vwnd[:ny,:])
            ksums.append(ksum)
            ksum = arlf.writedatarec(atime, lidx + 1, 'WWND', fhour, 99, wwnd)
            ksums.append(ksum)       
            ksum = arlf.writedatarec(atime, lidx + 1, 'SPHU', fhour, 99, sphu)
            ksums.append(ksum)
            ksumlist.append(ksums)
        #Re-write index record with checksum
        arlf.writeindexrec(atime, dhead, ksumlist)
        fhour += 6
    arlf.close()
print 'Finished!'
