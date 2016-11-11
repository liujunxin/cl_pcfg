from collections import defaultdict
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

def getTree(words, A, bp, left, right):
        if left == right:
            return "(" + A + " " + words[left - 1] + ")"
        else:
            B, C, mid = bp[(A, left, right)]
            return "(" + A + getTree(words, B, bp, left, mid) + getTree(words, C, bp, mid+1, right) + ")"

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

def writeBridge(sentence, nonterminal, lexicalRule, syntacticRule):
    output = []
    inside = insidePro(sentence, nonterminal, lexicalRule, syntacticRule)
    outside = outsidePro(sentence, nonterminal, lexicalRule, syntacticRule, inside)
    for i in inside.keys():
        for j in outside.keys():
            if i[0] == j[0]:
                if i[1] == j[1] and i[2] == j[2] and (inside.get(i) != 0 and outside.get(j) != 0):
                    s = '%s # %s # %s # %.6f # %.6f' %(j[0], j[1], j[2], inside.get(i), outside.get(j))
                    output.append(s)
    output.sort()
    return output


def insidePro(sentence, nonterminal, lexicalRule, syntacticRule):
    inside = defaultdict(float)
    x = sentence.split()
    n = len(x)
    for i in range(1,1+n):
        w = x[i-1]
        for X in nonterminal:
            inside[X, i, i] = lexicalRule[(X, w)]

    for l in range(1,n):
        for i in range(1,n-l+1):
            j = i+l
            for(A, B, C) in syntacticRule.keys():
                for k in range(i,j):
                    if inside[B, i, k] and inside[C, k+1, j]:
                        inside[A, i, j] += syntacticRule[(A, B, C)] * inside[B, i, k] * inside[C, k+1, j]

    if inside["S", 1, n]:
        return inside
    else:
        print(y)


def outsidePro(sentence, nonterminal, lexicalRule, syntacticRule, inside):
    outside = defaultdict(float)
    x = sentence.split()
    n = len(x)
    outside["S", 1, n] = 1
    for i in range(1,n+1):
        for j in range(n,0,-1):
            if(i==1 and j ==n):
                continue
            for (B, C, A) in syntacticRule.keys():
                for k in range(1,i):
                    outside[A, i, j] += syntacticRule[(B, C, A)] * inside[C, k, i-1] * outside[B, k, j]
            for (B, A, C) in syntacticRule.keys():
                for k in range(j+1, n+1):
                    outside[A, i, j] += syntacticRule[(B,A,C)] * inside[C, j+1, k] * outside[B, i, k]
    return outside

if __name__ == '__main__':
    nonterminal, lexicalRule, syntacticRule = loadmodel("model.txt")
    sentence = "a boy with a telescope saw a girl"
    parsePro, parseTree = CYKparser(sentence, nonterminal, lexicalRule, syntacticRule)
    ioProbs = writeBridge(sentence, nonterminal, lexicalRule, syntacticRule)
    with open("parse.txt", "w") as f:
        f.write(parseTree + "\n")
        f.write("%s\n" % parsePro)
        for ioProb in ioProbs:
            f.write(ioProb + "\n")
