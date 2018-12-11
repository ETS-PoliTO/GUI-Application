import pandas as pd
import sqlalchemy


#True => could be hidden
#false => NOT hidden

def isHidden (mac):
    n = int(mac.replace(":",''), 16)
    bin = format(n, '0>48b')
    if(bin[6]=="1"):
        #print(mac)
        #print("This mac address could be an hidden one!")
        return True
    else:
        #print(mac)
        #print("This mac is not hidden!")
        return False

class DbQuery:

    def __enter__(self):

        self.engine = sqlalchemy.create_engine('mysql+mysqlconnector://gallottino:pds@localhost:3306/pds')
        return self

    # intervallo in 2018-06-03 16:11:00 verrà scritto cosi
    # n numero di 5 10 15 min
    def n_devices(self, ts, n, room):
        
        self.df = pd.read_sql('select * from devices', self.engine)
        self.df = self.df[self.df.ROOMID == str(room)]
        
        ndevice = []
        for i in range(0,n):
            df1=self.df[(self.df.TID >= ts+i*60) & (self.df.TID < ts + (i+1)*60)]
            df1=df1.drop_duplicates(subset=['MAC'])
            df1=findHiddenMAC(df1)
            #print(df1)
            ndevice.append(df1.MAC.count())
        #print(ndevice)
        return ndevice

    def last_minute(self, room,timestamp):
        
        self.df = pd.read_sql('select * from pds.devices', self.engine)
        self.df=self.df[self.df.ROOMID==str(room)]
        timestamp = timestamp - 60
        #timestamp = self.df.TID.max()
        self.df=self.df[(self.df.TID<=timestamp) & (self.df.TID>timestamp-60)]
        #self.df=self.df.drop_duplicates()#DEBUG    
        self.df=self.df.drop_duplicates(subset=['MAC']) 
        #print(self.df)
        self.df = findHiddenMAC(self.df)
        #print(self.df)
        mac = self.df.MAC.tolist()
        x = self.df.X.tolist()
        y = self.df.Y.tolist()
        
        print("FINITO QUERY")
        return mac, x, y

    def long_period_stat (self, t_inizio, t_fine, room, num):
        
        
        self.df = pd.read_sql('select * from devices', self.engine)
        self.df = self.df[self.df.ROOMID == str(room)].drop_duplicates(subset=['MAC','TID'])
        df1 = self.df[(self.df.TID <= t_fine) & (self.df.TID > t_inizio)]
        df3=pd.DataFrame(columns=df1.columns)
        if abs(t_fine-t_inizio)<60*60:
            k=2*60
            q=60*60
        elif abs(t_fine-t_inizio)<60*60*24:
            k=60*30
            q=60*60
        elif abs(t_fine-t_inizio)<60*60*24*7:
            k=60*60*2
            q=60*60*24
        else:
            k=60*60*24
            q=60*60*24
            
        while t_fine>t_inizio:
            df2=df1[(self.df.TID <= t_fine) & (self.df.TID > t_fine-k)].drop_duplicates(subset=['MAC'])
            t_fine-=k
            df3 = pd.concat([df3, df2], ignore_index=True)

        #print(df3) 
        
        print("HO FINITO IL FOR")
        df4=df3
        df3=df3.groupby('MAC').MAC.agg('count').to_frame('COUNT').reset_index()
        df3=df3.sort_values('COUNT', ascending=[False]).head(num)
        macs=df3.MAC.tolist()
        freq=df3.COUNT.tolist()
        
        print(macs,freq)        
        
        max_tid = df4.TID.max()
        min_tid = df4.TID.min()
        t1=max_tid-max_tid%q+q
        t2=min_tid-min_tid%q
        intervalli = dict()
        for mac in macs:
            df_tmp=df4[df4.MAC==mac]
            i=t1
            tis = []
            while i!=t2:
                a=df_tmp[(df_tmp.TID <= i) & (df_tmp.TID > i-q)].TID.count()
                if a > 0:
                    tis.append(i-q)
                i = i - q
            intervalli[mac] = tis
        #intervalli contiene per un determiato mac i valori (in timestamp) delle ore in cui è rilevato (ora inzio)
        
        print("HO Fatto")        
        
        return intervalli,macs, freq

    def movement (self, t_inizio, t_fine, room):

        self.df = pd.read_sql('select * from devices', self.engine)
        self.df = self.df[self.df.ROOMID == str(room)]
        self.df = self.df[(self.df.TID <= t_fine) & (self.df.TID > t_inizio)]
        #self.df=self.df[(self.df.X<=4) & (self.df.Y<=2.6)] #DEBUG
        print(self.df[['MAC','TID','X','Y']])
        self.df = findHiddenMAC(self.df)
        intervallo = dict()
        i = t_fine
        print(i)
        while i>t_inizio:
            macz = dict()
            df1 = self.df[(self.df.TID <= i) & (self.df.TID > i - 60)].drop_duplicates(subset=['MAC'])
            #df1 = findHiddenMAC(df1)
            macs = df1.MAC.tolist()
            x = df1.X.tolist()
            y = df1.Y.tolist()
            j=0
            while j!=len(macs):
                macz[j] = (macs[j], x[j], y[j])
                j=j+1
            intervallo[i]=macz
            i=i-60
        print(len(intervallo))
        return intervallo

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.engine.dispose()



def findHiddenMAC (df):
    #print(df[['MAC', 'X', 'Y', 'TID', 'HTCI']])   
    df3=df[df.HTCI.isnull()]
    df2=df[df.MAC.apply(isHidden)!=True] #dataframe di mac normali
    df2 = df2[df2.HTCI.notnull()]
    df = df[df.MAC.apply(isHidden) == True] #dataframe di mac nascosti
    df = df[df.HTCI.notnull()]
    df2 = pd.concat([df2, df3], ignore_index=True)
    

    #resetto gli indici
    df=df.reset_index(drop=True) #database dove opero
    df2 = df2.reset_index(drop=True)
    
    #clusterizzazione
    UniqueHTCI = df.HTCI.unique()
    
    clusters = {elem: pd.DataFrame for elem in UniqueHTCI}
    for key in clusters.keys():
        clusters[key] = df[:][df.HTCI == key]
    final_cluster = []
    
    for key1 in clusters.keys():
        clusters[key1] = clusters[key1].sort_values('TID', ascending=[False])
        clusters[key1] = clusters[key1].reset_index(drop=True)
        subclusters = []
        for i in range(len(clusters[key1])):
            flag=0
            for j in range(len(subclusters)):

                if (abs(subclusters[j].TID.min()-clusters[key1].loc[i].TID)<100):
                    subclusters[j].loc[len(subclusters[j])]=clusters[key1].loc[i]
                    flag=1
                else:
                    flag=0

            if flag==0:

                df1=pd.DataFrame(columns=df.columns)
                df1.loc[0]=clusters[key1].loc[i]
                subclusters.append(df1)
        #print(subclusters)
        final_cluster+=subclusters
        
    count = 1
    #ricostituisco il dataframe sostituendo i mac nascosti con HiddenMACN
    for i in range(0,len(final_cluster)):

        n=final_cluster[i].HASH.count()
        if n==0:
            df2 = pd.concat([df2, final_cluster[i]], ignore_index=True)
        else:
            str1 = 'HiddenMAC' + str(count)

            count = count +1
            final_cluster[i].MAC = str1
            final_cluster[i]=final_cluster[i].drop_duplicates(subset=['MAC'])
            df2=pd.concat([df2, final_cluster[i]], ignore_index=True)
    #print (df2.MAC)

    return df2
