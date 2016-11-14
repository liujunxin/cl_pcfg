from collections import defaultdict
#树节点
class TreeNode(object):
    def __init__(self, s):
        self.val = s
        self.left = None
        self.right = None

#将语法树由括号表示解析成树节点表示
def parse(sentence = ""):
    sentence = sentence.replace("(", " ( ")
    sentence = sentence.replace(")", " ) ")
    symlist = sentence.split()
    stack = [TreeNode("")]
    while symlist:
        cursym = symlist.pop(0)
        if cursym == "(":
            if not stack[-1].left:
                stack[-1].left = TreeNode(symlist.pop(0))
                stack.append(stack[-1].left)
            elif not stack[-1].right:
                stack[-1].right = TreeNode(symlist.pop(0))
                stack.append(stack[-1].right)
            else:
                raise SyntaxError("error sentence!")
        elif cursym == ")":
            stack.pop()
        else:
            if not stack[-1].left:
                stack[-1].left = TreeNode(cursym)
            else:
                raise SyntaxError("error sentence!")
    return stack[-1].left

#训练PCFG模型
def train(outfile = "", corpus = []):
    corpusTrees = []
    for sentence in corpus:
        corpusTrees.append(parse(sentence))
    ruleMaps = defaultdict(float)
    leftMaps = defaultdict(float)
    for root in corpusTrees:
        stack = [root]
        while stack:
            node = stack.pop()
            if node.left and node.right:
                ruleMaps[node.val + "#" + node.left.val + " " + node.right.val] += 1
                leftMaps[node.val] +=1
                stack.append(node.right)
                stack.append(node.left)
            elif node.left:
                ruleMaps[node.val + "#" + node.left.val] += 1
                leftMaps[node.val] +=1
    for key in ruleMaps:
        ruleMaps[key] /= leftMaps[key.split("#")[0]]
    sortedMaps = sorted(ruleMaps.items(), key=lambda x:(x[0]))
    sortedMaps.sort(key=lambda x:(x[1]), reverse = True)
    with open(outfile, "w") as f:
        for rule in sortedMaps:
            string = rule[0].replace("#", " # ") + " # %.8f\n" % rule[1]
            f.write(string)

if __name__ == '__main__':
    corpus1 = "(S(NP(DT the)(NN boy))(VP(VP(VBD saw)(NP(DT a)(NN girl)))(PP(IN with)(NP(DT a)(NN telescope)))))"
    corpus2 = "(S(NP(DT the)(NN girl))(VP(VBD saw)(NP(NP(DT a)(NN boy))(PP(IN with)(NP(DT a)(NN telescope))))))"
    train("model.txt", [corpus1, corpus2])
