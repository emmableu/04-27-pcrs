
import copy
import math
import re


class Basket():
    items = []  # Apple,orange,....

    def __init__(self, items):
        self.items = items

    def setItems(self, items):
        self.items = items

    def __str__(self):
        mystr = 'Basket[ '
        for i in self.items:
            mystr = mystr + i + ' , '
        mystr += ']'
        return mystr


class Custom():
    baskets = []  # basket1,basket2
    mapNums = set()  # maped num

    def __init__(self, baskets):
        self.baskets = baskets

    def setBaskets(self, baskets):
        self.baskets = baskets

    def setMapedNums(self, mapNums):
        self.mapNums = mapNums

    def __str__(self):
        mystr = 'Custom[ '
        for i in self.baskets:
            mystr = mystr + i.__str__() + ' , '
        mystr += ']'
        return mystr

    def getMapedNums(self):
        return self.mapNums


class AprioriAll():
    customs = []
    minSuppCount = 0  # count  number ,considering the min_supp and the num of transactions
    allBaskets = []
    transMap = {}

    def __init__(self, min_supp=0.4, datafile='aprioriall.txt'):
        inputfile = open(datafile, "r")
        self.min_supp = min_supp
        baskets = []
        self.customs = []
        for line in inputfile.readlines():
            if (line != "\n"):
                items = re.compile(r"\w+").findall(line)
                basket = Basket(items)
                baskets.append(basket)
            else:
                custom = Custom((baskets))
                self.customs.append(custom)
                baskets = []
                # add the last custom
        custom = Custom((baskets))
        self.customs.append(custom)

        self.minSuppCount = math.ceil(min_supp * len(self.customs))

    def sortPhase(self):
        '''sort the transaction db :with  customer-id as the major key and
        transaction-time as the minor key. '''
        # has been done in the constructor
        pass

    def litemsetPhase(self):
        ''' find all the fequent-itemsets whose support is above the threshold'''
        '''
        假设给定支持度阈值0.4，则项集计算最小的重复次数应该为supportCount=0.4*len(sequcences)=0.4*5=2。
        同样首先得到频繁1项集，为[’30’], [’40’], [’70’], [’90’] （因为10只在seq2中出现一次，知道直到不能产生候选项集为止。
        本例中得到的频繁项集为4个频繁1-itemset和1个频繁2-itemset：[[’30’], [’40’], [’70’], [’90’], [’40’, ’70’]]。
               
        '''
        litemset = []
        items = []
        allBaskets = []
        for custom in self.customs:
            for basket in custom.baskets:
                allBaskets.append(basket)
                for item in basket.items:
                    if [item] not in items:
                        items.append([item])

        items.sort()

        # remove who blow the threshold
        candidates = items
        while True:
            temp = []
            for item1 in candidates:
                count = 0
                for basket in allBaskets:
                    set1 = set(item1)
                    if set1.issubset(basket.items):
                        count += 1
                if count >= self.minSuppCount:
                    print("Frequent %d-itemset : %s" % (len(item1), item1))
                    temp.append(item1)
                    litemset.append(item1)

            candidates = self.__genCandidate(temp)
            if len(candidates) == 0:
                break
        self.allBaskets = allBaskets
        return litemset

    def transformationPhase(self, transmap):

        '''
        '''
        '''
        构造一个Map，例如本例中transformation map :
        {1: [’30’], 2: [’40’], 3: [’70’], 4: [’90’], 5: [’40’, ’70’]}，
        然后再次扫描交易序列数据，得到新的序列数据集】：

        newseq1:{1, 4}
        newseq2: {1, [2, 3, 5]},
        newseq3: {1, 3}
        newseq4:{1, [2, 3, 5], 4},
        newseq5: {4}
        '''
        for custom in self.customs:
            mapNums = set()  # store the maped numbers of each custom
            for basket in custom.baskets:
                for k in transmap.keys():
                    s1 = set(transmap[k])
                    s2 = set(basket.items)
                    if s1.issubset(s2):
                        mapNums.add(k)
            custom.setMapedNums(mapNums)

    def sequencePhase(self, mapNums):
        ''''''
        '''
        序列阶段，采取同样的方式计数，子集在newseq中则count++,最后count数量大于supportCount保留下来，先得到频繁
        (以下是有错的）
        1-itemset：[1], [2], [3], [4], [5]，进而得到
        2-itemset：[1, 2], [1, 3], [1, 4], [1, 5], [2, 3], [2, 5], [3, 5]；
        3-itemset：[1, 2, 3], [1, 2, 5], [1, 3, 5], [2, 3, 5]
        4-itemset：[1, 2, 3, 5] (这个很明显，在newseq2和newseq4中出现两次刚好等于给定的阈值)
        '''
        item1set = set()  #
        for num in mapNums:
            item1set = item1set.union(num)

        item1list = list(item1set)
        item1list.sort()

        seqresult = []
        candidates = []
        for item in item1list:
            candidates.append([item])
        while True:
            for item in candidates:
                count = 0
                for seq in mapNums:
                    s1 = set(item)
                    if s1.issubset(seq):
                        count += 1
                if count >= self.minSuppCount:
                    print("Frequent %-itemsets : %s" % (len(item), item))
                    seqresult.append(item)
            candidates = self.__genCandidate(candidates)
            if len(candidates) == 0:
                break
        return seqresult

    def maxSeq(self, seqs):
        ''''''
        '''
        
        Maximal Phase最大化序列阶段，例如在本例中，一个频繁3-itemset:[1, 2, 3],就包含了频繁1-itemset3个，
        频繁2-itemset也是3个（[1, 2], [1, 3],[2, 3], ）那么这些被包含的也都将被删除，悲剧的是它自己也被那个频繁4-itemset：
        [1, 2, 3, 5]包含，所以也删除掉。最后就剩下一个频繁2-itemset，和一个频繁4-itemset：[[1, 4], [1, 2, 3, 5]]，
        已经得到最大化的序列了，最后只需要根据前面用到的map，转换一下即可，
        即得到序列模式两个<[’30’], [’90’]> 和<[’30’], [’40’], [’70’], [’40’, ’70’]>
        '''
        maxSeq = copy.deepcopy(seqs)
        for seq in seqs:
            t_set = set(seq)
            for seq1 in seqs:
                t_set1 = set(seq1)
                if t_set1 != t_set and t_set1.issuperset(t_set):
                    maxSeq.remove(seq)
                    break
        return self.__map2seq(maxSeq)

    def createTransMap(self, litemset):
        transmap = {}
        value = 1
        for each in litemset:
            transmap[value] = each
            value += 1
        self.transMap = transmap
        return transmap

    def __map2seq(self, seqs):
        # transform numseq to original seq
        origSeqs = []
        for seq in seqs:
            origSeq = []
            for item in seq:
                origSeq.append(self.transMap[item])
            origSeqs.append(origSeq)
        return origSeqs

    def __genCandidate(self, frequentItems):
        # gen new canidate
        length = len(frequentItems)
        result = []  # add one item
        for i in range(length):
            for j in range(i + 1, length):
                if self.__lastDiff(frequentItems[i], frequentItems[j]):
                    item = copy.deepcopy(frequentItems[i])
                    item.insert(len(frequentItems[i]), frequentItems[j][len(frequentItems[j]) - 1])
                    if False == self.__has_inFrequentItemsets(frequentItems, item):
                        result.append(item)
        return result

    # check if there is none  subsets of item in the frequentItems
    def __has_inFrequentItemsets(self, frequentItems, item):
        import SetTool
        subs = SetTool.getSubSets(item, len(item) - 1)
        for each in subs:
            flag = False
            for i in frequentItems:
                if i == each:
                    flag = True
                    break
            if flag == False:
                return True
        return False  # there is at least one subset in the freq-items

    def __lastDiff(self, items1, items2):
        if len(items2) != len(items1):  # length should be the same
            return False
        if items1 == items2:  # if all the same,return false
            return False
        return items1[:-1] == items2[:-1]


if __name__ == '__main__':
    aa = AprioriAll(min_supp=0.4, datafile='aprioriall2.txt')
    '''
    通过设定min_supp， 确定我们要找的是至少重复两次的序列
    '''
    litemset = aa.litemsetPhase()
    print("litemset:");
    print(litemset)
    transmap = aa.createTransMap(litemset);
    print("transformation map :");
    print(transmap)
    aa.transformationPhase(transmap)
    customs = aa.customs
    mapNums = []
    for each in customs:
        mapNums.append(each.getMapedNums())
    seqNums = aa.sequencePhase(mapNums)
    maxSeqs = aa.maxSeq(seqNums)
    print("The sequential patterns :");
    print(maxSeqs)