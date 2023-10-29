import time
import random
from BitHash import BitHash
import sys
import math
import pytest
from BitHash import ResetBitHash

#"I hereby certify that this program is solely the 
#result of my own work and is in compliance with the Academic Integrity 
#policy of the course syllabus and the academic integrity policy of the 
#CS department.”

class Link(object):
    def __init__(self, k, d):
        self.key  = k
        self.data = d

class CuckooHash(object):
    def __init__(self, size): #size is the amount of buckets (in EACH tab) 
        self.__tab1= [None] * size 
        self.__tab2= [None] * size
        self.__numKeys = 0        
    
    #returns number of keys in the cuckoo hash at the time
    def __len__(self):
        return self.__numKeys    
    
    
    def __findLink(self, k): 
        #check for the key in both arrrays 
        
        #check in tab1
        bucket1= BitHash(k,1) % len(self.__tab1)        #get Bucket for tab1
        l=self.__tab1[bucket1] 
        if l!=None and l.key==k:                         #check if k is there
            
            #return the link, the bucket, and # of which tab it is in          
            return l,bucket1,1  
        
        #check tab2
        bucket2= BitHash(k,2) % len(self.__tab2)        #get Bucket for tab2
        l=self.__tab2[bucket2]
        if l!=None and  l.key==k:                        #check if k is there 
                
                #return the link, the bucket, and # of which tab it is in  
                return l,bucket2,2  

        return None,bucket1,1 #otherwise return None (and the place in tab1 it
                              # it would go to
   
    #wrapper for findLink that returns only the dats ( if key was found) 
    def find(self, k): 
        l,bucket,HashTab= self.__findLink(k)
        return l.data if l else None
   
    def insert(self,k,d):
      
        #first check if its already there, if it is, return False
        l,bucket,HashTab= self.__findLink(k)
        if l: return False
        
        #if tabs completely full already -> growHash
        if self.__numKeys>=(len(self.__tab1) *2): self.__growHash()
        
        
        #start with trying to insert into tab1
        tab= self.__tab1 #start w Hashtab 1 
        val= 1 #hash val for tab1
        otherTab= self.__tab2
        loopCount=0 
        
        threshhold= 100    #the max amount of loops, before growing or reseting
        while loopCount< threshhold :#limit number loops is 
            
            #hash according to the tab your trying to insert into
            bucket= BitHash(k,val) % len(self.__tab1)
            
            #create the link 
            l = Link(k, d)  
            
            if tab[bucket]==None:           #if the bucet in tab1 is available
                tab[bucket]=l               #then insert the link 
                self.__numKeys+=1           #incriment numKeys 
                return True                 #return flag, exit function 
                
           
            else: #if spot occupied, evict and insert evictee into other tab
                
                #UPDATE k: 
                #get the link that is to be evicted 
                evictee= tab[bucket]        #save evictee
                k= evictee.key              #now gonna insert this key 
                d= evictee.data
                
                #put in the inserted one: 
                tab[bucket]=l
                
                #UPDATE tab: 
                #swap what is now tab with what is currently other 
                #new k will will try inserting into other HashTab
                temp= tab
                tab= otherTab
                otherTab=temp 
                
                loopCount+=1                 #incriment loop count
                
                #UPDATE hash val (because switching tabs): 
                #to alternate Hash Functions, update val to 1 or 2 
                if loopCount%2==1:    #when odd loop count, set the val to 
                    val=2             # the val for tab2 
                                     
                                      # starting from first time it reaches here 
                                      # when loopCount = 1 ( switches to tan2) 
                else: val= 1     
                
     #  if got here, too many loops, lets see whats wrong:  
        
        #tables may be too full key- so growHash ( only if more than half full) 
        if self.__numKeys>= len(self.__tab1):  #size 
            self.__growHash() 
            self.insert(k,d)                  #insert whatever key, return flag
            return True 
          
            
        #otherwise, it must have just ran an into an infinate loop 
        #so reHash it all and ResetBitHash
        #dont want to grow to much uncesisarily 
        else: 
            self.__reHash()
            self.insert(k,d) 
            return True #need these return statements 
                        #because the True flag in the actual insert ( in while 
                        #loop will make this insert call True) but we also want
                        # a True flag for the overall onsert that we were 
                        # inserting origionally 
        
    def delete(self,k):
       
        #find where it is 
        l,bucket,HashTab= self.__findLink(k)
        if not l: return False
        
        if HashTab==1: #found it in tab1
            self.__tab1[bucket]=None         #delete the link 
            self.__numKeys-=1
            return True
       
        else: #found in tab2
            self.__tab2[bucket]=None        #delete the link 
            self.__numKeys-=1
            return True
        
    def __growHash(self):
        
        temp1= self.__tab1                 #store the 2 tabsin variables
        temp2= self.__tab2
        
        self.__numKeys=0                   #empty the origional tabs
        
        #make the tabs of the cuckoo hash empty but double the size 
        self.__tab1= [None] *(2*len(temp1))
        self.__tab2= [None] *(2*len(temp2))
        
        
        #re- insert its links into the newly expanded tabs
        for bucket in  range(len(temp1)):     #go through buckets of old tabs
            
            #re-insert/reHash the links into the cuckoo hash w larger tabs
            l=temp1[bucket]                 #get link
            if l: self.insert(l.key,l.data) #insert
            
            j=temp2[bucket]                 #get link 
            if j: self.insert(j.key,j.data) #insert
       
        
    def __reHash(self): 
        ResetBitHash()             #reset the hash function 
        temp1= self.__tab1         #store the 2 tabs in variables
        temp2= self.__tab2
        
        self.__numKeys=0           #reset numKeys ( because emptying the tab) 
        
        #make the tabs of the cuckoo hash empty 
        self.__tab1= [None] *(len(temp1))
        self.__tab2= [None] *(len(temp2))
       
        #re- insert its links ( using the new hash) 
        for bucket in  range(len(temp1)):  #go through buckets of old tabs
            
            #re-insert/reHash the links into the cuckoo hash w larger tabs
            l=temp1[bucket]                 #get link
            if l: self.insert(l.key,l.data) #insert
            
            j=temp2[bucket]                 #get link 
            if j: self.insert(j.key,j.data) #insert
       
            
    def printHash(self):
        print("  tab1 | tab2" )
        for i in range(len(self.__tab1)):
            print(str(i)+ ": ",end="")
            
            l=self.__tab1[i]
            print(str(l.key)+", ",end="") if l else print("None, ",end="")
            
            j=self.__tab2[i]
            print(str(j.key),end="") if j else print("None",end="") 
            
            print()
  
    
    
    
  
    
def __main():
    

  
  
    print()
    print("BIG TEST: INSERTING 100,000 keys")
    b= CuckooHash(50) #many strings ( two tabs of 300) 
    count=0 
    string="hi"
    
    for i in range(100000): #fill it all the way up
        if b.insert(string+str(i),i): 
            count+=1 
    print("count: "+ str(count)) 
  
    count= 0
    for i in range(100000): #is one is not found, this would return it 
        if  b.find("hi"+str(i))!=i: count+=1
        
    print("amount of keys not sucessfully found: "+ str(count))
    
    print("keys successfully inserted: "+str(len(b))) 

if __name__ == '__main__':
        __main() 




#PYTESTS: 



#test that insert works 
# chekc that the eviction mechanism is actually happening 
# hash something to a a full spot in tab1 and see if it evicts and reHashes into
# tab2
def test_insert_few_keys():
    
    a= CuckooHash(5)
    #show that eviction works 
    #because even if the first 5 all went to tab1, there are six inserts here
    #so for them all ti be inserted correctly, a sucessfull evistion must 
    #have occured 
    assert a.insert("hi",1)  
    assert a.insert("hei",2) 
    assert a.insert("hsl",3) 
    assert a.insert("hssi",4) 
    assert a.insert("enf",5) 
    assert a.insert("ef",6) 
    
#test the find function on a few keys 
def test_find_few_keys():
    a= CuckooHash(5)
    #insert 6 distinct keys 
    assert a.insert("hi",1)  
    assert a.insert("hei",2) 
    assert a.insert("hsl",3) 
    assert a.insert("hssi",4) 
    assert a.insert("enf",5) 
    assert a.insert("ef",6) 
        

    #see that they are all found and still assocuated iwth the correct data
    assert a.find("hi")==1  
    assert a.find("hei")==2
    assert a.find("hsl")==3
    assert a.find("hssi")==4 
    assert a.find("enf")==5
    assert a.find("ef")==6
    

    
#test that tons of keys can be sucessfully inserted 
def test_insert_huge_amount():
    
    b= CuckooHash(50) #so it has a total of only 100 slots 
    
    for i in range(100000):                #do 100,000 inserts into it 
        assert b.insert(str(i),i)          #assert its inserted sucessfully
        assert len(b) == i+1               #see that it actually made it in
    
    
##test that tons of keys can be sucessfully found after many  inserted 
#test that it grows properly, to accomoate all the inserts
def test_find_huge_amount():
   
    c= CuckooHash(50)                     #so it has a total of only 100 slots 
    string="hi"
    for i in range(100000):                   #do 100,000 inserts into it 
        assert c.insert(string+str(i),i)      #assert its inserted sucessfully
        
        #see that all keys are found as they go
        assert c.find(string+str(i))== i
    
    #and after all those inserts, check again that all keys can be found 
    #is one is not found, this would return it
    missingKeys=0 
    for i in range(100000):  
        #the data, is i, so if it is found, it returns the associated i 
        if  c.find("hi"+str(i))!= i: missingKeys+=1   
    
    assert missingKeys== 0


#make sure that you cant insert duplicates 
def test_insert_duplicates():
    b= CuckooHash(5) 
    for i in range(50):                  #insert 50 keys ( data is i) 
        b.insert(str(i),i)
    
    assert len(b)==50                   #assert they all made it in
    
    for i in range(50):                  #try to insert 50 identical keys 
        b.insert(str(i),i+1)             #(but with diff data , i+1) 
        
    assert len(b)==50                 #assert that the amount of keys 
                                       #is still 50 and not 100 
                                       #a.k.a these keys could not be inserted) 
   
    for i in range(50):           #make sure that the keys are still 
                                   #associated with the origional data     
        assert b.find(str(i))== i  



#test what happens when you try to delete an item that isnt there
def test_find_nonexistent_key():

    b= CuckooHash(5) 
    for i in range(100):                 #insert 100 keys 
        b.insert(str(i),i)              
    
    assert b.find("8")== 8                #find a key that actually is there 
   
    assert b.find("notThere") is None     #key that should not be found
    assert b.find(" 8 ") is None          #very simlar key to one inserted
    
#test delete( make sure that they can not be found and that numkeys is 
#updated) 
def test_delete():
    #insert 100 inserts 
    b= CuckooHash(50) 
    for i in range(100):               
        b.insert(str(i),i)
    
    assert len(b) ==100
    
    #delete all the keys 
    for i in range(100):               
        b.delete(str(i))    
    
    #see that the cuckooo hash is now empty 
    assert len(b)==0
                              
    #delete all the keys 
    for i in range(100):               
        assert b.find(str(i)) is None        #assert all deleted keys can
                                             #no longer be found
                                             
# test that after an item is deleted, than an identical item can be inserted
def test_insert_after_delete():
    b= CuckooHash(5)             
    b.insert("hi",9)         #insert key
    
    b.delete("hi")            #then delete it         
    
    assert b.insert("hi",9)  # assert that it can be sucessfully re-inserted
    assert b.find("hi")==9   #assert that it can be found associetd w new data
    
#test what happens when you try to delete an item that isnt there
def test_delete_nonexistent_key():

    b= CuckooHash(5) 
    b.insert("hi",9)    #insert keys
    b.insert("hifj",9)
    
    #delete key not in the cukcoo hash, confirm that its not there 
    assert b.delete("notThere")== False
    assert b.delete("nope")== False
    assert b.delete("iDontExist")== False
    




pytest.main(["-v", "-s", "CuckooHash.py"])          

