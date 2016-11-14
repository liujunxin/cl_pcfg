from collections import defaultdict
#载入训练好的模型
def loadmodel(modelfile = ""):
    nonterminal = []
    lexicalRule = defaultdict(float)
    syntacticRule = defaultdict(float)
    with open(modelfile, "r") as f:
        for line in f:
            temp = line.replace("\n", "").split(" # ")
            if not temp[0] in nonterminal:
                nonterminal.append(temp[0])
            right = temp[1].split()
            if len(right) == 1:
                lexicalRule[(temp[0], right[0])] = float(temp[2])
            elif len(right) == 2:
                syntacticRule[(temp[0], right[0], right[1])] = float(temp[2])
    return nonterminal, lexicalRule, syntacticRule

#根据bp表得到解析的语法树的括号表示
def getTree(words, A, bp, left, right):
        if left == right:
            return "(" + A + " " + words[left - 1] + ")"
        else:
            B, C, mid = bp[(A, left, right)]
            return "(" + A + getTree(words, B, bp, left, mid) + getTree(words, C, bp, mid+1, right) + ")"

#CYK算法解析句子
def CYKparser(sentence, nonterminal, lexicalRule, syntacticRule):
    words = sentence.split()
    slen = len(words)
    chart = defaultdict(float)
    bp = {}
    for i in range(1, slen + 1):
        for N in nonterminal:
            chart[(N, i, i)] = lexicalRule[(N, words[i - 1])]
    for i in range(1, slen):
        for left in range(1, slen - i + 1):
            right = left + i
            for (A, B, C) in syntacticRule.keys():
                for mid in range(left, right):
                    prob = chart[(B, left, mid)] * chart[(C, mid+1, right)] * syntacticRule[(A, B, C)]
                    if prob > chart[(A, left, right)]:
                        chart[(A, left, right)] = prob
                        bp[(A, left, right)] = (B, C, mid)
    if not chart["S", 1, slen] > 0:
        raise SyntaxError("error sentence!")
    parseTree = getTree(words, "S", bp, 1, slen)
    return chart["S", 1, slen], parseTree

#计算内向概率
def calInside(sentence, nonterminal, lexicalRule, syntacticRule):
    words = sentence.split()
    slen = len(words)
    inside = defaultdict(float)
    for i in range(1, slen + 1):
        for N in nonterminal:
            inside[(N, i, i)] = lexicalRule[(N, words[i - 1])]

    for i in range(1, slen):
        for p in range(1, slen - i + 1):
            q = p + i
            for(A, B, C) in syntacticRule.keys():
                for d in range(p, q):
                    if inside[(B, p, d)] and inside[(C, d + 1, q)]:
                        inside[(A, p, q)] += syntacticRule[(A, B, C)] * inside[(B, p, d)] * inside[(C, d + 1, q)]

    return inside

#计算外向概率
def calOutside(sentence, nonterminal, lexicalRule, syntacticRule, inside):
    words = sentence.split()
    slen = len(words)
    outside = defaultdict(float)
    outside[("S", 1, slen)] = 1
    for p in range(1, slen + 1):
        for q in range(slen, 0, -1):
            # if(p == 1 and q == slen):
            #     continue
            for (A, B, C) in syntacticRule.keys():
                for e in range(q + 1, slen + 1):
                    outside[(B, p, q)] += outside[(A, p, e)] * syntacticRule[(A, B, C)] * inside[(C, q + 1, e)]
            for (A, C, B) in syntacticRule.keys():
                for e in range(1, p):
                    outside[(B, p, q)] += outside[(A, e, q)] * syntacticRule[(A, C, B)] * inside[(C, e, p - 1)]
    return outside

#将内向概率和外向概率组合用于输出
def getInAndOut(inside, outside):
    ioProbMap = {}
    for i in inside.keys():
        for j in outside.keys():
            if i == j and inside.get(i) != 0 and outside.get(j) != 0:
                    key = '%s # %s # %s # %.8f # %.8f' %(j[0], j[1], j[2], inside.get(i), outside.get(j))
                    ioProbMap[key] = (inside.get(i), outside.get(j))
    ioProbMap = sorted(ioProbMap.items(), key=lambda x:(x[0]))
    ioProbMap.sort(key=lambda x:(x[1]), reverse = True)
    ioProbs = []
    for item in ioProbMap:
        ioProbs.append(item[0])
    return ioProbs

if __name__ == '__main__':
    nonterminal, lexicalRule, syntacticRule = loadmodel("model.txt")
    sentence = "a boy with a telescope saw a girl"
    parsePro, parseTree = CYKparser(sentence, nonterminal, lexicalRule, syntacticRule)
    inside = calInside(sentence, nonterminal, lexicalRule, syntacticRule)
    outside = calOutside(sentence, nonterminal, lexicalRule, syntacticRule, inside)
    ioProbs = getInAndOut(inside, outside)
    with open("parse.txt", "w") as f:
        f.write(parseTree + "\n")
        f.write("%.8f\n" % parsePro)
        for ioProb in ioProbs:
            f.write(ioProb + "\n")
